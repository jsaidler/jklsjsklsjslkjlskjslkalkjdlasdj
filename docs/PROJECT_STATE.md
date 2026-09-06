# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Living-document invariant — LOCKED

Every state-changing action updates the thematic doc, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

- systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and causal living world;
- elevated 2D belt-scroller / false 3D;
- true modern pixel art at native gameplay raster;
- `640×360`, orthographic, pitch `26°`, protagonist standing body height approximately `128 px`.

## Final animation architecture — LOCKED

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact guide data -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

Critical clarification: **hidden 3D means the rig/skeleton. It does not require a skinned human body mesh.**

Hidden 3D owns skeletal topology, full joint transforms, anatomical side identity, near/far chain identity, foreshortening, contacts/root travel, depth/occlusion ordering, sockets and secondary-motion drivers.

Hidden 3D does **not** own a detailed 3D body, final RGB, alpha, anatomy silhouette or pixel-art language.

Canonical lock: `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`.

## Canonical Exilada body — PASS/CLOSED / LOCKED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical facing screen-left.

The B3B body is the visible identity/body-style anchor, not a deformation source for every gait pose.

## Motion backbone — RETAINED / ACTIVE

- G2 = PASS/CLOSED;
- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- G3V-R = PASS/CLOSED;
- retarget method `DIRECTION_SPACE_FK`;
- validated phase frames `1568, 1588, 1608, 1628`;
- `G3V_CMU_RIG` may be retained as the character-proportioned hidden armature.

`G3V_BODY` is no longer required for the animation-guide path. It remains historical G3V evidence only.

## Closed routes

- direct visible G3V 3D -> final pixels — CLOSED;
- C0 single-still cutout/warp/cage -> full gait — CLOSED;
- C1A skinned MPFB body render as mandatory pose/anatomy/silhouette/depth guide — CLOSED.

## Hair — DEFERRED

B4 remains paused by user. Do not resume automatically.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3/G3R/G3V direct visible 3D — CLOSED/REJECTED
- G3S-B3 production body — PASS/CLOSED
- G3S-B4 hair — DEFERRED/OPEN
- G3S-C0 single-still motion — FAIL/CLOSED
- G3S-C1A:
  - V1–V4 skinned-body depth/export attempts — CLOSED
  - V5 skinned-body visual guide — FAIL/CLOSED
  - V6 camera-relative skinned-body revision — **SUPERSEDED PRE-RUN** after import failure and architecture clarification
  - **CURRENT: skeleton-only hidden pose guide redesign**
- G3S-C1B native-2D non-rest pose — BLOCKED UNTIL skeleton guide review
- B5 clothing/restraints/accessories — DEFERRED

## C1A current decision

The hidden guide for animation is now deliberately minimal:

- no skinned mesh;
- no detailed 3D anatomy;
- no 3D silhouette requirement;
- export projected joints/bone chains;
- anatomical left/right;
- per-chain camera-space depth / near-far;
- contact foot/state;
- pelvis/root travel;
- direction/facing camera metadata;
- optional simple non-skinned debug capsules only if later proven useful.

The previous wording "full pose guide" means **full skeletal pose state**, not a full rendered human surface.

Canonical C1 record: `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`.

## Current operator state

**Do not rerun `21_run_g3s_c1_hidden_pose_guide.ps1` yet.** The V6 runner is superseded and must not be repaired as a skinned-body path.

Next implementation is a skeleton-only C1A runner. After that runner is committed, the normal operator loop resumes.

## Local state

- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- retained G3V blend remains historical/backbone evidence;
- Blender remains available as hidden rig host;
- no image model, paid API or new download is required for skeleton-only C1A;
- no cleanup applies to V6 because no new model/API/runtime was added.
