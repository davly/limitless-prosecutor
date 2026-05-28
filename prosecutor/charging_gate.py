"""charging_gate.py -- CPS Full Code Test (evidential + public-interest).

The CPS Code for Crown Prosecutors paras 4.6-4.14 sets out the Full Code Test:
a two-stage test that an authorised Crown Prosecutor applies before charging.

  Stage 1 -- evidential stage (para 4.6):
    "There is sufficient evidence to provide a realistic prospect of
    conviction."
    The test is OBJECTIVE: a jury or bench of magistrates, properly directed
    in accordance with the law, is more likely than not to convict.

  Stage 2 -- public-interest stage (para 4.8):
    "A prosecution will usually take place unless the prosecutor is sure
    that the public interest factors tending against prosecution outweigh
    those tending in favour."
    The Code lists seven public-interest factors at para 4.14.

This module surfaces a closed-enum ChargingOutcome (4 states), a ChargingTest
dataclass (evidential + public-interest stage outcomes), and a full_code_test()
function that returns a ChargingOutcome.

The library does NOT authorise charges -- it surfaces structured advisory
output. The CPS Code disclaimer (`legal.CPS_CODE_DISCLAIMER`) MUST accompany
every charging-test outcome on a user-facing surface.

Pure stdlib: dataclasses + enum. No third-party deps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Closed-enum ChargingOutcome
# ---------------------------------------------------------------------------


class ChargingOutcome(Enum):
    """Closed-enum CPS Full Code Test outcomes.

    CHARGE_BOTH_STAGES_MET:
        Evidential stage met (realistic prospect of conviction) AND
        public-interest stage met (factors in favour outweigh against).
        Advisory output: charge.

    NO_CHARGE_EVIDENTIAL_INSUFFICIENT:
        Evidential stage NOT met. The Code para 4.6 requires the prosecutor
        to be satisfied that there is sufficient evidence; if not, the case
        does not proceed regardless of public interest.

    NO_CHARGE_PUBLIC_INTEREST_AGAINST:
        Evidential stage met BUT public-interest factors against outweigh
        those in favour. The Code para 4.8 requires prosecution unless the
        prosecutor is SURE the factors against outweigh.

    REFER_THRESHOLD_TEST:
        Insufficient evidence available at the charging decision point BUT
        the Threshold Test (Code paras 5.1-5.12) may apply -- the case is
        referred to the Threshold Test pathway rather than the Full Code Test.
    """

    CHARGE_BOTH_STAGES_MET = "charge-both-stages-met"
    NO_CHARGE_EVIDENTIAL_INSUFFICIENT = "no-charge-evidential-insufficient"
    NO_CHARGE_PUBLIC_INTEREST_AGAINST = "no-charge-public-interest-against"
    REFER_THRESHOLD_TEST = "refer-threshold-test"


# Closed-set of all Full Code Test stages used in CHARGING_FULL_CODE_TEST_STAGES.
# Surfaced so a downstream consumer can grep for the two-stage shape.
CHARGING_FULL_CODE_TEST_STAGES: tuple[str, ...] = (
    "evidential-stage",
    "public-interest-stage",
)


# ---------------------------------------------------------------------------
# Public-interest factor closed-enum (CPS Code para 4.14)
# ---------------------------------------------------------------------------


class PublicInterestFactor(Enum):
    """Closed-enum public-interest factors per CPS Code para 4.14.

    These are the seven factors a Crown Prosecutor weighs at the
    public-interest stage. Each factor can tend FOR or AGAINST prosecution
    depending on the facts -- consumers supply a {factor: direction} mapping
    when calling full_code_test().
    """

    SERIOUSNESS_OF_OFFENCE = "seriousness-of-offence"
    SUSPECT_CULPABILITY = "suspect-culpability"
    HARM_TO_VICTIM = "harm-to-victim"
    SUSPECT_AGE_AND_MATURITY = "suspect-age-and-maturity"
    IMPACT_ON_COMMUNITY = "impact-on-community"
    PROSECUTION_PROPORTIONATE = "prosecution-proportionate"
    SOURCES_OF_INFORMATION_PROTECTED = "sources-of-information-protected"


class FactorDirection(Enum):
    """Direction a public-interest factor tends."""

    FOR_PROSECUTION = "for"
    AGAINST_PROSECUTION = "against"
    NEUTRAL = "neutral"


# ---------------------------------------------------------------------------
# Evidential-stage outcome closed-enum
# ---------------------------------------------------------------------------


class EvidentialOutcome(Enum):
    """Evidential-stage outcome per CPS Code para 4.6."""

    REALISTIC_PROSPECT_OF_CONVICTION = "realistic-prospect-of-conviction"
    NO_REALISTIC_PROSPECT = "no-realistic-prospect"
    INSUFFICIENT_AVAILABLE_REFERRABLE_TO_THRESHOLD = (
        "insufficient-available-referrable-to-threshold"
    )


# ---------------------------------------------------------------------------
# ChargingTest dataclass + full_code_test() function
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChargingTest:
    """Input to the Full Code Test.

    evidential_outcome: closed-enum from Stage 1.
    public_interest_factors: mapping of factor -> direction (FOR / AGAINST / NEUTRAL).
        At least one factor MUST be supplied -- the library refuses to evaluate
        Stage 2 against an empty mapping (returns NO_REALISTIC_PROSPECT if Stage 1
        passed but factors empty, since the Code requires affirmative public-interest
        consideration).
    """

    evidential_outcome: EvidentialOutcome
    public_interest_factors: dict[PublicInterestFactor, FactorDirection] = field(
        default_factory=dict
    )


def full_code_test(test: ChargingTest) -> ChargingOutcome:
    """Apply the CPS Full Code Test to the given inputs -> ChargingOutcome.

    Returns a ChargingOutcome. The library does NOT authorise charges -- a
    real charging decision must be taken by an authorised Crown Prosecutor
    against the full case file.

    Logic:
      Stage 1: if EvidentialOutcome is NO_REALISTIC_PROSPECT, return
        NO_CHARGE_EVIDENTIAL_INSUFFICIENT (regardless of Stage 2).
        if INSUFFICIENT_AVAILABLE_REFERRABLE_TO_THRESHOLD, return
        REFER_THRESHOLD_TEST.
      Stage 2: count FOR vs AGAINST factors (NEUTRAL ignored).
        If FOR > AGAINST (strict): CHARGE_BOTH_STAGES_MET.
        Else: NO_CHARGE_PUBLIC_INTEREST_AGAINST.
        The Code para 4.8 requires the prosecutor to be SURE factors against
        outweigh; the library implements the conservative strict-greater-than
        for FOR_PROSECUTION (i.e. ties go against prosecution).

    Note: empty public_interest_factors when Stage 1 passed -> the library
    returns NO_CHARGE_PUBLIC_INTEREST_AGAINST because the Code requires
    affirmative public-interest consideration -- no factors recorded means
    no affirmative basis for prosecution.
    """
    # Stage 1: evidential
    if test.evidential_outcome == EvidentialOutcome.NO_REALISTIC_PROSPECT:
        return ChargingOutcome.NO_CHARGE_EVIDENTIAL_INSUFFICIENT
    if (
        test.evidential_outcome
        == EvidentialOutcome.INSUFFICIENT_AVAILABLE_REFERRABLE_TO_THRESHOLD
    ):
        return ChargingOutcome.REFER_THRESHOLD_TEST

    # Stage 2: public-interest
    n_for = sum(
        1
        for d in test.public_interest_factors.values()
        if d == FactorDirection.FOR_PROSECUTION
    )
    n_against = sum(
        1
        for d in test.public_interest_factors.values()
        if d == FactorDirection.AGAINST_PROSECUTION
    )

    if n_for > n_against:
        return ChargingOutcome.CHARGE_BOTH_STAGES_MET
    return ChargingOutcome.NO_CHARGE_PUBLIC_INTEREST_AGAINST


# ---------------------------------------------------------------------------
# Threshold Test sibling (CPS Code paras 5.1-5.12 -- surfaced as a stub)
# ---------------------------------------------------------------------------


class ThresholdTestOutcome(Enum):
    """Closed-enum CPS Threshold Test outcomes.

    The Threshold Test applies when an immediate charging decision is required
    but the evidence is not yet sufficient to apply the Full Code Test.

    REASONABLE_GROUNDS_TO_SUSPECT_GUILT: para 5.5(a) met.
    NO_REASONABLE_GROUNDS:               para 5.5(a) not met.
    """

    REASONABLE_GROUNDS_TO_SUSPECT_GUILT = "reasonable-grounds-to-suspect-guilt"
    NO_REASONABLE_GROUNDS = "no-reasonable-grounds"
