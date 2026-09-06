# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Mandatory source of truth

Read `docs/PROJECT_STATE.md` first, then `docs/G3S_B4_HAIR_LOG.md` and the other G3S/visual pipeline docs. Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant — MANDATORY

Every state-changing project action updates thematic docs, `PROJECT_STATE`, this handoff when continuity changes, and commits before reporting completion.

## Canonical production body base

B3B V4 is **PASS/CLOSED / PROMOTED**:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

Body remains byte/pixel unchanged through B4/B5.

## G3S-B4 — HAIR CURRENT / OPEN

Canonical hair: black/nearly black, very long, heavy, voluminous, messy, wild, lived-in.

Mandatory composition:

`rear_hair -> body -> front_hair`

## Closed B4B route

- B4A preflight — **PASS/CLOSED DIAGNOSTIC**.
- B4B V1 master extraction — **FAIL/CLOSED PRE-RUN**.
- B4B V2 authored two-layer — **FAIL/CLOSED VISUAL / STRUCTURAL PASS**.
- B4B V3 — **FAIL/CLOSED VISUAL AND ALIGNMENT METHOD**.
- B4B V4 — **FAIL/CLOSED VISUAL AND METHOD**.

V4 failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchor_failure.json`

Reviewed V4 contact sheet SHA256:

`50dd663cbbeb0bb1a9865f2ac95daedc7990ceaf7a98ae6a968c8b7eacb4a8a5`

The procedural `Pillow polygons/lines + heuristic pose anchors` visual-authoring route is closed. `17_run_g3s_b4b_two_layer_hair_candidate.ps1` is intentionally disabled. Do not create another anchor/polygon revision.

## B4C FLUX.2 real visual adapter — CURRENT / RUNNER READY

User instruction `faça` authorizes narrow reuse of the **already-retained local FLUX.2 workspace** for this static hair visual-adaptation gate only. This does not reopen the old animation/refcontrol production route and does not authorize a broad new model search.

Spec:

`tools/structured-2d-character-pipeline/g3s_b4c_flux2_visual_adapter_spec.json`

Runner:

`tools/structured-2d-character-pipeline/18_run_g3s_b4c_flux2_visual_hair_adapter.ps1`

Supporting tools:

- `g3s_b4c_prepare_flux2_visual_adapter.py`
- `g3s_b4c_build_flux2_visual_review.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter`

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter\g3s_b4c_flux2_contact_sheet.png`

### B4C contract

- exact canonical B3B body is image 1 and authoritative for pose/proportion/scale/camera/placement;
- master is image 2 and supplies hair identity/style/material only;
- master clothing, restraints, chains, accessories and pose are explicitly excluded from transfer;
- no procedural hair geometry is authored;
- one visual generation only, fixed seed `20260906`;
- no automatic retry;
- no paid API;
- no download;
- no production promotion;
- generated composite is visual evidence only.

B4C expects existing files inside `Z:\AI\Flux2RefControlSpike\ComfyUI_windows_portable\ComfyUI`:

- `models\diffusion_models\flux-2-klein-base-4b-fp8.safetensors`;
- `models\text_encoders\qwen_3_4b.safetensors`;
- `models\vae\flux2-vae.safetensors`.

If they are not present, the runner fails before generation and prints the exact missing paths. Do not infer they are present from the directory name.

If B4C visually passes, proceed to two controlled visual-authoring passes for separate persistent `rear_hair` and `front_hair`, then validate/promote native 2D layers. If it fails, close this narrow route without touching the canonical body.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\18_run_g3s_b4c_flux2_visual_hair_adapter.ps1"
```

Then share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter\g3s_b4c_flux2_contact_sheet.png`

If it fails, share console output. Do not start B5/G3S-C before B4 passes.

## Actual local AI state

- retained shared/general runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`;
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- retained historical FLUX.2 workspace: `Z:\AI\Flux2RefControlSpike`; B4C may reuse its already-existing weights only after file checks;
- PixelLab is historical paid spike only, not active/authorized;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed.
