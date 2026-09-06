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

Normal operator loop:

`git pull -> one documented PowerShell command -> inspect/share output`

## Canonical animation architecture — LOCKED

`real/captured motion -> hidden 3D rig -> full pose-specific 3D guide package -> selected gait/action events -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

Hidden 3D owns pose/topology/laterality/near-far/foreshortening/contact/root/depth/occlusion/sockets. It does not own final visible RGB/alpha/silhouette.

Do not return to single-still warp/cutout/cage animation.

## Canonical body — LOCKED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- faces screen-left.

It is a static identity/style anchor, not the sole animation pixel source.

## Hair — DEFERRED

Do not resume B4 automatically.

## Motion backbone — RETAINED / ACTIVE

- G2 PASS, CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- G3V-R PASS using `DIRECTION_SPACE_FK`;
- phase frames `1568, 1588, 1608, 1628`;
- hidden guide blend `Z:\AI\RogueliteCharacterPipeline\g3v\g3v_representative_proxy.blend`.

## CURRENT gate — G3S-C1A

Purpose: produce one complete hidden-3D anatomical left-contact guide before any new visible pose pixels are authored.

### Closed technical revisions

V1: source/evaluated polygon index assumption failed (`18486` vs `13378`).

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`.

V2: evaluated local-object bake produced final guide height `102.4258804321289 px` instead of ~128 px.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`.

V3: world-space mesh replacement on the original rigged object failed geometry invariance: pre=`128.0000`, post=`99.0563`, delta=`28.9437 px`.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v3_worldspace_bake_failure.json`.

V4: detached evaluated proxy also failed geometry equivalence: original=`128.0000`, proxy=`102.4259`, delta=`25.5741 px`.

Marker: `tools/structured-2d-character-pipeline/g3s_c1a_v4_proxy_scale_failure.json`.

Closed technical class for C1A depth:

`evaluated MPFB body -> baked/copied/proxy geometry carrier -> depth render`

Do not create another mesh bake/proxy revision.

### V5 — CURRENT / RUNNER READY

Exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v5.py`

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

V5 keeps the exact original evaluated `G3V_BODY` that calibrated the locked camera and renders depth by material only:

- measure near/far from evaluated world-space vertices;
- assign a guide-only shader directly to original `G3V_BODY`;
- shader transforms each shading point WORLD -> CAMERA and maps camera-space depth continuously to grayscale;
- no mesh copy;
- no proxy object;
- no polygon-index mapping;
- no geometry/parent/armature/bind/object-transform mutation;
- projected height before/after material setup must differ by `<=0.01 px`.

Required depth metadata:

- `mode = original_body_camera_space_shader`;
- `source_geometry_mutated = false`;
- `proxy_object_used = false`;
- `topology_index_mapping_used = false`;
- projected height delta `<=0.01 px`.

Runner also requires approximately `128 px` body height and screen-left travel x < 0.

No model/API/download is used.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

If successful, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide\g3s_c1_contact_left_pose_guide_contact_sheet.png`

If it fails, share the full console output.

Do not start C1B, resume hair or promote any 3D guide pixels before C1A visual review.

## After C1A PASS

C1B authors one complete persistent native-2D left-contact body pose using C1A as pose/anatomy/laterality/near-far/occlusion control and B3B V4 as identity/body-style anchor. No static-body warp and no quantized 3D render.
