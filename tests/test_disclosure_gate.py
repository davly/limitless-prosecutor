"""Tests for prosecutor.disclosure_gate -- CPIA 1996 4-state classifier."""
from __future__ import annotations

import datetime as dt

import pytest

from prosecutor import disclosure_gate


def test_disclosure_outcome_closed_set():
    """DisclosureOutcome has the 4 task-brief values."""
    values = {o.value for o in disclosure_gate.DisclosureOutcome}
    assert values == {
        "cpia-compliant-fresh",
        "schedule-stale",
        "sensitive-material-flag",
        "unused-material-incomplete",
    }


def test_material_category_closed_set():
    """MaterialCategory has used/unused/sensitive."""
    values = {m.value for m in disclosure_gate.MaterialCategory}
    assert values == {"used", "unused", "sensitive"}


def test_disclosure_tests_constant():
    """CPIA_DISCLOSURE_TESTS lists the 4 cohort-canonical test labels."""
    assert len(disclosure_gate.CPIA_DISCLOSURE_TESTS) == 4
    for label in disclosure_gate.CPIA_DISCLOSURE_TESTS:
        assert label


def _entry(eid: str, cat=disclosure_gate.MaterialCategory.UNUSED, pii=False):
    return disclosure_gate.DisclosureScheduleEntry(
        entry_id=eid, category=cat, description=f"entry {eid}", is_pii_flagged=pii
    )


def test_classify_fresh_compliant():
    """Fresh schedule, no sensitive, complete unused -> CPIA_COMPLIANT_FRESH."""
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=today,
        freshness_window_days=30,
        entries=(_entry("a"), _entry("b")),
        used_material_referenced_entry_ids=("a",),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.CPIA_COMPLIANT_FRESH


def test_classify_stale_schedule():
    """Schedule outside window -> SCHEDULE_STALE (highest priority)."""
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=dt.date(2024, 1, 1),
        freshness_window_days=30,
        entries=(_entry("a"),),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.SCHEDULE_STALE


def test_classify_sensitive_material_flag():
    """Any SENSITIVE-category entry -> SENSITIVE_MATERIAL_FLAG."""
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=today,
        freshness_window_days=30,
        entries=(_entry("a"), _entry("s", disclosure_gate.MaterialCategory.SENSITIVE)),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.SENSITIVE_MATERIAL_FLAG


def test_classify_pii_flagged_treated_as_sensitive():
    """is_pii_flagged=True triggers SENSITIVE_MATERIAL_FLAG."""
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=today,
        freshness_window_days=30,
        entries=(_entry("p", pii=True),),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.SENSITIVE_MATERIAL_FLAG


def test_classify_unused_material_incomplete():
    """Used-referenced id missing from schedule -> UNUSED_MATERIAL_INCOMPLETE."""
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=today,
        freshness_window_days=30,
        entries=(_entry("a"),),
        used_material_referenced_entry_ids=("a", "missing-id"),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.UNUSED_MATERIAL_INCOMPLETE


def test_classify_stale_beats_sensitive():
    """Stale + sensitive: STALE wins (cohort priority ordering)."""
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=dt.date(2024, 1, 1),
        freshness_window_days=30,
        entries=(_entry("s", disclosure_gate.MaterialCategory.SENSITIVE),),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.SCHEDULE_STALE


def test_classify_sensitive_beats_incomplete():
    """Fresh + sensitive + incomplete-unused: SENSITIVE wins."""
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=today,
        freshness_window_days=30,
        entries=(_entry("a"), _entry("s", disclosure_gate.MaterialCategory.SENSITIVE)),
        used_material_referenced_entry_ids=("missing",),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.SENSITIVE_MATERIAL_FLAG


def test_disclosure_gate_class_default_now():
    """DisclosureGate() uses today as default."""
    gate = disclosure_gate.DisclosureGate()
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=dt.date.today(),
        freshness_window_days=30,
        entries=(_entry("a"),),
    )
    assert gate.classify(req) == disclosure_gate.DisclosureOutcome.CPIA_COMPLIANT_FRESH


def test_schedule_entry_frozen():
    """DisclosureScheduleEntry is frozen."""
    e = _entry("a")
    with pytest.raises(Exception):
        e.entry_id = "b"  # type: ignore[misc]
