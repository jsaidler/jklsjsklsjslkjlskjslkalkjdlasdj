# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **B4A PASS/CLOSED — B4B V1 FAIL/CLOSED PRE-RUN — B4B V2 FAIL/CLOSED VISUAL — B4B V3 FAIL/CLOSED POSE-MISMATCH — B4B V4 FAIL/CLOSED VISUAL+METHOD — B4 REMAINS OPEN**

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

The Exilada's hair is black/nearly black, very long, heavy, voluminous, messy, wild and materially lived-in. `exilada_master.png` is an **identity/style/mass/material reference only**. Its pose is not a placement template for production hair.

## Hair depth architecture — LOCKED

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

- `rear_hair`: persistent transparent mass behind head/neck/shoulders/back/body;
- `front_hair`: persistent transparent scalp/framing/locks in front where needed;
- one flat overlay is invalid;
- later side/intermediate sublayers are allowed only if real occlusion/secondary motion requires them.

## B4A — PASS/CLOSED DIAGNOSTIC

Reviewed contact sheet SHA256:

`efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

B4A established the two-layer depth contract and the `96×160` review frame. It did not create production hair pixels.

## B4B V1 — FAIL/CLOSED PRE-RUN METHOD

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

Reason: the master does not contain enough hidden rear-hair information to recover a valid `rear_hair` by extraction.

No model/API was used; no cleanup applies.

## B4B V2 — FAIL/CLOSED VISUAL / STRUCTURAL PASS

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_visual_failure.json`

The two-layer ownership split passed, but the visual result failed as a centered curtain/bell with excessive front coverage, cape-like rear mass and repetitive lock rhythm.

No model/API was used; no cleanup applies.

## B4B V3 — FAIL/CLOSED VISUAL AND ALIGNMENT METHOD

Reviewed contact sheet SHA256:

`9d922756f8815ea55cf55bed26d2bc0d24f51f93f89b3f47392126e027573f33`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_pose_mismatch_failure.json`

V3 authored hair in fixed master-like canvas coordinates even though master and production body use different poses. Crown/rear/front placement therefore did not follow the actual B3B pose.

No model/API was used; no cleanup applies.

## B4B V4 — FAIL/CLOSED VISUAL AND METHOD

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Reviewed SHA256:

`50dd663cbbeb0bb1a9865f2ac95daedc7990ceaf7a98ae6a968c8b7eacb4a8a5`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchor_failure.json`

Structural split: **PASS**.

Visual/method result: **FAIL**.

Observed evidence:

- the contact sheet reports `shoulder_span=6.36 px` for a `37 px`-wide body; this is not a credible shoulder measurement and proves the detector is not locating the actual shoulder span;
- head center, shoulder row/span, torso center and a binary facing flag are far too weak to represent the production body's 3/4 anatomy;
- the abstraction does not encode head tilt, shoulder slope, torso rotation, arm occlusion, back contour or local depth;
- hard-coded polygon/line hair geometry therefore does not wrap around the actual body pose;
- the result remains visibly detached geometric scaffolding rather than convincing Exilada hair.

### Route closure — LOCKED

The deterministic **Pillow polygon + heuristic-anchor hair-authoring route is closed** as a visual-production method.

Do **not** create a V5 by adding more hand-tuned anchor heuristics, polygon coordinates, curves or procedural locks. The repeated V2/V3/V4 failures show that this method is not a viable visual author for the character.

The valid parts are retained:

- canonical immutable B3B body;
- `rear_hair -> body -> front_hair` ownership;
- master as hair identity/material reference;
- native pixel-art target and `128 px` standing body scale.

No model weights or external paid API were used by V4, so no cleanup command applies.

## Current exact state

**B4 remains OPEN / NOT APPROVED.**

There is **no approved B4 runner** now.

The next B4 method must perform real visual 2D authoring/adaptation to the canonical B3B pose and produce separate `rear_hair` and `front_hair` assets. It must not return to:

- master-pixel extraction;
- fixed master-pose geometry;
- heuristic body anchors + hard-coded Pillow shapes;
- primitive procedural hair drawing.

Do not start B5 or G3S-C before B4 passes.
