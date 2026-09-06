# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/GAME_VISION.md`
5. `docs/VISUAL_DIRECTION.md`
6. `docs/CHARACTERS.md`
7. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
8. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
9. `docs/PIXEL_ART_PRODUCTION.md`
10. `docs/ANIMATION_PIPELINE.md`
11. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
12. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
13. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
14. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
15. `docs/G3S_B4_HAIR_LOG.md`
16. `docs/G3S_C0_BODY_MOTION_PROOF.md`
17. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

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

`real/captured motion -> hidden 3D rig -> full pose-specific 3D guide package -> selected gait/action events -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

Hidden 3D owns motion/topology, anatomical side, near/far identity, complete pose, foreshortening reference, contacts/root travel, depth/occlusion, sockets and semantic guides.

Hidden 3D does **not** own final visible RGB, alpha or production silhouette. Rendered 3D may guide only; it may not be promoted/quantized/recolored into final sprite geometry.

## Canonical Exilada body — PASS/CLOSED / LOCKED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical facing **screen-left**.

The body remains a static identity/style anchor, not the sole animation pixel source.

## Facing/laterality — LOCKED

- current family faces/travels screen-left;
- do not mirror silently;
- screen-x is not anatomical left/right or near/far;
- laterality and near/far come from hidden rig data.

## Motion infrastructure — RETAINED / ACTIVE

- G2 = PASS/CLOSED;
- CMU `105_34 NormalWalk`;
- source rig `G2_CANONICAL_RIG`;
- G3V-R = PASS/CLOSED;
- retarget method `DIRECTION_SPACE_FK`;
- validated phase frames `1568, 1588, 1608, 1628`.

This is guide/control infrastructure only.

## Closed visible routes

- direct visible G3V 3D translation — CLOSED/REJECTED;
- C0 V1/V2 single-still cutout/warp — CLOSED/REJECTED;
- no weighted/cage revision using only the single B3B still.

## Hair — DEFERRED

B4 remains open but paused by user. Do not resume automatically.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3/G3R/G3V direct visible 3D routes — CLOSED/REJECTED
- G3S-B3 production body — PASS/CLOSED
- G3S-B4 hair — DEFERRED/OPEN
- G3S-C0 single-still motion — FAIL/CLOSED
- G3S-C1A hidden-3D full-pose guide:
  - V1 source/evaluated polygon-index assumption — FAIL/CLOSED TECHNICAL
  - V2 evaluated local-object bake — FAIL/CLOSED TECHNICAL
  - V3 mutate original rigged object after world-space bake — FAIL/CLOSED TECHNICAL
  - **V4 detached evaluated depth proxy — CURRENT / RUNNER READY / REVIEW NEXT**
- G3S-C1B native-2D non-rest pose — BLOCKED UNTIL C1A REVIEW
- B5 clothing/restraints/accessories — DEFERRED

## C1A technical history

### V1

Failed because MPFB source polygons=`18486`, evaluated polygons=`13378`; polygon-index identity was false.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`.

### V2

Produced frame `1588`, near=`left`, far=`right`, travel x=`-62.7345 px`, but guide height drifted to `102.4258804321289 px`.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`.

### V3

Invariant caught another transform failure before depth render:

- pre=`128.0000 px`;
- post=`99.0563 px`;
- delta=`28.9437 px`.

Cause: replacing `G3V_BODY.data` and neutralizing the original rigged object's parent/bind/object state is not geometry-invariant on this MPFB stack.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v3_worldspace_bake_failure.json`.

### V4 — CURRENT

V4 never mutates `G3V_BODY`.

Depth pass:

1. evaluate posed `G3V_BODY`;
2. copy evaluated mesh to a new detached temporary object;
3. assign exact evaluated `matrix_world` to that object;
4. require no parent/modifiers/constraints;
5. compare original evaluated body vs detached proxy projected height; delta must be `<=0.25 px`;
6. assign depth bands on detached topology;
7. hide original body only for the depth render;
8. keep original rigged body intact for bbox/joints/metadata.

Current exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v4.py`

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1_pose_guide_spec.json`

Required V4 depth mode: `detached_evaluated_object`; `source_body_mutated=false`.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

Then share:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide\g3s_c1_contact_left_pose_guide_contact_sheet.png`

If the runner fails, share the complete console output.

Do not resume hair and do not start/promote C1B before C1A visual review.

## Local state relevant to C1A

- workspace: `Z:\AI\RogueliteCharacterPipeline`;
- hidden guide blend: `Z:\AI\RogueliteCharacterPipeline\g3v\g3v_representative_proxy.blend`;
- embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- Blender is headless guide host;
- no image model, paid API or new download in C1A;
- FLUX.2 not used by C1A;
- PixelLab not authorized.
