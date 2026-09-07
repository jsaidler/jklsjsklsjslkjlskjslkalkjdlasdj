# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G1_CAMERA_SCALE_LOG.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
5. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
6. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
7. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
8. `docs/G3S_C0_BODY_MOTION_PROOF.md`
9. `docs/G3S_B4_HAIR_LOG.md`

## Presentation simplification — LOCKED

The project is no longer pursuing true isometric character production.

Locked presentation is elevated arcade beat'em-up / belt-scroller false 3D:

- fixed orthographic `640×360` camera;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- walkable depth band retained;
- first visible body family screen-left front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite sets;
- do not silently recreate multi-directional/isometric art complexity.

This decision exists specifically to make 2D character production feasible.

## Canonical body

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- screen-left front-three-quarter family;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`.

## Hair

DEFERRED. Do not resume automatically.

## Motion backbone — PASS

- G2 PASS;
- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- C1A skeleton walk PASS/CLOSED;
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`;
- projected root travel approximately `-43.77 px` screen-left.

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

## Closed methods

- visible 3D -> final pixel art;
- C0 V1 nearest-segment hard partition + independent rigid rotations;
- single-still full-body cutout/warp/cage -> gait;
- skinned MPFB body as mandatory hidden guide;
- independent full-body generative redraw per walk frame;
- implicit return to isometric/multi-directional character coverage.

## Latest visual failure — C1B Flux2

Reviewed user-supplied output failed persistent identity:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Observed drift: face, skin tone, body proportions, silhouette/view and pixel-art treatment.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_visual_failure.json`

`22_run_g3s_c1b_flux2_walk_visual_proof.ps1` is intentionally disabled. Do not tune/rerun it for locomotion.

No new model/runtime was installed; no cleanup applies.

## CURRENT — C1B minimal segmented persistent 2D puppet

Architecture:

`approved hidden skeleton -> persistent native-2D part atlas -> explicit anatomical pivots + deliberate overlap -> projected skeleton transforms -> camera-space depth sort -> composited sprite`

Detailed doc:

`docs/G3S_C1B_SEGMENTED_PUPPET.md`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`

Current revision:

`SEGMENTED_2D_SKELETAL_PUPPET_V2_BELT_SCROLLER_MINIMAL`

Initial parts: head/neck, torso, pelvis, bilateral upper arms, forearms, hands, thighs, shins and feet.

This is **not** the failed C0 V1 method. Requirements:

- deliberate overlapping art under joints;
- explicit anatomical pivots;
- continuous torso/pelvis connection;
- projected bone direction/length drives each part;
- skeleton depth drives draw order.

### First-proof simplification

- screen-left family only;
- same persistent part artwork reused across all 8 walk states;
- no north/south/isometric directions;
- no pre-emptive orientation/foreshortening library;
- no frame-specific redraw;
- no generative model;
- no manual frame repair required from the user.

Only if the composed left-facing walk demonstrates one specific unavoidable projection failure may a small persistent reusable part variant be added.

## Exact next implementation

Implement a new headless runner after the disabled runner 22. It must:

1. derive/cut the persistent part atlas from the canonical B3B without altering the source file;
2. write a pivot/binding/overlap manifest;
3. attach the parts to the approved C1A projected skeleton;
4. composite all eight left-facing walk frames using skeleton depth order;
5. generate in-place GIF, travel GIF and contact sheet with optional skeleton overlay.

Initial proof uses no new model/API/download. Hair remains deferred.
