"""Godfather flagship-uplift transfer (2026-06-26): degenerate-input / fail-open lens.

The DisclosureGate check ORDERING is correct (ruled out). The real defect is degenerate-input
fail-open: an EMPTY disclosure schedule (entries=()) passed the freshness leg, `any()` over the
empty iterable was False, and the empty for-loop never ran -> CPIA_COMPLIANT_FRESH. An unpopulated /
never-recorded schedule earned a clean GREEN bill of health -- the opposite of CPIA's withhold-by-
default duty, and exactly where human review is most needed. Also: a future-dated schedule
(age < 0) sneaked past the stale check. Both must fail closed (not GREEN).
"""
from __future__ import annotations

import datetime as dt

from prosecutor import disclosure_gate


def test_empty_schedule_is_not_compliant_fresh():
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=today,
        freshness_window_days=30,
        entries=(),  # empty / never-populated schedule
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome != disclosure_gate.DisclosureOutcome.CPIA_COMPLIANT_FRESH
    assert outcome == disclosure_gate.DisclosureOutcome.UNUSED_MATERIAL_INCOMPLETE


def test_future_dated_schedule_is_not_compliant_fresh():
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=dt.date(2026, 6, 10),  # dated in the future
        freshness_window_days=30,
        entries=(disclosure_gate.DisclosureScheduleEntry(
            entry_id="a", category=disclosure_gate.MaterialCategory.UNUSED, description="x"),),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.SCHEDULE_STALE


def test_populated_fresh_schedule_still_compliant():
    # Behaviour-preserving: a normal populated, fresh, complete schedule is still GREEN.
    today = dt.date(2026, 5, 28)
    req = disclosure_gate.DisclosureRequest(
        schedule_last_updated=today,
        freshness_window_days=30,
        entries=(disclosure_gate.DisclosureScheduleEntry(
            entry_id="a", category=disclosure_gate.MaterialCategory.UNUSED, description="x"),),
        used_material_referenced_entry_ids=("a",),
    )
    outcome = disclosure_gate.classify_disclosure(req, now=today)
    assert outcome == disclosure_gate.DisclosureOutcome.CPIA_COMPLIANT_FRESH
