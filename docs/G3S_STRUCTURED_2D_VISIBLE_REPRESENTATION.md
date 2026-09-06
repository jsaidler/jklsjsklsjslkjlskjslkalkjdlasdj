# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR DEFERRED / C0 SINGLE-STILL MOTION CLOSED / C1A SKELETON-ONLY WALK TECHNICAL FIX COMMITTED / RERUN NEXT**

Canonical animation lock:

`docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`

Current motion-guide gate:

`docs/G3S_C1_HIDDEN_POSE_GUIDE.md`

## Locked visible/hidden ownership

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root guide data -> persistent native-2D pose assets -> deterministic sprite playback -> QA`

The hidden 3D is an armature. It may own skeletal motion, joint transforms, laterality, depth/order, contacts, root travel and sockets. It does **not** require a skinned human mesh and does not own final RGB, alpha, anatomy or sprite silhouette.

## Canonical B3 body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- visible standing body height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- authored front-three-quarter view facing screen-left.

B3B remains the visible identity/body-style anchor. It is not stretched or warped into arbitrary gait poses.

## Closed methods

- direct hidden-3D render -> final pixel art — CLOSED;
- single B3B still -> cutout/warp/cage -> full walk — CLOSED;
- skinned MPFB body as mandatory animation pose/anatomy/silhouette/depth guide — CLOSED.

C1A V5 made the reason explicit: the skeleton overlay remained coherent while the skinned MPFB body visibly exploded. The guide never needed that body mesh.

## Facing/laterality

- current visible source family faces/travels screen-left;
- anatomical left/right comes from the skeleton, never screen-x;
- near/far comes from camera-space skeleton depth;
- hidden directional-family selection is a camera/view decision relative to real root travel, not a transform of a skinned character object;
- if Blender's evaluated camera screen-X handedness does not match the canonical family, C1A may normalize only the hidden guide's screen-X coordinates; rig/world transforms and depth remain unchanged.

## B4 hair — DEFERRED

Hair remains paused by user. Eventual composition still requires `rear_hair -> body -> front_hair`. No B4 pixels are promoted and C1 does not resume hair.

## C1A — current skeleton walk cycle

C1A consumes the approved `G2_CANONICAL_RIG` directly, using CMU `105_34 NormalWalk`.

Current eight-state cycle:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

It exports complete bone matrices, projected joints, chain lengths/depths, anatomical ownership, near/far state, support foot, ground distances and projected root travel.

Camera baseline remains `640×360`, orthographic, pitch `26°`, front-three-quarter `45°` relative to real travel, approximately `128 px` maximum skeleton height. The rig itself is not rotated for facing.

### Latest technical failure and fix

First skeleton-only local run failed before visual output with:

`RuntimeError: could not choose front-three-quarter camera with screen-left forward travel`

This was a camera-evaluation/selection bug, not a motion-method failure. The exporter now forces dependency-graph updates after camera transforms, records both lateral camera candidates, and has a deterministic guide-coordinate X-normalization fallback while retaining the final screen-left root-travel assertion.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_camera_selection_failure.json`

Runner remains:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk`

Primary visual review outputs after rerun:

- `g3s_c1_skeleton_walk_zoom.gif`;
- `g3s_c1_skeleton_walk_contact_sheet.png`;
- `g3s_c1_skeleton_walk_travel.gif`.

No MPFB body, image model, API or new download is involved. No cleanup applies.

## C1B — immediately after C1A PASS

C1B authors the **eight complete persistent native-2D body poses** needed for the first left-facing walk cycle. C1A supplies motion/spatial control; B3B V4 supplies visible body identity/style.

C1B may not deform the static B3B still into the gait, promote a hidden-3D render, or make the user repair frames manually. An offline visual authoring tool, if used, must be explicitly approved for that gate; accepted results become frozen native-2D source assets.

## Later layered animation

After the body walk is viable, hair, clothing, restraints and equipment return as separate persistent layers. Full layered composition remains later; it does not block proving body locomotion first.
