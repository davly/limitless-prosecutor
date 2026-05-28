"""Tests for prosecutor.charging_gate -- CPS Full Code Test."""
from __future__ import annotations

import pytest

from prosecutor import charging_gate


def test_charging_outcome_closed_set():
    """ChargingOutcome has the 4 documented states."""
    values = {c.value for c in charging_gate.ChargingOutcome}
    assert values == {
        "charge-both-stages-met",
        "no-charge-evidential-insufficient",
        "no-charge-public-interest-against",
        "refer-threshold-test",
    }


def test_full_code_test_stages_constant():
    """CHARGING_FULL_CODE_TEST_STAGES names the two stages."""
    assert charging_gate.CHARGING_FULL_CODE_TEST_STAGES == (
        "evidential-stage",
        "public-interest-stage",
    )


def test_public_interest_factor_seven_factors():
    """PublicInterestFactor has the 7 CPS Code para 4.14 factors."""
    assert len(charging_gate.PublicInterestFactor) == 7


def test_factor_direction_three_values():
    """FactorDirection has FOR / AGAINST / NEUTRAL."""
    values = {d.value for d in charging_gate.FactorDirection}
    assert values == {"for", "against", "neutral"}


def test_evidential_outcome_three_values():
    """EvidentialOutcome has 3 closed-set values."""
    values = {e.value for e in charging_gate.EvidentialOutcome}
    assert values == {
        "realistic-prospect-of-conviction",
        "no-realistic-prospect",
        "insufficient-available-referrable-to-threshold",
    }


def test_full_code_test_charge_when_both_stages_met():
    """Evidential PASS + majority FOR factors -> CHARGE_BOTH_STAGES_MET."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.REALISTIC_PROSPECT_OF_CONVICTION,
        public_interest_factors={
            charging_gate.PublicInterestFactor.SERIOUSNESS_OF_OFFENCE: charging_gate.FactorDirection.FOR_PROSECUTION,
            charging_gate.PublicInterestFactor.HARM_TO_VICTIM: charging_gate.FactorDirection.FOR_PROSECUTION,
            charging_gate.PublicInterestFactor.SUSPECT_AGE_AND_MATURITY: charging_gate.FactorDirection.AGAINST_PROSECUTION,
        },
    )
    assert (
        charging_gate.full_code_test(test)
        == charging_gate.ChargingOutcome.CHARGE_BOTH_STAGES_MET
    )


def test_full_code_test_no_charge_evidential_insufficient():
    """NO_REALISTIC_PROSPECT short-circuits to NO_CHARGE_EVIDENTIAL_INSUFFICIENT."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.NO_REALISTIC_PROSPECT,
        public_interest_factors={
            charging_gate.PublicInterestFactor.SERIOUSNESS_OF_OFFENCE: charging_gate.FactorDirection.FOR_PROSECUTION,
        },
    )
    assert (
        charging_gate.full_code_test(test)
        == charging_gate.ChargingOutcome.NO_CHARGE_EVIDENTIAL_INSUFFICIENT
    )


def test_full_code_test_refers_to_threshold():
    """INSUFFICIENT_AVAILABLE_REFERRABLE_TO_THRESHOLD -> REFER_THRESHOLD_TEST."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.INSUFFICIENT_AVAILABLE_REFERRABLE_TO_THRESHOLD,
    )
    assert (
        charging_gate.full_code_test(test)
        == charging_gate.ChargingOutcome.REFER_THRESHOLD_TEST
    )


def test_full_code_test_no_charge_public_interest_against():
    """Evidential PASS + majority AGAINST -> NO_CHARGE_PUBLIC_INTEREST_AGAINST."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.REALISTIC_PROSPECT_OF_CONVICTION,
        public_interest_factors={
            charging_gate.PublicInterestFactor.SUSPECT_AGE_AND_MATURITY: charging_gate.FactorDirection.AGAINST_PROSECUTION,
            charging_gate.PublicInterestFactor.PROSECUTION_PROPORTIONATE: charging_gate.FactorDirection.AGAINST_PROSECUTION,
            charging_gate.PublicInterestFactor.SERIOUSNESS_OF_OFFENCE: charging_gate.FactorDirection.FOR_PROSECUTION,
        },
    )
    assert (
        charging_gate.full_code_test(test)
        == charging_gate.ChargingOutcome.NO_CHARGE_PUBLIC_INTEREST_AGAINST
    )


def test_full_code_test_tie_goes_against_prosecution():
    """Ties between FOR and AGAINST go AGAINST (conservative para 4.8 reading)."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.REALISTIC_PROSPECT_OF_CONVICTION,
        public_interest_factors={
            charging_gate.PublicInterestFactor.SERIOUSNESS_OF_OFFENCE: charging_gate.FactorDirection.FOR_PROSECUTION,
            charging_gate.PublicInterestFactor.SUSPECT_AGE_AND_MATURITY: charging_gate.FactorDirection.AGAINST_PROSECUTION,
        },
    )
    assert (
        charging_gate.full_code_test(test)
        == charging_gate.ChargingOutcome.NO_CHARGE_PUBLIC_INTEREST_AGAINST
    )


def test_full_code_test_neutral_factors_ignored():
    """NEUTRAL factors are ignored in the FOR vs AGAINST count."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.REALISTIC_PROSPECT_OF_CONVICTION,
        public_interest_factors={
            charging_gate.PublicInterestFactor.SERIOUSNESS_OF_OFFENCE: charging_gate.FactorDirection.FOR_PROSECUTION,
            charging_gate.PublicInterestFactor.HARM_TO_VICTIM: charging_gate.FactorDirection.NEUTRAL,
            charging_gate.PublicInterestFactor.SUSPECT_AGE_AND_MATURITY: charging_gate.FactorDirection.NEUTRAL,
        },
    )
    assert (
        charging_gate.full_code_test(test)
        == charging_gate.ChargingOutcome.CHARGE_BOTH_STAGES_MET
    )


def test_full_code_test_empty_factors_no_charge():
    """Evidential PASS + empty factors -> NO_CHARGE (no affirmative basis)."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.REALISTIC_PROSPECT_OF_CONVICTION,
        public_interest_factors={},
    )
    assert (
        charging_gate.full_code_test(test)
        == charging_gate.ChargingOutcome.NO_CHARGE_PUBLIC_INTEREST_AGAINST
    )


def test_threshold_test_outcome_closed_set():
    """ThresholdTestOutcome has 2 closed-set values."""
    values = {o.value for o in charging_gate.ThresholdTestOutcome}
    assert values == {
        "reasonable-grounds-to-suspect-guilt",
        "no-reasonable-grounds",
    }


def test_charging_test_frozen():
    """ChargingTest dataclass is frozen."""
    test = charging_gate.ChargingTest(
        evidential_outcome=charging_gate.EvidentialOutcome.REALISTIC_PROSPECT_OF_CONVICTION,
    )
    with pytest.raises(Exception):
        test.evidential_outcome = charging_gate.EvidentialOutcome.NO_REALISTIC_PROSPECT  # type: ignore[misc]
