# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR DEFERRED / C1A SKELETON WALK PASS/CLOSED / C1B FLUX2 REDRAW FAIL/CLOSED / SEGMENTED PUPPET CURRENT**

Canonical animation lock:

`docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`

## Locked ownership

`real/captured motion -> hidden skeleton/rig -> persistent native-2D visible parts -> skeleton-driven transforms/depth -> composited sprite -> QA`

Hidden 3D is an armature only. It owns motion, joint transforms, anatomical side, near/far depth/order, contact, root travel and sockets. It does not own final visible RGB, alpha, anatomy or silhouette.

## Canonical B3 body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- visible standing body height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- front-three-quarter screen-left family.

The source remains unchanged.

## Closed visible methods

- direct hidden-3D render -> final pixel art;
- C0 V1 nearest-segment hard partition + independent rigid rotation;
- full-body cutout/cage/chain warp from a single still;
- skinned MPFB body as mandatory animation guide;
- independent full-body diffusion redraw for each gait frame.

## C1A — PASS/CLOSED

Approved eight-state skeleton cycle:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

C1A uses only `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk`.

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

## C1B Flux2 full-body redraw — FAIL/CLOSED

Reviewed evidence:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

The generated walk changes face, skin tone, proportions, silhouette and pixel-art language across frames. It fails persistent-character continuity.

Marker:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_visual_failure.json`

Runner 22 is disabled.

## CURRENT — segmented persistent 2D puppet

Detailed architecture:

`docs/G3S_C1B_SEGMENTED_PUPPET.md`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`

Visible body ownership becomes a reusable part atlas:

- head/neck;
- torso;
- pelvis;
- bilateral upper arms;
- bilateral forearms;
- bilateral hands;
- bilateral thighs;
- bilateral shins;
- bilateral feet.

Each part has an explicit anatomical pivot and is attached to the approved hidden skeleton chain. The proximal joint controls pivot position; the distal joint controls projected direction/length; camera-space skeleton depth controls draw order.

### Joint continuity

Unlike C0 V1, adjacent parts must deliberately overlap under joints. Joint cover/cap sprites are permitted where necessary. Torso/pelvis continuity must be designed, not inferred from nearest-pixel ownership.

### Foreshortening

A flat sprite part may use a small frozen set of orientation variants where the 3D projection materially changes visible shape. Example: normal vs foreshortened thigh/shin/forearm, near/far hands/feet, optional pelvis/torso lead-side variant.

These variants are persistent reusable assets selected deterministically from skeleton orientation/depth. They are not generated independently per animation frame.

## Facing/laterality

- visible family faces/travels screen-left;
- anatomical left/right comes from skeleton identity, never screen-x;
- near/far and draw order come from camera-space depth;
- rig is never rotated merely to manufacture facing.

## B4 hair — DEFERRED

Hair remains paused. Eventual composition remains `rear_hair -> body -> front_hair`, but hair does not block proving the body puppet.

## Next proof

The next runner must create the body-part atlas/bindings and play the full approved eight-state walk as one persistent 2D puppet, with both in-place and travel GIFs plus a contact sheet.

The initial proof should require no new model/API/download and no manual frame-by-frame repair by the user.
