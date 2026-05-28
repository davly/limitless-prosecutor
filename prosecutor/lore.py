"""lore.py -- R-AI-SURFACE-CITATION-GATE Profile-B sealed-citation gate.

R-AI-SURFACE-CITATION-GATE cohort discipline (promoted from sage canonical):
when a library surfaces a citation to a CPS Charging Standard, a Sentencing
Council guideline, a CPIA section, or a PACE Code in a user-facing AI surface,
that citation MUST be:

  1. Sealed via L43 Mirror-Mark (cohort-canonical signing).
  2. Marked with an explicit reviewed_by_counsel flag.
  3. Gated through a Profile-B multi-state outcome enum (CitationGateOutcome)
     rather than a boolean "is-citation-valid" -- the Profile-B cohort
     discipline forbids boolean gates on AI-citation surfaces.

Prosecutor implements Profile-B with 5 closed-enum outcomes:
  - ADMITTED:                  citation passes all gates, sealed + reviewed
  - REFUSED_STALE_MANIFEST:    manifest is stale; the cited corpus is no
                               longer current
  - REFUSED_PLACEHOLDER_CORPUS: corpus_sha is placeholder; cannot seal
                               authentically
  - REFUSED_UNREVIEWED:        citation has reviewed_by_counsel=False
  - REFUSED_MALFORMED:         citation text or category fails the schema

The library ships the PRIMITIVE; consumers wire it on their AI surface.

Pure stdlib: dataclasses + enum + hashlib + sys. No third-party deps.
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from . import honest, legal, manifest, mirrormark


# ---------------------------------------------------------------------------
# Citation categories (closed-enum, R115)
# ---------------------------------------------------------------------------


class CitationCategory(Enum):
    """Closed-enum citation categories.

    CPS_CHARGING_STANDARD: CPS Charging Standards corpus citation.
    SENTENCING_GUIDELINE:  Sentencing Council guideline citation.
    CPIA_SECTION:          CPIA 1996 section citation.
    PACE_CODE:             PACE 1984 code citation (A through H).
    OTHER_STATUTORY:       any other statutory citation (Bail Act, POA, etc).
    """

    CPS_CHARGING_STANDARD = "cps-charging-standard"
    SENTENCING_GUIDELINE = "sentencing-guideline"
    CPIA_SECTION = "cpia-section"
    PACE_CODE = "pace-code"
    OTHER_STATUTORY = "other-statutory"


# ---------------------------------------------------------------------------
# Profile-B multi-state outcome enum
# ---------------------------------------------------------------------------


class CitationGateOutcome(Enum):
    """Profile-B multi-state outcome enum for the R-AI-SURFACE-CITATION-GATE.

    Five closed-enum members; ADMITTED is the single success path. All other
    members are refusal-with-specific-reason -- the consumer SHOULD log the
    refusal reason and refuse to render the citation on the AI surface.
    """

    ADMITTED = "admitted"
    REFUSED_STALE_MANIFEST = "refused-stale-manifest"
    REFUSED_PLACEHOLDER_CORPUS = "refused-placeholder-corpus"
    REFUSED_UNREVIEWED = "refused-unreviewed"
    REFUSED_MALFORMED = "refused-malformed"


class CitationGateRefusalReason(Enum):
    """Sub-classification of REFUSED_MALFORMED for callers that want sub-paths."""

    EMPTY_TEXT = "empty-text"
    OVERSIZE_TEXT = "oversize-text"
    INVALID_CATEGORY = "invalid-category"
    EMPTY_BODY = "empty-body"


# Soft maximum size for citation text -- bigger than this almost certainly
# means the consumer is dumping a whole guideline rather than a citation.
MAX_CITATION_TEXT_BYTES: int = 4096


# ---------------------------------------------------------------------------
# SealedCitation dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SealedCitation:
    """A citation sealed with a L43 Mirror-Mark.

    Constructed via seal_citation() rather than directly.

    text: the human-readable citation text.
    category: closed-enum CitationCategory.
    reviewed_by_counsel: honest-default False until a real review has happened.
    body_hash: hex SHA-256 over UTF-8 bytes of text. Stable across deploys.
    mirror_mark: L43 Mirror-Mark v1 string. May be empty when sealing failed
                 (e.g. placeholder corpus) -- check `outcome` not mirror_mark.
    outcome: the Profile-B CitationGateOutcome at seal time.
    refusal_sub_reason: sub-classification when outcome is REFUSED_MALFORMED.
    """

    text: str
    category: CitationCategory
    reviewed_by_counsel: bool
    body_hash: str
    mirror_mark: str
    outcome: CitationGateOutcome
    refusal_sub_reason: Optional[CitationGateRefusalReason] = None


# ---------------------------------------------------------------------------
# seal_citation -- pure-function seal-and-classify entry point
# ---------------------------------------------------------------------------


def _body_hash(s: str) -> str:
    """Hex SHA-256 over UTF-8 bytes."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def seal_citation(
    *,
    text: str,
    category: CitationCategory,
    reviewed_by_counsel: bool,
    corpus_sha: bytes,
    key: bytes,
    current_manifest: Optional[manifest.Manifest] = None,
) -> SealedCitation:
    """Seal a citation + classify via the Profile-B gate.

    Returns a SealedCitation with an outcome in {ADMITTED, REFUSED_*}. The
    library NEVER throws on a refusal -- the consumer decides what to do
    with each outcome.

    Sealing logic:
      - If text is empty / oversize / category not in enum -> REFUSED_MALFORMED.
      - If corpus_sha is placeholder (32x0x00) -> REFUSED_PLACEHOLDER_CORPUS,
        mirror_mark is empty.
      - If current_manifest is stale -> REFUSED_STALE_MANIFEST.
      - If reviewed_by_counsel is False -> REFUSED_UNREVIEWED, mirror_mark
        is still computed (so a downstream reviewer can verify the unreviewed
        citation hasn't been mutated post-flag-flip).
      - Otherwise -> ADMITTED, mirror_mark is computed.
    """
    # Malformed checks (return early, no seal computed)
    if not text:
        return SealedCitation(
            text=text,
            category=category if isinstance(category, CitationCategory) else CitationCategory.OTHER_STATUTORY,
            reviewed_by_counsel=reviewed_by_counsel,
            body_hash="",
            mirror_mark="",
            outcome=CitationGateOutcome.REFUSED_MALFORMED,
            refusal_sub_reason=CitationGateRefusalReason.EMPTY_TEXT,
        )
    if not isinstance(category, CitationCategory):
        return SealedCitation(
            text=text,
            category=CitationCategory.OTHER_STATUTORY,
            reviewed_by_counsel=reviewed_by_counsel,
            body_hash=_body_hash(text),
            mirror_mark="",
            outcome=CitationGateOutcome.REFUSED_MALFORMED,
            refusal_sub_reason=CitationGateRefusalReason.INVALID_CATEGORY,
        )
    if len(text.encode("utf-8")) > MAX_CITATION_TEXT_BYTES:
        return SealedCitation(
            text=text,
            category=category,
            reviewed_by_counsel=reviewed_by_counsel,
            body_hash=_body_hash(text),
            mirror_mark="",
            outcome=CitationGateOutcome.REFUSED_MALFORMED,
            refusal_sub_reason=CitationGateRefusalReason.OVERSIZE_TEXT,
        )

    body_hash = _body_hash(text)
    payload = text.encode("utf-8")

    # Placeholder corpus -- refuse to seal authentically
    if corpus_sha == b"\x00" * 32:
        honest.warn(
            honest.WARN_MIRROR_MARK_PLACEHOLDER,
            "citation seal refused: corpus_sha is placeholder (32x0x00); "
            "marks would not pass cold-verify",
        )
        return SealedCitation(
            text=text,
            category=category,
            reviewed_by_counsel=reviewed_by_counsel,
            body_hash=body_hash,
            mirror_mark="",
            outcome=CitationGateOutcome.REFUSED_PLACEHOLDER_CORPUS,
        )

    # Stale manifest -- refuse to seal against an outdated corpus
    if current_manifest is not None:
        staleness = manifest.is_stale(current_manifest)
        if staleness != manifest.StalenessOutcome.FRESH_BOTH:
            return SealedCitation(
                text=text,
                category=category,
                reviewed_by_counsel=reviewed_by_counsel,
                body_hash=body_hash,
                mirror_mark="",
                outcome=CitationGateOutcome.REFUSED_STALE_MANIFEST,
            )

    # Compute the mark even when unreviewed (so a downstream reviewer can
    # confirm the citation hasn't been mutated when reviewed_by_counsel flips
    # True later).
    try:
        mark = mirrormark.sign(corpus_sha, payload, key)
    except mirrormark.MirrorMarkError:
        return SealedCitation(
            text=text,
            category=category,
            reviewed_by_counsel=reviewed_by_counsel,
            body_hash=body_hash,
            mirror_mark="",
            outcome=CitationGateOutcome.REFUSED_MALFORMED,
            refusal_sub_reason=CitationGateRefusalReason.EMPTY_BODY,
        )

    if not reviewed_by_counsel:
        return SealedCitation(
            text=text,
            category=category,
            reviewed_by_counsel=False,
            body_hash=body_hash,
            mirror_mark=mark,
            outcome=CitationGateOutcome.REFUSED_UNREVIEWED,
        )

    return SealedCitation(
        text=text,
        category=category,
        reviewed_by_counsel=True,
        body_hash=body_hash,
        mirror_mark=mark,
        outcome=CitationGateOutcome.ADMITTED,
    )


def citation_gate(sealed: SealedCitation) -> CitationGateOutcome:
    """Profile-B gate helper -- just returns the outcome attribute.

    Convenience accessor so a consumer's flow can read:
      `if citation_gate(sealed) is CitationGateOutcome.ADMITTED: ...`
    rather than reaching into the dataclass.
    """
    return sealed.outcome
