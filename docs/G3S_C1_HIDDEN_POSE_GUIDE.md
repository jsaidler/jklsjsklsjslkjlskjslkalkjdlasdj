# G3S-C1 — Hidden-3D Full Pose Guide

Status date: **2026-09-06**

Gate status: **C1A V1 FAIL/CLOSED TECHNICAL — C1A V2 FAIL/CLOSED TECHNICAL — C1A V3 RUNNER READY / REVIEW REQUIRED — C1B BLOCKED UNTIL GUIDE REVIEW**

## Purpose

C1 implements the locked animation architecture after C0 proved that a single static 3/4 sprite cannot be warped into a convincing walk.

Canonical architecture:

`real motion -> hidden 3D full pose guide -> persistent native-2D pose asset -> sprite playback`

The hidden 3D guide is **not** the final visible art owner.

## C1A — first full pose guide

C1A exports exactly one non-rest gait event first: **anatomical left contact, screen-left directional family**.

It reuses the retained validated infrastructure:

- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG` real motion;
- MPFB continuous adult female hidden body from the retained G3V workspace;
- `G3V_CMU_RIG`;
- `DIRECTION_SPACE_FK` approval from `tools/deterministic-character-pipeline/g3v_retarget_approval.json`;
- locked G1 camera baseline: `640×360`, orthographic, pitch `26°`, target body height `128 px`.

The four validated gait phase frames are `1568, 1588, 1608, 1628`. C1A deterministically selected frame `1588` for the first anatomical-left contact candidate during V2 execution. That event remains subject to visual review after the guide package passes all numeric invariants.

## Transform-space safeguards — LOCKED

- `DIRECTION_SPACE_FK` solves the complete hidden pose first;
- directional-family conversion happens only after the full hidden pose is solved;
- hidden body mesh and armature rotate together by `180°` around world Z for the screen-left family;
- grounding translation applies to mesh and armature together;
- travel direction is projected through the final C1 camera and must have negative screen x;
- anatomical left/right remains hidden-rig bone identity, never screen-x position.

These safeguards control the hidden guide only and do not create final visible pixels.

## C1A V1 — FAIL/CLOSED TECHNICAL

The first local run wrote neutral, silhouette and region passes, then failed preparing depth:

`evaluated body topology changed: eval=13378 source=18486`

Root cause: V1 incorrectly assumed a 1:1 polygon mapping between MPFB source mesh and evaluated/deformed mesh.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`

This did not invalidate the hidden-3D guide architecture.

## C1A V2 — FAIL/CLOSED TECHNICAL

V2 correctly moved the depth bands onto evaluated topology. The second local run completed all four rendered passes and produced the review package, with:

- selected frame `1588`;
- near side `left`;
- far side `right`;
- projected travel `-62.7345 px` in screen x;
- source polygons `18486`;
- evaluated polygons `13378`.

However the final guide height was only `102.4258804321289 px` instead of the locked approximately `128 px`, so the runner correctly failed the camera-scale invariant.

Root cause: V2 copied evaluated mesh data back into the source object's local mesh while retaining the source object transform. On this retained MPFB stack that did not preserve the exact evaluated world-space geometry used by camera calibration.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`

This also does **not** invalidate the hidden-3D guide architecture.

## C1A V3 — CURRENT

V3 fixes the scale drift by making the depth bake explicitly world-space invariant:

1. measure the projected evaluated body before baking;
2. copy the already-posed evaluated mesh;
3. transform copied vertices into exact evaluated **world coordinates** using the evaluated object's matrix;
4. remove parenting/modifiers from the temporary in-process guide object;
5. set its object matrix to identity;
6. verify projected body height before/after bake differs by no more than `0.25 px`;
7. assign depth bands directly on this frozen world-space topology.

This guarantees that depth-pass topology freezing cannot silently change the G1 camera scale.

Current exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v3.py`

Historical exporters remain as failure evidence:

- V1: `tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide.py`;
- V2: `tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v2.py`.

The source `.blend`, canonical B3B sprite and repository art assets remain untouched. All topology freezing exists only inside the headless guide-export process.

## Guide outputs

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide`

C1A generates:

- `g3s_c1_contact_left_hidden3d_neutral.png` — continuous body/anatomy pose guide;
- `g3s_c1_contact_left_silhouette_guide.png` — pose silhouette reference only;
- `g3s_c1_contact_left_regions_guide.png` — explicit anatomical region/laterality guide;
- `g3s_c1_contact_left_depth_guide.png` — camera-space depth-band guide;
- `g3s_c1_contact_left_skeleton_overlay.png` — projected skeleton/laterality overlay;
- `g3s_c1_contact_left_pose_guide.json` — joints, anatomical sides, near/far, contact, root/camera/selection metadata;
- `g3s_c1_contact_left_pose_guide_contact_sheet.png` — review sheet including the canonical B3B static body anchor;
- five `96×160` logical guide crops.

## Ownership lock

All C1A rendered 3D outputs are **guide/control evidence only**. They may not be promoted as final sprite RGB, alpha or silhouette, nor cropped/recolored/quantized into final pixel art.

Canonical B3B body remains the static identity/body-style anchor:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

## Direction/laterality lock

The C1A target family faces and travels **screen-left**. Guide JSON explicitly records anatomical side, near/far side, selected contact foot and screen-space travel vector. No screen-x heuristic substitutes for anatomical laterality.

## Runner

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Support:

- `tools/structured-2d-character-pipeline/g3s_c1_pose_guide_spec.json`;
- `tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v3.py`;
- `tools/structured-2d-character-pipeline/g3s_c1_build_pose_guide_review.py`.

C1A uses no image-generation model, paid API or new download.

## PASS requirement

C1A passes only if the review package visibly and numerically shows:

- one coherent non-rest contact pose;
- correct screen-left directional family;
- explicit anatomical laterality;
- plausible near/far ownership;
- correct whole-body foreshortening/occlusion reference;
- readable pelvis/torso/leg relationship;
- explicit contact/root metadata;
- approximately `128 px` body height at the locked G1 camera;
- depth guide `mode = evaluated_worldspace_bake`;
- projected guide height delta across the depth bake `<= 0.25 px`;
- no claim that hidden-3D RGB/silhouette is final pixel art.

## Next gate after C1A review

**C1B — one persistent native-2D left-contact pose candidate.**

C1B must use the approved C1A guide as pose/anatomy/occlusion control and B3B V4 as identity/body-style anchor. It must create new complete native-2D visible anatomy for that pose; it may not warp the rest still into shape or quantize the 3D guide.

No C1B runner is approved until the C1A contact sheet is reviewed.
