# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G1_CAMERA_SCALE_LOG.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
5. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
6. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
7. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
8. `docs/G3S_C0_BODY_MOTION_PROOF.md`
9. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
10. `docs/G3S_B4_HAIR_LOG.md`
11. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED FOR FEASIBILITY

The project originally considered true isometric 2D presentation. That direction was deliberately abandoned because it multiplied view families, pose coverage, occlusion cases and animation production cost.

The locked gameplay presentation is an **elevated 2D arcade beat'em-up / belt-scroller / false 3D**:

- fixed orthographic camera;
- `640×360` native raster;
- pitch `26 deg`;
- protagonist standing body height about `128 px`;
- walkable gameplay depth band retained;
- first visible character family is screen-left front-three-quarter;
- movement through gameplay depth does not require north/south/isometric sprite families;
- screen-right is deferred until the left family is proven.

This simplification is part of the production architecture. Any route that silently recreates isometric/multi-directional complexity is drift.

## Canonical Exilada body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- screen-left front-three-quarter family.

## Hair — DEFERRED

B4 remains paused by user. Do not resume automatically.

## Motion backbone — PASS/RETAINED

- G2 = PASS/CLOSED;
- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- C1A skeleton walk = PASS/CLOSED;
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`;
- projected root travel approximately `-43.77 px` screen-left.

C1A approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

## Closed visible routes

- direct visible 3D -> final pixel art — CLOSED;
- single B3B still -> nearest-segment hard partition / independent rigid parts -> full walk — CLOSED in C0 V1 form;
- single B3B still -> continuous full-body chain/cage warp -> full walk — CLOSED;
- MPFB skinned body as mandatory hidden animation guide — CLOSED;
- independent full-body generative redraw for each walk frame — CLOSED after C1B Flux2 review;
- implicit return to isometric/multi-directional character coverage — CLOSED unless presentation is explicitly reopened.

## C1B Flux2 per-frame redraw — FAIL/CLOSED

Reviewed artifacts:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Failure: visible identity, skin tone, proportions, silhouette, view and pixel treatment changed across frames. The sequence does not represent one persistent Exilada.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_visual_failure.json`

Runner 22 is intentionally disabled. No new model/runtime was installed by this gate; no cleanup applies.

## CURRENT — C1B MINIMAL SEGMENTED 2D SKELETAL PUPPET

The corrected visible animation architecture is:

`real mocap -> approved hidden 3D skeleton -> persistent native-2D body-part atlas -> explicit pivots/overlap -> projected bone transforms -> camera-space depth sort -> composited sprite -> QA`

The hidden 3D owns motion/spatial control only. Final visible pixels are persistent 2D parts.

Current design docs/spec:

- `docs/G3S_C1B_SEGMENTED_PUPPET.md`;
- `tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json` revision `SEGMENTED_2D_SKELETAL_PUPPET_V2_BELT_SCROLLER_MINIMAL`.

Initial persistent parts:

- head/neck;
- torso;
- pelvis;
- bilateral upper arms, forearms, hands;
- bilateral thighs, shins, feet.

### Non-negotiable difference from failed C0 V1

Do not use nearest-segment pixel assignment and independent rigid rotation with exposed joints.

The current puppet requires:

- explicit anatomical pivots;
- deliberate overlap under joints;
- continuous torso/pelvis connection;
- skeleton-driven position/rotation/projected length;
- draw order from camera-space skeleton depth.

### Non-negotiable simplification

The first proof must not pre-emptively add art families that the belt-scroller decision was meant to eliminate:

- one screen-left family only;
- same persistent part set across all eight walk states;
- no north/south/isometric directions;
- no frame-specific redraw;
- no generative model;
- no foreshortening/orientation variants unless the first composed walk demonstrates a specific unavoidable failure;
- no manual frame repair required from the user.

## Next implementation

Implement one runner for the full body-only eight-state walk proof. It must generate:

- segmented part atlas;
- binding/pivot manifest;
- eight composited body frames;
- in-place GIF;
- travel GIF;
- review contact sheet with optional skeleton overlay.

No model/API/download is required for the initial segmented-puppet proof. Hair stays deferred.
