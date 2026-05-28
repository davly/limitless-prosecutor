"""Tests for prosecutor.mirrormark -- L43 cohort + KAT-1 parity."""
from __future__ import annotations

import hashlib
import hmac

import pytest

from prosecutor import mirrormark


# ---------------------------------------------------------------------------
# KAT-1 cohort cross-substrate parity
# ---------------------------------------------------------------------------


def test_kat1_digest_hex_literal_pin():
    """KAT-1 digest hex is byte-identical to cohort canonical anchor."""
    assert mirrormark.KAT1_DIGEST_HEX == (
        "239a7d0d3f1bbe3a98aede01e2ad818c2db60b7177c02e2f015035b2b5b7dbca"
    )


def test_kat1_input_shape():
    """KAT-1 input is 33 bytes = 0x01 || 32x0x00."""
    assert len(mirrormark.KAT1_INPUT) == 33
    assert mirrormark.KAT1_INPUT[0] == 0x01
    assert mirrormark.KAT1_INPUT[1:] == b"\x00" * 32


def test_kat1_key_is_empty():
    """KAT-1 HMAC key is empty bytes."""
    assert mirrormark.KAT1_KEY == b""


def test_kat1_reproduces_via_openssl_recipe():
    """KAT-1 HMAC-SHA256 (empty key, 0x01 || 32x0x00) reproduces."""
    mac = hmac.new(b"", digestmod=hashlib.sha256)
    mac.update(b"\x01" + b"\x00" * 32)
    assert mac.hexdigest() == mirrormark.KAT1_DIGEST_HEX


def test_assert_kat1_parity_passes():
    """assert_kat1_parity() returns without raising."""
    mirrormark.assert_kat1_parity()  # no AssertionError


def test_kat1_reproduces_cohort_anchor_returns_true():
    """Boolean sibling returns True for in-cohort library."""
    assert mirrormark.kat1_reproduces_cohort_anchor() is True


def test_mark_prefix_is_lore_v1():
    """Cohort canonical mark prefix."""
    assert mirrormark.MARK_PREFIX == "lore@v1:"


def test_mark_version_byte_is_0x01():
    """v1 version byte is 0x01."""
    assert mirrormark.MARK_VERSION_BYTE == b"\x01"


def test_kat1_mark_literal_pin():
    """KAT-1 full mark string byte-identical to cohort."""
    assert mirrormark.KAT1_MARK == (
        "lore@v1:AAAAAAAAAAAjmn0NPxu-Opiu3gHirYGMLbYLcXfALi8BUDWytbfbyg"
    )


# ---------------------------------------------------------------------------
# sign() pure function
# ---------------------------------------------------------------------------


def test_sign_kat1_inputs_produces_kat1_mark():
    """sign(KAT-1 inputs) produces the canonical KAT-1 mark."""
    mark = mirrormark.sign(b"\x00" * 32, b"", b"")
    assert mark == mirrormark.KAT1_MARK


def test_sign_rejects_wrong_corpus_length():
    """sign() raises InvalidCorpusLengthError for non-32-byte corpus_sha."""
    with pytest.raises(mirrormark.InvalidCorpusLengthError):
        mirrormark.sign(b"\x00" * 31, b"payload", b"key")
    with pytest.raises(mirrormark.InvalidCorpusLengthError):
        mirrormark.sign(b"\x00" * 33, b"payload", b"key")


def test_sign_produces_lore_v1_prefix():
    """Every sign() output starts with 'lore@v1:'."""
    mark = mirrormark.sign(b"\x01" * 32, b"hi", b"k")
    assert mark.startswith("lore@v1:")


def test_sign_is_deterministic():
    """sign() with the same inputs produces the same mark."""
    a = mirrormark.sign(b"\x42" * 32, b"payload", b"key")
    b = mirrormark.sign(b"\x42" * 32, b"payload", b"key")
    assert a == b


def test_sign_changes_with_payload():
    """sign() differs when payload differs."""
    a = mirrormark.sign(b"\x42" * 32, b"a", b"k")
    b = mirrormark.sign(b"\x42" * 32, b"b", b"k")
    assert a != b


def test_sign_changes_with_key():
    """sign() differs when key differs."""
    a = mirrormark.sign(b"\x42" * 32, b"x", b"k1")
    b = mirrormark.sign(b"\x42" * 32, b"x", b"k2")
    assert a != b


# ---------------------------------------------------------------------------
# verify() round-trip
# ---------------------------------------------------------------------------


def test_verify_kat1_round_trip():
    """verify(KAT-1 inputs, KAT-1 mark) returns True."""
    assert mirrormark.verify(b"\x00" * 32, b"", b"", mirrormark.KAT1_MARK) is True


def test_verify_returns_false_on_payload_drift():
    """verify() returns False when payload doesn't match the signed mark."""
    mark = mirrormark.sign(b"\x42" * 32, b"payload-a", b"key")
    assert mirrormark.verify(b"\x42" * 32, b"payload-b", b"key", mark) is False


def test_verify_returns_false_on_key_drift():
    """verify() returns False when key doesn't match."""
    mark = mirrormark.sign(b"\x42" * 32, b"payload", b"k1")
    assert mirrormark.verify(b"\x42" * 32, b"payload", b"k2", mark) is False


def test_verify_raises_on_missing_prefix():
    """verify() raises MalformedMarkError on missing v1 prefix."""
    with pytest.raises(mirrormark.MalformedMarkError):
        mirrormark.verify(b"\x00" * 32, b"", b"", "not-a-mark")


def test_verify_raises_on_bad_base64():
    """verify() raises MalformedMarkError on un-decodable body."""
    with pytest.raises(mirrormark.MalformedMarkError):
        mirrormark.verify(b"\x00" * 32, b"", b"", "lore@v1:!!!@@@###")


# ---------------------------------------------------------------------------
# Marker class
# ---------------------------------------------------------------------------


def test_marker_refuses_empty_key():
    """Marker raises EmptyKeyError when constructed with empty key."""
    with pytest.raises(mirrormark.EmptyKeyError):
        mirrormark.Marker(corpus_sha=b"\x01" * 32, key=b"")


def test_marker_refuses_wrong_corpus_length():
    """Marker raises InvalidCorpusLengthError on bad corpus length."""
    with pytest.raises(mirrormark.InvalidCorpusLengthError):
        mirrormark.Marker(corpus_sha=b"\x01" * 16, key=b"k")


def test_marker_round_trip():
    """Marker.mark() + verify() round-trip."""
    m = mirrormark.Marker(corpus_sha=b"\x42" * 32, key=b"secret")
    mark = m.mark(b"payload")
    assert m.verify(b"payload", mark) is True


def test_marker_placeholder_corpus_detected(capsys):
    """Marker detects all-zero corpus_sha as placeholder + emits stderr."""
    m = mirrormark.Marker(corpus_sha=b"\x00" * 32, key=b"real-key")
    placeholder_corpus, placeholder_key = m.using_placeholders()
    assert placeholder_corpus is True
    assert placeholder_key is False
    m.mark(b"payload")
    out = capsys.readouterr()
    assert "WARNING" in out.err
    assert "placeholder" in out.err


def test_marker_placeholder_warns_only_once(capsys):
    """Marker stderr fires exactly once per instance."""
    m = mirrormark.Marker(corpus_sha=b"\x00" * 32, key=b"real-key")
    m.mark(b"a")
    capsys.readouterr()  # discard
    m.mark(b"b")
    out = capsys.readouterr()
    assert out.err == ""
