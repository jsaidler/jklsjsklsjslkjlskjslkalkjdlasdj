# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — BASE BF16 OFFICIAL W0 INFERENCE GATE.**

The historical 2026-09-04 Base INT8 run remains valid negative evidence for that constrained configuration, but it does not count as model-family exhaustion.

## Active local paths — LOCKED 2026-09-07

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model workspace root: `Z:\AI`

Current Wan workspace: `Z:\AI\WanAnimate2`

Other retained workspaces: `Z:\AI\RogueliteCharacterPipeline` and `Z:\AI\SpriteSheetDiffusionSpike`.

`D:\AI` is stale/historical and must not be hard-coded by current tooling.

## Hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB RAM

Checkpoint quality is chosen independently of hardware. Execution concessions are tested only if the canonical checkpoint cannot run.

## Canonical BF16 W0 asset set

- `models/diffusion_models/wan_animate_2_bf16.safetensors` — ~32.8 GB
- `models/text_encoders/umt5_xxl_fp16.safetensors` — ~11.4 GB
- `models/clip_vision/clip_vision_h.safetensors` — ~1.26 GB
- `models/vae/Wan2_1_VAE_bf16.safetensors` — ~0.254 GB

Total payload: approximately **45.7 GB**.

Not retained for W0: Base INT8 ConvRot, Distilled BF16/INT8, LightX2V distillation LoRA and UMT5 FP8.

## Official W0 inputs

Upstream `examples/demo1/reference.png` and `examples/demo1/template.mp4`, stored under the active ComfyUI input directory at `wan_animate2_w0/`.

## Scripts

### `bootstrap.ps1`

Prepares/restores `Z:\AI\WanAnimate2`, checks disk space, removes superseded Wan-specific assets, downloads the canonical BF16 set and official W0 inputs, copies `exilada_master.png` for later W1, writes `wan_bf16_route.json`, and removes completed HF cache.

### `inspect.ps1`

Starts the workspace ComfyUI headlessly, validates BF16 files/native Wan nodes and stores the installed schema in:

`Z:\AI\WanAnimate2\object_info_wan_bf16.json`

Runner 35 completed this gate successfully on 2026-09-07.

### `build_and_run_w0.py`

Active W0 builder/executor. It:

1. queries live ComfyUI `/object_info`;
2. validates all node classes needed by the W0 API graph;
3. builds the graph against the live installed schema rather than stale widget assumptions;
4. feeds the official reference image and raw official driving-video frames directly to native `WanAnimate2ToVideo`;
5. feeds the first driving frame to the dedicated driving CLIP-vision branch when the installed schema supports it;
6. runs Base BF16 at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0;
7. trims the model's overlap latent using native `TrimVideoLatent`;
8. decodes, creates and saves the MP4;
9. records the live schema, API prompt and run manifest.

No DWPose/custom motion preprocessor is installed or used in this W0 graph.

Expected evidence after success:

- `Z:\AI\WanAnimate2\object_info_w0_live.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`

### Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the earlier 384×576 / 17-frame INT8 experiment. Do not use them for current W0.

## Current operator entry point

Preparation is complete. Current runner:

`tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

This is the first expensive Base-BF16 inference and remains W0 only. It does not use the Exilada master.

## Cleanup discipline

- remove model variants/generated material when they no longer belong to the active hypothesis;
- do not retain duplicate quantizations/Distilled checkpoints in advance;
- preserve small manifests/logs/results;
- do not delete the active Base BF16 route after one failed execution or poor image; apply the model-exhaustion protocol first.