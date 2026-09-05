# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-B PERSISTENT PART DECOMPOSITION READY**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character color pixels.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI operation by the user;
- no beauty-render shrink/pixel-filter route as final art;
- no bilinear filtering;
- recurring work remains scriptable/headless;
- one-time source construction may use deterministic native-grid edits;
- animation consumes persistent parts rather than regenerating frames;
- anatomical details are semantically important, but localized defects must be isolated into replaceable parts rather than forcing whole-character redraws.

## Model-discard cleanup rule — LOCKED

Whenever a model/route is declared **FAIL/CLOSED/REJECTED** and no longer required, the same response must include exact PowerShell cleanup commands for its model-specific files. Shared runtimes still in use are preserved; small result/log evidence remains unless explicitly removed.

### Current closed-model cleanup commands

```powershell
# Alucard
Remove-Item -LiteralPath "Z:\AI\AlucardSpike" -Recurse -Force -ErrorAction SilentlyContinue

# PixelLock
Remove-Item -LiteralPath "Z:\AI\PixelLockSpike" -Recurse -Force -ErrorAction SilentlyContinue

# SD1.5 native re-author
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\checkpoints\v1-5-pruned-emaonly.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\loras\pixel-art-sd15.safetensors" -Force -ErrorAction SilentlyContinue

# Qwen weights — fixed control retained; shared embedded Python runtime remains
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\unet\Qwen-Image-Edit-2509-Q4_0.gguf" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\vae\qwen_image_vae.safetensors" -Force -ErrorAction SilentlyContinue
```

# G3S-A source history — CLOSED AS MODEL SEARCH

Bounded source experiments:

- Qwen direct-native `640×360` — FAIL;
- Qwen preferred-resolution control — PASS only as design/scaffold provenance;
- SD1.5 + pixel LoRA native re-author — FAIL;
- PixelLock initial-source authoring — FAIL;
- Alucard external-reference attempt — INVALID;
- Alucard text-only native-128 control — FAIL.

Do not start another source-model search.

Retained design/provenance control:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Pinned SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## Authored native V1 — FAIL / CLOSED

V1 added nominal mouth/restraint/chain pixels to a native 128 scaffold. Visual review showed the mouth still did not read. Pixel existence is not semantic readability.

Marker:

`tools/structured-2d-character-pipeline/g3s_a_authored_v1_failure.json`

## G3S-A1 Facial / Anatomy Lock V2 — FAIL / CLOSED

Detailed log:

`docs/G3S_A1_FACIAL_ANATOMY_LOCK_LOG.md`

V2 produced explicit face/hands/feet diagnostics, but visual review rejected the mouth as an exaggerated dark/red block.

Marker:

`tools/structured-2d-character-pipeline/g3s_a1_v2_failure.json`

### Locked decision after V2

The user chose to continue the planned structured-2D architecture:

- macro body/scaffold is accepted **provisionally for decomposition only**;
- `head_face` is unresolved and must become a replaceable part;
- the bad V2 mouth patch is not authoritative;
- broken chain segments are not baked into the permanent body sprite;
- chains become initial accessories with sockets/state;
- G3S-B is unblocked;
- G3S-C remains blocked until G3S-B review.

# G3S-B — Persistent Part Decomposition — CURRENT

Canonical log:

`docs/G3S_B_PERSISTENT_PART_DECOMPOSITION_LOG.md`

Purpose: convert the provisional 128×128 scaffold into persistent native pixel assets with stable IDs, pivots and metadata.

V1 part set:

- hair back mass;
- head/face placeholder;
- torso/pelvis core;
- front cloth mass;
- screen-left/right upper arms;
- screen-left/right forearms;
- screen-left/right hands;
- screen-left/right thighs;
- screen-left/right shins;
- screen-left/right feet;
- front-left/front-right hair masses.

The static image stores screen-side identity only. Anatomical left/right is resolved in G3S-C against projected hidden-rig joints.

Broken-chain accessory slots are created for both wrists and both ankles with `baked_into_body = false` and `art_status = NOT_AUTHORED`.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b_parts_spec_v1.json`
- `tools/structured-2d-character-pipeline/g3s_b_decompose_v1.py`
- `tools/structured-2d-character-pipeline/09_run_g3s_b_decomposition.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b_decomposition`

Review artifact:

`g3s_b_contact_sheet.png`

Technical requirement: recomposition from named parts plus audited residual must be pixel-exact to the provisional scaffold. Visual review remains authoritative for mask boundaries, hair/cloth isolation, pivots, hands/feet and chain sockets.

# G3S-C — Four-phase walk proof

Blocked until G3S-B visual PASS.

Persistent parts will then be bound to the validated motion frames `1568,1588,1608,1628`. No frame may be independently regenerated by diffusion.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\09_run_g3s_b_decomposition.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b_decomposition\g3s_b_contact_sheet.png`
