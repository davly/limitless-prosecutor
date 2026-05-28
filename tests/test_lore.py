"""Tests for prosecutor.lore -- R-AI-SURFACE-CITATION-GATE Profile-B."""
from __future__ import annotations

import datetime as dt

import pytest

from prosecutor import honest, lore, manifest


# A non-placeholder corpus + key for sealing tests.
GOOD_CORPUS = b"\x42" * 32
GOOD_KEY = b"super-secret-key"


def test_citation_category_closed_set():
    """CitationCategory has exactly 5 closed-enum values."""
    values = {c.value for c in lore.CitationCategory}
    assert values == {
        "cps-charging-standard",
        "sentencing-guideline",
        "cpia-section",
        "pace-code",
        "other-statutory",
    }


def test_citation_gate_outcome_closed_set():
    """CitationGateOutcome has exactly 5 outcomes (Profile-B cohort discipline)."""
    values = {o.value for o in lore.CitationGateOutcome}
    assert values == {
        "admitted",
        "refused-stale-manifest",
        "refused-placeholder-corpus",
        "refused-unreviewed",
        "refused-malformed",
    }


def test_seal_citation_admitted_path():
    """seal_citation() with valid inputs + reviewed=True -> ADMITTED."""
    honest.reset_all_loud_once_for_tests()
    fresh_manifest = manifest.Manifest(
        cps_charging_standards_rev_date=dt.date.today().isoformat(),
        sentencing_council_guideline_rev_date=dt.date.today().isoformat(),
    )
    sealed = lore.seal_citation(
        text="CPS Code para 4.6 -- evidential stage",
        category=lore.CitationCategory.CPS_CHARGING_STANDARD,
        reviewed_by_counsel=True,
        corpus_sha=GOOD_CORPUS,
        key=GOOD_KEY,
        current_manifest=fresh_manifest,
    )
    assert sealed.outcome == lore.CitationGateOutcome.ADMITTED
    assert sealed.mirror_mark.startswith("lore@v1:")
    assert sealed.reviewed_by_counsel is True


def test_seal_citation_refused_unreviewed():
    """reviewed_by_counsel=False -> REFUSED_UNREVIEWED but mark IS computed."""
    honest.reset_all_loud_once_for_tests()
    fresh_manifest = manifest.Manifest(
        cps_charging_standards_rev_date=dt.date.today().isoformat(),
        sentencing_council_guideline_rev_date=dt.date.today().isoformat(),
    )
    sealed = lore.seal_citation(
        text="CPIA s3 initial disclosure",
        category=lore.CitationCategory.CPIA_SECTION,
        reviewed_by_counsel=False,
        corpus_sha=GOOD_CORPUS,
        key=GOOD_KEY,
        current_manifest=fresh_manifest,
    )
    assert sealed.outcome == lore.CitationGateOutcome.REFUSED_UNREVIEWED
    assert sealed.mirror_mark.startswith("lore@v1:")  # mark still computed


def test_seal_citation_refused_placeholder_corpus(capsys):
    """corpus_sha=32x0x00 -> REFUSED_PLACEHOLDER_CORPUS + LOUD-ONCE warning."""
    honest.reset_all_loud_once_for_tests()
    sealed = lore.seal_citation(
        text="PACE Code C",
        category=lore.CitationCategory.PACE_CODE,
        reviewed_by_counsel=True,
        corpus_sha=b"\x00" * 32,
        key=GOOD_KEY,
    )
    assert sealed.outcome == lore.CitationGateOutcome.REFUSED_PLACEHOLDER_CORPUS
    assert sealed.mirror_mark == ""
    cap = capsys.readouterr()
    assert "placeholder" in cap.err


def test_seal_citation_refused_stale_manifest():
    """Stale manifest -> REFUSED_STALE_MANIFEST."""
    honest.reset_all_loud_once_for_tests()
    stale_manifest = manifest.Manifest(
        cps_charging_standards_rev_date="2010-01-01",
        sentencing_council_guideline_rev_date="2010-01-01",
        staleness_window_days=30,
    )
    sealed = lore.seal_citation(
        text="Sentencing Council guideline X",
        category=lore.CitationCategory.SENTENCING_GUIDELINE,
        reviewed_by_counsel=True,
        corpus_sha=GOOD_CORPUS,
        key=GOOD_KEY,
        current_manifest=stale_manifest,
    )
    assert sealed.outcome == lore.CitationGateOutcome.REFUSED_STALE_MANIFEST


def test_seal_citation_refused_malformed_empty_text():
    """Empty text -> REFUSED_MALFORMED + EMPTY_TEXT sub-reason."""
    honest.reset_all_loud_once_for_tests()
    sealed = lore.seal_citation(
        text="",
        category=lore.CitationCategory.CPS_CHARGING_STANDARD,
        reviewed_by_counsel=True,
        corpus_sha=GOOD_CORPUS,
        key=GOOD_KEY,
    )
    assert sealed.outcome == lore.CitationGateOutcome.REFUSED_MALFORMED
    assert sealed.refusal_sub_reason == lore.CitationGateRefusalReason.EMPTY_TEXT


def test_seal_citation_refused_malformed_oversize():
    """Oversize text -> REFUSED_MALFORMED + OVERSIZE_TEXT sub-reason."""
    honest.reset_all_loud_once_for_tests()
    big = "x" * (lore.MAX_CITATION_TEXT_BYTES + 1)
    sealed = lore.seal_citation(
        text=big,
        category=lore.CitationCategory.OTHER_STATUTORY,
        reviewed_by_counsel=True,
        corpus_sha=GOOD_CORPUS,
        key=GOOD_KEY,
    )
    assert sealed.outcome == lore.CitationGateOutcome.REFUSED_MALFORMED
    assert sealed.refusal_sub_reason == lore.CitationGateRefusalReason.OVERSIZE_TEXT


def test_seal_citation_refused_malformed_invalid_category():
    """Non-enum category -> REFUSED_MALFORMED + INVALID_CATEGORY sub-reason."""
    honest.reset_all_loud_once_for_tests()
    sealed = lore.seal_citation(
        text="PACE Code A",
        category="not-an-enum",  # type: ignore[arg-type]
        reviewed_by_counsel=True,
        corpus_sha=GOOD_CORPUS,
        key=GOOD_KEY,
    )
    assert sealed.outcome == lore.CitationGateOutcome.REFUSED_MALFORMED
    assert sealed.refusal_sub_reason == lore.CitationGateRefusalReason.INVALID_CATEGORY


def test_citation_gate_helper_returns_outcome():
    """citation_gate() helper returns the sealed.outcome attribute."""
    honest.reset_all_loud_once_for_tests()
    fresh_manifest = manifest.Manifest(
        cps_charging_standards_rev_date=dt.date.today().isoformat(),
        sentencing_council_guideline_rev_date=dt.date.today().isoformat(),
    )
    sealed = lore.seal_citation(
        text="t",
        category=lore.CitationCategory.OTHER_STATUTORY,
        reviewed_by_counsel=True,
        corpus_sha=GOOD_CORPUS,
        key=GOOD_KEY,
        current_manifest=fresh_manifest,
    )
    assert lore.citation_gate(sealed) is sealed.outcome
