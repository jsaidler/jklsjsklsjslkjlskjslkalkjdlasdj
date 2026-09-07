# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
5. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
6. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
7. `docs/G3S_C0_BODY_MOTION_PROOF.md`
8. `docs/G3S_B4_HAIR_LOG.md`

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
- independent full-body generative redraw per walk frame.

## Latest visual failure — C1B Flux2

Reviewed user-supplied output failed persistent identity:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Observed drift: face, skin tone, body proportions, silhouette/view and pixel-art treatment.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_visual_failure.json`

`22_run_g3s_c1b_flux2_walk_visual_proof.ps1` is intentionally disabled. Do not tune/rerun it for locomotion.

No new model/runtime was installed; no cleanup applies.

## CURRENT — C1B segmented persistent 2D skeletal puppet

Architecture:

`approved hidden skeleton -> persistent native-2D part atlas -> explicit anatomical pivots -> skeleton projected transform -> camera-space depth sort -> composited sprite`

Detailed doc:

`docs/G3S_C1B_SEGMENTED_PUPPET.md`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`

Initial parts: head/neck, torso, pelvis, bilateral upper arms, forearms, hands, thighs, shins and feet.

This is **not** the failed C0 V1 method. Requirements:

- deliberate overlapping art under joints;
- explicit anatomical pivots;
- optional joint caps/covers;
- continuous torso/pelvis connection;
- projected bone direction/length drives each part;
- skeleton depth drives draw order;
- small reusable orientation/foreshortening variants only where needed.

Variants are persistent assets, not frame-specific redraws.

## Exact next implementation

Implement a new runner after the disabled runner 22. It must generate in one pass:

- segmented body-part atlas from/founded on canonical B3B;
- pivot/binding manifest;
- eight body-only walk frames driven by approved C1A;
- in-place GIF;
- travel GIF;
- contact sheet with optional skeleton overlay.

Initial proof should use no new model/API/download and require no user frame-by-frame repair.
