# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 EXILADA CROSS-IDENTITY ACTIVE.**

## Active local paths

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model root: `Z:\AI`

Current Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical.

## Hardware

- Windows 11
- RTX 3060 12 GB
- 48 GB RAM

Checkpoint quality is chosen independently of hardware.

## Active Base-BF16 asset set

- `models/diffusion_models/wan_animate_2_bf16.safetensors` ~32.8 GB
- `models/text_encoders/umt5_xxl_fp16.safetensors` ~11.4 GB
- `models/clip_vision/clip_vision_h.safetensors` ~1.26 GB
- `models/vae/Wan2_1_VAE_bf16.safetensors` ~0.254 GB

Do not keep Base INT8, Distilled BF16/INT8, LightX2V LoRA or UMT5 FP8 unless a later controlled comparison explicitly needs them.

## `bootstrap.ps1`

Prepares/restores `Z:\AI\WanAnimate2`, downloads the canonical BF16 set, official W0 inputs, copies `exilada_master.png`, writes `wan_bf16_route.json`, cleans superseded model variants and removes completed HF cache.

## `inspect.ps1`

Validates BF16 assets/native nodes and captures `object_info_wan_bf16.json`.

Runner 35 completed this successfully.

## `build_and_run_w0.py`

Builds the official W0 graph from live ComfyUI schema and runs official demo1 reference + raw official driver at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0.

### W0 attempt 1

Infrastructure failure: `hostbuf_file_reader_read failed` in `comfy_aimdo/host_buffer.py`.

### W0 attempt 2

Runner 36 relaunched ComfyUI with only `--disable-pinned-memory` changed. Result: **PASS**.

Canonical evidence:

- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\object_info_w0_live.json`

Inference took about 1896.94 s (~31m37s). Visual baseline showed substantial motion transfer and stable complete-character coherence, so the local raw-video Base-BF16 integration is accepted as `PASS_BASELINE`.

## `run_w1_from_w0_prompt.py`

Active W1 executor.

It loads the exact successful `w0_api_prompt.json` instead of rebuilding a new graph from guesses. It then changes the target appearance package only:

- official cat reference -> `exilada_master.png`;
- official cat-positive prompt -> canonical Exilada appearance/style description;
- output prefix -> W1.

The positive prompt must change with the reference because the W0 text literally describes the official cat character; leaving that text would create an invalid contradictory cross-identity test.

All motion/execution settings and the W0 negative prompt remain unchanged.

Outputs:

- `Z:\AI\WanAnimate2\w1_exilada_official_driver.mp4`
- `Z:\AI\WanAnimate2\w1_run_manifest.json`
- `Z:\AI\WanAnimate2\w1_api_prompt.json`

## Current operator runner

`tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

It restarts only the managed ComfyUI process, keeps the proven `--disable-pinned-memory` workaround and runs W1.

## W1 QA

Judge:

- Exilada identity and adult proportions;
- complete initial-state appearance;
- long black hair persistence/inertia;
- ragged cloth behavior;
- soft-body response;
- shackles/chains;
- motion adherence;
- topology;
- driver/cat leakage;
- preservation of discrete modern pixel/game-art language rather than smooth/painterly reinterpretation;
- zero routine manual repair.

## Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the earlier 384×576 / 17-frame INT8 experiment. Do not use them for current W0/W1.

## Cleanup discipline

Remove large model variants when they no longer belong to the active hypothesis. Preserve small manifests/logs/results. Do not delete the active Base-BF16 route after one poor W1 output; apply the exhaustion protocol first.