"""manifest.py -- R150 IsStale jurisdiction-version manifest for limitless-prosecutor.

R150 cohort discipline: when a library carries hard-coded references to
domain-specific jurisdiction-version artefacts (charging standards, sentencing
guidelines, PACE codes), it MUST expose a Manifest dataclass with:
  - The rev-date / version-string of each pinned artefact.
  - An is_stale() check that compares against `now` and returns a closed-set
    StalenessOutcome enum.
  - 7 honest-TODO sentinels (cohort-canonical 5-field shape + 9-path IsStale).

Prosecutor pins TWO jurisdiction-version artefacts:
  1. CPS Charging Standards (CPS-published guidance per offence category).
  2. Sentencing Council guideline corpus (definitive guidelines E&W).

Both are revision-dated; both go stale; both MUST trigger an R143 LOUD-ONCE
warning when stale is detected at runtime.

Pure stdlib: dataclasses + enum + datetime + os + sys. No third-party deps.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from . import honest


# ---------------------------------------------------------------------------
# Pinned jurisdiction-version rev-dates (universal facts)
# ---------------------------------------------------------------------------

# CPS Charging Standards corpus rev-date. CPS publishes Charging Standards
# per offence category; the corpus-as-a-whole is informally rev-tagged. The
# date below is the most recent corpus refresh known to this library version.
#
# When the CPS publishes a substantive revision, this constant MUST be bumped
# atomically with the manifest version bump.
CPS_CHARGING_STANDARDS_REV_DATE: str = "2024-04-01"

# Sentencing Council definitive guidelines corpus rev-date. The Sentencing
# Council publishes definitive guidelines per offence; the most recent
# corpus refresh is the rev-date for the pinned set.
SENTENCING_COUNCIL_GUIDELINE_REV_DATE: str = "2024-07-01"

# Default staleness window. After this many days, the pinned rev-date is
# considered stale and IsStale returns STALE.
DEFAULT_STALENESS_WINDOW_DAYS: int = 365

# Manifest schema version (bumped atomically with any pinned rev-date bump).
MANIFEST_SCHEMA_VERSION: str = "v1"


# ---------------------------------------------------------------------------
# StalenessOutcome closed-enum (R115 cohort discipline + R150 9-path IsStale)
# ---------------------------------------------------------------------------


class StalenessOutcome(Enum):
    """Closed-enum staleness outcomes.

    The 9-path IsStale shape is cohort-canonical: every branch is a distinct
    enum member so consumers cannot accidentally collapse paths.

    FRESH_BOTH: both CPS + Sentencing rev-dates within window.
    STALE_CPS_ONLY: CPS rev-date stale, Sentencing fresh.
    STALE_SENTENCING_ONLY: Sentencing stale, CPS fresh.
    STALE_BOTH: both stale.
    FUTURE_DATE_CPS: CPS rev-date is in the future (clock skew / config error).
    FUTURE_DATE_SENTENCING: Sentencing rev-date is in the future.
    FUTURE_DATE_BOTH: both rev-dates in the future.
    UNPARSEABLE_CPS: CPS rev-date does not parse as ISO-8601 date.
    UNPARSEABLE_SENTENCING: Sentencing rev-date does not parse.
    """

    FRESH_BOTH = "fresh-both"
    STALE_CPS_ONLY = "stale-cps-only"
    STALE_SENTENCING_ONLY = "stale-sentencing-only"
    STALE_BOTH = "stale-both"
    FUTURE_DATE_CPS = "future-date-cps"
    FUTURE_DATE_SENTENCING = "future-date-sentencing"
    FUTURE_DATE_BOTH = "future-date-both"
    UNPARSEABLE_CPS = "unparseable-cps"
    UNPARSEABLE_SENTENCING = "unparseable-sentencing"


# ---------------------------------------------------------------------------
# 7 honest-TODO sentinels (cohort R150 canonical-shape pin)
# ---------------------------------------------------------------------------

# Cohort R150 convention: every Manifest carries 7 honest-TODO sentinel strings
# naming the open jurisdiction-version work the library has NOT yet absorbed.
# These are author-time-honest declarations; downstream consumers grep for
# them via cohort-walker.

HONEST_TODO_SENTINELS: tuple[str, ...] = (
    # 1. Per-offence Charging Standards are NOT in this library -- only the
    # corpus rev-date is pinned. Per-offence text MUST come from the CPS website.
    "HONEST-TODO-1: per-offence Charging Standards text not in-source; "
    "production deploys MUST fetch from cps.gov.uk per case",
    # 2. Sentencing Council guideline text is NOT in this library -- only the
    # corpus rev-date is pinned.
    "HONEST-TODO-2: per-offence Sentencing Council guideline text not in-source; "
    "production deploys MUST fetch from sentencingcouncil.org.uk per case",
    # 3. PACE Codes are pinned by name only (not by full text). The library
    # CANNOT enforce PACE compliance against the code-text -- only against
    # operator-supplied compliance assertions.
    "HONEST-TODO-3: PACE Code text (A-H) not in-source; library pins code names "
    "only; downstream compliance check is operator-supplied assertion",
    # 4. Bail Act 1976 conditions are not enumerated in this library.
    "HONEST-TODO-4: Bail Act 1976 condition taxonomy not in-source; downstream "
    "consumer must supply bail-condition shape",
    # 5. CPIA Code of Practice (2020) revision text not in-source.
    "HONEST-TODO-5: CPIA Code of Practice (2020) text not in-source; only "
    "section-number references pinned",
    # 6. Sentencing Act 2020 consolidated code not in-source.
    "HONEST-TODO-6: Sentencing Act 2020 consolidated provisions not in-source; "
    "library pins act-name only",
    # 7. Cross-jurisdiction (Scotland / NI) NOT covered. Library is E&W only.
    "HONEST-TODO-7: Scotland (COPFS) and Northern Ireland (PPS) NOT covered; "
    "library is E&W (CPS) only",
)

assert len(HONEST_TODO_SENTINELS) == 7, "R150 cohort canonical pin: 7 honest-TODO sentinels"


# ---------------------------------------------------------------------------
# Manifest dataclass (cohort-canonical 5-field shape)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Manifest:
    """R150 jurisdiction-version manifest.

    Cohort-canonical 5-field shape:
      - schema_version: manifest schema version (bumped atomically with any
        pinned rev-date bump).
      - cps_charging_standards_rev_date: CPS Charging Standards corpus rev-date.
      - sentencing_council_guideline_rev_date: Sentencing Council corpus rev-date.
      - staleness_window_days: how many days before a rev-date is considered stale.
      - honest_todo_sentinels: tuple of 7 author-time-honest open-work declarations.
    """

    schema_version: str = MANIFEST_SCHEMA_VERSION
    cps_charging_standards_rev_date: str = CPS_CHARGING_STANDARDS_REV_DATE
    sentencing_council_guideline_rev_date: str = SENTENCING_COUNCIL_GUIDELINE_REV_DATE
    staleness_window_days: int = DEFAULT_STALENESS_WINDOW_DAYS
    honest_todo_sentinels: tuple[str, ...] = field(default_factory=lambda: HONEST_TODO_SENTINELS)


def default_manifest() -> Manifest:
    """Return the library-default Manifest with cohort-canonical rev-dates."""
    return Manifest()


def _parse_date(s: str) -> Optional[dt.date]:
    """Parse an ISO-8601 date string. Returns None on failure."""
    try:
        return dt.date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# is_stale() -- 9-path IsStale (R150 cohort-canonical)
# ---------------------------------------------------------------------------


def is_stale(manifest: Manifest, now: Optional[dt.date] = None) -> StalenessOutcome:
    """R150 9-path IsStale check against the pinned jurisdiction-version manifest.

    Returns one of the 9 closed-set StalenessOutcome values. Callers SHOULD
    pair this with a R143 LOUD-ONCE-WARNING when the outcome is anything other
    than FRESH_BOTH.

    The 9 paths are:
      1. FRESH_BOTH:                 both fresh
      2. STALE_CPS_ONLY:             CPS stale, Sentencing fresh
      3. STALE_SENTENCING_ONLY:      Sentencing stale, CPS fresh
      4. STALE_BOTH:                 both stale
      5. FUTURE_DATE_CPS:            CPS in future
      6. FUTURE_DATE_SENTENCING:     Sentencing in future
      7. FUTURE_DATE_BOTH:           both in future
      8. UNPARSEABLE_CPS:            CPS rev-date doesn't parse
      9. UNPARSEABLE_SENTENCING:     Sentencing rev-date doesn't parse
    """
    if now is None:
        now = dt.date.today()

    cps = _parse_date(manifest.cps_charging_standards_rev_date)
    sentencing = _parse_date(manifest.sentencing_council_guideline_rev_date)

    if cps is None:
        return StalenessOutcome.UNPARSEABLE_CPS
    if sentencing is None:
        return StalenessOutcome.UNPARSEABLE_SENTENCING

    cps_future = cps > now
    sent_future = sentencing > now

    if cps_future and sent_future:
        return StalenessOutcome.FUTURE_DATE_BOTH
    if cps_future:
        return StalenessOutcome.FUTURE_DATE_CPS
    if sent_future:
        return StalenessOutcome.FUTURE_DATE_SENTENCING

    window = dt.timedelta(days=manifest.staleness_window_days)
    cps_stale = (now - cps) > window
    sent_stale = (now - sentencing) > window

    if cps_stale and sent_stale:
        outcome = StalenessOutcome.STALE_BOTH
    elif cps_stale:
        outcome = StalenessOutcome.STALE_CPS_ONLY
    elif sent_stale:
        outcome = StalenessOutcome.STALE_SENTENCING_ONLY
    else:
        outcome = StalenessOutcome.FRESH_BOTH

    if outcome != StalenessOutcome.FRESH_BOTH:
        honest.warn(
            honest.WARN_STALE_MANIFEST,
            f"manifest staleness detected: outcome={outcome.value} "
            f"(cps={manifest.cps_charging_standards_rev_date} "
            f"sentencing={manifest.sentencing_council_guideline_rev_date} "
            f"window_days={manifest.staleness_window_days})",
        )

    return outcome


def is_fresh(manifest: Manifest, now: Optional[dt.date] = None) -> bool:
    """Boolean shortcut: True iff is_stale() returns FRESH_BOTH."""
    return is_stale(manifest, now=now) == StalenessOutcome.FRESH_BOTH


# ---------------------------------------------------------------------------
# from_env -- override rev-dates from env for ops drills
# ---------------------------------------------------------------------------


def manifest_from_env() -> Manifest:
    """Construct a Manifest with rev-dates optionally overridden from env vars.

    PROSECUTOR_MANIFEST_CPS_REV_DATE and PROSECUTOR_MANIFEST_SENTENCING_REV_DATE
    override the defaults. Used for ops drills that simulate future-date /
    stale-corpus shapes without modifying the source.
    """
    cps = os.environ.get("PROSECUTOR_MANIFEST_CPS_REV_DATE", CPS_CHARGING_STANDARDS_REV_DATE)
    sentencing = os.environ.get(
        "PROSECUTOR_MANIFEST_SENTENCING_REV_DATE", SENTENCING_COUNCIL_GUIDELINE_REV_DATE
    )
    window_str = os.environ.get(
        "PROSECUTOR_MANIFEST_STALENESS_WINDOW_DAYS", str(DEFAULT_STALENESS_WINDOW_DAYS)
    )
    try:
        window = int(window_str)
    except ValueError:
        window = DEFAULT_STALENESS_WINDOW_DAYS
    return Manifest(
        cps_charging_standards_rev_date=cps,
        sentencing_council_guideline_rev_date=sentencing,
        staleness_window_days=window,
    )
