# limitless-prosecutor

UK Crown Prosecution Service (CPS) / Criminal Procedure and Investigations Act 1996 (CPIA) / Police and Criminal Evidence Act 1984 (PACE) compliance forge. Pure-stdlib Python 3.11+.

## What it does

Surfaces structured compliance posture for the three load-bearing UK criminal-procedure regimes:

- **CPS Code Full Code Test** (Code paras 4.6-4.14): evidential + public-interest two-stage charging test.
- **CPIA 1996 prosecution disclosure** (s3 initial duty + s7A continuing duty): schedule freshness + sensitive-material flagging + unused-material completeness.
- **PACE 1984 codes** (A-H): reference-only pinning; downstream consumer supplies the compliance assertion.

Plus cohort-canonical R-rule surfaces:

- L43 Mirror-Mark v1 (R151 KAT-1 anchor `239a7d0d...b7dbca`).
- R143 LOUD-ONCE-WARNING via `threading.Lock`.
- R166 LIABILITY_FOOTER cohort constant.
- R150 IsStale jurisdiction-version manifest (CPS Charging Standards x Sentencing Council).
- KAT-1/6/7 firewall pins.
- R-AI-SURFACE-CITATION-GATE Profile-B sealed-citation gate.

## What it does NOT do

- Does NOT authorise charges. The library surfaces STRUCTURED ADVISORY OUTPUT only. The CPS Code para 2.1 requires that a real charging decision is taken by an authorised Crown Prosecutor exercising independent judgment.
- Does NOT certify disclosure to the court. The disclosure officer / Crown Prosecutor remains responsible for certifying CPIA compliance.
- Does NOT cover Scotland (COPFS) or Northern Ireland (PPS). The library is E&W (CPS) only. See `manifest.HONEST_TODO_SENTINELS` item 7.

## Criminal-justice GDPR carve-out

Criminal-justice data sits OUTSIDE UK GDPR Article 9 special-category logic. Recital 19 of the EU GDPR and Directive (EU) 2016/680 (Law Enforcement Directive) carve out competent-authority processing. The UK implementation is Part 3 of the Data Protection Act 2018. See `legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT`.

## Composes with

- `flagships/arbiter-legal` (Python case-law forge).
- `flagships/counsel` (Go contract drafting forge).
- 3-flagship legal-regime cluster: arbiter-legal + counsel + prosecutor.

## Install

```bash
pip install -e .
```

## Run tests

```bash
pytest -q
```
