# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR DEFERRED / C0 SINGLE-STILL MOTION CLOSED / C1A SKELETON WALK PASS/CLOSED / C1B VISIBLE WALK PROOF RUNNER READY**

Canonical animation lock:

`docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`

## Locked visible/hidden ownership

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root guide data -> complete visible 2D pose assets -> deterministic sprite playback -> QA`

Hidden 3D is an armature only. It may own skeletal motion, joint transforms, anatomical side, near/far depth/order, contacts, root travel and sockets. It does not require a skinned human mesh and does not own final visible RGB, alpha, anatomy or silhouette.

## Canonical B3 body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- visible standing body height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- front-three-quarter family facing screen-left.

B3B is identity/body-style reference only. It is never stretched/warped into arbitrary gait poses.

## Closed methods

- direct hidden-3D render -> final pixel art — CLOSED;
- single B3B still -> cutout/warp/cage -> full walk — CLOSED;
- skinned MPFB human as mandatory hidden animation guide — CLOSED.

## Facing/laterality

- visible family faces/travels screen-left;
- anatomical left/right comes from skeleton identity, never screen-x;
- near/far comes from camera-space depth;
- hidden directional-family handling may normalize guide screen-X convention without transforming the rig or changing anatomical ownership.

## B4 hair — DEFERRED

Hair remains paused. Eventual composition still requires `rear_hair -> body -> front_hair`. C1 body locomotion does not resume hair.

## C1A — PASS/CLOSED

Approved eight-state cycle:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

C1A uses only `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk`.

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

Reviewed evidence:

- contact sheet SHA256 `672c8f9cb419cb8aa317447801931ce76da07b101b766c3f616bb2c25a39c2cd`;
- zoom GIF SHA256 `9a61ae7414be04ef4a89d8f83127e73d58e46da2075f37e23b7b048864286970`;
- projected root travel approximately `-43.77 px` screen-left.

C1A visually passed coherent gait, left/right progression, support-foot progression, limb-chain integrity and readable pelvis/trunk/leg relationship.

The earlier skeleton camera-selection failure is closed/resolved in:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_camera_selection_failure.json`

No model/API/download was used in C1A; no cleanup applies.

## C1B — CURRENT visible walk proof

Goal: finally show the bald body of the Exilada walking as one eight-frame visible sequence.

Current bounded authoring route:

`C1A approved skeleton pose -> exact B3B identity/style reference + pose-control reference -> existing local FLUX.2 Klein -> complete redraw for each of 8 gait states -> review GIF/contact sheet`

This is a **visual proof gate**, not automatic production promotion.

It reuses only the already-retained local stack at:

`Z:\AI\Flux2RefControlSpike`

No download and no paid API are allowed.

Current files:

- `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`;
- `tools/structured-2d-character-pipeline/g3s_c1b_flux2_walk_spec.json`;
- `tools/structured-2d-character-pipeline/g3s_c1b_prepare_flux2_walk_inputs.py`;
- `tools/structured-2d-character-pipeline/g3s_c1b_build_flux2_walk_review.py`;
- `tools/structured-2d-character-pipeline/22_run_g3s_c1b_flux2_walk_visual_proof.ps1`.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof`

Expected primary outputs:

- `g3s_c1b_exilada_walk_visual_proof.gif`;
- `g3s_c1b_exilada_walk_contact_sheet.png`;
- `g3s_c1b_review.json`.

Hard locks:

- no static-body warp;
- no hidden-3D RGB promotion;
- no hair/clothing/restraints/accessories/weapons;
- no automatic promotion of generated frames;
- no manual frame repair demanded from the user.

The `96×160` reductions made by the review builder are inspection images only and are not production sprite assets.

## After C1B review

If the visible eight-frame body proof is coherent, freeze/author the accepted walk family into native persistent 2D assets under the existing production-art rules. Only after body locomotion is viable do hair, clothing, restraints and equipment return as separate layers.
