# G3S-C1 — Hidden-3D Full Pose Guide

Status date: **2026-09-06**

Gate status: **C1A V1 FAIL/CLOSED TECHNICAL REVISION — C1A V2 RUNNER READY / REVIEW REQUIRED — C1B BLOCKED UNTIL GUIDE REVIEW**

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

The four validated gait phase frames are `1568, 1588, 1608, 1628`. C1A chooses the left-contact candidate deterministically by preferring anatomical-left lead in source travel and strongest contact-like foot separation/grounding score. The selected frame is recorded in the output JSON and must be visually reviewed.

## Transform-space safeguards — LOCKED

C1A does not repeat the C0 facing/rest-space mistakes.

- `DIRECTION_SPACE_FK` solves the complete hidden pose first;
- directional-family conversion happens only **after** the full hidden pose is solved;
- the hidden body mesh and its armature are rotated together by `180°` around world Z for the screen-left family, preserving mesh↔armature bind-space relationships;
- grounding translation is applied to body mesh and armature together for the same reason;
- the real G2 travel direction is explicitly flipped into the selected directional family and then projected through the final C1 camera;
- the runner aborts unless projected travel x is negative for this screen-left family;
- anatomical left/right remains bone identity from the hidden rig, never screen-x position.

These safeguards control the hidden guide only and do not create final visible pixels.

## C1A V1 — FAIL/CLOSED TECHNICAL REVISION

The first local run successfully produced the neutral, silhouette and anatomical-region guide passes, then failed while preparing the depth-band guide.

Observed error:

`evaluated body topology changed: eval=13378 source=18486`

Root cause:

- V1 assumed that MPFB `G3V_BODY` source-mesh polygons and the evaluated/deformed render mesh had a 1:1 polygon-index mapping;
- that assumption is false on the retained MPFB stack because modifiers/helper masking change evaluated topology;
- therefore depth measured on the evaluated mesh cannot be written back to `body.data.polygons[i]` by the same polygon index.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`

This is **not** an animation-architecture failure. The complete hidden pose, screen-left direction contract and first three guide passes remained viable.

## C1A V2 — CURRENT

V2 keeps the same hidden-pose architecture and fixes only the depth-pass topology assumption.

For the single frozen guide pose:

1. evaluate the already-retargeted MPFB body;
2. copy that evaluated/deformed mesh in-process;
3. replace the temporary Blender object's mesh data with that evaluated copy;
4. remove modifiers from that temporary in-process object so the evaluated geometry is not deformed twice;
5. assign depth-band materials directly to the evaluated topology;
6. record both source and evaluated polygon counts in the pose JSON.

The source `.blend`, canonical B3B sprite and any repository art asset remain untouched. This bake exists only inside the headless guide-export process.

V2 exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v2.py`

The original V1 exporter is retained as historical implementation evidence:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide.py`

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
- five `96×160` logical guide crops for later source-authoring control.

## Ownership lock

All C1A rendered 3D outputs are **guide/control evidence only**.

They may not be:

- promoted as final sprite RGB;
- promoted as final alpha;
- promoted as final sprite silhouette;
- cropped/recolored/quantized and relabeled as pixel art;
- used to reopen the rejected direct-visible-G3V route.

The canonical B3B body remains the static identity/body-style anchor for the screen-left family:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

## Direction/laterality lock

The C1A target family faces and travels **screen-left**.

The guide JSON explicitly records:

- anatomical left/right for every projected joint;
- near/far anatomical side from camera-space depth;
- selected contact foot;
- screen-space travel vector, which must have negative x displacement.

No screen-x heuristic is allowed to substitute for anatomical laterality.

## Runner

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Support:

- `tools/structured-2d-character-pipeline/g3s_c1_pose_guide_spec.json` — current revision `HIDDEN_3D_FULL_POSE_GUIDE_V2`;
- `tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v2.py`;
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
- depth guide produced from the evaluated mesh topology (`mode = evaluated_mesh_bake`);
- no claim that hidden-3D RGB/silhouette is final pixel art.

## Next gate after C1A review

**C1B — one persistent native-2D left-contact pose candidate.**

C1B must use the approved C1A guide as pose/anatomy/occlusion control and B3B V4 as identity/body-style anchor. It must create new complete native-2D visible anatomy for that pose; it may not warp the rest still into shape or quantize the 3D guide.

No C1B runner is approved until the C1A contact sheet is reviewed.
