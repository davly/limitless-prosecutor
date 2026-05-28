"""Tests for prosecutor.honest -- R143 LOUD-ONCE + threading."""
from __future__ import annotations

import threading

from prosecutor import honest


def test_warn_kinds_closed_set():
    """ALL_WARN_KINDS contains the documented 5 kinds."""
    assert honest.WARN_OPERATOR_PLACEHOLDER in honest.ALL_WARN_KINDS
    assert honest.WARN_DEVELOPER_CURATED_CHARGING_STANDARDS in honest.ALL_WARN_KINDS
    assert honest.WARN_DEVELOPER_CURATED_SENTENCING_GUIDELINES in honest.ALL_WARN_KINDS
    assert honest.WARN_MIRROR_MARK_PLACEHOLDER in honest.ALL_WARN_KINDS
    assert honest.WARN_STALE_MANIFEST in honest.ALL_WARN_KINDS
    assert len(honest.ALL_WARN_KINDS) == 5


def test_loud_once_flag_fires_exactly_once(capsys):
    """LoudOnceFlag fires once and is silent after."""
    flag = honest.LoudOnceFlag(kind="test-kind")
    assert flag.fire("first") is True
    captured1 = capsys.readouterr()
    assert "test-kind" in captured1.err
    assert "first" in captured1.err
    assert flag.fire("second") is False
    captured2 = capsys.readouterr()
    assert captured2.err == ""


def test_loud_once_flag_fired_after_first():
    """fired() returns True only after first fire()."""
    flag = honest.LoudOnceFlag(kind="kk")
    assert flag.fired() is False
    flag.fire("msg")
    assert flag.fired() is True


def test_loud_once_flag_reset_for_tests(capsys):
    """reset_for_tests() re-arms the flag."""
    flag = honest.LoudOnceFlag(kind="rk")
    flag.fire("a")
    capsys.readouterr()
    flag.reset_for_tests()
    assert flag.fired() is False
    assert flag.fire("b") is True


def test_loud_once_thread_safety_only_one_winner():
    """Under contention, exactly one thread wins the fire()."""
    flag = honest.LoudOnceFlag(kind="threaded")
    results: list[bool] = []
    lock = threading.Lock()

    def worker():
        r = flag.fire("contended")
        with lock:
            results.append(r)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # Exactly one True, nineteen False
    assert sum(results) == 1
    assert len(results) == 20


def test_honest_warner_warn_returns_true_first_time(capsys):
    """HonestWarner.warn() returns True on first call per kind."""
    honest.reset_all_loud_once_for_tests()
    out = honest.warn(honest.WARN_OPERATOR_PLACEHOLDER, "configure me")
    assert out is True
    cap = capsys.readouterr()
    assert "operator-identity-placeholder" in cap.err


def test_honest_warner_warn_returns_false_subsequent(capsys):
    """HonestWarner.warn() returns False on subsequent calls per kind."""
    honest.reset_all_loud_once_for_tests()
    honest.warn(honest.WARN_OPERATOR_PLACEHOLDER, "first")
    capsys.readouterr()
    out = honest.warn(honest.WARN_OPERATOR_PLACEHOLDER, "second")
    assert out is False


def test_honest_warner_warn_different_kinds_independent(capsys):
    """Different kinds fire independently."""
    honest.reset_all_loud_once_for_tests()
    a = honest.warn(honest.WARN_OPERATOR_PLACEHOLDER, "a")
    b = honest.warn(honest.WARN_STALE_MANIFEST, "b")
    assert a is True
    assert b is True


def test_honest_warner_lazy_kind_registration(capsys):
    """A previously-unseen kind registers lazily and fires once."""
    honest.reset_all_loud_once_for_tests()
    out = honest.warn("custom-kind-not-in-set", "lazy")
    assert out is True
    out2 = honest.warn("custom-kind-not-in-set", "lazy2")
    assert out2 is False


def test_honest_warner_fired_returns_false_for_unknown():
    """fired() returns False for an unregistered kind."""
    honest.reset_all_loud_once_for_tests()
    assert honest.fired("never-seen-kind") is False


def test_honest_warner_fired_returns_true_after_fire():
    """fired() returns True after a kind has fired."""
    honest.reset_all_loud_once_for_tests()
    honest.warn(honest.WARN_STALE_MANIFEST, "y")
    assert honest.fired(honest.WARN_STALE_MANIFEST) is True


def test_get_singleton_returns_module_singleton():
    """get_singleton() returns the same instance across calls."""
    a = honest.get_singleton()
    b = honest.get_singleton()
    assert a is b


def test_reset_all_re_arms_every_kind():
    """reset_all_for_tests() re-arms every flag."""
    honest.reset_all_loud_once_for_tests()
    for k in honest.ALL_WARN_KINDS:
        honest.warn(k, "x")
    for k in honest.ALL_WARN_KINDS:
        assert honest.fired(k) is True
    honest.reset_all_loud_once_for_tests()
    for k in honest.ALL_WARN_KINDS:
        assert honest.fired(k) is False
