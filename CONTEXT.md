# limitless-prosecutor -- Context

*Created 2026-05-28 during INFRA_MARATHON_2026-05-28 task I44 (M81 deferred-set). New flagship; R174 5-of-5 cohort-maturity from inception per the post-Conjure template.*

## One-line purpose

UK criminal-procedure compliance forge: CPS Code Full Code Test + CPIA 1996 disclosure-schedule classification + PACE 1984 code referencing + cohort-canonical Mirror-Mark + R143/R150/R166 surfaces.

## Current state

| Field | Value |
|---|---|
| **Status** | NEW (created I44 2026-05-28) -- R174 5-of-5 from inception |
| **Layer** | flagship |
| **Language** | Python 3.11+ pure stdlib |
| **Build tool** | setuptools (pyproject.toml) |
| **Version** | 0.1.0 |
| **Package** | `prosecutor` (8 .py modules: mirrormark + honest + legal + manifest + firewall + lore + disclosure_gate + charging_gate) |
| **Pure stdlib** | YES (hashlib + hmac + base64 + dataclasses + enum + threading + os + datetime + sys -- no third-party deps) |
| **Cohort siblings** | arbiter-legal (Py case-law forge) + counsel (Go contract drafting) -- 3-flagship legal-regime cluster |
| **R-rule cohort markers** | R143 (honest.LoudOnceFlag) + R150 (manifest.is_stale 9-path) + R151 (mirrormark KAT-1) + R166 (legal.LIABILITY_FOOTER) + R174 (this manifest -- 5-of-5 inception) + R-AI-SURFACE-CITATION-GATE Profile-B (lore.citation_gate) |

## Domain

UK criminal-procedure compliance via three pinned regimes:

1. **CPS Code for Crown Prosecutors (8th edition, 2018)** -- Full Code Test (paras 4.6-4.14) + Threshold Test (paras 5.1-5.12). Implemented in `charging_gate.py`.

2. **Criminal Procedure and Investigations Act 1996 (CPIA)** -- s3 initial duty + s7A continuing duty + CPIA Code of Practice 2020. Implemented in `disclosure_gate.py`. 4-state closed enum DisclosureOutcome (CPIA_COMPLIANT_FRESH / SCHEDULE_STALE / SENSITIVE_MATERIAL_FLAG / UNUSED_MATERIAL_INCOMPLETE).

3. **Police and Criminal Evidence Act 1984 (PACE) + codes A-H** -- pinned by name only (codes A through H). Compliance check is operator-supplied assertion. See `manifest.HONEST_TODO_SENTINELS` item 3.

## Criminal-justice GDPR carve-out

Criminal-justice data sits OUTSIDE UK GDPR Article 9 (special-category) logic. Recital 19 of the EU GDPR + Directive (EU) 2016/680 (Law Enforcement Directive) carve out competent-authority processing for criminal-justice purposes. UK implementation is Part 3 of the Data Protection Act 2018.

This carve-out is surfaced as a load-bearing string constant in `legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT` and as the 4th default LegalAdvisory (`AdvisoryKind.CRIMINAL_JUSTICE_GDPR_CARVE_OUT`). Pinned by KAT-7 firewall.

## Top-level structure

```
prosecutor/
  __init__.py        -- package exports (R174 5-of-5 from inception)
  mirrormark.py      -- L43 Mirror-Mark v1 KAT-1 cohort port (R151)
  honest.py          -- R143 LOUD-ONCE-WARNING surface via threading.Lock
  legal.py           -- R166 LIABILITY_FOOTER + CPS disclaimer + criminal-justice carve-out
  manifest.py        -- R150 IsStale jurisdiction-version manifest (9-path closed-enum)
  firewall.py        -- KAT-1 / KAT-6 / KAT-7 cohort firewall pins
  lore.py            -- R-AI-SURFACE-CITATION-GATE Profile-B sealed-citation gate
  disclosure_gate.py -- CPIA 1996 DisclosureOutcome 4-state classifier
  charging_gate.py   -- CPS Full Code Test (evidential + public-interest)
tests/
  test_mirrormark.py     -- L43 cohort + KAT-1 parity
  test_honest.py         -- LOUD-ONCE-WARNING + threading invariants
  test_legal.py          -- R166 + CPS disclaimer + carve-out + advisories
  test_manifest.py       -- R150 9-path IsStale + 7 honest-TODO sentinels
  test_firewall.py       -- KAT-1/6/7 parity + compose-all gate
  test_lore.py           -- Profile-B citation gate (5 outcomes)
  test_disclosure_gate.py -- CPIA 4-state classifier
  test_charging_gate.py  -- CPS Full Code Test
```

## Where to find stuff

- **Mirror-Mark KAT-1 anchor:** `prosecutor/mirrormark.py:KAT1_DIGEST_HEX`
- **CPS Code disclaimer:** `prosecutor/legal.py:CPS_CODE_DISCLAIMER`
- **Criminal-justice carve-out:** `prosecutor/legal.py:CRIMINAL_JUSTICE_GDPR_CARVE_OUT`
- **R150 manifest:** `prosecutor/manifest.py:Manifest` + `is_stale()` 9-path
- **Firewall compose-all:** `prosecutor/firewall.py:assert_all_kat_parity()`
- **Profile-B citation gate:** `prosecutor/lore.py:CitationGateOutcome` (5-state)
- **Disclosure 4-state:** `prosecutor/disclosure_gate.py:DisclosureOutcome`
- **Full Code Test:** `prosecutor/charging_gate.py:full_code_test()`

## Cohort relationships

- **Sibling Python forge `flagships/arbiter-legal`:** common-law precedent forge (case-law reasoning). Shares the L43 Mirror-Mark + R143 LOUD-ONCE + R166 LIABILITY_FOOTER + AdvisoryKind closed-enum cohort patterns.
- **Sibling Go forge `flagships/counsel`:** contract drafting + Mirror-Mark wire-in. Together with arbiter-legal forms the 3-flagship legal-regime cluster.
- **Composes with `flagships/arbiter` (Go):** distinct project, R74 dual-axis attorney-required UPL gate. The prosecutor library's `legal.CPS_CODE_DISCLAIMER` is the criminal-justice sibling of arbiter's UPL gate.
