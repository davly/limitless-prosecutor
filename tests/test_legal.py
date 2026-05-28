"""Tests for prosecutor.legal -- LIABILITY_FOOTER + advisories + carve-out."""
from __future__ import annotations

import pytest

from prosecutor import legal


def test_liability_footer_non_empty():
    """LIABILITY_FOOTER is non-empty + R166 length floor."""
    assert legal.LIABILITY_FOOTER
    assert len(legal.LIABILITY_FOOTER) > 200


def test_liability_footer_names_forge_does_not_authorise():
    """LIABILITY_FOOTER names the cohort 'library-recommends-host-acts' shape."""
    f = legal.LIABILITY_FOOTER.lower()
    assert "forge" in f
    assert ("does not" in f) or ("do not" in f)


def test_cps_code_disclaimer_non_empty():
    """CPS_CODE_DISCLAIMER is non-empty."""
    assert legal.CPS_CODE_DISCLAIMER
    assert "NOT a charging decision" in legal.CPS_CODE_DISCLAIMER


def test_cps_code_disclaimer_cites_code_2_1():
    """CPS_CODE_DISCLAIMER cites CPS Code para 2.1."""
    assert "2.1" in legal.CPS_CODE_DISCLAIMER


def test_criminal_justice_carve_out_non_empty():
    """CRIMINAL_JUSTICE_GDPR_CARVE_OUT names Recital 19 + LED + DPA Part 3."""
    co = legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT
    assert "Recital 19" in co
    assert "2016/680" in co  # LED reference
    assert "Part 3" in co
    assert "DPA 2018".upper() in co.upper() or "Data Protection Act 2018" in co


def test_footer_returns_liability_footer():
    """footer() returns LIABILITY_FOOTER verbatim."""
    assert legal.footer() == legal.LIABILITY_FOOTER


# ---------------------------------------------------------------------------
# Statutory refs
# ---------------------------------------------------------------------------


def test_statutory_refs_cps_present():
    """STATUTORY_REFS includes CPS Code keys."""
    assert "CPS_CODE_2018" in legal.STATUTORY_REFS
    assert "CPS_FULL_CODE_TEST" in legal.STATUTORY_REFS
    assert "CPS_THRESHOLD_TEST" in legal.STATUTORY_REFS


def test_statutory_refs_cpia_present():
    """STATUTORY_REFS includes CPIA 1996 keys."""
    assert "CPIA_1996" in legal.STATUTORY_REFS
    assert "CPIA_S3" in legal.STATUTORY_REFS
    assert "CPIA_S7A" in legal.STATUTORY_REFS
    assert "CPIA_CODE_OF_PRACTICE" in legal.STATUTORY_REFS


def test_statutory_refs_pace_codes_a_through_h():
    """STATUTORY_REFS includes all PACE codes A through H."""
    for letter in "ABCDEFGH":
        key = f"PACE_CODE_{letter}"
        assert key in legal.STATUTORY_REFS, f"missing {key}"


def test_statutory_refs_poa_1985_present():
    """STATUTORY_REFS includes POA 1985 (creates the CPS)."""
    assert "POA_1985" in legal.STATUTORY_REFS
    assert "POA_S3" in legal.STATUTORY_REFS
    assert "POA_S10" in legal.STATUTORY_REFS


def test_statutory_refs_carve_out_present():
    """STATUTORY_REFS includes carve-out references."""
    assert "UK_GDPR_RECITAL_19" in legal.STATUTORY_REFS
    assert "DPA_2018_PART_3" in legal.STATUTORY_REFS
    assert "LED_2016_680" in legal.STATUTORY_REFS


def test_statutory_refs_all_values_non_empty():
    """Every STATUTORY_REFS value is non-empty."""
    for k, v in legal.STATUTORY_REFS.items():
        assert v, f"empty value for {k}"


# ---------------------------------------------------------------------------
# OperatorIdentity invariants
# ---------------------------------------------------------------------------


def test_operator_identity_placeholder_shape():
    """OperatorIdentity.placeholder() returns REPLACE-IN-PRODUCTION strings."""
    op = legal.OperatorIdentity.placeholder()
    assert op.name == "REPLACE-IN-PRODUCTION"
    assert op.cps_area == "REPLACE-IN-PRODUCTION"
    assert op.force_code == "REPLACE-IN-PRODUCTION"
    assert op.contact_email == "REPLACE-IN-PRODUCTION"
    assert op.delegated_dpp_role == "REPLACE-IN-PRODUCTION"
    assert op.is_configured() is False


def test_operator_identity_from_env_uses_placeholders_when_env_absent(monkeypatch):
    """OperatorIdentity.from_env() defaults to placeholder."""
    for key in (
        "PROSECUTOR_OPERATOR_NAME",
        "PROSECUTOR_OPERATOR_CPS_AREA",
        "PROSECUTOR_OPERATOR_FORCE_CODE",
        "PROSECUTOR_OPERATOR_CONTACT_EMAIL",
        "PROSECUTOR_OPERATOR_DELEGATED_DPP_ROLE",
    ):
        monkeypatch.delenv(key, raising=False)
    op = legal.OperatorIdentity.from_env()
    assert op.name == "REPLACE-IN-PRODUCTION"
    assert op.is_configured() is False


def test_operator_identity_from_env_round_trip(monkeypatch):
    """OperatorIdentity.from_env() reads PROSECUTOR_OPERATOR_* env vars."""
    monkeypatch.setenv("PROSECUTOR_OPERATOR_NAME", "CPS West Midlands Demo")
    monkeypatch.setenv("PROSECUTOR_OPERATOR_CPS_AREA", "West Midlands")
    monkeypatch.setenv("PROSECUTOR_OPERATOR_FORCE_CODE", "WMP")
    monkeypatch.setenv("PROSECUTOR_OPERATOR_CONTACT_EMAIL", "cps@example.gov.uk")
    monkeypatch.setenv("PROSECUTOR_OPERATOR_DELEGATED_DPP_ROLE", "DCCP")
    op = legal.OperatorIdentity.from_env()
    assert op.name == "CPS West Midlands Demo"
    assert op.cps_area == "West Midlands"
    assert op.force_code == "WMP"
    assert op.is_configured() is True


def test_operator_identity_is_configured_rejects_partial():
    """is_configured() returns False when any field is empty."""
    op = legal.OperatorIdentity(
        name="X",
        cps_area="",
        force_code="WMP",
        contact_email="x@y.z",
        delegated_dpp_role="DCCP",
    )
    assert op.is_configured() is False


# ---------------------------------------------------------------------------
# LegalAdvisory + default_advisories
# ---------------------------------------------------------------------------


def test_default_advisories_returns_four_rows():
    """default_advisories() returns 4 LegalAdvisory rows."""
    advisories = legal.default_advisories()
    assert len(advisories) == 4


def test_default_advisories_all_unreviewed():
    """Every default advisory ships reviewed_by_counsel=False."""
    for adv in legal.default_advisories():
        assert adv.reviewed_by_counsel is False


def test_default_advisories_body_hash_64_hex():
    """Every advisory body_hash is 64-char hex SHA-256."""
    for adv in legal.default_advisories():
        assert adv.body_hash
        assert len(adv.body_hash) == 64
        int(adv.body_hash, 16)  # raises on non-hex


def test_default_advisories_includes_carve_out_kind():
    """Default advisories include the criminal-justice carve-out kind."""
    kinds = {a.kind for a in legal.default_advisories()}
    assert legal.AdvisoryKind.CRIMINAL_JUSTICE_GDPR_CARVE_OUT in kinds


def test_default_advisories_includes_not_a_charging_decision_kind():
    """Default advisories include not-a-charging-decision kind."""
    kinds = {a.kind for a in legal.default_advisories()}
    assert legal.AdvisoryKind.NOT_A_CHARGING_DECISION in kinds


def test_advisory_kind_four_values():
    """AdvisoryKind has exactly 4 closed-set values."""
    values = {k.value for k in legal.AdvisoryKind}
    assert values == {
        "general-not-legal-advice",
        "not-a-charging-decision",
        "disclosure-not-certified",
        "criminal-justice-gdpr-carve-out",
    }


def test_default_reviewed_by_counsel_false_constant():
    """DEFAULT_REVIEWED_BY_COUNSEL is False (honest-default cohort discipline)."""
    assert legal.DEFAULT_REVIEWED_BY_COUNSEL is False


def test_default_placeholder_alert_names_unreviewed():
    """DEFAULT_PLACEHOLDER_ALERT names the un-reviewed posture."""
    assert "NOT been reviewed" in legal.DEFAULT_PLACEHOLDER_ALERT


# ---------------------------------------------------------------------------
# R143 LOUD-ONCE-WARNING surface
# ---------------------------------------------------------------------------


def test_warn_operator_placeholder_fires_once(capsys):
    """warn_operator_placeholder() emits exactly one warning per process."""
    legal.reset_warned_once_for_tests()
    first = legal.warn_operator_placeholder()
    cap1 = capsys.readouterr()
    assert first is True
    assert "LOUD-ONCE" in cap1.err
    second = legal.warn_operator_placeholder()
    cap2 = capsys.readouterr()
    assert second is False
    assert cap2.err == ""
