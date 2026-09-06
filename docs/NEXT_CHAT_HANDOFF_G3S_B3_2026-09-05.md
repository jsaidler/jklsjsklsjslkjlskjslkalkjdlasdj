# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/G3S_C0_BODY_MOTION_PROOF.md`
5. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
6. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
7. `docs/G3S_B4_HAIR_LOG.md`

## Living-document invariant

Every state-changing project action updates thematic docs, `PROJECT_STATE`, this handoff and commits before reporting completion.

## Canonical animation architecture — LOCKED

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact guide data -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

**Critical correction:** hidden 3D is the rig/skeleton. A skinned human body mesh is not required for the animation guide.

Hidden rig owns joint transforms, skeletal topology, anatomical side identity, near/far/depth ordering, foreshortening, contact/root travel, sockets and secondary-motion drivers.

Visible anatomy, RGB, alpha and silhouette belong to persistent native-2D assets.

## Canonical body — LOCKED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- faces screen-left;
- remains identity/body-style anchor only.

## Hair — DEFERRED

Do not resume B4 automatically.

## Motion backbone — RETAINED

- G2 PASS, CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- G3V-R PASS using `DIRECTION_SPACE_FK`;
- phase frames `1568, 1588, 1608, 1628`;
- `G3V_CMU_RIG` may be retained as the hidden character-proportioned armature.

`G3V_BODY` is historical G3V evidence only and is no longer required for C1A.

## Closed routes

- direct visible 3D -> final pixel art;
- single-still cutout/warp/cage -> full gait;
- skinned MPFB body render as mandatory animation pose/anatomy/silhouette/depth guide.

## C1A history

V1–V4: skinned-body depth/export failures — closed.

V5: numeric guide succeeded but skinned body visually exploded into large triangular surfaces; skeleton overlay remained coherent — closed.

V6: first run failed before execution with:

`ModuleNotFoundError: No module named 'g3s_c1_export_hidden_pose_guide_v5'`

Do **not** repair V6. It is **SUPERSEDED PRE-RUN** because the skinned-body dependency itself has been removed from the architecture.

## CURRENT — C1A skeleton-only redesign

Next implementation must export one left-contact guide containing only control data derived from the rig:

- projected skeleton;
- complete bone-chain pose;
- anatomical left/right;
- per-chain camera-space depth and near/far ordering;
- contact foot/state;
- pelvis/root travel;
- screen-left travel/facing camera metadata.

No detailed 3D body mesh or 3D anatomy silhouette is required.

Optional debug capsules/line thickness may be generated directly from bones if useful, but must remain non-skinned control visualization.

## Operator state

**Do not rerun runner 21 yet.** A new skeleton-only C1A runner must be implemented and committed first.

After C1A skeleton guide PASS, C1B authors one complete persistent native-2D left-contact pose using the skeleton guide as spatial control and B3B V4 as identity/body-style anchor.

No model/API/download was added by V6; no cleanup applies.
