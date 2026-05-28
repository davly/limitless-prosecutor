"""legal.py -- Operator transparency + UK statutory cross-references for limitless-prosecutor.

Cohort-aligned Python port of foundation/legal/{refs.go, types.go, config.go}
(Go canonical) + arbiter-legal/legal.py (Python sibling) tailored for the
criminal-justice prosecution forge library shape. Surfaces:

  - UK criminal-procedure statutory reference constants (CPS Code, CPIA 1996,
    PACE 1984, POA 1985, Bail Act 1976, Sentencing Act 2020).
  - LegalAdvisory dataclass + closed-enum AdvisoryKind.
  - OperatorIdentity (CPS area + delegated DPP role + force code).
  - R166 LIABILITY_FOOTER cohort constant.
  - CPS Code disclaimer (the explicit "this is not a charging decision" surface).
  - CRIMINAL_JUSTICE_GDPR_CARVE_OUT (Recital 19 + DPA 2018 Part 3 surface).
  - REVIEWED_BY_COUNSEL = False honest-default + DEFAULT_PLACEHOLDER_ALERT.

Prosecutor-specific framing: prosecutor is a forge that recommends charging
posture + disclosure compliance; the human Crown Prosecutor or police custody
sergeant acts. The library does not authorise charges. See SECURITY.md.

Knowledge-bedrock posture (per Marc 2026-05-18):
  - CPS Code stage names, CPIA section numbers, PACE codes are universal across
    UK operators -> hardcoded refs OK.
  - Operator identity (CPS area name, area code, contact) is per-tenant ->
    injected via OperatorIdentity at boot.

Criminal-justice GDPR carve-out:
  Recital 19 of the EU GDPR (and the Law Enforcement Directive 2016/680 Art 2)
  carves out processing by competent authorities for the prevention,
  investigation, detection or prosecution of criminal offences. The UK
  implementation is Part 3 of the Data Protection Act 2018. This carve-out
  means Article 9 special-category logic does NOT apply to criminal-justice
  data in the same way it applies to GDPR Part 2 (general processing).

Pure stdlib: dataclasses + enum + hashlib + os + threading + sys. No third-party deps.
"""
from __future__ import annotations

import hashlib
import os
import sys
import threading
from dataclasses import dataclass
from enum import Enum

from . import honest


# ---------------------------------------------------------------------------
# UK criminal-procedure statutory references
# ---------------------------------------------------------------------------

# CPS Code for Crown Prosecutors (8th edition, October 2018).
REF_CPS_CODE_2018: str = "CPS Code for Crown Prosecutors (8th edition, 2018)"
REF_CPS_FULL_CODE_TEST: str = "CPS Code paras 4.6-4.14 (Full Code Test)"
REF_CPS_THRESHOLD_TEST: str = "CPS Code paras 5.1-5.12 (Threshold Test)"

# Criminal Procedure and Investigations Act 1996 (CPIA).
REF_CPIA_1996: str = "Criminal Procedure and Investigations Act 1996"
REF_CPIA_S3: str = "CPIA 1996 s3 (initial duty of disclosure by prosecutor)"
REF_CPIA_S7A: str = "CPIA 1996 s7A (continuing duty of disclosure)"
REF_CPIA_S23: str = "CPIA 1996 s23 (Code of Practice)"
REF_CPIA_CODE_OF_PRACTICE: str = "CPIA Code of Practice (2020 revision)"

# Police and Criminal Evidence Act 1984 (PACE) + codes.
REF_PACE_1984: str = "Police and Criminal Evidence Act 1984"
REF_PACE_CODE_A: str = "PACE Code A (stop and search)"
REF_PACE_CODE_B: str = "PACE Code B (search of premises and seizure)"
REF_PACE_CODE_C: str = "PACE Code C (detention, treatment and questioning)"
REF_PACE_CODE_D: str = "PACE Code D (identification)"
REF_PACE_CODE_E: str = "PACE Code E (audio recording of interviews)"
REF_PACE_CODE_F: str = "PACE Code F (visual recording of interviews)"
REF_PACE_CODE_G: str = "PACE Code G (statutory power of arrest)"
REF_PACE_CODE_H: str = "PACE Code H (detention under Terrorism Act)"

# Prosecution of Offences Act 1985 (POA) -- creates the CPS + DPP role.
REF_POA_1985: str = "Prosecution of Offences Act 1985"
REF_POA_S3: str = "POA 1985 s3 (functions of the DPP)"
REF_POA_S10: str = "POA 1985 s10 (the Code for Crown Prosecutors)"

# Bail Act 1976.
REF_BAIL_ACT_1976: str = "Bail Act 1976"

# Sentencing Act 2020 (consolidated sentencing code).
REF_SENTENCING_ACT_2020: str = "Sentencing Act 2020"

# Sentencing Council guideline corpus (universal-fact reference; specific
# guideline versions are pinned per-tenant in manifest.py).
REF_SENTENCING_COUNCIL_GUIDELINES: str = (
    "Sentencing Council definitive guidelines (England and Wales)"
)

# UK GDPR cross-refs (surfaced for the carve-out narrative).
REF_UK_GDPR_RECITAL_19: str = "UK GDPR Recital 19 (criminal-justice carve-out)"
REF_DPA_2018_PART_3: str = "Data Protection Act 2018 Part 3 (law enforcement processing)"
REF_LED_2016_680: str = (
    "Directive (EU) 2016/680 (Law Enforcement Directive)"
)


STATUTORY_REFS: dict[str, str] = {
    "CPS_CODE_2018": REF_CPS_CODE_2018,
    "CPS_FULL_CODE_TEST": REF_CPS_FULL_CODE_TEST,
    "CPS_THRESHOLD_TEST": REF_CPS_THRESHOLD_TEST,
    "CPIA_1996": REF_CPIA_1996,
    "CPIA_S3": REF_CPIA_S3,
    "CPIA_S7A": REF_CPIA_S7A,
    "CPIA_S23": REF_CPIA_S23,
    "CPIA_CODE_OF_PRACTICE": REF_CPIA_CODE_OF_PRACTICE,
    "PACE_1984": REF_PACE_1984,
    "PACE_CODE_A": REF_PACE_CODE_A,
    "PACE_CODE_B": REF_PACE_CODE_B,
    "PACE_CODE_C": REF_PACE_CODE_C,
    "PACE_CODE_D": REF_PACE_CODE_D,
    "PACE_CODE_E": REF_PACE_CODE_E,
    "PACE_CODE_F": REF_PACE_CODE_F,
    "PACE_CODE_G": REF_PACE_CODE_G,
    "PACE_CODE_H": REF_PACE_CODE_H,
    "POA_1985": REF_POA_1985,
    "POA_S3": REF_POA_S3,
    "POA_S10": REF_POA_S10,
    "BAIL_ACT_1976": REF_BAIL_ACT_1976,
    "SENTENCING_ACT_2020": REF_SENTENCING_ACT_2020,
    "SENTENCING_COUNCIL_GUIDELINES": REF_SENTENCING_COUNCIL_GUIDELINES,
    "UK_GDPR_RECITAL_19": REF_UK_GDPR_RECITAL_19,
    "DPA_2018_PART_3": REF_DPA_2018_PART_3,
    "LED_2016_680": REF_LED_2016_680,
}


# ---------------------------------------------------------------------------
# R166 LIABILITY_FOOTER (cohort-canonical, byte-aligned with arbiter-legal +
# counsel + deeds + arbiter)
# ---------------------------------------------------------------------------

LIABILITY_FOOTER: str = (
    "limitless-prosecutor is a criminal-justice compliance forge: it recommends "
    "charging posture (CPS Full Code Test outcome class) and disclosure "
    "completeness (CPIA 1996 schedule status); it does not authorise charges, "
    "does not file informations, and does not certify disclosure to the court. "
    "Any charging-test outcome, disclosure-schedule status, or PACE-compliance "
    "audit surfaced by this library is structured advisory output -- the human "
    "Crown Prosecutor, custody sergeant, or disclosure officer acts. Do not "
    "rely on this output as a substitute for advice from a qualified UK Crown "
    "Prosecutor authorised by the Director of Public Prosecutions."
)

# CPS Code disclaimer surface (the regulator-rejectable explicit form). The
# library MUST surface this on every charging-decision-shaped output so the
# downstream caller cannot accidentally rely on prosecutor output as a
# substantive charging decision.
CPS_CODE_DISCLAIMER: str = (
    "This output is NOT a charging decision. The CPS Code for Crown Prosecutors "
    "para 2.1 requires that 'the decision to prosecute is a serious step' taken "
    "by a Crown Prosecutor exercising independent judgment under the Director "
    "of Public Prosecutions. limitless-prosecutor surfaces the Full Code Test "
    "stage outcomes (evidential + public-interest) as STRUCTURED ADVISORY "
    "OUTPUT only. A real charging decision must be taken by an authorised "
    "prosecutor against the full case file -- not against this library's "
    "summary inputs."
)

# Criminal-justice GDPR carve-out surface.
CRIMINAL_JUSTICE_GDPR_CARVE_OUT: str = (
    "Criminal-justice data processed for the purposes of the prevention, "
    "investigation, detection or prosecution of criminal offences sits OUTSIDE "
    "UK GDPR Part 2 (general processing) and Article 9 special-category logic. "
    "Recital 19 of the EU GDPR and Directive (EU) 2016/680 (Law Enforcement "
    "Directive) carve out competent-authority processing; the UK implementation "
    "is Part 3 of the Data Protection Act 2018. This means a DSAR / Article 9 "
    "consent / pseudonymisation analysis applied to criminal-justice data must "
    "be done against DPA 2018 Part 3 NOT UK GDPR Part 2. limitless-prosecutor "
    "surfaces this carve-out so downstream consumers do not apply general-GDPR "
    "logic to criminal-justice data and reach the wrong compliance posture."
)

# Operator-identity placeholder shape (cohort convention).
OPERATOR_PLACEHOLDER: dict[str, str] = {
    "name": "REPLACE-IN-PRODUCTION",
    "cps_area": "REPLACE-IN-PRODUCTION",
    "force_code": "REPLACE-IN-PRODUCTION",
    "contact_email": "REPLACE-IN-PRODUCTION",
    "delegated_dpp_role": "REPLACE-IN-PRODUCTION",
}

# Honest-default constant. Every flagship's per-document ReviewedByCounsel
# constant SHOULD ship as False until a real legal review has happened.
# Byte-identical to foundation/legal/refs.DefaultReviewedByCounsel.
DEFAULT_REVIEWED_BY_COUNSEL: bool = False

# Honest-defaults LOUD banner emitted at the top of any un-reviewed legal
# document. Cohort-aligned with foundation/legal/refs.DefaultPlaceholderAlert.
DEFAULT_PLACEHOLDER_ALERT: str = (
    "IMPORTANT: This advisory is structured output from the limitless-prosecutor "
    "forge and has NOT been reviewed by a qualified UK Crown Prosecutor. The "
    "operator must obtain authorised prosecutor review before any charging or "
    "disclosure decision is taken on the basis of this output."
)


# ---------------------------------------------------------------------------
# OperatorIdentity (cohort-aligned with foundation/legal/config.LegalConfig)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OperatorIdentity:
    """Operator-injected legal-identity strings for a CPS-area operator.

    Cohort-extracted from foundation/legal/config.LegalConfig + extended with
    CPS-area + force-code + delegated-DPP-role fields specific to UK criminal
    justice. Every operator must set every required field before going live.
    """

    name: str = ""
    cps_area: str = ""
    force_code: str = ""
    contact_email: str = ""
    delegated_dpp_role: str = ""

    @classmethod
    def placeholder(cls) -> "OperatorIdentity":
        """Return an OperatorIdentity populated with REPLACE-IN-PRODUCTION placeholders."""
        return cls(
            name=OPERATOR_PLACEHOLDER["name"],
            cps_area=OPERATOR_PLACEHOLDER["cps_area"],
            force_code=OPERATOR_PLACEHOLDER["force_code"],
            contact_email=OPERATOR_PLACEHOLDER["contact_email"],
            delegated_dpp_role=OPERATOR_PLACEHOLDER["delegated_dpp_role"],
        )

    @classmethod
    def from_env(cls) -> "OperatorIdentity":
        """Construct an OperatorIdentity from `PROSECUTOR_OPERATOR_*` env vars.

        When env vars are unset, returns the placeholder shape. The cohort
        convention is that production deploys MUST set every field.
        """
        return cls(
            name=os.environ.get("PROSECUTOR_OPERATOR_NAME", OPERATOR_PLACEHOLDER["name"]),
            cps_area=os.environ.get(
                "PROSECUTOR_OPERATOR_CPS_AREA", OPERATOR_PLACEHOLDER["cps_area"]
            ),
            force_code=os.environ.get(
                "PROSECUTOR_OPERATOR_FORCE_CODE", OPERATOR_PLACEHOLDER["force_code"]
            ),
            contact_email=os.environ.get(
                "PROSECUTOR_OPERATOR_CONTACT_EMAIL", OPERATOR_PLACEHOLDER["contact_email"]
            ),
            delegated_dpp_role=os.environ.get(
                "PROSECUTOR_OPERATOR_DELEGATED_DPP_ROLE",
                OPERATOR_PLACEHOLDER["delegated_dpp_role"],
            ),
        )

    def is_configured(self) -> bool:
        """Return True iff every required field is non-placeholder + non-empty."""
        for v in (
            self.name,
            self.cps_area,
            self.force_code,
            self.contact_email,
            self.delegated_dpp_role,
        ):
            if not v or v == "REPLACE-IN-PRODUCTION":
                return False
        return True


# ---------------------------------------------------------------------------
# LegalAdvisory closed-enum + dataclass
# ---------------------------------------------------------------------------


class AdvisoryKind(Enum):
    """Closed-enum advisory kinds (R115 cohort discipline).

    GENERAL_NOT_LEGAL_ADVICE: blanket disclaimer.
    NOT_A_CHARGING_DECISION: per-charging-test disclaimer (CPS Code para 2.1).
    DISCLOSURE_NOT_CERTIFIED: per-disclosure-schedule disclaimer.
    CRIMINAL_JUSTICE_GDPR_CARVE_OUT: carve-out advisory (Recital 19).
    """

    GENERAL_NOT_LEGAL_ADVICE = "general-not-legal-advice"
    NOT_A_CHARGING_DECISION = "not-a-charging-decision"
    DISCLOSURE_NOT_CERTIFIED = "disclosure-not-certified"
    CRIMINAL_JUSTICE_GDPR_CARVE_OUT = "criminal-justice-gdpr-carve-out"


@dataclass(frozen=True)
class LegalAdvisory:
    """A single legal advisory surface row.

    kind: AdvisoryKind closed-enum value.
    body: human-readable advisory text.
    reviewed_by_counsel: honest-default False until a real review has happened.
    body_hash: hex SHA-256 over body bytes (UTF-8). Stable across deploys.
    """

    kind: AdvisoryKind
    body: str
    reviewed_by_counsel: bool
    body_hash: str


def _body_hash(body: str) -> str:
    """Return hex-encoded SHA-256 over body bytes."""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def default_advisories() -> tuple[LegalAdvisory, ...]:
    """Return the 4 baseline LegalAdvisory rows with reviewed_by_counsel=False.

    Cohort convention: the default advisories ship un-reviewed; an operator
    MUST obtain authorised prosecutor review before any user-facing publication.
    """
    general = (
        "This output is not legal advice. limitless-prosecutor recommends "
        "criminal-justice compliance posture (CPS Full Code Test outcome class "
        "+ CPIA disclosure completeness); the human Crown Prosecutor or "
        "disclosure officer acts. See LIABILITY_FOOTER for full disclaimer."
    )
    not_charging = CPS_CODE_DISCLAIMER
    disclosure = (
        "Disclosure outcomes surfaced by limitless-prosecutor are structured "
        "advisory output gated on the recorded schedule entries and CPIA s3/s7A "
        "duty-frame. They do NOT certify completeness of disclosure to the "
        "court. The disclosure officer or Crown Prosecutor is responsible for "
        "certifying completeness against the full case-file."
    )
    carve_out = CRIMINAL_JUSTICE_GDPR_CARVE_OUT
    return (
        LegalAdvisory(
            kind=AdvisoryKind.GENERAL_NOT_LEGAL_ADVICE,
            body=general,
            reviewed_by_counsel=DEFAULT_REVIEWED_BY_COUNSEL,
            body_hash=_body_hash(general),
        ),
        LegalAdvisory(
            kind=AdvisoryKind.NOT_A_CHARGING_DECISION,
            body=not_charging,
            reviewed_by_counsel=DEFAULT_REVIEWED_BY_COUNSEL,
            body_hash=_body_hash(not_charging),
        ),
        LegalAdvisory(
            kind=AdvisoryKind.DISCLOSURE_NOT_CERTIFIED,
            body=disclosure,
            reviewed_by_counsel=DEFAULT_REVIEWED_BY_COUNSEL,
            body_hash=_body_hash(disclosure),
        ),
        LegalAdvisory(
            kind=AdvisoryKind.CRIMINAL_JUSTICE_GDPR_CARVE_OUT,
            body=carve_out,
            reviewed_by_counsel=DEFAULT_REVIEWED_BY_COUNSEL,
            body_hash=_body_hash(carve_out),
        ),
    )


# ---------------------------------------------------------------------------
# R143 LOUD-ONCE-WARNING surface (delegated to honest singleton)
# ---------------------------------------------------------------------------


def warn_operator_placeholder() -> bool:
    """R143 LOUD-ONCE for un-configured OperatorIdentity.

    Emits exactly ONE warning per process via stderr when first called.
    Subsequent calls are no-ops. Delegates to honest.warn() singleton.
    """
    return honest.warn(
        honest.WARN_OPERATOR_PLACEHOLDER,
        "operator identity is unconfigured (REPLACE-IN-PRODUCTION placeholders detected). "
        "Production deploys must set PROSECUTOR_OPERATOR_NAME / _CPS_AREA / "
        "_FORCE_CODE / _CONTACT_EMAIL / _DELEGATED_DPP_ROLE before going live.",
    )


def footer() -> str:
    """Return the cohort-canonical liability footer text."""
    return LIABILITY_FOOTER


# ---------------------------------------------------------------------------
# Backwards-compat shim (reset_warned_once_for_tests for cohort-aligned API)
# ---------------------------------------------------------------------------

_legacy_lock = threading.Lock()


def reset_warned_once_for_tests() -> None:
    """Test-only re-arming compatible with arbiter-legal API shape."""
    honest.reset_all_loud_once_for_tests()
