"""mirrormark.py -- L43 Mirror-Mark v1 stamping for limitless-prosecutor.

This module is the Python port of the cohort-canonical L43 Mirror-Mark v1
HMAC-SHA256 over canonical-bytes algorithm shipped across the Go cohort
(foundation/pkg/mirrormark + pulse + baseline + foundry + oracle + iris +
nexus + folio) and the Python cohort (arbiter-legal + counsel + iris + haven
+ archaeologist + absurd).

Prosecutor becomes a Python cohort consumer extending substrate-portability
for the criminal-justice-regime compliance flagship shape.

Algorithm (intentionally minimal so a regulator with `openssl dgst` can
re-derive any mark from canonical inputs without any Limitless toolchain):

    mark = "lore@v1:" + base64url(corpusSHA[:8] || HMAC-SHA256(0x01 || corpusSHA || payload, key))

This is the R151 ECOSYSTEM_QUALITY_STANDARD.md Part XII cohort cross-substrate
pin. The KAT-1 anchor `239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca`
is reproducible OFFLINE via:

    # KAT-1 input: 0x01 || 32x0x00 (33 bytes); HMAC key: empty
    printf '\\x01' > /tmp/kat1.bin
    printf '\\x00%.0s' {1..32} >> /tmp/kat1.bin
    openssl dgst -sha256 -mac hmac -macopt key: /tmp/kat1.bin
    # -> HMAC-SHA256(stdin) = 239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca

The hex IS the cohort firewall: drift on the literal here breaks parity
with every Go cohort port + the lore-mark-verify CLI.

Prosecutor-specific use cases (opt-in by downstream host; library does
NOT wire automatically):
  - ChargingDecisionRecord sealing: stamp Mirror-Mark over canonical-JSON
    bytes of a Full Code Test outcome so a downstream verifier can re-derive
    "this charging decision came from prosecutor at commit X against inputs Y".
  - DisclosureScheduleEntry sealing: same byte-stable evidence chain over
    a CPIA disclosure schedule entry.

The library ships the PRIMITIVE; consumers wire it.

Pure stdlib: hashlib + hmac + base64. No third-party deps.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import sys
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Cohort-canonical constants (R151 KAT-1 cross-substrate pin)
# ---------------------------------------------------------------------------

# 1-byte version tag prefixing the HMAC input. Bumping invalidates every
# mark in flight -- necessary if canonicalization rules ever change.
MARK_VERSION_BYTE: bytes = b"\x01"

# Human-readable header-value prefix. Byte-identical to
# foundation/pkg/mirrormark.MarkPrefix.
MARK_PREFIX: str = "lore@v1:"

# Corpus-SHA prefix length embedded in the mark body. Exposed so a non-
# Limitless re-implementation of Verify can be byte-compatible.
MARK_CORPUS_PREFIX_LEN: int = 8

# Unencoded mark body length (8 bytes corpusSHA prefix + 32 bytes HMAC).
# Base64URL-encoded becomes the fixed 54-char suffix after MARK_PREFIX.
MARK_BODY_LEN: int = MARK_CORPUS_PREFIX_LEN + hashlib.sha256().digest_size

# ---------------------------------------------------------------------------
# R151 KAT-1 anchor (cohort cross-substrate firewall)
# ---------------------------------------------------------------------------

# KAT-1 input: 33 bytes = 0x01 followed by 32x 0x00.
KAT1_INPUT: bytes = b"\x01" + b"\x00" * 32

# KAT-1 HMAC key: empty.
KAT1_KEY: bytes = b""

# KAT-1 HMAC-SHA256 digest, hex-encoded. THIS IS THE COHORT CROSS-SUBSTRATE
# FIREWALL: byte-identical to foundation/pkg/mirrormark.KAT1Digest.
KAT1_DIGEST_HEX: str = "239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca"

# KAT-1 mark string (the full "lore@v1:..." output for KAT-1 inputs).
# Cohort-canonical mark string parity test target.
KAT1_MARK: str = "lore@v1:AAAAAAAAAAAjmn0NPxu-Opiu3gHirYGMLbYLcXfALi8BUDWytbfbyg"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class MirrorMarkError(Exception):
    """Base exception for Mirror-Mark errors."""


class EmptyKeyError(MirrorMarkError):
    """Raised when a non-test caller attempts to sign with an empty HMAC key."""


class InvalidCorpusLengthError(MirrorMarkError):
    """Raised when the corpus SHA isn't exactly 32 bytes."""


class MalformedMarkError(MirrorMarkError):
    """Raised when verify() receives a mark string that doesn't parse."""


# ---------------------------------------------------------------------------
# Module-level sign + verify (pure functions)
# ---------------------------------------------------------------------------


def sign(corpus_sha: bytes, payload: bytes, key: bytes) -> str:
    """Compute the canonical Mirror-Mark string for the given inputs.

    Mark format:
        "lore@v1:" + base64url(corpusSHA[:8] || HMAC-SHA256(0x01 || corpusSHA || payload, key))

    Pure function. Safe to call from a cold-verify regulator binary.
    """
    if len(corpus_sha) != hashlib.sha256().digest_size:
        raise InvalidCorpusLengthError(
            f"corpus_sha must be {hashlib.sha256().digest_size} bytes, got {len(corpus_sha)}"
        )
    mac = hmac.new(key, digestmod=hashlib.sha256)
    mac.update(MARK_VERSION_BYTE)
    mac.update(corpus_sha)
    mac.update(payload)
    digest = mac.digest()
    body = corpus_sha[:MARK_CORPUS_PREFIX_LEN] + digest
    encoded = base64.urlsafe_b64encode(body).rstrip(b"=").decode("ascii")
    return MARK_PREFIX + encoded


def verify(corpus_sha: bytes, payload: bytes, key: bytes, mark: str) -> bool:
    """Verify a Mirror-Mark string against (corpus_sha, payload, key).

    Returns True iff the mark matches the canonical sign(...) output for
    the given inputs. Constant-time compare via hmac.compare_digest.
    """
    if not mark.startswith(MARK_PREFIX):
        raise MalformedMarkError(f"mark missing v1 prefix {MARK_PREFIX!r}")
    encoded = mark[len(MARK_PREFIX):]
    pad_len = (4 - (len(encoded) % 4)) % 4
    try:
        body = base64.urlsafe_b64decode(encoded + ("=" * pad_len))
    except Exception as exc:
        raise MalformedMarkError(f"mark body base64 decode failed: {exc}") from exc
    if len(body) != MARK_BODY_LEN:
        raise MalformedMarkError(
            f"mark body wrong length: got {len(body)}, want {MARK_BODY_LEN}"
        )
    expected = sign(corpus_sha, payload, key)
    return hmac.compare_digest(mark, expected)


# ---------------------------------------------------------------------------
# Marker class (placeholder-tracking + LoudOnce surface)
# ---------------------------------------------------------------------------


@dataclass(frozen=False)
class Marker:
    """A long-lived Mirror-Mark signer.

    Constructed with (corpus_sha, key); both are immutable post-construction.
    Calling `mark(payload)` returns a canonical Mirror-Mark string for the
    given payload bytes.

    The Marker tracks placeholder usage and exposes `using_placeholders()`.
    """

    corpus_sha: bytes
    key: bytes
    _using_placeholder_corpus: bool = False
    _using_placeholder_key: bool = False
    _warned_once: bool = False

    def __post_init__(self) -> None:
        if len(self.corpus_sha) != hashlib.sha256().digest_size:
            raise InvalidCorpusLengthError(
                f"corpus_sha must be {hashlib.sha256().digest_size} bytes, got {len(self.corpus_sha)}"
            )
        if len(self.key) == 0:
            raise EmptyKeyError(
                "Marker refuses empty HMAC key; use module-level sign() for KAT-1 vectors"
            )
        if self.corpus_sha == b"\x00" * hashlib.sha256().digest_size:
            self._using_placeholder_corpus = True
        if self.key == b"\x00" * len(self.key):
            self._using_placeholder_key = True

    def mark(self, payload: bytes) -> str:
        """Sign payload bytes; returns the canonical Mirror-Mark string."""
        if (self._using_placeholder_corpus or self._using_placeholder_key) and not self._warned_once:
            self._warned_once = True
            parts = []
            if self._using_placeholder_corpus:
                parts.append("corpus")
            if self._using_placeholder_key:
                parts.append("key")
            sys.stderr.write(
                f"prosecutor.mirrormark: WARNING -- signing with placeholder {' '.join(parts)}; "
                f"emitted marks will NOT pass cold-verify against a real lore corpus / "
                f"production key\n"
            )
        return sign(self.corpus_sha, payload, self.key)

    def verify(self, payload: bytes, mark: str) -> bool:
        """Verify a mark against (corpus_sha, key, payload)."""
        return verify(self.corpus_sha, payload, self.key, mark)

    def using_placeholders(self) -> tuple[bool, bool]:
        """Returns (placeholder_corpus, placeholder_key)."""
        return self._using_placeholder_corpus, self._using_placeholder_key


# ---------------------------------------------------------------------------
# KAT-1 self-test (callable as a sanity check at boot)
# ---------------------------------------------------------------------------


def assert_kat1_parity() -> None:
    """Verify the KAT-1 anchor reproduces. Raises AssertionError on drift.

    Callable from a host's boot phase as a R73-style import-time parity
    assertion. Cohort firewall pin: drift surfaces here, not at the next
    cross-substrate verification round-trip.
    """
    mac = hmac.new(KAT1_KEY, digestmod=hashlib.sha256)
    mac.update(KAT1_INPUT)
    digest_hex = mac.hexdigest()
    assert digest_hex == KAT1_DIGEST_HEX, (
        f"L43 Mirror-Mark KAT-1 drift detected: "
        f"got {digest_hex}, expected {KAT1_DIGEST_HEX}. "
        f"This breaks cohort parity with the Go + Python cohort."
    )


def kat1_reproduces_cohort_anchor() -> bool:
    """Boolean-returning sibling of assert_kat1_parity() for boot-time gates."""
    mac = hmac.new(KAT1_KEY, digestmod=hashlib.sha256)
    mac.update(KAT1_INPUT)
    return mac.hexdigest() == KAT1_DIGEST_HEX
