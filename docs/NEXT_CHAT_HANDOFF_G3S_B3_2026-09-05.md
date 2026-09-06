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
8. `docs/ANIMATION_PIPELINE.md`

Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant

Every state-changing project action updates thematic docs, `PROJECT_STATE`, this handoff and commits before reporting completion.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Canonical animation architecture — LOCKED

`real/captured motion -> hidden 3D rig -> full pose-specific 3D guide package -> selected gait/action events -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

Canonical lock: `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`.

Hidden 3D owns motion/topology, anatomical side identity, near/far identity, full pose, foreshortening reference, contacts, root travel, depth/occlusion, sockets and semantic/body-part guides.

Hidden 3D does **not** own final visible RGB/alpha/silhouette. Hidden-3D render/mask/silhouette is guide/control data only.

Critical correction: C0 V1/V2 incorrectly reduced the hidden rig to projected joint deltas applied to one static sprite. Do not repeat that.

## Canonical body — LOCKED

B3B V4 is PASS/CLOSED / PROMOTED:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical screen-facing: **LEFT**.

This is a static body identity/style anchor, not the sole source to be warped into every gait pose.

## Facing/laterality — LOCKED

- left-facing source family travels screen-left;
- do not mirror silently;
- screen-x is not anatomical left/right or near/far ownership in a 3/4 sprite;
- anatomical side and near/far identity come from the hidden 3D guide package.

## Hair — DEFERRED

B4 remains open and unapproved. Eventual minimum structure remains:

`rear_hair -> body -> front_hair`

Do not resume B4 automatically.

## Motion backbone — RETAINED / ACTIVE

- G2 = PASS using CMU `105_34 NormalWalk`;
- source rig = `G2_CANONICAL_RIG`;
- G3V-R = PASS using `DIRECTION_SPACE_FK`;
- validated phase frames = `1568, 1588, 1608, 1628`.

Retained hidden body/rig artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_representative_proxy.blend`

It is used only as guide/control infrastructure.

## Closed visible routes

Direct visible G3V = FAIL/CLOSED because output read as low-resolution 3D, not intentional pixel art.

C0 single-still deformation V1/V2 = FAIL/CLOSED. Closed class:

`single B3B still -> projected joints -> cutout/chain/cage warp -> full walk`

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1` is disabled.

## CURRENT gate — G3S-C1A HIDDEN-3D FULL-POSE GUIDE

Purpose: export **one complete non-rest anatomical left-contact pose guide** from the retained hidden 3D backbone before any new visible pose pixels are authored.

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1_pose_guide_spec.json`

Current exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v3.py`

Review builder:

`tools/structured-2d-character-pipeline/g3s_c1_build_pose_guide_review.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide`

## C1A V1 — FAIL/CLOSED TECHNICAL

First local run wrote neutral, silhouette and region passes, then failed because MPFB source/evaluated polygon counts differed (`18486` vs `13378`) and V1 incorrectly assumed polygon-index identity.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`

## C1A V2 — FAIL/CLOSED TECHNICAL

Second local run completed all four rendered passes and the review package. It selected frame `1588`, produced near=`left`, far=`right`, and projected screen travel `-62.7345 px`, but the measured hidden-body guide height became `102.4258804321289 px` instead of approximately `128 px`.

Cause: V2 copied evaluated mesh data into source local data while retaining source object transforms, so the frozen topology did not preserve the exact world-space geometry used during camera calibration.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`

This is a technical export-space failure, not an architecture failure.

## C1A V3 — CURRENT / RUNNER READY

V3 keeps the same full-pose/retarget/direction architecture but freezes the evaluated mesh in exact **world coordinates**:

- copy evaluated posed mesh;
- transform its vertices by the evaluated object matrix;
- remove modifiers and parenting from the temporary in-process guide object;
- set object matrix to identity;
- verify projected body height before/after bake differs by no more than `0.25 px`;
- assign depth bands directly on this world-space frozen topology.

Runner also still requires:

- `DIRECTION_SPACE_FK` approval PASS;
- canonical B3B hash unchanged;
- negative screen-x travel for the screen-left family;
- approximately `128 px` body height;
- `depth_guide.mode = evaluated_worldspace_bake`.

No source `.blend`, B3B sprite or production art is modified. No model/API/download is used.

All hidden-3D rendered outputs remain **non-promotable guide evidence only**.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

Then share:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide\g3s_c1_contact_left_pose_guide_contact_sheet.png`

If it fails, share the complete console output.

Do **not** start C1B, resume hair or promote any 3D guide pixels before C1A visual review.

## Next after C1A PASS

C1B authors **one complete persistent native-2D left-contact body pose** using C1A as pose/anatomy/laterality/near-far/occlusion control and B3B V4 as identity/body-style anchor.

C1B may not warp the static B3B still into the gait pose and may not quantize/recolor/crop the hidden-3D guide into final sprite art.

If one C1B pose passes, expand to the first eight-event left-facing walk family: left contact/down/passing/up and right contact/down/passing/up.

Runtime playback is standard sprite animation driven by motion-derived timing/contact/root metadata.

## Local state

- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- retained hidden G3V body/rig blend as above;
- Blender remains the headless pose-guide host;
- C1A requires no image-generation model, paid API or new download;
- FLUX.2 is not used by C1A;
- no broad model search is open;
- PixelLab remains historical paid spike only and is not authorized.
