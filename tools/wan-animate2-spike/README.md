# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 COMPLETE WITH APPEARANCE CONFIGURATION FAIL / W1A REFERENCE-STRENGTH 1.5 ACTIVE.**

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

W0 attempt 1 failed in AIMDO host-buffer streaming. Runner 36 relaunched with only `--disable-pinned-memory`; attempt 2 completed and is accepted as `PASS_BASELINE`.

## `run_w1_from_w0_prompt.py`

Completed W1 executor.

It loaded the exact successful `w0_api_prompt.json`, then changed only the target appearance package:

- official cat reference -> `exilada_master.png`;
- official cat-positive prompt -> canonical Exilada appearance/style description;
- output prefix -> W1.

All motion/execution settings and the W0 negative prompt stayed fixed.

Observed W1:

- `INFERENCE_COMPLETE`;
- elapsed 1746.69 s (~29m07s);
- reference strength 1.0 / pose strength 1.0;
- substantial cross-identity motion transfer;
- no cat/costume leakage;
- long hair visibly moves non-rigidly;
- ragged hip cloth changes drape;
- coarse Exilada package survives;
- smooth/painterly output instead of required pixel/game-art;
- face/body detail drift;
- wrist restraint/chain largely lost and ankle chain unstable;
- some hand/foot blur/stretch and a transient detached artifact.

Classification: **production-appearance CONFIGURATION FAIL, not Wan model failure.**

## Native `reference_image_strength`

Current native ComfyUI `WanAnimate2ToVideo` exposes `reference_image_strength`, default 1.0, and documents values above 1.0 as tighter reference/appearance adherence. `pose_strength` remains separate.

This is the next controlled variable because it targets the exact W1 failure without changing driver/model/seed/sampler.

## `run_w1a_reference_strength.py`

Active W1A executor.

It loads the exact completed `w1_api_prompt.json` and changes only:

`reference_image_strength: 1.0 -> 1.5`

Outputs:

- `Z:\AI\WanAnimate2\w1a_exilada_refstrength15.mp4`
- `Z:\AI\WanAnimate2\w1a_run_manifest.json`
- `Z:\AI\WanAnimate2\w1a_api_prompt.json`

## Current operator runner

`tools/structured-2d-character-pipeline/38_run_wan_animate2_bf16_w1a_refstrength15.ps1`

It restarts only the managed ComfyUI process, keeps the proven `--disable-pinned-memory` workaround and runs W1A.

Everything except reference strength remains exact W1: Exilada reference/prompt, official driver, Base BF16 stack, `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0 and negative prompt.

## W1A QA

Compare directly against W1 on:

- identity/body/face fidelity;
- pixel/game-art preservation;
- long-hair mass and clothing layout persistence;
- shackles/chains/accessories;
- topology/artifacts;
- motion adherence loss, if any.

## Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the earlier 384×576 / 17-frame INT8 experiment. Do not use them for current W0/W1/W1A.

## Cleanup discipline

Remove large model variants when they no longer belong to the active hypothesis. Preserve small manifests/logs/results. Do not delete the active Base-BF16 route while Wan is under exhaustion.