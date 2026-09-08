# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 PAINTERLY LOOK APPROVED / W1A 1.5 RETAINED AS STRONGER STRUCTURAL BRANCH / W1F WHOLE-FRAME SAFE FRAMING FAILED / W1G TRACKED SUBJECT FRAMING ACTIVE.**

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
- coarse Exilada package survives;
- painterly illustrated result explicitly approved as the preferred visual direction.

Technical issues:

- wrist restraint/chain largely lost;
- ankle chain unstable;
- some hand/foot blur/stretch and transient artifacting;
- later crop inherited from driver framing.

## W1A — `reference_image_strength=1.5`

`run_w1a_reference_strength.py` + Runner 38 changed exactly one variable from W1: reference strength 1.0 -> 1.5.

Uploaded result:

- `INFERENCE_COMPLETE`;
- elapsed 1912.32 s;
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Revised interpretation after user review:

- 1.5 preserves body structure/topology better;
- 1.0 is cleaner in some phases;
- 1.5 has more destructive blur/ghosting;
- retain **1.5 as the structural branch** and solve blur separately.

## `run_w1f_safe_framing.py` — COMPLETE / CROP FAIL

Runner 39 retry completed validly after OpenCV preflight was added.

The complete `480×854` source frame was placed at `360×640` inside `640×800`, offset `(140,80)`, with no source crop and no camera breathing.

Visual verdict: **crop remained**. Head/hair still leave the top later and the character still pushes right.

Conclusion: whole-frame letterbox margins do not map to equivalent Wan output margins. Do not iterate simple 70%/60%/50% letterbox-only variants.

## `run_w1g_subject_framing_ref15.py` — CURRENT

Runner:

`tools/structured-2d-character-pipeline/40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1`

Parent = exact W1A prompt, so reference strength stays 1.5.

### W1G v1 — PRE-INFERENCE FAIL

The initial implementation used a single temporal-activity union over the first 37 source frames. It aborted before inference with:

`automatic subject bbox covers almost the whole source frame (1.000)`

Classification: preprocessor/integration fail; no Wan inference.

The safety guard worked. The global activity-union assumption is closed for this clip.

### W1G v2 — ACTIVE

The executor now:

1. runs OpenCV built-in HOG person detection per frame;
2. selects a temporally coherent performer box;
3. interpolates missing boxes;
4. expands for head/hair/hands/feet safety;
5. smooths translation only;
6. keeps one constant scale for all frames, so there is no zoom/camera breathing;
7. targets envelope-height ratio 0.48, center x 300, bottom y 620 on 640×800;
8. preflights minimum canvas margins and CLIP center-square margins;
9. aborts before Wan if person detection or margins are insufficient;
10. downloads no new detector checkpoint/model.

Everything else remains exact W1A: Exilada reference/prompt, BF16 stack, 37 frames, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.5, negative prompt and `--disable-pinned-memory`.

Expected evidence after a valid run:

- `Z:\AI\WanAnimate2\w1g_exilada_subject_framed_ref15.mp4`
- `Z:\AI\WanAnimate2\w1g_run_manifest.json`
- `Z:\AI\WanAnimate2\w1g_api_prompt.json`
- `Z:\AI\WanAnimate2\w1g_subject_driver_manifest.json`

If framing passes while structure survives, the next isolated axis is destructive-blur reduction.

## Current operator runner

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1"
```

## Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the earlier 384×576 / 17-frame INT8 experiment. Do not use them for the current BF16 route.

## Cleanup discipline

Remove large model variants when they no longer belong to the active hypothesis. Preserve small manifests/logs/results. Do not delete the active Base-BF16 route while Wan is under exhaustion.
