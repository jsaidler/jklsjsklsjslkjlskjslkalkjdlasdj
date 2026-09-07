# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE AGAIN FOR A CONTROLLED BASE-BF16 MODEL-EXHAUSTION PASS.**

The historical 2026-09-04 Base INT8 run remains valid negative evidence for that constrained configuration, but it no longer counts as a model-family rejection. The current project gate rebuilds Wan-Animate-2 around the highest-quality Base BF16 checkpoint before another verdict.

## Active local paths — LOCKED 2026-09-07

Project repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model workspace root:

`Z:\AI`

Current Wan workspace:

`Z:\AI\WanAnimate2`

Other retained AI workspaces already use the same root, including `Z:\AI\RogueliteCharacterPipeline` and `Z:\AI\SpriteSheetDiffusionSpike`.

`D:\AI` is **not** the active AI workspace root and must not be hard-coded by current tooling.

## Hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB RAM

The GPU is not used to choose the checkpoint. The canonical checkpoint is Base BF16 even if execution later requires aggressive offload or reduced spatial/temporal settings.

## Canonical BF16 W0 asset set

Only these model files belong to the reference-quality W0 route:

- `models/diffusion_models/wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `models/text_encoders/umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `models/clip_vision/clip_vision_h.safetensors` — ~1.26 GB;
- `models/vae/Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total payload is about **45.7 GB**, excluding ComfyUI/runtime/temp files.

The following are deliberately not retained in active W0:

- Base INT8 ConvRot;
- Distilled BF16;
- Distilled INT8 ConvRot;
- LightX2V distillation LoRA;
- UMT5 FP8.

`bootstrap.ps1` removes those superseded Wan-specific files if found.

## Official W0 inputs

The bootstrap downloads upstream `examples/demo1/reference.png` and `examples/demo1/template.mp4` under `ComfyUI/input/wan_animate2_w0/`.

## Scripts

### `bootstrap.ps1`

Active. Rebuilds/restores `Z:\AI\WanAnimate2`, checks free space, removes superseded Wan-specific assets, downloads the canonical BF16 set, downloads W0 inputs, copies `exilada_master.png`, writes `wan_bf16_route.json`, and removes the completed Hugging Face download cache.

The comfy-cli working directory is resolved dynamically from the parent of `$Workspace`; there is no fixed `D:\AI` dependency.

### `inspect.ps1`

Active. Starts the workspace ComfyUI headlessly, validates BF16 files/native Wan nodes, proves superseded assets are absent, and stores schemas in:

`Z:\AI\WanAnimate2\object_info_wan_bf16.json`

### Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the earlier 384×576 / 17-frame INT8 experiment. Do not use them for W0.

## Current operator entry point

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Runner 35 performs setup + cleanup + download + schema preflight and intentionally stops before inference.

## Cleanup discipline

- remove model variants/generated material when no longer part of the current diagnostic hypothesis;
- do not retain duplicate quantizations/Distilled checkpoints in advance;
- preserve small manifests/logs/results;
- do not delete the current Base BF16 route after one bad output; apply the model-exhaustion protocol first.
