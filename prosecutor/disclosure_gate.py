"""disclosure_gate.py -- CPIA 1996 prosecution-disclosure outcome enum.

The Criminal Procedure and Investigations Act 1996 (CPIA) imposes two duties
on the prosecutor:

  - s3 initial duty:    disclose to the accused any material that might
                        reasonably be considered capable of undermining the
                        case for the prosecution or of assisting the case
                        for the accused.
  - s7A continuing duty: a continuing obligation to disclose newly-arising
                        material until trial.

The CPIA Code of Practice (2020 revision) requires the disclosure officer to
maintain a schedule of:
  - Used material (will form part of the prosecution case).
  - Unused material (will NOT form part of the prosecution case but may need
    to be disclosed under s3/s7A).
  - Sensitive material (e.g. material attracting public-interest immunity).

This module surfaces a DisclosureOutcome closed-enum (4 states) + a
DisclosureGate that classifies a recorded schedule against the duties.

The library does NOT certify disclosure to the court -- it surfaces structured
compliance posture. The downstream disclosure officer or Crown Prosecutor
remains responsible for certification.

Pure stdlib: dataclasses + enum + datetime. No third-party deps.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# DisclosureOutcome closed-enum (4 states per task brief)
# ---------------------------------------------------------------------------


class DisclosureOutcome(Enum):
    """Closed-enum CPIA disclosure outcomes.

    CPIA_COMPLIANT_FRESH:
        The schedule is fresh (within window), no sensitive material flagged
        as withheld, no unused-material gaps. CPIA s3 initial duty satisfied
        on the recorded evidence.

    SCHEDULE_STALE:
        The schedule was last updated outside the freshness window.
        CPIA s7A continuing duty exposes the prosecutor to a finding of
        non-compliance.

    SENSITIVE_MATERIAL_FLAG:
        Sensitive material flagged on the schedule (e.g. PII applications,
        source-protection, intercept material). MUST go through a separate
        sensitive-material review path before disclosure.

    UNUSED_MATERIAL_INCOMPLETE:
        Unused-material section of the schedule has gaps (entries missing
        a category, or entries referenced from used-material with no schedule
        row). CPIA Code of Practice 2020 para 6.9 violated on the recorded
        evidence.
    """

    CPIA_COMPLIANT_FRESH = "cpia-compliant-fresh"
    SCHEDULE_STALE = "schedule-stale"
    SENSITIVE_MATERIAL_FLAG = "sensitive-material-flag"
    UNUSED_MATERIAL_INCOMPLETE = "unused-material-incomplete"


# Closed-set of all disclosure-test labels used by CPIA_DISCLOSURE_TESTS map.
# Surfaced so a downstream consumer can grep for the list.
CPIA_DISCLOSURE_TESTS: tuple[str, ...] = (
    "schedule-freshness",
    "sensitive-material-review",
    "unused-material-completeness",
    "used-material-cross-reference",
)


# ---------------------------------------------------------------------------
# DisclosureScheduleEntry + DisclosureRequest dataclasses
# ---------------------------------------------------------------------------


class MaterialCategory(Enum):
    """Closed-enum CPIA material categories.

    USED:       material that will form part of the prosecution case.
    UNUSED:     material that will NOT form part of the prosecution case.
    SENSITIVE:  material attracting public-interest immunity / source-protection.
    """

    USED = "used"
    UNUSED = "unused"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class DisclosureScheduleEntry:
    """A single row on a CPIA disclosure schedule.

    entry_id: stable identifier for the entry (e.g. "MG-6C-001").
    category: MaterialCategory closed-enum value.
    description: free-text description of the material.
    is_pii_flagged: whether the entry attracts a PII application.
    """

    entry_id: str
    category: MaterialCategory
    description: str
    is_pii_flagged: bool = False


@dataclass(frozen=True)
class DisclosureRequest:
    """A disclosure-completeness request to the gate.

    schedule_last_updated: date the schedule was last updated.
    freshness_window_days: how many days a schedule remains fresh.
    entries: tuple of DisclosureScheduleEntry rows.
    used_material_referenced_entry_ids: entry ids referenced from the used
        material that MUST appear on the schedule. If any are missing from
        `entries`, the gate returns UNUSED_MATERIAL_INCOMPLETE.
    """

    schedule_last_updated: dt.date
    freshness_window_days: int
    entries: tuple[DisclosureScheduleEntry, ...]
    used_material_referenced_entry_ids: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# DisclosureGate -- the classifier
# ---------------------------------------------------------------------------


class DisclosureGate:
    """Classifier returning a DisclosureOutcome for a DisclosureRequest.

    The classifier walks the schedule entries and returns the first matching
    outcome. The order of checks is:
      1. SCHEDULE_STALE (freshness window check).
      2. SENSITIVE_MATERIAL_FLAG (any sensitive entry OR pii_flagged).
      3. UNUSED_MATERIAL_INCOMPLETE (any used-material referenced id missing).
      4. CPIA_COMPLIANT_FRESH (all checks pass).

    Order matters: a STALE schedule with sensitive material returns STALE
    first, because a stale schedule is the bigger compliance risk and the
    disclosure officer must refresh before any sensitive-review pathway is
    relevant.
    """

    def __init__(self, now: Optional[dt.date] = None) -> None:
        self._now = now or dt.date.today()

    def classify(self, request: DisclosureRequest) -> DisclosureOutcome:
        """Classify the request -> DisclosureOutcome."""
        # 1. Freshness check (stale-first ordering)
        age = (self._now - request.schedule_last_updated).days
        if age > request.freshness_window_days:
            return DisclosureOutcome.SCHEDULE_STALE
        # 2. Sensitive-material flag (any sensitive entry OR pii_flagged)
        if any(
            e.category == MaterialCategory.SENSITIVE or e.is_pii_flagged
            for e in request.entries
        ):
            return DisclosureOutcome.SENSITIVE_MATERIAL_FLAG
        # 3. Unused-material completeness (every used-referenced id present)
        scheduled_ids = {e.entry_id for e in request.entries}
        for ref_id in request.used_material_referenced_entry_ids:
            if ref_id not in scheduled_ids:
                return DisclosureOutcome.UNUSED_MATERIAL_INCOMPLETE
        # 4. All checks passed
        return DisclosureOutcome.CPIA_COMPLIANT_FRESH


# ---------------------------------------------------------------------------
# Convenience module-level function
# ---------------------------------------------------------------------------


def classify_disclosure(
    request: DisclosureRequest, now: Optional[dt.date] = None
) -> DisclosureOutcome:
    """Module-level convenience wrapper around DisclosureGate.classify()."""
    return DisclosureGate(now=now).classify(request)
