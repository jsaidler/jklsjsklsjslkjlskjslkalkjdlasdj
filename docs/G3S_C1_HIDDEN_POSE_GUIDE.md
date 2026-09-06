# G3S-C1 — Hidden Skeleton Walk Guide

Status date: **2026-09-06**

Gate status: **C1A SKINNED-BODY REVISIONS CLOSED / SKELETON-ONLY EIGHT-STATE WALK RUNNER READY / REVIEW REQUIRED**

## Purpose

C1 now implements the architecture the user originally intended:

`real motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root control -> persistent native-2D walk poses -> sprite playback`

The hidden guide is skeletal control data only. It does not require or render a skinned human body.

## Closed skinned-body history

C1A V1–V4 failed while trying to derive guide depth from MPFB body topology/bakes/proxies. V5 finally produced stable numeric metadata but the rendered skin visibly exploded into large triangular surfaces while the skeleton itself remained coherent. V6 then failed before execution because of an import error, but was deliberately **superseded rather than repaired** after the user clarified that hidden 3D should simply be a rig/skeleton.

The following class is closed for C1A:

`mocap -> character-proportioned skinned MPFB human -> rendered anatomy/silhouette/depth guide`

Historical failure evidence remains in the repository. `G3V_BODY` is not required by current C1A.

## Current source

C1A reads the already-approved G2 motion artifact directly:

- motion: `CMU 105_34 NormalWalk`;
- armature: `G2_CANONICAL_RIG`;
- local blend: `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`;
- G2 approval: `tools/deterministic-character-pipeline/g2_approval.json` = PASS.

No MPFB body or G3V body is used.

## Current eight-state walk cycle

To stop iterating on isolated pose proofs, the current gate exports all eight first-walk states in one run:

| Index | Source frame | Event | Support foot |
|---:|---:|---|---|
| 0 | 1588 | left_contact | left |
| 1 | 1598 | left_down | left |
| 2 | 1608 | left_passing | left |
| 3 | 1618 | left_up | left |
| 4 | 1628 | right_contact | right |
| 5 | 1638 | right_down | right |
| 6 | 1648 | right_passing | right |
| 7 | 1658 | right_up | right |

These states preserve the existing real-motion basis and left/right alternation. Frame duration for the first review playback is `83 ms`, matching a 10-source-frame interval at approximately 120 fps.

## Camera / direction

- native raster: `640×360`;
- orthographic;
- pitch: `26°`;
- horizontal view: front-three-quarter at `45°` from the measured root-travel heading;
- the rig is never rotated to manufacture screen facing;
- the camera chooses the lateral side that makes real forward root travel project **screen-left**;
- maximum projected skeleton height is calibrated to approximately `128 px`;
- camera tracking follows only forward root translation, preserving lateral sway and vertical gait movement in the in-place diagnostic.

## Data exported per state

- full world matrix for every required motion bone;
- bone head/tail world coordinates;
- projected pelvis/chest/neck/head;
- projected left/right shoulder, elbow, wrist;
- projected left/right hip, knee, ankle, toe;
- camera-space depth for each joint;
- chain screen length, world length and mean depth;
- anatomical left/right ownership;
- near/far anatomical side;
- support foot;
- left/right distance from the cycle ground reference;
- real projected root-travel displacement.

No visible body pixels are produced by Blender.

## Current implementation

Spec:

`tools/structured-2d-character-pipeline/g3s_c1_skeleton_walk_spec.json`

Blender exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_skeleton_walk.py`

Review/animation builder:

`tools/structured-2d-character-pipeline/g3s_c1_build_skeleton_walk_review.py`

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk`

Expected review outputs:

- `g3s_c1_skeleton_walk_guide.json`;
- `g3s_c1_skeleton_walk_in_place.gif`;
- `g3s_c1_skeleton_walk_travel.gif`;
- `g3s_c1_skeleton_walk_zoom.gif`;
- `g3s_c1_skeleton_walk_contact_sheet.png`;
- eight labeled frame PNGs.

Blue means anatomical left, red anatomical right, yellow the center chain, and white rings mark the support foot.

## PASS requirement

C1A passes only if the animated skeleton shows:

- one coherent eight-state human gait cycle;
- correct left/right progression;
- no duplicated/missing/reversed limb chains;
- plausible depth/near-far switching through the stride;
- support-foot states consistent with the gait;
- real root travel to screen-left;
- readable pelvis/trunk/leg relationship;
- approximately 128 px maximum skeletal height at the locked camera;
- no use of a skinned human mesh, final 3D pixels, static-body warp, model/API or manual user rigging.

## Next gate

After this skeleton animation passes, C1B goes directly to the **eight persistent native-2D body poses** for the first left-facing walk family. It uses C1A as motion/spatial control and B3B V4 as the visible identity/body-style anchor.

The user will not be asked to redraw or repair frames manually. The static B3B still will not be warped into the gait, and hidden 3D will not become the visible sprite.
