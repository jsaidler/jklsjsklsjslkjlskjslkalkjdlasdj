# G3S-C1 — Hidden-3D Full Pose Guide

Status date: **2026-09-06**

Gate status: **C1A V1/V2/V3 FAIL/CLOSED TECHNICAL — C1A V4 RUNNER READY / REVIEW REQUIRED — C1B BLOCKED UNTIL GUIDE REVIEW**

## Purpose

C1 implements the locked animation architecture:

`real motion -> hidden 3D full pose guide -> persistent native-2D pose asset -> sprite playback`

The hidden 3D guide is **not** the final visible art owner.

## C1A target

Export one non-rest gait event first: **anatomical left contact, screen-left directional family**.

Retained validated infrastructure:

- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- MPFB continuous adult female hidden body from retained G3V workspace;
- `G3V_CMU_RIG`;
- `DIRECTION_SPACE_FK` approval;
- G1 camera baseline: `640×360`, orthographic, pitch `26°`, target body height `128 px`.

Validated gait phase frames are `1568, 1588, 1608, 1628`. Local executions selected frame `1588` for the first left-contact candidate. Final visual approval still depends on the C1A review sheet.

## Transform/facing safeguards — LOCKED

- solve complete pose with `DIRECTION_SPACE_FK` first;
- rotate hidden mesh and rig together for screen-left family;
- ground mesh and rig together;
- require projected travel x < 0;
- anatomical left/right comes from rig bone identity, never screen-x.

## C1A V1 — FAIL/CLOSED TECHNICAL

Observed:

`evaluated body topology changed: eval=13378 source=18486`

V1 incorrectly assumed source and evaluated MPFB polygon indices were 1:1.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`

## C1A V2 — FAIL/CLOSED TECHNICAL

V2 moved depth assignment to evaluated topology but replaced the source object's mesh data with that evaluated topology while retaining source object state.

Observed successful metadata before rejection:

- frame `1588`;
- near=`left`, far=`right`;
- travel x=`-62.7345 px`;
- source polygons `18486`;
- evaluated polygons `13378`.

Final body height became `102.4258804321289 px` instead of approximately `128 px`.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`

## C1A V3 — FAIL/CLOSED TECHNICAL

V3 attempted to preserve the evaluated geometry by transforming copied evaluated vertices into world space and then neutralizing the **same rigged source object's** parent/object state.

The runner's new invariant caught that this still changed the projected geometry:

- pre-bake height: `128.0000 px`;
- post-bake height: `99.0563 px`;
- delta: `28.9437 px`.

Root cause: replacing `G3V_BODY.data` and neutralizing the rigged object's parent/bind/object transform state is not geometry-invariant on this retained MPFB stack. The error is in mutating the rigged source object, not in the hidden-pose architecture.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_v3_worldspace_bake_failure.json`

Closed sub-method:

`evaluate posed body -> replace G3V_BODY mesh -> neutralize G3V_BODY rig/parent/object state -> depth render`

## C1A V4 — CURRENT

V4 stops mutating `G3V_BODY` entirely.

For the depth pass only:

1. measure the original evaluated posed body's projected bbox at the locked camera;
2. obtain the already evaluated posed mesh;
3. copy that mesh into a **new detached temporary object**;
4. assign the new object the exact `ev.matrix_world` from the evaluated source;
5. leave it unparented, without armature modifiers or constraints;
6. compare its projected height against the original evaluated body and require delta `<= 0.25 px`;
7. assign depth-band materials directly on the detached evaluated topology;
8. hide `G3V_BODY` only for the depth render so the proxy is the sole depth-pass geometry;
9. retain `G3V_BODY` untouched for joints, bbox and all subsequent metadata.

Current exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v4.py`

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

V4 requires:

- `depth_guide.mode = detached_evaluated_object`;
- `depth_guide.source_body_mutated = false`;
- projected height delta `<= 0.25 px`;
- final original-body guide height approximately `128 px`;
- screen-left travel x < 0.

No source `.blend`, B3B sprite or production art is modified. No model/API/download is used.

## Guide outputs

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide`

Outputs:

- `g3s_c1_contact_left_hidden3d_neutral.png`;
- `g3s_c1_contact_left_silhouette_guide.png`;
- `g3s_c1_contact_left_regions_guide.png`;
- `g3s_c1_contact_left_depth_guide.png`;
- `g3s_c1_contact_left_skeleton_overlay.png`;
- `g3s_c1_contact_left_pose_guide.json`;
- `g3s_c1_contact_left_pose_guide_contact_sheet.png`;
- five `96×160` logical guide crops.

All rendered 3D outputs are **guide/control evidence only**. They may not become final sprite RGB, alpha or silhouette and may not be quantized/recolored into final pixel art.

## PASS requirement

C1A passes only if the review package visibly and numerically shows:

- coherent non-rest contact pose;
- correct screen-left directional family;
- explicit anatomical laterality;
- plausible near/far ownership;
- coherent whole-body foreshortening/occlusion reference;
- readable pelvis/torso/leg relationship;
- explicit contact/root metadata;
- approximately `128 px` original-body height at locked G1 camera;
- detached evaluated depth proxy with `<=0.25 px` projected-height difference;
- no promotion of hidden-3D pixels.

## Next gate after C1A review

**C1B — one persistent native-2D left-contact pose candidate.**

C1B must use C1A as pose/anatomy/occlusion control and B3B V4 as identity/body-style anchor. It may not warp the rest still into the gait pose or quantize the hidden-3D guide.
