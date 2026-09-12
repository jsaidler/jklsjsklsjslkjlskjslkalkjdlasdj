# Runner69 — dedicated SDXL Inpainting 0.1 precision gate

Status date: **2026-09-11**

Status: **COMPLETE / TECHNICAL PASS / MASK-NATIVE RESPONSE PASS / VISUAL OPERATION FAIL AT SUBTRAINING RESOLUTION / FINAL SDXL VERDICT DEFERRED TO RUNNER70**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner69 replaced only the regional editor behind the already-accepted automatic precision stack:

`Runner66 automatic target mask -> dedicated mask-native editor -> deterministic full-resolution composite`.

Perception/decomposition/composition were held constant. No user-drawn mask or box was introduced.

The tested editor was `SDXL Inpainting 0.1`, using:

- dedicated FP16 inpainting UNet;
- SDXL Base 1.0 checkpoint only as CLIP/VAE authority;
- native ComfyUI `InpaintModelConditioning`;
- 30 steps;
- CFG `6.0`;
- `dpmpp_2m`;
- Karras scheduler;
- denoise `1.0`;
- seed `0`;
- low-VRAM / reserve 1 GB.

## Payload

### SDXL Inpainting 0.1 FP16 UNet

Local name:

`sdxl_inpaint_0.1_fp16.safetensors`

SHA256:

`6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f`

### SDXL Base 1.0 checkpoint

Local name:

`sd_xl_base_1.0.safetensors`

SHA256:

`31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`

Used only as CLIP/VAE authority in the graph.

License provenance: CreativeML Open RAIL++-M.

## Actual execution

Technical execution completed on RTX 3060 12 GB with no OOM.

Total elapsed: `29.422 s`.

### Plank

Input crop:

- source-coordinate crop size `256x512`;
- approved automatic bbox `[358,295,388,644]`;
- operation = full atomic plank.

Result:

- elapsed `18.075 s`;
- inside-allowed changed ratio >Delta12 `0.539487`;
- outside-allowed changed ratio >Delta12 `0.0`;
- raw model output strongly reacted to the mask;
- final result did **not** become a clean opening;
- instead it produced bright/shiny vertical reconstruction artifacts and inconsistent local hardware/wood.

Visual verdict: **FAIL at tested resolution**.

### Strap

Input crop:

- source-coordinate crop size `384x256`;
- approved full strap bbox `[456,549,550,592]`;
- operation bbox `[484,550,522,590]`, the automatically derived central 40%.

Result:

- elapsed `10.047 s`;
- inside-allowed changed ratio >Delta12 `0.336265`;
- outside-allowed changed ratio >Delta12 `0.0`;
- model reacted inside the mask but did not create a clear physical break with coherent aged wood underneath;
- strap remained effectively continuous/ambiguous.

Visual verdict: **FAIL at tested resolution**.

## What Runner69 proved

1. dedicated SDXL inpainting runs comfortably on the project hardware;
2. native `InpaintModelConditioning` is technically healthy;
3. the backend reacts much more strongly inside accepted masks than Qwen2511 Runner68;
4. the deterministic full-resolution compositor still preserves unrelated source pixels;
5. perception, mask generation and containment remain accepted.

## Why Runner69 is not the final SDXL verdict

The official SDXL Inpainting 0.1 model was trained at `1024x1024`, while Runner69 fed crops of only `256x512` and `384x256`.

Those dimensions are far below the model's intended spatial regime and provide a plausible explanation for the unstable shiny reconstruction on the plank and weak semantics on the small strap region.

The project therefore does **not** delete or replace SDXL after Runner69.

## Final classification

**TECHNICAL PASS / DEDICATED MASK-NATIVE RESPONSE PASS / OUTSIDE-REGION CONTAINMENT PASS / VISUAL OPERATION FAIL AT SUBTRAINING RESOLUTION / SDXL HYPOTHESIS STILL OPEN.**

## Next gate

Runner70 changes one variable only: model-input resolution.

Architecture:

`Runner66 accepted target -> 512x512 source-authoritative context -> jointly upscale source+mask to 1024x1024 -> same SDXL Inpainting recipe -> downsample to exact 512 source coordinates -> deterministic full-resolution composite`.

Canonical next record:

`docs/RUNNER70_SDXL_INPAINT_1024_PARITY_2026-09-11.md`

Runner:

`tools/structured-2d-character-pipeline/70_run_sdxl_inpaint_1024_parity_gate.ps1`

No additional model download is allowed for Runner70.

Only if Runner70 still fails the plank/strap operations is the SDXL Inpainting hypothesis considered exhausted and its provisional payload eligible for cleanup.