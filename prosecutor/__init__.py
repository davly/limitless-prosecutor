"""Limitless Flagship: limitless-prosecutor -- UK CPS/CPIA/PACE compliance forge.

A criminal-justice compliance forge built around the Crown Prosecution Service
(CPS) Code for Crown Prosecutors, the Criminal Procedure and Investigations Act
1996 (CPIA), and the Police and Criminal Evidence Act 1984 (PACE).

Surfaces (all opt-in by downstream host; no auto-wiring):

- `mirrormark`: L43 Mirror-Mark v1 KAT-1 cohort port (HMAC-SHA256 byte-identical
  with foundation/pkg/mirrormark + the Go/Python/Rust cohort).
- `honest`: R143 LOUD-ONCE-WARNING surface via threading.Lock.
- `legal`: R166 LIABILITY_FOOTER constant + CPS Code disclaimer + criminal-
  justice GDPR carve-out (Recital 19) + ReviewedByCounsel=False honest default.
- `manifest`: R150 IsStale jurisdiction-version pin (CPS Charging Standards x
  Sentencing Council guidelines).
- `firewall`: KAT-1 / KAT-6 / KAT-7 cohort firewall pins.
- `lore`: R-AI-SURFACE-CITATION-GATE Profile-B sealed-citation gate.
- `disclosure_gate`: CPIA 1996 prosecution-disclosure DisclosureOutcome enum.
- `charging_gate`: CPS Full Code Test (evidential + public-interest stages).

Knowledge-bedrock posture (per Marc 2026-05-18):
  - CPS Code stage names, CPIA section numbers, PACE codes are universal facts
    across UK operators -> hardcoded constants OK.
  - Operator identity (CPS area, force code, Director of Public Prosecutions
    delegate) is per-tenant -> injected via OperatorIdentity at boot.
  - Charging Standards rev-date + Sentencing Council guideline version are
    jurisdiction-version stale-checked via R150 IsStale.

Criminal-justice GDPR carve-out:
  Criminal-justice data is OUTSIDE the GDPR Article 9 special-category regime.
  Recital 19 of the Law Enforcement Directive (LED, EU 2016/680) carves out
  processing by competent authorities for the purposes of the prevention,
  investigation, detection or prosecution of criminal offences. The UK
  implementation is Part 3 of the Data Protection Act 2018. This library
  surfaces that carve-out in `legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT`.

Pure stdlib: hashlib + hmac + base64 + dataclasses + enum + threading + os +
json + sys. No third-party deps.
"""
from __future__ import annotations

__version__ = "0.1.0"

# Additive: L43 Mirror-Mark v1 cohort port
from . import mirrormark  # noqa: F401
# Additive: R143 LOUD-ONCE-WARNING surface
from . import honest  # noqa: F401
# Additive: R166 LIABILITY_FOOTER + CPS disclaimer + criminal-justice carve-out
from . import legal  # noqa: F401
# Additive: R150 IsStale jurisdiction-version manifest
from . import manifest  # noqa: F401
# Additive: KAT-1 / KAT-6 / KAT-7 firewall pins
from . import firewall  # noqa: F401
# Additive: R-AI-SURFACE-CITATION-GATE Profile-B sealed-citation gate
from . import lore  # noqa: F401
# Additive: CPIA 1996 disclosure-outcome closed enum
from . import disclosure_gate  # noqa: F401
# Additive: CPS Full Code Test charging gate
from . import charging_gate  # noqa: F401

from .charging_gate import (
    CHARGING_FULL_CODE_TEST_STAGES,
    ChargingOutcome,
    ChargingTest,
    PublicInterestFactor,
    full_code_test,
)
from .disclosure_gate import (
    CPIA_DISCLOSURE_TESTS,
    DisclosureGate,
    DisclosureOutcome,
    DisclosureRequest,
    DisclosureScheduleEntry,
)
from .firewall import (
    KAT1_DIGEST_HEX,
    KAT6_CPS_CODE_HASH_HEX,
    KAT7_CPIA_VERSION_HASH_HEX,
    assert_all_kat_parity,
)
from .honest import (
    HonestWarner,
    LoudOnceFlag,
    reset_all_loud_once_for_tests,
)
from .legal import (
    CPS_CODE_DISCLAIMER,
    CRIMINAL_JUSTICE_GDPR_CARVE_OUT,
    DEFAULT_REVIEWED_BY_COUNSEL,
    LIABILITY_FOOTER,
    LegalAdvisory,
    OperatorIdentity,
    default_advisories,
    footer,
)
from .lore import (
    CitationGateOutcome,
    CitationGateRefusalReason,
    SealedCitation,
    citation_gate,
    seal_citation,
)
from .manifest import (
    CPS_CHARGING_STANDARDS_REV_DATE,
    SENTENCING_COUNCIL_GUIDELINE_REV_DATE,
    Manifest,
    StalenessOutcome,
    is_stale,
)
from .mirrormark import (
    KAT1_MARK,
    MARK_PREFIX,
    Marker,
    assert_kat1_parity,
    sign,
    verify,
)

__all__ = [
    "__version__",
    # mirrormark
    "Marker",
    "sign",
    "verify",
    "assert_kat1_parity",
    "MARK_PREFIX",
    "KAT1_MARK",
    # honest
    "HonestWarner",
    "LoudOnceFlag",
    "reset_all_loud_once_for_tests",
    # legal
    "LIABILITY_FOOTER",
    "CPS_CODE_DISCLAIMER",
    "CRIMINAL_JUSTICE_GDPR_CARVE_OUT",
    "DEFAULT_REVIEWED_BY_COUNSEL",
    "LegalAdvisory",
    "OperatorIdentity",
    "default_advisories",
    "footer",
    # manifest
    "Manifest",
    "StalenessOutcome",
    "is_stale",
    "CPS_CHARGING_STANDARDS_REV_DATE",
    "SENTENCING_COUNCIL_GUIDELINE_REV_DATE",
    # firewall
    "KAT1_DIGEST_HEX",
    "KAT6_CPS_CODE_HASH_HEX",
    "KAT7_CPIA_VERSION_HASH_HEX",
    "assert_all_kat_parity",
    # lore
    "SealedCitation",
    "CitationGateOutcome",
    "CitationGateRefusalReason",
    "seal_citation",
    "citation_gate",
    # disclosure_gate
    "DisclosureOutcome",
    "DisclosureRequest",
    "DisclosureScheduleEntry",
    "DisclosureGate",
    "CPIA_DISCLOSURE_TESTS",
    # charging_gate
    "ChargingOutcome",
    "ChargingTest",
    "PublicInterestFactor",
    "full_code_test",
    "CHARGING_FULL_CODE_TEST_STAGES",
    # submodules
    "mirrormark",
    "honest",
    "legal",
    "manifest",
    "firewall",
    "lore",
    "disclosure_gate",
    "charging_gate",
]
