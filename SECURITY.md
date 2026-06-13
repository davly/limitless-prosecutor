# SECURITY — limitless-prosecutor

## Reporting a vulnerability

Report suspected vulnerabilities privately to **david@vocala.co** with subject
line `SECURITY: limitless-prosecutor`. Do **not** open a public issue for a
security report. Please include: affected version, a description, and a
minimal reproduction if available. You will receive an acknowledgement within
a reasonable timeframe and a coordinated-disclosure window before any public
write-up.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ (current; pre-1.0, accepts security fixes) |
| < 0.1.0 | ❌ |

This is a `0.x` library: the public API is not yet frozen, but security fixes
land on the latest `0.1.x`. Pin to a known-good revision for production use.

## Phase-1 scope (load-bearing)

limitless-prosecutor surfaces **structured advisory output** for UK
criminal-procedure compliance (CPS Code Full Code Test, CPIA 1996 disclosure,
PACE 1984 code referencing). It is a high-sensitivity legal-evidence surface
handling disclosure-schedule freshness and SENSITIVE-material flagging
(CPIA s.3 initial duty / s.7A continuing duty). The deployment MUST NOT make
automated charging or disclosure determinations without:

1. **Counsel review** — `legal.DEFAULT_REVIEWED_BY_COUNSEL = False` is the
   R166 honest-default. Library output has NOT been reviewed by an authorised
   Crown Prosecutor or qualified criminal counsel. Per CPS Code para 2.1, a
   real charging decision MUST be taken by an authorised Crown Prosecutor
   exercising independent judgment; per CPIA, the disclosure officer / Crown
   Prosecutor remains responsible for certifying disclosure to the court.
2. **R143 advisory acknowledgement** — the baseline `LegalAdvisory` rows
   (`legal.default_advisories()`, all `reviewed_by_counsel=False`) MUST be
   visible to every operator. The R143 LOUD-ONCE-WARNING surface
   (`honest.LoudOnceFlag`) MUST fire at least once per process.
3. **Corpus cold-verification** — before any live use, the pinned
   jurisdiction-version manifest (`manifest.Manifest` / `manifest.is_stale()`
   9-path) MUST be cold-verified against the canonical published sources
   (CPS Charging Standards × Sentencing Council). A stale manifest MUST block
   the determination, not warn-and-proceed.

## R166 LIABILITY-FOOTER-CONST

The constant `legal.LIABILITY_FOOTER` is the cohort-canonical liability
escape phrase (byte-aligned with arbiter-legal + counsel). Every advisory
payload that crosses a trust boundary MUST embed it verbatim until counsel
review flips the per-document `reviewed_by_counsel` flag to `True`. The CPS
Code disclaimer (`legal.CPS_CODE_DISCLAIMER`) and the criminal-justice GDPR
carve-out (`legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT`, Recital 19 + DPA 2018
Part 3) are likewise load-bearing and pinned by the firewall (see below).

## Mirror-Mark v1 receipt tamper-evidence

The library ships the L43 Mirror-Mark v1 primitive (`mirrormark`):

    mark = "lore@v1:" + base64url(corpusSHA[:8] || HMAC-SHA256(0x01 || corpusSHA || payload, key))

A downstream host may seal a `ChargingDecisionRecord` or
`DisclosureScheduleEntry` with a Mirror-Mark so a verifier can later confirm
"this output came from prosecutor at commit X against inputs Y". Any drift in
corpus SHA, payload, or key changes the mark — tamper-evident by construction.
Verification uses a constant-time comparison (`hmac.compare_digest` /
`mirrormark.verify`). The KAT-1 anchor
(`mirrormark.KAT1_DIGEST_HEX = 239a7d0d…b7dbca`) is reproducible **offline**
with `openssl dgst -sha256 -mac hmac` and is enforced cohort-wide by the
firewall.

## Firewall pins (cold-verifiable)

`firewall.assert_all_kat_parity()` re-derives three Known-Answer Tests at
import/verify time. Drift fails loudly:

- **KAT-1** — L43 Mirror-Mark digest parity (`KAT1_DIGEST_HEX`).
- **KAT-6** — `legal.CPS_CODE_DISCLAIMER` SHA-256 (`KAT6_CPS_CODE_HASH_HEX`).
- **KAT-7** — `legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT` SHA-256
  (`KAT7_CPIA_VERSION_HASH_HEX`).

These let a regulator cold-verify the corpus integrity layer without any
Limitless toolchain.

## Threat model — what this library DOES NOT defend against

- **It does NOT make charging or disclosure determinations.** Output is
  structured advisory only; an authorised Crown Prosecutor / disclosure
  officer must exercise independent judgment (CPS Code para 2.1; CPIA s.3/s.7A).
- **Sensitive-material handling is the host's responsibility.** The library
  *flags* SENSITIVE material (`disclosure_gate.DisclosureOutcome`); it does
  not encrypt, access-control, or store it. Hosts processing CPIA sensitive /
  unused material MUST provide their own at-rest protection and access
  control. (Criminal-justice data is processed under DPA 2018 Part 3 /
  LED 2016/680, outside UK GDPR Art. 9 — see `legal.CRIMINAL_JUSTICE_GDPR_CARVE_OUT`.)
- **Compromised signing key** — there is no KMS integration; the Mirror-Mark
  key is supplied by the host.
- **Compromised / stale corpus SHA** — the manifest staleness check is only
  as good as the canonical reference the host pins it against.
- **Side-channel timing attacks** on base64 decode or prefix compare beyond
  the constant-time HMAC comparison.
- **Jurisdiction gaps** — England & Wales (CPS) only. Does NOT cover Scotland
  (COPFS) or Northern Ireland (PPS). PACE codes A–H are pinned by name only;
  the compliance assertion is operator-supplied. See
  `manifest.HONEST_TODO_SENTINELS`.
