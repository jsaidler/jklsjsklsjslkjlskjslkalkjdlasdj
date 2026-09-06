# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR DEFERRED / C0 SINGLE-STILL MOTION ROUTE CLOSED / C1A V6 HIDDEN-3D FULL-POSE GUIDE CURRENT**

Canonical animation architecture lock:

`docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`

Current pose-guide gate:

`docs/G3S_C1_HIDDEN_POSE_GUIDE.md`

## Locked architecture

`real/captured motion -> validated hidden rig -> full pose/contact/depth/laterality/occlusion guides -> persistent native-2D pose assets -> deterministic timing/depth composition -> native sprite -> QA`

Hidden 3D may own motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB, alpha or final sprite silhouette.

The hidden rig must guide the **entire pose state**, not merely export joint deltas. A pose guide may include projected semantic shapes/masks and 3D-derived silhouette reference, but those are guide/control data only and may not be promoted into final sprite geometry.

## Production constraints

- final visible character art is owned by persistent native 2D assets;
- no per-frame diffusion as runtime animation owner;
- no routine frame-by-frame repainting by the user;
- no beauty-render shrink/pixel-filter route;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer;
- animation may not assume one static raster contains every hidden surface needed by every pose.

## Canonical B3 body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing body height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- authored front-three-quarter view facing **screen-left**.

This B3B asset remains the approved static body identity/style anchor for that view. It is not by itself an animation-ready source for arbitrary gait silhouettes.

## Facing/laterality rule — LOCKED

A 3/4 raster cannot infer anatomical left/right or near/far ownership from screen-x alone. Any animation source family must explicitly register screen facing, anatomical side, near/far limb ownership, occlusion order and pose/rest basis relative to hidden motion guides.

The current B3B family faces screen-left; travel using that family must move screen-left unless another direction family is authored.

For hidden-3D guide presentation, **directional family is now a camera/view selection relative to real motion heading, not an object-space rotation of the skinned rig/body**. This rule was locked after C1A V5 visually exploded the MPFB body while its skeleton remained coherent.

## B4 hair — DEFERRED

Hair remains structurally separate and later must still satisfy:

`rear_hair -> body -> front_hair`

No hair candidate is approved. No B4C generated pixels were promoted. The user paused hair on 2026-09-06.

## G3S-C0 — BODY-ONLY MOTION DIAGNOSTIC

Motion infrastructure retained:

- G2 real-motion/topology = PASS;
- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- G3V-R `DIRECTION_SPACE_FK` = PASS.

C0 V1 hard cutout and C0 V2 continuous-chain warp are FAIL/CLOSED. The entire route `single still -> projected joints -> cutout/warp/cage -> manufacture gait` is closed.

## G3S-C1A — HIDDEN FULL-POSE GUIDE — CURRENT

C1A implements the retained hidden-3D backbone as a **full pose guide**.

### V5 reviewed failure

Reviewed contact sheet SHA256:

`74ee1979afa58b8bbe77a3549fdc6af41e24524287f6329a33425aa7b15f6ba9`

V5 numerically hit 128 px, screen-left travel and correct explicit contact/near/far metadata, but visually failed because the skinned body formed giant triangular stretched surfaces while the skeleton remained coherent.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_v5_visual_transform_failure.json`

The rejected presentation sub-method was post-retarget object-space rotation/translation of both target rig and skinned body to manufacture facing/grounding.

### V6 current architecture

For the first event C1A V6 exports an anatomical **left-contact** pose in the screen-left family using:

- real CMU G2 motion;
- retained continuous MPFB adult female hidden body;
- `G3V_CMU_RIG`;
- validated `DIRECTION_SPACE_FK`;
- unchanged post-retarget rig/body object matrices and parent state;
- G1 `640×360` / `26°` / approximately `128 px` scale;
- front-three-quarter camera at `45°` azimuth relative to real motion heading, selected so forward travel projects screen-left;
- original-body camera-space depth shader from V5 with no geometry proxy/bake/index mapping.

V6 explicitly forbids directional or grounding transforms on the target rig/body. Object matrix delta must remain `<=1e-8`.

C1A exports neutral body guide, silhouette guide, anatomical region/laterality guide, camera-space depth guide, projected skeleton overlay, JSON metadata, logical `96×160` guide crops and one review contact sheet.

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1_pose_guide_spec.json`

All rendered hidden-3D outputs remain **guide/control data only**. They may not become final RGB, alpha or sprite silhouette.

C1A must pass visual review before C1B begins.

## G3S-C1B — BLOCKED UNTIL C1A REVIEW

C1B will author one complete persistent native-2D left-contact body pose using C1A as pose/anatomy/laterality/near-far/occlusion control and B3B V4 as identity/body-style anchor.

C1B may not deform the static B3B still into the pose, quantize/recolor/crop the 3D guide into a sprite, or make hidden 3D the final visible owner.

If the first C1B pose passes, the same architecture expands to the remaining seven gait events.

## Full layered motion remains later

C1 does not waive eventual persistent hair, clothing, restraints and equipment. Full layered G3S-C approval still waits for those layer families after the body animation source architecture is viable.
