# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 CURRENT PREFERRED VISUAL-MOTION BASELINE / W1A 1.5 NOT PREFERRED / W1F SAFE FRAMING ACTIVE.**

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

## W0

`build_and_run_w0.py` + Runner 36 reproduced the official Base-BF16 demo path at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0.

First attempt failed in AIMDO host-buffer streaming. Relaunching with only `--disable-pinned-memory` fixed the infrastructure issue. W0 is accepted as `PASS_BASELINE`.

## W1

`run_w1_from_w0_prompt.py` + Runner 37 used the exact successful W0 graph but changed the target package to Exilada.

Observed positives:

- substantial cross-identity raw-video motion transfer;
- no cat/costume leakage;
- long hair visibly moves as a non-rigid mass;
- ragged hip cloth changes drape;
- coarse Exilada package survives.

Technical issues:

- wrist restraint/chain largely lost;
- ankle chain unstable;
- some hand/foot blur/stretch and transient artifacting;
- later crop inherited from driver framing.

### Visual direction note

The W1 painterly illustrated look was explicitly approved by the user as the preferred whole-game visual direction. Smooth/painterly rendering is therefore **not** a failure by itself anymore. Localized/restrained motion blur may be aesthetically positive.

The preferred art direction now includes an explicit 1980s sword-and-sorcery charge. See `docs/VISUAL_DIRECTION.md`.

## W1A — `reference_image_strength=1.5`

`run_w1a_reference_strength.py` + Runner 38 changed exactly one variable from W1: reference strength 1.0 -> 1.5.

Uploaded result:

- `INFERENCE_COMPLETE`;
- elapsed 1912.32 s;
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Direct comparison against W1:

- no material identity/clothing/restraint gain;
- more blur/ghosting in several phases;
- weaker limb definition in those phases;
- crop unchanged;
- no better overall tradeoff.

Conclusion: **reference strength 1.5 is not preferred. Return to W1 reference strength 1.0.**

## `run_w1f_safe_framing.py` — CURRENT

W1F safe-framing executor.

It loads the exact W1 prompt and changes only the raw-driver framing:

1. read the original official driver;
2. estimate a fixed pad colour from source-frame corners;
3. preserve the whole original frame;
4. fit it inside a fixed centered 80% safe box on a `640×800` canvas;
5. write a new deterministic safe-framed driver;
6. replace only the `LoadVideo` path in the W1 prompt;
7. keep reference strength 1.0 and every Wan/sampler/seed/model setting unchanged;
8. run inference and emit driver/run manifests.

No destructive crop, no temporal tracking/camera breathing, no manual alignment.

Expected evidence:

- `Z:\AI\WanAnimate2\w1f_exilada_safe_framing80.mp4`
- `Z:\AI\WanAnimate2\w1f_run_manifest.json`
- `Z:\AI\WanAnimate2\w1f_api_prompt.json`
- `Z:\AI\WanAnimate2\w1f_safe_driver_manifest.json`

## Current operator runner

`tools/structured-2d-character-pipeline/39_run_wan_animate2_bf16_w1f_safe_framing80.ps1`

It restarts only the managed ComfyUI process, keeps `--disable-pinned-memory`, prepares the safe-framed raw driver and runs W1F.

Success criterion: full head/hair/body stay safely inside generated frame without unacceptable shrinkage, motion weakening or new topology drift.

## After W1F

- lock framing policy;
- run separate 1980s/torn-clothing/body-exposure prompt test;
- W2 Internet walking driver;
- W3 secondary-motion stress driver;
- W4 finite variants only if justified.

## Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the earlier 384×576 / 17-frame INT8 experiment. Do not use them for current W0/W1/W1A/W1F.

## Cleanup discipline

Remove large model variants when they no longer belong to the active hypothesis. Preserve small manifests/logs/results. Do not delete the active Base-BF16 route while Wan is under exhaustion.
