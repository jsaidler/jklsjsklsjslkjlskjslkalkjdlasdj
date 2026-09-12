# Runner70 — SDXL Inpainting 0.1 / 1024 training-resolution parity gate

Status date: **2026-09-11**

Status: **PREPARED / CURRENT MASK-NATIVE EDITOR GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner70 exists

Runner69 proved that the dedicated SDXL Inpainting 0.1 backend is technically healthy, mask-native, fast and materially more active inside the accepted automatic masks than Qwen2511. However, its model inputs were far below the model's training regime:

- plank crop: `256x512`;
- strap crop: `384x256`;
- official SDXL Inpainting 0.1 training resolution: `1024x1024`.

Runner69 therefore cannot be used as the final verdict on the SDXL inpainting hypothesis.

Actual Runner69 visual result:

### Plank

- mask and target were correct;
- raw inpaint strongly modified the masked strip;
- result produced bright/shiny vertical reconstruction artifacts rather than a clean opening;
- final inside-allowed changed ratio >Delta12: `0.539487`;
- outside-allowed changed ratio >Delta12: `0.0`;
- elapsed `18.075 s`.

### Strap

- mask and target were correct;
- inpainting remained too conservative/continuous and did not create a clean central break exposing coherent wood;
- final inside-allowed changed ratio >Delta12: `0.336265`;
- outside-allowed changed ratio >Delta12: `0.0`;
- elapsed `10.047 s`.

Runner69 classification:

**TECHNICAL PASS / MASK-NATIVE RESPONSE PASS / OUTSIDE-REGION CONTAINMENT PASS / VISUAL OPERATION FAIL AT SUBTRAINING RESOLUTION / FINAL SDXL VERDICT DEFERRED.**

## One-variable correction

Runner70 changes only model-input geometry.

Unchanged:

- SDXL Inpainting 0.1 FP16 UNet;
- SDXL Base 1.0 CLIP/VAE authority;
- Runner66 automatic masks;
- plank full atomic operation;
- strap central-40-percent break operation;
- 30 steps;
- CFG 6.0;
- DPM++ 2M;
- Karras;
- denoise 1.0;
- seed 0;
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`;
- deterministic final full-resolution composite;
- no manual box or mask.

Changed:

1. extract an exact `512x512` source-authoritative context square around each accepted target;
2. upscale source image and operation mask together to `1024x1024`;
3. run the existing native `InpaintModelConditioning` graph at 1024;
4. downsample the generated result to the exact `512x512` source-coordinate crop;
5. composite through the same deterministic allowed region into the untouched full source.

This preserves aspect ratio and avoids stretching a rectangular crop to a square by taking a square source context before scaling.

## Why 1024

The official `diffusers/stable-diffusion-xl-1.0-inpainting-0.1` model card states that the model was trained for 40k steps at `1024x1024`. Runner70 therefore tests the backend in its intended spatial regime before the project decides whether to retain or remove the ~12.1 GB SDXL payload.

## Runtime and payload

No download.

Reuse:

- `sdxl_inpaint_0.1_fp16.safetensors`
- SHA256 `6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f`
- `sd_xl_base_1.0.safetensors`
- SHA256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`
- shared pinned ComfyUI under `Z:\AI\QwenImageEdit\ComfyUI_windows_portable`
- Runner66 masks under `Z:\AI\RogueliteAssetStudio\localization\runner66_gate`.

Output root:

`Z:\AI\SDXLInpaint\runner70_1024_parity_gate`

## Implementation

Executor:

`tools/roguelite-asset-studio/sdxl_inpaint_1024_parity_gate.py`

Runner:

`tools/structured-2d-character-pipeline/70_run_sdxl_inpaint_1024_parity_gate.ps1`

Existing adapter reused unchanged:

`tools/roguelite-asset-studio/sdxl_inpaint_adapter.py`

## Expected diagnostics

Per task:

- `*_source_context_512.png`
- `*_model_source_1024.png`
- `*_inpaint_mask_1024.png`
- `*_sdxl_1024_raw.png`
- `*_sdxl_1024_downsampled_512.png`
- `*_sdxl_1024_region_final.png`
- `*_allowed_region.png`

Comparison:

`runner70_sdxl_1024_contact_sheet.png`

Manifest:

`runner70_sdxl_1024_manifest.json`

## PASS criteria

Technical PASS:

- existing SDXL hashes and pinned ComfyUI validate;
- Runner66 masks validate;
- Runner69 evidence validates;
- exact 512 square context is produced for each task;
- source and mask are both exactly 1024x1024 at model input;
- both 30-step jobs complete;
- output is downsampled back to the exact source coordinate system;
- deterministic final composites are produced;
- no download or manual mask occurs.

Visual PASS requires both tasks.

### Plank

- one atomic board is truly absent;
- its region reads as a narrow opening/background continuation;
- no bright/chrome/shiny reconstructed strip remains;
- neighboring boards and hardware remain coherent.

### Strap

- central strap section is absent;
- matching aged wood is visible in the break;
- both external strap ends survive;
- no continuous/replacement bar appears.

### Preservation

Outside the deterministic allowed neighborhood, source pixels remain authoritative.

## Decision after Runner70

If both tasks pass, promote SDXL Inpainting 0.1 as the first `automatic_region_inpaint` specialist and continue to semantic multi-reference role separation before Character Lab.

If Runner70 still fails either hard operation, the SDXL Inpainting hypothesis is exhausted fairly. Preserve Runner69/70 evidence, remove the provisional SDXL payload under the cleanup rule, and test the next dedicated mask-native backend behind the already-accepted perception/mask/compositor contract. Do not add more arbitrary step/prompt tuning.