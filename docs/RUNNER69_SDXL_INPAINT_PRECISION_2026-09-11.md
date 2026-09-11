# Runner69 — dedicated SDXL Inpainting 0.1 precision gate

Status date: **2026-09-11**

Status: **PREPARED / CURRENT MASK-NATIVE EDITOR GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner69 exists

Runner68 proved that the automatic target masks and sampler containment work, but Qwen-Image-Edit-2511 remained semantically too conservative inside the mask.

Runner68 actual result:

- no colored-guide leakage;
- outside-region changed ratio >Δ12 remained `0.0` for plank and strap;
- plank inside-allowed changed ratio >Δ12 only `0.059154`;
- strap inside-allowed changed ratio >Δ12 only `0.052066`;
- visually the plank remained present and the strap remained continuous.

Classification:

**TECHNICAL PASS / AUTOMATIC MASK CONTROL PASS / OUTSIDE-REGION CONTAINMENT PASS / SEMANTIC OPERATION FAIL / QWEN MASKED-PRECISION ROLE CLOSED.**

Perception/decomposition/composition are accepted and are not changed in Runner69.

## Editor hypothesis

Runner69 replaces only the regional editor with `SDXL Inpainting 0.1`.

Why this model is a rational next gate:

- it is explicitly trained for mask-native inpainting;
- its inpainting UNet accepts the masked image + mask channels through the native SDXL inpaint conditioning path;
- the official FP16 UNet is ~5.14 GB rather than another ~20 GB semantic-edit diffusion model;
- it is mature, local and feasible on the RTX 3060 12 GB with ComfyUI low-VRAM mode;
- the project does not need it to solve semantic localization because Runner66 already supplies valid automatic masks.

License: **CreativeML Open RAIL++-M**. Preserve license/use-restriction provenance for any production use.

## Payload

### SDXL Inpainting 0.1 FP16 UNet

Source:

`diffusers/stable-diffusion-xl-1.0-inpainting-0.1`

File:

`unet/diffusion_pytorch_model.fp16.safetensors`

Local name:

`sdxl_inpaint_0.1_fp16.safetensors`

SHA256:

`6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f`

Approximate size: `5.14 GB`.

### SDXL Base 1.0 checkpoint

Source:

`stabilityai/stable-diffusion-xl-base-1.0`

File:

`sd_xl_base_1.0.safetensors`

SHA256:

`31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`

Approximate size: `6.94 GB`.

The base checkpoint is used only as CLIP/VAE authority in the Runner69 graph. Its base diffusion MODEL output is intentionally unused.

Total new model payload: approximately `12.1 GB`.

## Runtime

Runner69 reuses the already-pinned ComfyUI runtime currently under:

`Z:\AI\QwenImageEdit\ComfyUI_windows_portable`

Pinned commit:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

This avoids duplicating another full Python/ComfyUI installation for the first feasibility gate. The SDXL outputs and gate state live separately under `Z:\AI\SDXLInpaint`.

## Native graph

`UNETLoader(SDXL Inpaint) + CheckpointLoaderSimple(SDXL Base CLIP/VAE) + source + automatic mask -> InpaintModelConditioning -> KSampler -> VAEDecode`

Required native nodes:

- `UNETLoader`;
- `CheckpointLoaderSimple`;
- `LoadImage`;
- `ImageToMask`;
- `CLIPTextEncode`;
- `InpaintModelConditioning`;
- `KSampler`;
- `VAEDecode`;
- `SaveImage`.

Recipe:

- 30 steps;
- CFG `6.0`;
- `dpmpp_2m`;
- Karras scheduler;
- denoise `1.0`;
- seed `0`;
- ComfyUI `--lowvram --reserve-vram 1.0`.

## Automatic control contract

Runner69 consumes Runner66 masks only. No manual production mask or box is accepted.

### Plank

- semantic target: Runner66 one-plank mask;
- inpaint mask: small deterministic dilation of that mask;
- desired operation: remove the board and synthesize a clean narrow opening/background continuation.

### Strap

- semantic target: Runner66 retained full strap mask;
- operation target: automatically derived central 40% of the strap;
- inpaint mask: small deterministic dilation of that central section;
- desired operation: remove only the middle iron section and reconstruct the aged wood behind it while preserving the two outside strap ends.

## Crop/alignment rule

Unlike the earlier Qwen crop path, Runner69 does not pass the crop through a model-specific rescaling node before applying a separate full-resolution mask.

The contextual crop and its mask are cut from the exact same source coordinates and padded to dimensions divisible by 64. `InpaintModelConditioning` consumes them together.

The final full-resolution composite remains a second deterministic containment layer.

## Files

Adapter:

`tools/roguelite-asset-studio/sdxl_inpaint_adapter.py`

Executor:

`tools/roguelite-asset-studio/sdxl_inpaint_region_gate.py`

Runner:

`tools/structured-2d-character-pipeline/69_bootstrap_and_run_sdxl_inpaint_precision_gate.ps1`

Output root:

`Z:\AI\SDXLInpaint\runner69_precision_gate`

Principal outputs:

- `plank_inpaint_mask.png`
- `plank_sdxl_raw_crop.png`
- `plank_sdxl_region_final.png`
- `strap_inpaint_mask.png`
- `strap_sdxl_raw_crop.png`
- `strap_sdxl_region_final.png`
- `runner69_sdxl_inpaint_contact_sheet.png`
- `runner69_sdxl_inpaint_manifest.json`
- `runner69_executor.log`

## PASS criteria

Technical PASS:

- hashes validate;
- native nodes exist;
- both dedicated inpaint jobs complete on RTX 3060 12 GB;
- outputs/manifest/contact sheet are written;
- no manual mask is used.

Visual PASS requires both tasks:

### Plank

- exactly the atomic board region is absent;
- the edited area reads as a real opening/background continuation, not reconstructed wood;
- neighboring planks/hardware remain coherent.

### Strap

- the central metal section is absent;
- coherent aged wood appears underneath;
- both outside strap ends survive;
- no replacement bar appears.

### Preservation

The deterministic final composite must keep unrelated geometry source-authoritative.

## Decision after Runner69

If both operations pass, promote a dedicated `automatic_region_inpaint` route and keep Qwen2511 as the higher-level semantic editor while SDXL Inpainting handles exact masked removal/fill operations.

If SDXL Inpainting fails semantically despite correct masks, remove its payload after preserving evidence and test the next dedicated inpainting backend behind the same accepted automatic-mask contract. Do not regress to global prompt-only editing or user-drawn masks.
