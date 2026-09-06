# G3S-C1 — Hidden Skeleton Pose Guide

Status date: **2026-09-06**

Gate status: **C1A V1–V5 CLOSED / V6 SUPERSEDED PRE-RUN / C1A SKELETON-ONLY REDESIGN CURRENT / C1B BLOCKED UNTIL GUIDE REVIEW**

## Purpose

C1 follows the canonical animation architecture:

`real motion -> hidden skeleton/rig -> pose/laterality/depth/contact guide data -> persistent native-2D pose asset -> sprite playback`

The hidden guide is not a visible-art owner and does not require a skinned human body mesh.

## Architectural correction

The previous C1A implementation incorrectly interpreted "full pose guide" as "render a full posed MPFB body". That was unnecessary.

The project only needs the hidden 3D to supply the **full skeletal spatial state**:

- joint/bone transforms;
- anatomical left/right;
- near/far identity;
- camera-space depth/order;
- foreshortening of chains;
- foot contact;
- root/pelvis travel;
- sockets and secondary-motion drivers.

Visible anatomy remains entirely owned by the persistent native-2D pose asset.

Therefore `G3V_BODY` is no longer required by C1A. The retained `G3V_CMU_RIG` may remain as the hidden character-proportioned armature receiving the validated `DIRECTION_SPACE_FK` motion.

## What happened to V1–V6

V1–V4 were technical attempts to obtain depth from the MPFB skinned body and are closed.

V5 finally produced stable numeric depth/camera data, but visual review showed catastrophic stretched triangles in the skinned body. The skeleton itself remained coherent. This demonstrated that the rig data was useful while the skinned mesh was unnecessary and harmful to this gate.

V6 attempted to preserve the rig/body object state and move directional-family selection to the camera. Its first local run failed immediately with:

`ModuleNotFoundError: No module named 'g3s_c1_export_hidden_pose_guide_v5'`

V6 is **SUPERSEDED PRE-RUN**, not repaired, because the entire skinned-body dependency it was trying to preserve has now been removed from the canonical guide architecture.

## Current C1A target

Export one **left-contact skeleton-only guide** from the retained real-motion backbone.

The guide must contain:

- selected gait event/frame;
- projected skeleton at locked `640×360`, pitch `26°`;
- screen-left travel direction;
- anatomical left/right labels;
- per-chain camera-space depth and near/far ordering;
- contact foot/state;
- root/pelvis transform;
- camera metadata;
- no skinned body mesh;
- no rendered 3D anatomy/silhouette requirement.

If useful for review, simple non-skinned debug capsules or line thickness may be generated from bone transforms. They are optional control visualization only.

## PASS requirement

C1A passes when the skeleton guide visibly and numerically shows:

- coherent human locomotion pose;
- correct left-contact event;
- correct screen-left travel family;
- explicit anatomical laterality;
- plausible near/far chain ownership;
- coherent pelvis/trunk/limb relationship;
- readable contact/root metadata;
- stable production camera/view basis.

No hidden 3D mesh needs to resemble the Exilada.

## Next gate

**C1B — one complete persistent native-2D left-contact body pose.**

C1B uses:

- the approved C1A skeleton/depth/contact guide as spatial control;
- B3B V4 as identity/body-style anchor.

C1B may not deform the rest still into the gait pose and may not promote a hidden-3D render into final sprite art.
