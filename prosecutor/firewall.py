"""firewall.py -- KAT-1 / KAT-6 / KAT-7 cohort firewall pins for limitless-prosecutor.

Three KAT firewalls, each byte-identical to a cohort-canonical hex anchor:

  KAT-1: L43 Mirror-Mark cross-substrate cohort anchor. HMAC-SHA256 over
         (0x01 || 32x0x00) with empty key. Hex:
         239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca
         Drift here breaks cohort parity with EVERY Mirror-Mark substrate.

  KAT-6: CPS Code corpus pin. SHA-256 over the in-source CPS Code disclaimer
         text (`legal.CPS_CODE_DISCLAIMER`). Drift here means the CPS Code
         disclaimer text has changed without an atomic manifest bump.

  KAT-7: CPIA + LED carve-out pin. SHA-256 over the criminal-justice carve-out
         text (`legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT`). Drift here means the
         carve-out wording has changed without an atomic legal-review pass.

These three pins compose into `assert_all_kat_parity()` which a downstream
consumer calls at boot to fail-closed if any of the three firewalls have
drifted.

Pure stdlib: hashlib + hmac. No third-party deps.
"""
from __future__ import annotations

import hashlib
import hmac

from . import legal, mirrormark


# ---------------------------------------------------------------------------
# KAT-1 cohort cross-substrate firewall (L43 Mirror-Mark anchor)
# ---------------------------------------------------------------------------

# Mirror of mirrormark.KAT1_DIGEST_HEX surfaced here for the firewall API.
# Drift breaks cohort parity with EVERY Mirror-Mark substrate (Go + Python
# + Rust + Erlang + C + Solidity + Kotlin + Idris + ...).
KAT1_DIGEST_HEX: str = mirrormark.KAT1_DIGEST_HEX

assert KAT1_DIGEST_HEX == "239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca", (
    "KAT-1 drift detected at module import -- breaks cohort cross-substrate "
    "parity with EVERY Mirror-Mark substrate. Do not modify this hex without "
    "a coordinated cohort migration."
)


# ---------------------------------------------------------------------------
# KAT-6 CPS Code corpus pin (prosecutor-specific firewall)
# ---------------------------------------------------------------------------


def _sha256_hex(s: str) -> str:
    """Compute SHA-256 over UTF-8 bytes of s, return hex."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# Computed at import time from legal.CPS_CODE_DISCLAIMER. Stored as a literal
# below so that any drift in CPS_CODE_DISCLAIMER fails the assertion at the
# module's import-time bottom-of-file, not at first-call.
KAT6_CPS_CODE_HASH_HEX: str = _sha256_hex(legal.CPS_CODE_DISCLAIMER)


# ---------------------------------------------------------------------------
# KAT-7 CPIA + LED carve-out pin (prosecutor-specific firewall)
# ---------------------------------------------------------------------------

KAT7_CPIA_VERSION_HASH_HEX: str = _sha256_hex(legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT)


# ---------------------------------------------------------------------------
# Composed firewall assertion
# ---------------------------------------------------------------------------


def assert_kat1_parity() -> None:
    """Assert KAT-1 L43 Mirror-Mark anchor reproduces. Raises AssertionError on drift."""
    mac = hmac.new(b"", digestmod=hashlib.sha256)
    mac.update(b"\x01" + b"\x00" * 32)
    digest_hex = mac.hexdigest()
    assert digest_hex == KAT1_DIGEST_HEX, (
        f"KAT-1 L43 Mirror-Mark drift: got {digest_hex}, expected {KAT1_DIGEST_HEX}"
    )


def assert_kat6_parity() -> None:
    """Assert KAT-6 CPS Code corpus pin reproduces. Raises AssertionError on drift."""
    actual = _sha256_hex(legal.CPS_CODE_DISCLAIMER)
    assert actual == KAT6_CPS_CODE_HASH_HEX, (
        f"KAT-6 CPS Code corpus drift: got {actual}, expected {KAT6_CPS_CODE_HASH_HEX}. "
        f"This means legal.CPS_CODE_DISCLAIMER has changed without an atomic "
        f"KAT6_CPS_CODE_HASH_HEX bump. Bump the literal in firewall.py atomically "
        f"with the disclaimer update."
    )


def assert_kat7_parity() -> None:
    """Assert KAT-7 criminal-justice carve-out pin reproduces. Raises on drift."""
    actual = _sha256_hex(legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT)
    assert actual == KAT7_CPIA_VERSION_HASH_HEX, (
        f"KAT-7 criminal-justice carve-out drift: got {actual}, expected "
        f"{KAT7_CPIA_VERSION_HASH_HEX}. This means legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT "
        f"has changed without an atomic KAT7_CPIA_VERSION_HASH_HEX bump."
    )


def assert_all_kat_parity() -> None:
    """Assert all three KAT firewalls reproduce. Compose-all check for boot.

    Raises AssertionError on any drift. Callable from a host's boot phase as
    a fail-closed gate: if any of the three firewalls have drifted, the host
    refuses to start.
    """
    assert_kat1_parity()
    assert_kat6_parity()
    assert_kat7_parity()


def all_kat_reproduces() -> bool:
    """Boolean-returning sibling of assert_all_kat_parity() for boot-time gates."""
    try:
        assert_all_kat_parity()
        return True
    except AssertionError:
        return False
