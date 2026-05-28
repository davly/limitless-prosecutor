"""honest.py -- R143 LOUD-ONCE-WARNING surface for limitless-prosecutor.

R143 cohort discipline: when a library detects a placeholder / developer-curated
default / regulator-rejectable shape at runtime, it MUST emit EXACTLY ONE
warning per process via stderr. Subsequent triggers are no-ops to keep production
log volume bounded.

The cohort canonical implementation uses a module-level threading.Lock + bool
sentinel; this Python port follows that shape via the LoudOnceFlag class and
the HonestWarner orchestrator that holds one flag per warning kind.

Wired by a downstream consumer (the library NEVER calls the warner itself --
the consumer that constructs the offending shape calls warn()).

Pure stdlib: threading + sys + dataclasses. No third-party deps.
"""
from __future__ import annotations

import sys
import threading
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Closed-set warning kinds (R115 cohort discipline)
# ---------------------------------------------------------------------------

# Named constants for warning kinds. Surfacing them as module-level strings
# allows the test layer to assert exact-stderr match without pulling in an Enum
# (which Marker callers would need to import).

WARN_OPERATOR_PLACEHOLDER: str = "operator-identity-placeholder"
WARN_DEVELOPER_CURATED_CHARGING_STANDARDS: str = "developer-curated-charging-standards"
WARN_DEVELOPER_CURATED_SENTENCING_GUIDELINES: str = "developer-curated-sentencing-guidelines"
WARN_MIRROR_MARK_PLACEHOLDER: str = "mirror-mark-placeholder"
WARN_STALE_MANIFEST: str = "stale-manifest"

ALL_WARN_KINDS: tuple[str, ...] = (
    WARN_OPERATOR_PLACEHOLDER,
    WARN_DEVELOPER_CURATED_CHARGING_STANDARDS,
    WARN_DEVELOPER_CURATED_SENTENCING_GUIDELINES,
    WARN_MIRROR_MARK_PLACEHOLDER,
    WARN_STALE_MANIFEST,
)


# ---------------------------------------------------------------------------
# LoudOnceFlag (R143 saturator -- single-flag implementation)
# ---------------------------------------------------------------------------


@dataclass
class LoudOnceFlag:
    """Single LOUD-ONCE warning flag.

    Tracks whether a specific warning has been emitted this process.
    Thread-safe via a per-flag Lock. The R143 contract is exactly-one emission
    per process; reset_for_tests() re-arms the flag for unit tests.
    """

    kind: str
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _fired: bool = False

    def fire(self, message: str, stream=None) -> bool:
        """Emit the warning ONCE; subsequent calls are no-ops.

        Returns True on first emission, False on subsequent emissions.
        Thread-safe under contention: two concurrent calls will see exactly
        one fire() succeed.
        """
        if stream is None:
            stream = sys.stderr
        with self._lock:
            if self._fired:
                return False
            self._fired = True
        # Stderr write is OUTSIDE the lock to avoid serialising callers.
        stream.write(
            f"prosecutor.honest: LOUD-ONCE WARNING [{self.kind}] -- {message}\n"
        )
        return True

    def fired(self) -> bool:
        """Return True iff this flag has emitted at least once this process."""
        with self._lock:
            return self._fired

    def reset_for_tests(self) -> None:
        """Test-only re-arming of the LOUD-ONCE flag. Production callers MUST NOT call."""
        with self._lock:
            self._fired = False


# ---------------------------------------------------------------------------
# HonestWarner (multi-kind orchestrator)
# ---------------------------------------------------------------------------


class HonestWarner:
    """Orchestrator for multiple LOUD-ONCE flags.

    Constructed once at process start (or lazily on first warn()). Holds one
    LoudOnceFlag per warning kind. Used by `legal`, `manifest`, `mirrormark`
    to keep stderr noise bounded per process.

    Thread-safe via per-flag locks (no global lock -- different kinds can
    fire concurrently).
    """

    def __init__(self) -> None:
        self._flags: dict[str, LoudOnceFlag] = {
            kind: LoudOnceFlag(kind=kind) for kind in ALL_WARN_KINDS
        }
        self._registry_lock = threading.Lock()

    def warn(self, kind: str, message: str, stream=None) -> bool:
        """Emit a warning of the given kind ONCE per process.

        kind MUST be in ALL_WARN_KINDS or a new LoudOnceFlag is created
        lazily (allows downstream consumers to define their own warning kinds
        without modifying this module).

        Returns True on first emission, False on subsequent.
        """
        with self._registry_lock:
            if kind not in self._flags:
                self._flags[kind] = LoudOnceFlag(kind=kind)
            flag = self._flags[kind]
        return flag.fire(message, stream=stream)

    def fired(self, kind: str) -> bool:
        """Return True iff a warning of the given kind has been emitted."""
        with self._registry_lock:
            if kind not in self._flags:
                return False
            return self._flags[kind].fired()

    def reset_kind_for_tests(self, kind: str) -> None:
        """Test-only re-arm for a specific kind."""
        with self._registry_lock:
            if kind in self._flags:
                self._flags[kind].reset_for_tests()

    def reset_all_for_tests(self) -> None:
        """Test-only re-arm for ALL kinds."""
        with self._registry_lock:
            for flag in self._flags.values():
                flag.reset_for_tests()


# ---------------------------------------------------------------------------
# Module-level singleton + helpers
# ---------------------------------------------------------------------------

# Process-wide singleton. Initialised lazily on first import. Tests that need
# to re-arm specific flags call reset_all_loud_once_for_tests().
_singleton: HonestWarner = HonestWarner()


def warn(kind: str, message: str, stream=None) -> bool:
    """Module-level convenience for the singleton HonestWarner."""
    return _singleton.warn(kind, message, stream=stream)


def fired(kind: str) -> bool:
    """Module-level convenience for the singleton fired() check."""
    return _singleton.fired(kind)


def reset_all_loud_once_for_tests() -> None:
    """Test-only re-arm of every flag on the module singleton."""
    _singleton.reset_all_for_tests()


def get_singleton() -> HonestWarner:
    """Return the module-level singleton (for tests + introspection)."""
    return _singleton
