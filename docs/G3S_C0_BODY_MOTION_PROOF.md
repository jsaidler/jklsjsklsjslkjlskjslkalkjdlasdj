# G3S-C0 — Body-Only Motion Proof

Status date: **2026-09-06**

Gate status: **V1 FAIL/CLOSED — V2 FAIL/CLOSED — SINGLE-STILL PUPPET/WARP ROUTE CLOSED — NEXT: FULL HIDDEN-3D-GUIDED NATIVE-2D POSE SOURCE**

Canonical architecture lock:

`docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`

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

## Critical architecture correction

The project had already decided that hidden 3D would guide animation while final visible art remained native 2D.

C0 V1/V2 drifted away from that decision by using only **projected joint deltas** from the hidden rig and attempting to force the entire walk out of the single B3B still.

That reduction was wrong.

The intended role of hidden 3D is to guide the **full pose state**:

- anatomical left/right;
- near/far ownership;
- complete limb pose;
- foreshortening;
- occlusion/depth order;
- contact foot/foot roll;
- pelvis/root transform;
- body-part semantic shapes;
- fixed camera/scale.

Hidden-3D RGB/alpha/final silhouette still remain forbidden as final visible art.

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

1. **The hidden-3D guide was reduced incorrectly.** Full 3D pose information was collapsed to projected joint-angle deltas instead of being used as a complete pose/anatomy/occlusion guide.
2. **Facing/laterality was not registered correctly.** The authored sprite faces screen-left in 3/4. Screen-x position was treated as if it directly encoded anatomical left/right/near/far ownership. It does not.
3. **Rest/camera basis mismatch.** G2 screen-space direction deltas were applied to an unrelated authored sprite rest pose without a validated sprite-to-rig rest registration.
4. **Depth/foreshortening loss.** A real walk contains substantial toward/away-from-camera limb motion. V1/V2 tried to express this as 2D angle deformation, producing impossible arcs.
5. **Missing visible information.** One monolithic 3/4 raster does not contain the hidden limb/body surfaces that become visible as near/far occlusion changes during the stride.
6. **Invalid grounding shortcut.** Grounding every frame by the alpha-bbox bottom is not equivalent to preserving the actual contact foot and root motion.

### Closed methods

Do not create another revision by tuning:

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
- hidden motion/topology infrastructure is valid and remains the guide/control backbone;
- the promoted body sprite remains a valid static identity/style anchor;
- no hidden-3D RGB or runtime/per-frame diffusion is required for motion control.

Rejected:

- deriving a convincing full walk by deforming the single B3B still from joint deltas.

## Next architecture — CURRENT

The first walk proof now follows the already-decided hidden-3D-guided architecture correctly.

### Step 1 — hidden 3D exports a full guide package

For one selected non-rest gait event first, export:

- projected joints;
- anatomical-side labels;
- near/far limb identity;
- depth/body-part order;
- contact foot and foot-roll state;
- root/pelvis transform;
- projected semantic body-part shapes/guide masks;
- fixed G1 camera/scale.

These are pose/anatomy/occlusion controls only.

### Step 2 — author one matching persistent native-2D pose

The resulting 2D pose must own its own final RGB, alpha, silhouette, foreshortening and occlusion. It must preserve the Exilada body identity from B3B without being a warped copy of the rest pose.

The user is not expected to redraw it manually.

### Step 3 — expand to the first walk family

Target eight persistent native-2D gait states:

1. left contact;
2. left down/loading;
3. left passing;
4. left up;
5. right contact;
6. right down/loading;
7. right passing;
8. right up.

Runtime playback is normal sprite animation using motion-derived timing/contact/root metadata. No interpolation is required for the first proof.

No new runner is approved until Step 1 is implemented correctly and the source-authoring method for Step 2 is selected/proven.

Hair remains deferred until the user resumes it.
