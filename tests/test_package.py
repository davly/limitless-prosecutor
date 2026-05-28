"""Tests for the package surface -- __init__ exports + cohort markers."""
from __future__ import annotations

import prosecutor


def test_version_present():
    """Package exports __version__."""
    assert prosecutor.__version__ == "0.1.0"


def test_all_exports():
    """Package __all__ lists every public name."""
    assert "Marker" in prosecutor.__all__
    assert "HonestWarner" in prosecutor.__all__
    assert "LIABILITY_FOOTER" in prosecutor.__all__
    assert "DisclosureOutcome" in prosecutor.__all__
    assert "ChargingOutcome" in prosecutor.__all__
    assert "SealedCitation" in prosecutor.__all__
    assert "Manifest" in prosecutor.__all__
    assert "KAT1_DIGEST_HEX" in prosecutor.__all__


def test_submodules_importable():
    """All 8 submodules are importable through the package."""
    assert prosecutor.mirrormark is not None
    assert prosecutor.honest is not None
    assert prosecutor.legal is not None
    assert prosecutor.manifest is not None
    assert prosecutor.firewall is not None
    assert prosecutor.lore is not None
    assert prosecutor.disclosure_gate is not None
    assert prosecutor.charging_gate is not None


def test_kat1_anchor_present_at_top_level():
    """KAT-1 anchor is exposed at top-level for boot-time gates."""
    assert prosecutor.KAT1_DIGEST_HEX == (
        "239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca"
    )


def test_r174_5_of_5_cohort_packages_present():
    """R174 5-of-5 cohort-maturity from inception: 5 dedicated cohort modules."""
    # The 5 cohort packages: mirrormark + honest + legal + manifest + firewall
    # are the 5 named-as-cohort modules per Conjure / atelier R174 template.
    cohort_modules = [
        prosecutor.mirrormark,
        prosecutor.honest,
        prosecutor.legal,
        prosecutor.manifest,
        prosecutor.firewall,
    ]
    assert len(cohort_modules) == 5
    for m in cohort_modules:
        assert m is not None
