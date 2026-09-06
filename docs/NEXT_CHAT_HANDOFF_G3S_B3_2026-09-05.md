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

### Closed revisions

V1–V4 are closed technical depth/export revisions. Do not reopen mesh bake/proxy depth methods.

Markers:

- `tools/structured-2d-character-pipeline/g3s_c1a_depth_topology_failure.json`;
- `tools/structured-2d-character-pipeline/g3s_c1a_v2_scale_failure.json`;
- `tools/structured-2d-character-pipeline/g3s_c1a_v3_worldspace_bake_failure.json`;
- `tools/structured-2d-character-pipeline/g3s_c1a_v4_proxy_scale_failure.json`.

### V5 visual review — FAIL/CLOSED

Reviewed sheet SHA256:

`74ee1979afa58b8bbe77a3549fdc6af41e24524287f6329a33425aa7b15f6ba9`

Numeric checks passed at frame `1588`: body height `128 px`, travel x about `-62.735 px`, left contact, near=`left`, far=`right`.

Visual review failed immediately:

- giant triangular/kite-like stretched surfaces on both upper-body sides;
- silhouette not human-coherent;
- region guide confirms stretched geometry belongs to skinned limb regions;
- skeleton overlay remains coherent.

Cause: the base C1 presentation still manufactured facing by independently rotating and grounding the target rig and skinned body after retarget. That object-space directional-family path is not geometry-preserving on retained MPFB.

Marker:

`tools/structured-2d-character-pipeline/g3s_c1a_v5_visual_transform_failure.json`

Closed method:

`retarget -> rotate/translate target rig + skinned body objects for facing/grounding`

V5 original-body camera-space **depth shader remains retained**.

### V6 — CURRENT / RUNNER READY

Exporter:

`tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide_v6.py`

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

V6 leaves the `DIRECTION_SPACE_FK` result untouched:

- no target-rig directional rotation;
- no skinned-body directional rotation;
- no visual grounding translation;
- preserve rig/body parent state and object matrices exactly;
- directional family comes from camera placement relative to real motion heading;
- camera is front-three-quarter, `45°` azimuth from heading, `26°` elevation;
- unmodified forward motion must project screen-left;
- original body must remain about `128 px`;
- V5 original-body camera-space depth shader remains, with no mesh proxy/bake/index mapping;
- max rig/body object-matrix delta after render `<=1e-8`.

No model/API/download is used.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

If successful, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide\g3s_c1_contact_left_pose_guide_contact_sheet.png`

Do not start C1B, resume hair or promote any 3D guide pixels before C1A visual review.

## After C1A PASS

C1B authors one complete persistent native-2D left-contact body pose using C1A as pose/anatomy/laterality/near-far/occlusion control and B3B V4 as identity/body-style anchor. No static-body warp and no quantized 3D render.
