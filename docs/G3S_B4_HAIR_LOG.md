# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **B4A PASS/CLOSED DIAGNOSTIC — B4B V1 FAIL/CLOSED PRE-RUN METHOD — B4B V2 FAIL/CLOSED VISUAL — B4B V3 RUNNER READY / REVIEW NEXT**

## Entry condition

G3S-B3/B3B is PASS/CLOSED.

Canonical immutable body base:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body is immutable input to B4. Hair may surround/occlude it through composition but may not overwrite its ownership.

## Canonical hair identity

The Exilada's hair is black / nearly black, very long, heavy, voluminous, messy and a primary silhouette anchor. It must read as deprivation/survival material rather than salon styling.

Identity/design authority:

`assets/source/characters/exilada/reference/exilada_master.png`

The master is a **visual inspiration/reference** for hair identity, mass, material and framing. It is not a complete geometric source for the final hair layers.

## Hair depth architecture — LOCKED

Minimum valid representation:

1. `rear_hair` — persistent transparent layer behind body/head/shoulders/back;
2. `front_hair` — persistent transparent layer in front where hair crosses face/neck/chest/shoulders.

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

Additional side/intermediate masses may be introduced later only if occlusion or secondary motion requires them. One flat hair overlay is invalid.

## Ownership rule

Hair owns its own visible RGB/alpha/silhouette and later its own secondary-motion anchors. It must not:

- modify the canonical body asset;
- be baked irreversibly into the body;
- use hidden-3D RGB/masks as final visible art;
- require per-frame generation;
- require manual frame-by-frame repainting by the user.

## B4A preflight — PASS/CLOSED DIAGNOSTIC

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4_hair_preflight\g3s_b4_hair_preflight_contact_sheet.png`

SHA256:

`efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

The preflight confirmed the local master is suitable as hair identity/mass inspiration, the body remains immutable, the shared `96×160` frame is adequate for first static review, and the minimum depth order is `rear_hair -> body -> front_hair`.

## B4B V1 — MASTER EXTRACTION — FAIL/CLOSED PRE-RUN METHOD

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

Reason: the master does not contain enough information for the hair mass that falls behind the head, shoulders and back. Valid `rear_hair` geometry therefore cannot be recovered by extracting visible master pixels.

V1 was not run by the user. No production art/model was created or downloaded; no cleanup applies.

## B4B V2 — AUTHORED TWO-LAYER STATIC CANDIDATE — FAIL/CLOSED VISUAL

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Reviewed SHA256:

`73a9b53d35c158d78079039b4425c94028c8836e82b775ee0ce3e38b8d32a09d`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_visual_failure.json`

Structural result: **PASS**. The candidate correctly used two persistent transparent layers and preserved the canonical body.

Visual result: **FAIL**.

Observed failures:

- silhouette reads as a centered curtain/bell rather than the Exilada's wild irregular hair mass;
- `front_hair` hides too much face/neck/chest/body readability;
- `rear_hair` reads too uniformly and cape-like rather than as a convincing rear mass behind shoulders/back;
- lock hierarchy is too repetitive/equal-width and approaches a dread/cable rhythm;
- head/face become buried inside the dark mass;
- insufficient asymmetry and hierarchy between primary mass, side masses and dominant long falls.

No model weights or paid API were used, so no cleanup command applies.

## B4B V3 — AUTHORED TWO-LAYER STATIC CANDIDATE — CURRENT / RUNNER READY

Machine-readable spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_authored_two_layer_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_two_layer_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair`

### V3 correction

V3 keeps the valid architecture and rewrites the visual massing:

- `rear_hair` becomes the dominant mass;
- rear silhouette is intentionally asymmetric and irregular;
- front coverage is reduced to sparse lateral framing;
- center face/clavicle/chest/abdomen remain substantially open;
- equal-width curtain/dread rhythm is removed;
- broad primary masses, side masses and distinct long falls replace repetitive locks;
- rear geometry explicitly represents hair behind head/shoulders/back;
- master remains inspiration only; no master pixels are extracted/copied/traced;
- body remains exact hash-verified B3B V4;
- no external paid API/model;
- no automatic promotion.

Expected outputs remain:

- `g3s_b4b_rear_hair_candidate.png`;
- `g3s_b4b_front_hair_candidate.png`;
- `g3s_b4b_body_hair_composite.png`;
- `g3s_b4b_gameplay_preview.png`;
- `g3s_b4b_contact_sheet.png`;
- `g3s_b4b_two_layer_hair_candidate.json`.

## Current exact action

Run B4B V3 once and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C until V3 visual/structural review is complete.
