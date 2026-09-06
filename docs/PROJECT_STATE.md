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

Normal operator loop only after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

Native gameplay baseline:

- `640×360`;
- orthographic camera;
- pitch `26°`;
- protagonist standing body height approximately `128 px`.

## Final animation architecture — LOCKED

Canonical architecture:

`real/captured motion -> hidden 3D rig -> full pose-specific 3D guide package -> selected gait/action events -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

Canonical lock document: `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`.

Hidden 3D owns motion/topology, anatomical left/right, near/far identity, full pose/foreshortening reference, contacts/root travel, depth/occlusion, sockets/secondary-motion drivers and semantic/body-part guides.

Hidden 3D does **not** own final visible RGB, alpha or production silhouette. A hidden-3D render/mask/silhouette may guide pose/anatomy/occlusion only and may not be cropped/recolored/quantized/promoted into final sprite geometry.

The failed C0 experiments incorrectly reduced the hidden-3D role to joint deltas imposed on one static sprite. That is explicitly not the locked architecture.

## Canonical Exilada body — PASS/CLOSED / LOCKED

Production body:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- dimensions `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical screen-facing for this asset: **LEFT**.

The body remains byte/pixel unchanged as source art. It is a valid static left-facing 3/4 body anchor, not the sole pixel source for all animated poses.

## Facing/laterality invariant — LOCKED

The current body is an authored **front-three-quarter, screen-left-facing** sprite. Screen-left/screen-right positions in this raster are not automatically anatomical left/right or near/far limb ownership.

Any travel preview using this exact directional family must move screen-left unless a separately authored right-facing family is selected. Do not mirror silently and do not infer anatomical laterality from x-position alone.

## Motion infrastructure — RETAINED / ACTIVE AS GUIDE BACKBONE

- G2 real motion/topology — **PASS/CLOSED**;
- motion source: CMU `105_34 NormalWalk`;
- source rig: `G2_CANONICAL_RIG`;
- G3V-R retarget preflight — **PASS/CLOSED**;
- method: `DIRECTION_SPACE_FK`;
- validated phase frames: `1568, 1588, 1608, 1628`.

This infrastructure is the production guide/control backbone. It supplies complete pose guides, contacts, timing, root travel, laterality, near/far ownership, sockets and depth. It does not directly produce final visible pixels.

## Direct visible 3D route — CLOSED

G3V proved the hidden rig and retargeting but failed the visual kill switch: the output still read as low-resolution 3D rather than intentional modern pixel art.

Therefore direct hidden-3D RGB as final sprite is CLOSED, while hidden 3D itself is RETAINED as guide/control infrastructure.

Canonical record: `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`.

## Hair — DEFERRED BY USER

B4 remains open and unapproved. Eventual minimum structure remains:

`rear_hair -> body -> front_hair`

No hair pixels were promoted. Hair does not resume automatically.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3/G3R/G3V direct visible 3D translation routes — CLOSED/REJECTED
- G3S-B3 production body — **PASS/CLOSED**
- G3S-B4 hair — **DEFERRED / OPEN**
- G3S-C0 body-only motion proof
  - V1 rigid cutout — **FAIL/CLOSED**
  - V2 continuous chain warp — **FAIL/CLOSED**
  - single-still puppet/warp route — **CLOSED**
- G3S-C1A hidden-3D full-pose guide
  - V1 source/evaluated topology-index assumption — **FAIL/CLOSED TECHNICAL**
  - V2 evaluated-topology local-space bake — **FAIL/CLOSED TECHNICAL**
  - **V3 evaluated world-space bake — CURRENT / RUNNER READY / REVIEW NEXT**
- G3S-C1B one native-2D non-rest pose — **BLOCKED UNTIL C1A REVIEW**
- G3S-B5 clothing/restraints/accessories — DEFERRED
- full layered G3S-C — later, after visible layer families exist

## G3S-C0 failures — CLOSED METHOD, NOT MOTION BACKBONE

V1 failure marker: `tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`.

V2 reviewed contact sheet: `Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_contact_sheet.png`.

V2 SHA256: `6d6199aa7bc159cad344c8dbc31b52577f2c70bb70f674ab5216ea40db67fba3`.

V2 failure marker: `tools/structured-2d-character-pipeline/g3s_c0_v2_visual_failure.json`.

Closed class:

`single B3B still -> projected joints -> cutout / chain warp / cage warp -> manufacture full gait`

The V2 runner remains intentionally disabled: `tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1`.

## G3S-C1A — CURRENT

C1A exports one **full hidden-3D left-contact pose guide** before authoring any new visible sprite pose.

Canonical gate record: `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`.

Spec: `tools/structured-2d-character-pipeline/g3s_c1_pose_guide_spec.json`.

Runner: `tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`.

Current exporter: `tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v3.py`.

Review builder: `tools/structured-2d-character-pipeline/g3s_c1_build_pose_guide_review.py`.

C1A uses the retained `Z:\AI\RogueliteCharacterPipeline\g3v\g3v_representative_proxy.blend` only as hidden guide geometry and re-applies the validated `DIRECTION_SPACE_FK` solver.

### C1A V1 technical failure — CLOSED

First local execution rendered neutral, silhouette and regions, then failed because evaluated topology had `13378` polygons while the source mesh had `18486`. V1 incorrectly assumed polygon-index identity.

Failure marker: `tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`.

### C1A V2 technical failure — CLOSED

Second local execution completed the rendered passes and review package. Numeric results included:

- selected event/frame: `left_contact`, frame `1588`;
- near side `left`, far side `right`;
- screen travel dx `-62.7345 px`;
- evaluated topology `13378` polygons;
- final measured body height `102.4258804321289 px` vs locked approximately `128 px`.

The runner correctly rejected this scale drift.

Cause: V2 froze evaluated mesh data in the source object's local data space while retaining source object transforms; that did not preserve the exact evaluated world geometry used during camera calibration.

Failure marker: `tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`.

### C1A V3 fix — CURRENT

V3 freezes the evaluated guide mesh in exact **world coordinates**, removes parenting/modifiers, sets the temporary object's matrix to identity, and asserts that projected body height changes by no more than `0.25 px` across the depth-topology bake.

The runner still separately enforces approximately `128 px` total guide height, negative screen-x travel for the left-facing family, and `depth_guide.mode = evaluated_worldspace_bake`.

No source `.blend`, B3B body sprite or production art is modified.

C1A outputs remain neutral guide, silhouette guide, anatomical-region guide, depth-band guide, projected skeleton overlay, machine-readable pose JSON, five `96×160` logical guide crops and a review contact sheet.

**None of these hidden-3D images may become final sprite pixels or silhouette.**

## Current exact operator action

Run exactly:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

Then share:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide\g3s_c1_contact_left_pose_guide_contact_sheet.png`

If the runner fails, share the complete console output.

Do not resume hair and do not create/promote C1B pixels before C1A visual review.

## Local state relevant to C1A

- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- retained G3V hidden body/rig blend: `Z:\AI\RogueliteCharacterPipeline\g3v\g3v_representative_proxy.blend`;
- retained embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- Blender remains the headless hidden-pose guide host;
- C1A requires no AI model, paid API or new download;
- retained FLUX.2 workspace is not used by C1A;
- no broad model search is open;
- PixelLab remains historical paid spike only and is not authorized.
