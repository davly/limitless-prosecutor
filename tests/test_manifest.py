"""Tests for prosecutor.manifest -- R150 9-path IsStale + honest-TODO sentinels."""
from __future__ import annotations

import datetime as dt

import pytest

from prosecutor import honest, manifest


def test_cps_rev_date_iso_8601():
    """CPS_CHARGING_STANDARDS_REV_DATE parses as ISO-8601 date."""
    dt.date.fromisoformat(manifest.CPS_CHARGING_STANDARDS_REV_DATE)


def test_sentencing_rev_date_iso_8601():
    """SENTENCING_COUNCIL_GUIDELINE_REV_DATE parses as ISO-8601 date."""
    dt.date.fromisoformat(manifest.SENTENCING_COUNCIL_GUIDELINE_REV_DATE)


def test_default_staleness_window_positive():
    """DEFAULT_STALENESS_WINDOW_DAYS is positive."""
    assert manifest.DEFAULT_STALENESS_WINDOW_DAYS > 0


def test_manifest_schema_version_v1():
    """MANIFEST_SCHEMA_VERSION is v1."""
    assert manifest.MANIFEST_SCHEMA_VERSION == "v1"


# ---------------------------------------------------------------------------
# 7 honest-TODO sentinels
# ---------------------------------------------------------------------------


def test_honest_todo_sentinels_seven():
    """HONEST_TODO_SENTINELS has exactly 7 entries (R150 canonical pin)."""
    assert len(manifest.HONEST_TODO_SENTINELS) == 7


def test_honest_todo_sentinels_all_named():
    """Every sentinel starts with HONEST-TODO-N."""
    for i, s in enumerate(manifest.HONEST_TODO_SENTINELS, start=1):
        assert s.startswith(f"HONEST-TODO-{i}"), f"sentinel {i} mis-named: {s!r}"


def test_honest_todo_sentinels_non_empty():
    """Every sentinel string is non-empty."""
    for s in manifest.HONEST_TODO_SENTINELS:
        assert s


# ---------------------------------------------------------------------------
# Manifest dataclass
# ---------------------------------------------------------------------------


def test_default_manifest_constructed():
    """default_manifest() returns a Manifest with the pinned defaults."""
    m = manifest.default_manifest()
    assert m.schema_version == manifest.MANIFEST_SCHEMA_VERSION
    assert m.cps_charging_standards_rev_date == manifest.CPS_CHARGING_STANDARDS_REV_DATE
    assert (
        m.sentencing_council_guideline_rev_date
        == manifest.SENTENCING_COUNCIL_GUIDELINE_REV_DATE
    )
    assert m.staleness_window_days == manifest.DEFAULT_STALENESS_WINDOW_DAYS
    assert len(m.honest_todo_sentinels) == 7


def test_manifest_is_frozen():
    """Manifest is a frozen dataclass."""
    m = manifest.default_manifest()
    with pytest.raises(Exception):
        m.schema_version = "v2"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# is_stale 9-path (R150 canonical)
# ---------------------------------------------------------------------------


def _m(cps: str, sent: str, window: int = 365) -> manifest.Manifest:
    return manifest.Manifest(
        cps_charging_standards_rev_date=cps,
        sentencing_council_guideline_rev_date=sent,
        staleness_window_days=window,
    )


def test_is_stale_path_1_fresh_both():
    """Path 1: both fresh."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2026-05-01", "2026-04-01")
    assert manifest.is_stale(m, now=now) == manifest.StalenessOutcome.FRESH_BOTH


def test_is_stale_path_2_stale_cps_only():
    """Path 2: CPS stale, Sentencing fresh."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2024-01-01", "2026-04-01")
    assert manifest.is_stale(m, now=now) == manifest.StalenessOutcome.STALE_CPS_ONLY


def test_is_stale_path_3_stale_sentencing_only():
    """Path 3: Sentencing stale, CPS fresh."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2026-04-01", "2024-01-01")
    assert (
        manifest.is_stale(m, now=now) == manifest.StalenessOutcome.STALE_SENTENCING_ONLY
    )


def test_is_stale_path_4_stale_both():
    """Path 4: both stale."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2024-01-01", "2024-01-01")
    assert manifest.is_stale(m, now=now) == manifest.StalenessOutcome.STALE_BOTH


def test_is_stale_path_5_future_cps_only():
    """Path 5: CPS in future, Sentencing fresh past."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2030-01-01", "2026-04-01")
    assert manifest.is_stale(m, now=now) == manifest.StalenessOutcome.FUTURE_DATE_CPS


def test_is_stale_path_6_future_sentencing_only():
    """Path 6: Sentencing in future, CPS fresh past."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2026-04-01", "2030-01-01")
    assert (
        manifest.is_stale(m, now=now) == manifest.StalenessOutcome.FUTURE_DATE_SENTENCING
    )


def test_is_stale_path_7_future_both():
    """Path 7: both in future."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2030-01-01", "2030-01-01")
    assert manifest.is_stale(m, now=now) == manifest.StalenessOutcome.FUTURE_DATE_BOTH


def test_is_stale_path_8_unparseable_cps():
    """Path 8: CPS rev-date doesn't parse."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("not-a-date", "2026-04-01")
    assert manifest.is_stale(m, now=now) == manifest.StalenessOutcome.UNPARSEABLE_CPS


def test_is_stale_path_9_unparseable_sentencing():
    """Path 9: Sentencing rev-date doesn't parse."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2026-04-01", "not-a-date")
    assert (
        manifest.is_stale(m, now=now) == manifest.StalenessOutcome.UNPARSEABLE_SENTENCING
    )


def test_is_stale_all_nine_outcomes_covered():
    """The 9 StalenessOutcome enum members map 1:1 with the test paths above."""
    members = {o.value for o in manifest.StalenessOutcome}
    expected = {
        "fresh-both",
        "stale-cps-only",
        "stale-sentencing-only",
        "stale-both",
        "future-date-cps",
        "future-date-sentencing",
        "future-date-both",
        "unparseable-cps",
        "unparseable-sentencing",
    }
    assert members == expected


def test_is_fresh_boolean_shortcut():
    """is_fresh() returns True for fresh-both, False otherwise."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    assert manifest.is_fresh(_m("2026-04-01", "2026-04-01"), now=now) is True
    assert manifest.is_fresh(_m("2024-01-01", "2024-01-01"), now=now) is False


def test_is_stale_fires_loud_once_on_stale(capsys):
    """is_stale() returning non-fresh triggers honest.warn() once."""
    honest.reset_all_loud_once_for_tests()
    now = dt.date(2026, 5, 28)
    m = _m("2024-01-01", "2024-01-01")
    manifest.is_stale(m, now=now)
    cap1 = capsys.readouterr()
    assert "stale-manifest" in cap1.err
    # Subsequent calls don't re-fire
    manifest.is_stale(m, now=now)
    cap2 = capsys.readouterr()
    assert cap2.err == ""


def test_manifest_from_env_uses_pinned_defaults_when_env_absent(monkeypatch):
    """manifest_from_env() returns the pinned defaults with no env vars set."""
    for k in (
        "PROSECUTOR_MANIFEST_CPS_REV_DATE",
        "PROSECUTOR_MANIFEST_SENTENCING_REV_DATE",
        "PROSECUTOR_MANIFEST_STALENESS_WINDOW_DAYS",
    ):
        monkeypatch.delenv(k, raising=False)
    m = manifest.manifest_from_env()
    assert m.cps_charging_standards_rev_date == manifest.CPS_CHARGING_STANDARDS_REV_DATE


def test_manifest_from_env_overrides(monkeypatch):
    """manifest_from_env() applies env overrides."""
    monkeypatch.setenv("PROSECUTOR_MANIFEST_CPS_REV_DATE", "2030-01-01")
    monkeypatch.setenv("PROSECUTOR_MANIFEST_SENTENCING_REV_DATE", "2030-02-02")
    monkeypatch.setenv("PROSECUTOR_MANIFEST_STALENESS_WINDOW_DAYS", "30")
    m = manifest.manifest_from_env()
    assert m.cps_charging_standards_rev_date == "2030-01-01"
    assert m.sentencing_council_guideline_rev_date == "2030-02-02"
    assert m.staleness_window_days == 30


def test_manifest_from_env_invalid_window_falls_back(monkeypatch):
    """Invalid PROSECUTOR_MANIFEST_STALENESS_WINDOW_DAYS falls back to default."""
    monkeypatch.setenv("PROSECUTOR_MANIFEST_STALENESS_WINDOW_DAYS", "not-an-int")
    m = manifest.manifest_from_env()
    assert m.staleness_window_days == manifest.DEFAULT_STALENESS_WINDOW_DAYS
