# G3S-C0 — Body-Only Motion Proof

Status date: **2026-09-06**

Gate status: **V1 FAIL/CLOSED — V2 FAIL/CLOSED — SINGLE-STILL PUPPET/WARP ROUTE CLOSED — NEXT: ANIMATION-READY NATIVE-2D SOURCE ARCHITECTURE**

## Purpose

The user paused hair and asked to see the approved Exilada body moving. C0 is a diagnostic exception to the full layered build order.

Canonical body remains:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- source faces **screen-left** in a front-three-quarter view;
- source remains byte/pixel unchanged.

Motion backbone remains valid:

- G2 = PASS;
- source motion = CMU `105_34 NormalWalk`;
- source rig = `G2_CANONICAL_RIG`;
- G3V-R = PASS using `DIRECTION_SPACE_FK` as hidden motion/retarget infrastructure.

## C0 V1 — FAIL/CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`

Method: hard partition of the one monolithic sprite into upper/lower limbs and independent rigid rotations.

Failure: joints detached; legs/feet formed broken loops/arcs; the figure read as assembled slabs instead of one body.

Closed method:

`single still -> hard body-part cutout -> independent rigid rotations`

## C0 V2 — FAIL/CLOSED VISUAL + METHOD

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_contact_sheet.png`

Reviewed SHA256:

`6d6199aa7bc159cad344c8dbc31b52577f2c70bb70f674ab5216ea40db67fba3`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v2_visual_failure.json`

V2 replaced rigid pieces with continuous arm/leg chain warps, but the result still produced anatomically impossible stride shapes. This is not a local seam/pivot bug; the representation is insufficient.

### Root causes — LOCKED

1. **Facing/laterality was not registered correctly.** The authored sprite faces screen-left in 3/4. Screen-x position was treated as if it directly encoded anatomical left/right/near/far ownership. It does not.
2. **Rest/camera basis mismatch.** G2 screen-space direction deltas were applied to an unrelated authored sprite rest pose without a validated sprite-to-rig rest registration.
3. **Depth/foreshortening loss.** A real walk contains substantial toward/away-from-camera limb motion. V1/V2 used depth mainly for draw order and tried to express the rest as 2D angle deformation, producing impossible arcs.
4. **Missing visible information.** One monolithic 3/4 raster does not contain the hidden limb/body surfaces that become visible as near/far occlusion changes during the stride. Warping can only stretch existing pixels; it cannot reveal correct new anatomy.
5. **Invalid grounding shortcut.** Grounding every frame by the alpha-bbox bottom is not equivalent to preserving the actual contact foot and root motion.

### Closed methods

Do not create V2.1/V3 by tuning more:

- pivots;
- anchors;
- ownership heuristics;
- overlap widths;
- chain blend radii;
- rigid cutout regions;
- continuous chain warp;
- weighted cage/mesh whose only visible source is still this single monolithic sprite.

A weighted mesh can make deformation smoother, but it cannot create missing anatomical surfaces or correct near/far limb ownership from a still image.

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1` is intentionally disabled.

## Direction/facing rule — LOCKED

The current canonical B3B source faces **screen-left**.

Any travel preview using this source family must therefore move screen-left unless a separately authored right-facing source family is explicitly selected. Do not mirror silently and do not confuse screen side with anatomical side.

## What C0 actually proved

Retained:

- real CMU walk data reaches the project;
- hidden motion/topology infrastructure is usable;
- the promoted body sprite can remain persistent visible source art;
- no hidden-3D RGB or per-frame diffusion is required for motion control.

Rejected:

- deriving a convincing full walk by deforming the single B3B still.

## Next architecture — CURRENT

The animation-ready visible representation must contain **pose-specific native-2D information**.

For the first walk proof, the preferred production shape is a small persistent left-facing pose family tied to real gait events, e.g. contact/down/passing/up across both sides. Each accepted key pose is a complete native-2D body sprite (or equivalently complete pose-specific visible body state), with correct:

- anatomical left/right;
- near/far limb ownership;
- foreshortening;
- hip/knee/ankle relationships;
- foot contact/roll;
- torso/pelvis counter-motion;
- silhouette and occlusion.

The hidden G2 rig supplies pose guides, timing, contacts, root travel and depth metadata. It does **not** supply final visible RGB/silhouette.

No new runner is approved until the source-authoring method for those pose-specific native-2D states is demonstrated on at least one non-rest gait pose without asking the user to manually redraw frames.

Hair remains deferred until the user resumes it.
