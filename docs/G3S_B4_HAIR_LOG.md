# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **B4A PASS/CLOSED — B4B V1 FAIL/CLOSED PRE-RUN — B4B V2 FAIL/CLOSED VISUAL — B4B V3 FAIL/CLOSED POSE-MISMATCH — B4B V4 POSE-ANCHORED RUNNER READY**

## Immutable entry condition

Canonical B3B production body:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body remains byte/pixel unchanged. Hair owns separate visible RGB/alpha/silhouette.

## Canonical hair identity

The Exilada's hair is black/nearly black, very long, heavy, voluminous, messy, wild and materially lived-in. The canonical `exilada_master.png` is an **identity/style/mass/material reference only**. Its pose is not a placement template for production hair.

## Hair depth architecture — LOCKED

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

- `rear_hair`: persistent transparent mass behind head/neck/shoulders/back/body;
- `front_hair`: persistent transparent scalp/framing/locks in front where needed;
- one flat overlay is invalid;
- later side/intermediate sublayers are allowed only if occlusion/secondary motion requires them.

## B4A — PASS/CLOSED DIAGNOSTIC

Reviewed contact sheet SHA256:

`efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

B4A established the two-layer depth contract and the `96×160` review frame. It did not create production hair pixels.

## B4B V1 — FAIL/CLOSED PRE-RUN METHOD

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

Reason: the master does not contain enough hidden rear-hair information to recover a valid `rear_hair` layer by extraction.

No model/API was used; no cleanup applies.

## B4B V2 — FAIL/CLOSED VISUAL / STRUCTURAL PASS

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_visual_failure.json`

Structural split passed, but visual result failed as a centered curtain/bell with excessive front coverage, cape-like rear mass and repetitive lock rhythm.

No model/API was used; no cleanup applies.

## B4B V3 — FAIL/CLOSED VISUAL AND ALIGNMENT METHOD

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Reviewed SHA256:

`9d922756f8815ea55cf55bed26d2bc0d24f51f93f89b3f47392126e027573f33`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_pose_mismatch_failure.json`

V3 fixed some V2 massing problems but still authored hair in **fixed master-like canvas coordinates**. This ignored the fact that the canonical production body and the master use different poses. As a result:

- crown placement did not follow the actual production head orientation;
- rear mass did not follow the production shoulder/back pose;
- front locks framed an imagined master-like pose instead of the B3B pose;
- structural ownership remained valid, but visual alignment was fundamentally invalid.

No model/API was used; no cleanup applies.

## B4B V4 — POSE-ANCHORED TWO-LAYER CANDIDATE — CURRENT / RUNNER READY

Spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchored_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_pose_anchored_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair`

### V4 correction

V4 no longer uses the master pose for placement. It measures the actual promoted B3B body alpha/silhouette and derives:

- head center/bounds;
- shoulder row/span;
- torso center;
- 3/4 facing bias.

Both new hair layers are then authored relative to those **production-body anchors**.

The master remains visible in the contact sheet only as identity/style/material inspiration.

The contact sheet must explicitly show the immutable body with detected pose anchors before showing `rear_hair`, `front_hair`, composite and native `640×360` preview.

### V4 review contract

- body hashes must remain canonical;
- rear/front assets must be separate and non-empty;
- composition must remain `rear_hair -> body -> front_hair`;
- master pose coordinates must not drive placement;
- front hair must remain subordinate to rear mass;
- no external paid API/model;
- no automatic promotion.

## Current exact action

Run B4B V4 once and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C before V4 review.
