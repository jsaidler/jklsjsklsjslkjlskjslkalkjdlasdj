# G3S-C1 — Hidden-3D Full Pose Guide

Status date: **2026-09-06**

Gate status: **C1A V1/V2/V3/V4 FAIL/CLOSED TECHNICAL — C1A V5 RUNNER READY / REVIEW REQUIRED — C1B BLOCKED UNTIL GUIDE REVIEW**

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

## Closed technical revisions

### V1 — source/evaluated polygon identity

Observed:

`evaluated body topology changed: eval=13378 source=18486`

V1 incorrectly assumed source and evaluated MPFB polygon indices were 1:1.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`.

### V2 — evaluated local-object bake

V2 moved depth assignment to evaluated topology but the frozen guide height became `102.4258804321289 px` instead of approximately `128 px`.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`.

### V3 — world-space bake on original rigged object

The invariant caught:

- pre=`128.0000 px`;
- post=`99.0563 px`;
- delta=`28.9437 px`.

Replacing `G3V_BODY.data` and neutralizing the original rigged object's parent/bind/object state is not geometry-invariant on this MPFB stack.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v3_worldspace_bake_failure.json`.

### V4 — detached evaluated proxy

V4 stopped mutating `G3V_BODY` and created a detached object from `ev.to_mesh()` with `ev.matrix_world`.

The new invariant still caught a mismatch:

- original evaluated body=`128.0000 px`;
- detached proxy=`102.4259 px`;
- delta=`25.5741 px`.

Therefore a detached evaluated mesh object is also not a trustworthy substitute for the exact projected geometry of the retained MPFB body.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v4_proxy_scale_failure.json`.

Closed sub-method class:

`original evaluated MPFB body -> bake/copy/proxy topology carrier -> depth render`

The depth guide no longer uses a substitute geometry carrier at all.

## C1A V5 — CURRENT

V5 renders depth **directly on the original evaluated `G3V_BODY`**. No bake, proxy object or polygon-index mapping is used.

For the depth pass only:

1. retain the exact rigged/evaluated body that calibrated the locked 128 px camera;
2. measure camera-space near/far depth range from its evaluated world-space vertices;
3. assign a guide-only emission shader to `G3V_BODY`;
4. shader transforms each shading point from WORLD to CAMERA space and maps camera-space depth continuously to grayscale;
5. keep body geometry, parenting, armature modifiers, bind state and object transform unchanged;
6. require projected body height before/after the material-only depth setup to differ by no more than `0.01 px`.

This removes the entire source/evaluated topology correspondence problem from C1A.

Current exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v5.py`

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Required depth metadata:

- `mode = original_body_camera_space_shader`;
- `source_geometry_mutated = false`;
- `proxy_object_used = false`;
- `topology_index_mapping_used = false`;
- projected height delta `<= 0.01 px`.

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
- approximately `128 px` body height at locked G1 camera;
- original-body camera-space depth shader with no proxy/topology substitution;
- projected-height delta `<=0.01 px` across depth material setup;
- no promotion of hidden-3D pixels.

## Next gate after C1A review

**C1B — one persistent native-2D left-contact pose candidate.**

C1B must use C1A as pose/anatomy/occlusion control and B3B V4 as identity/body-style anchor. It may not warp the rest still into the gait pose or quantize the hidden-3D guide.
