# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **OPEN / DEFERRED BY USER**

## Locked structure retained

Canonical body remains:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

Hair remains a separate persistent visible owner. Minimum composition remains:

`rear_hair -> body -> front_hair`

The Exilada's hair remains black/nearly black, very long, heavy, voluminous, messy and wild. `exilada_master.png` remains identity/style/material reference only.

## Closed route history retained

- B4A preflight — PASS/CLOSED DIAGNOSTIC;
- B4B V1 master extraction — FAIL/CLOSED PRE-RUN;
- B4B V2 authored two-layer — FAIL/CLOSED VISUAL / STRUCTURAL PASS;
- B4B V3 — FAIL/CLOSED VISUAL + ALIGNMENT METHOD;
- B4B V4 — FAIL/CLOSED VISUAL + METHOD;
- Pillow polygon/heuristic-anchor hair authoring — CLOSED.

The runner `17_run_g3s_b4b_two_layer_hair_candidate.ps1` remains disabled.

## B4C FLUX.2 review evidence

A one-shot B4C visual-adaptation review artifact was produced at:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter\g3s_b4c_flux2_contact_sheet.png`

User-provided artifact SHA256:

`ac95bf9e3fae2df1e25cc91bcbda69be061526c163ce61cbe0d065cfc7be1c1c`

No B4C pixels were promoted into production hair layers.

## User priority change — LOCKED 2026-09-06

The user explicitly instructed:

> forget hair for now; show the doll implemented in motion.

Therefore:

- B4 is paused/deferred, not approved;
- no further hair runner is the current action;
- B4C review is left as evidence only;
- the current gate is `G3S-C0` body-only motion proof;
- hair work resumes only after explicit user direction.

See:

`docs/G3S_C0_BODY_MOTION_PROOF.md`
