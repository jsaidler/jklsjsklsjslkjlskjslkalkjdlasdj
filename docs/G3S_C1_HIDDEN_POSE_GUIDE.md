# G3S-C1 — Hidden-3D Full Pose Guide

Status date: **2026-09-06**

Gate status: **C1A V1/V2/V3/V4 FAIL/CLOSED TECHNICAL — V5 FAIL/CLOSED VISUAL TRANSFORM METHOD — V6 RUNNER READY / REVIEW REQUIRED — C1B BLOCKED UNTIL GUIDE REVIEW**

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

Validated gait phase frames are `1568, 1588, 1608, 1628`. Local executions selected frame `1588` for the first left-contact candidate. Final event approval still depends on a coherent C1A visual guide.

## Closed technical revisions V1–V4

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

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v3_worldspace_bake_failure.json`.

### V4 — detached evaluated proxy

Detached `ev.to_mesh()` + `ev.matrix_world` still did not reproduce the exact projected retained-MPFB geometry:

- original=`128.0000 px`;
- proxy=`102.4259 px`;
- delta=`25.5741 px`.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v4_proxy_scale_failure.json`.

Closed depth sub-method class:

`original evaluated MPFB body -> baked/copied/proxy geometry carrier -> depth render`

No further mesh-bake/proxy depth revisions are allowed.

## C1A V5 — FAIL/CLOSED VISUAL TRANSFORM METHOD

V5 successfully removed the depth-topology problem by rendering camera-space depth directly on the unchanged original evaluated `G3V_BODY` with a guide-only shader.

The reviewed contact sheet:

`g3s_c1_contact_left_pose_guide_contact_sheet.png`

SHA256:

`74ee1979afa58b8bbe77a3549fdc6af41e24524287f6329a33425aa7b15f6ba9`

Numeric invariants that passed on that sheet:

- body height `128.0 px`;
- travel x approximately `-62.735 px`;
- selected frame `1588`;
- contact foot `left`;
- near anatomical side `left`;
- far anatomical side `right`.

But visual review is an immediate FAIL:

- the neutral guide contains huge triangular/kite-like stretched surfaces projecting from both upper-body sides;
- the silhouette is not a coherent adult human silhouette;
- the anatomical-region pass assigns those stretched surfaces to left/right limb regions;
- the skeleton/laterality overlay itself remains coherent while the skinned body geometry is visibly exploded.

This proves that numeric scale/direction checks were insufficient.

The C1A base setup was still transforming the skinned presentation after retarget by independently rotating both `G3V_CMU_RIG` and `G3V_BODY` by 180° and then translating both for visual grounding. On this retained MPFB bind/parent/armature stack, that object-space directional-family path is not geometry-preserving.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_v5_visual_transform_failure.json`

Closed presentation sub-method:

`retarget complete hidden body -> rotate/translate rig + skinned body objects to manufacture screen-left family`

The V5 **depth shader itself is retained**. The rejected part is the object-transform directional-family setup.

## C1A V6 — CURRENT

V6 leaves the retargeted hidden rig and skinned body object state untouched.

Directional family is now produced by **camera placement relative to the real motion heading**, not by transforming the rig/body:

1. select frame and apply validated `DIRECTION_SPACE_FK`;
2. snapshot the resulting `G3V_CMU_RIG` and `G3V_BODY` object matrices and parent state;
3. apply **no** directional rotation and **no** visual grounding translation to either object;
4. derive heading from the real G2 travel vector;
5. place the orthographic camera at a `45°` horizontal front-three-quarter azimuth relative to that heading and `26°` elevation;
6. choose the lateral side so unmodified forward travel projects screen-left;
7. calibrate the same original evaluated body to approximately `128 px`;
8. render neutral/silhouette/regions on that intact body;
9. retain V5 original-body camera-space depth shader;
10. abort if rig/body parent state changes or either object matrix changes by more than `1e-8`.

Current exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v6.py`

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Required V6 metadata:

- `revision = HIDDEN_3D_FULL_POSE_GUIDE_V6_CAMERA_DIRECTIONAL_FAMILY`;
- `direction_family_method = camera_relative_to_motion_no_rig_or_body_transform`;
- `camera.horizontal_view = front_three_quarter`;
- `camera.azimuth_from_motion_heading_deg = 45`;
- `transform_safeguard.rig_or_body_directional_transform_applied = false`;
- `transform_safeguard.grounding_transform_applied = false`;
- parent state preserved;
- object-matrix delta `<= 1e-8`;
- travel screen x `< 0`;
- body height approximately `128 px`;
- depth mode `original_body_camera_space_shader` with no proxy/topology substitution.

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

- coherent adult human non-rest contact pose with no exploded/stretched skin geometry;
- correct screen-left directional family;
- explicit anatomical laterality;
- plausible near/far ownership;
- coherent whole-body foreshortening/occlusion reference;
- readable pelvis/torso/leg relationship;
- explicit contact/root metadata;
- approximately `128 px` body height;
- front-three-quarter camera relative to real motion heading;
- no directional/grounding transform of the rigged body or target rig;
- original-body camera-space depth shader with no proxy/topology substitution;
- no promotion of hidden-3D pixels.

## Next gate after C1A review

**C1B — one persistent native-2D left-contact pose candidate.**

C1B must use C1A as pose/anatomy/occlusion control and B3B V4 as identity/body-style anchor. It may not warp the rest still into the gait pose or quantize the hidden-3D guide.
