# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — BASE BF16 OFFICIAL W0 RETRY GATE.**

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

Starts the workspace ComfyUI headlessly, validates BF16 files/native Wan nodes and stores the installed schema in `Z:\AI\WanAnimate2\object_info_wan_bf16.json`.

Runner 35 completed this gate successfully on 2026-09-07.

### `build_and_run_w0.py`

W0 builder/executor. It queries live ComfyUI `/object_info`, validates required node classes, builds the graph against the actual installed schema, feeds official reference + raw official driving-video frames to native `WanAnimate2ToVideo`, runs Base BF16 at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, then trims/decodes/saves and records evidence.

No DWPose/custom motion preprocessor is installed or used in W0.

## W0 attempt 1 — infrastructure failure

The first BF16 W0 inference submission failed after about 74 seconds with:

`RuntimeError: hostbuf_file_reader_read failed`

Trace location: `comfy_aimdo/host_buffer.py`, during host-buffer/dynamic model weight streaming.

This happened before meaningful denoising/output evaluation and therefore does **not** count as a Wan model failure.

## W0 attempt 2 — pinned-memory workaround

Current runner:

`tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

It now restarts the managed ComfyUI server and adds one launch option only:

`--disable-pinned-memory`

All model/graph/W0 generation settings remain unchanged.

Current ComfyUI exposes this option natively, and contemporary ComfyUI/Wan reports document the same `comfy_aimdo` host-buffer failure being resolved with pinned memory disabled.

Do not add `--disable-dynamic-vram`, reduce resolution/frame count or quantize until this narrower retry is tested.

Expected evidence after success:

- `Z:\AI\WanAnimate2\object_info_w0_live.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`

## Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the earlier 384×576 / 17-frame INT8 experiment. Do not use them for current W0.

## Cleanup discipline

- remove model variants/generated material when they no longer belong to the active hypothesis;
- do not retain duplicate quantizations/Distilled checkpoints in advance;
- preserve small manifests/logs/results;
- do not delete the active Base BF16 route after one failed execution or poor image; apply the model-exhaustion protocol first.