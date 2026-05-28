"""Tests for prosecutor.firewall -- KAT-1/6/7 cohort firewall pins."""
from __future__ import annotations

import hashlib

import pytest

from prosecutor import firewall, legal, mirrormark


def test_kat1_digest_hex_byte_identical_to_mirrormark():
    """firewall.KAT1_DIGEST_HEX mirrors mirrormark.KAT1_DIGEST_HEX."""
    assert firewall.KAT1_DIGEST_HEX == mirrormark.KAT1_DIGEST_HEX


def test_kat1_digest_hex_literal_canonical():
    """firewall.KAT1_DIGEST_HEX is byte-identical to cohort anchor."""
    assert firewall.KAT1_DIGEST_HEX == (
        "239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca"
    )


def test_assert_kat1_parity_passes():
    """firewall.assert_kat1_parity() returns without raising."""
    firewall.assert_kat1_parity()


def test_kat6_cps_code_hash_hex_64_chars():
    """KAT6_CPS_CODE_HASH_HEX is 64-char hex."""
    assert len(firewall.KAT6_CPS_CODE_HASH_HEX) == 64
    int(firewall.KAT6_CPS_CODE_HASH_HEX, 16)


def test_kat6_cps_code_hash_matches_legal_constant():
    """KAT6 reproduces SHA-256 over legal.CPS_CODE_DISCLAIMER."""
    actual = hashlib.sha256(legal.CPS_CODE_DISCLAIMER.encode("utf-8")).hexdigest()
    assert actual == firewall.KAT6_CPS_CODE_HASH_HEX


def test_assert_kat6_parity_passes():
    """firewall.assert_kat6_parity() returns without raising."""
    firewall.assert_kat6_parity()


def test_kat7_cpia_hash_64_chars():
    """KAT7_CPIA_VERSION_HASH_HEX is 64-char hex."""
    assert len(firewall.KAT7_CPIA_VERSION_HASH_HEX) == 64
    int(firewall.KAT7_CPIA_VERSION_HASH_HEX, 16)


def test_kat7_matches_carve_out_string():
    """KAT7 reproduces SHA-256 over legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT."""
    actual = hashlib.sha256(
        legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT.encode("utf-8")
    ).hexdigest()
    assert actual == firewall.KAT7_CPIA_VERSION_HASH_HEX


def test_assert_kat7_parity_passes():
    """firewall.assert_kat7_parity() returns without raising."""
    firewall.assert_kat7_parity()


def test_assert_all_kat_parity_passes():
    """compose-all check returns without raising for in-cohort library."""
    firewall.assert_all_kat_parity()


def test_all_kat_reproduces_returns_true():
    """all_kat_reproduces() boolean returns True for clean library."""
    assert firewall.all_kat_reproduces() is True


def test_kat6_distinct_from_kat7():
    """KAT-6 and KAT-7 differ (anchor distinct corpora)."""
    assert firewall.KAT6_CPS_CODE_HASH_HEX != firewall.KAT7_CPIA_VERSION_HASH_HEX


def test_kat1_distinct_from_kat6_kat7():
    """KAT-1 hex differs from KAT-6 / KAT-7 (different algorithms)."""
    assert firewall.KAT1_DIGEST_HEX != firewall.KAT6_CPS_CODE_HASH_HEX
    assert firewall.KAT1_DIGEST_HEX != firewall.KAT7_CPIA_VERSION_HASH_HEX
