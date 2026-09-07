# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN-ANIMATE-2 BASE BF16 W0 RETRY ACTIVE / SCAIL-2 NEXT OPEN LOCAL CANDIDATE**

## Purpose

Select only model classes capable of generating the Exilada as a **complete animated character** from two distinct references:

1. `exilada_master.png` owns appearance/state;
2. an arbitrary real driving video owns movement/performance.

The driving performer does not need matching clothing, hair, body type or identity and may come from Internet video.

## Local workspace lock — 2026-09-07

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model workspace root: `Z:\AI`

Active Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical. The first BF16 preparation attempt failed before installation because of an old hard-code; that was an **INFRASTRUCTURE/PATH FAIL** only and was fixed in current tooling.

## Hard production contract — LOCKED

A production candidate must accept a complete reference image plus a separate driving video, consume richer motion information than a body skeleton, preserve target appearance strongly, automatically infer locomotion/weight transfer, jiggle/soft response, long-hair inertia, cloth/material/wind response and restraint/accessory behavior, and require no routine manual animation cleanup or repair.

Automatic preprocessing is allowed. Runtime output remains complete precomposed character frames suitable for automatic spritesheet packing.

## Pose-only methods

Body-pose-only conditioning is not a valid final production foundation under this contract. Moore/AnimateAnyone and the released SSD-UNet compatibility reconstruction remain research evidence only. Exact public SSD remains independently `BLOCKED` by the absent custom SSD pose-guider checkpoint.

## Candidate ranking

### 1 — Wan-Animate-2 / Wan2.2-Animate-2-14B

**Class:** reference image + direct driving video.

**Architectural fit:** YES — pending visual proof.

The old 2026-09-04 project run used constrained Base INT8/FP8 at approximately `384×576`, 17 frames and seed 42. It produced recognizable Exilada identity but weak movement transfer and a painted/smoothed visual result. That is a configuration-level negative result, not model-family exhaustion.

### 2 — SCAIL-2

**Class:** end-to-end driving video + reference image.

**Architectural fit:** YES.

Strongest next open/local candidate if Wan reaches a documented `EXHAUSTED_FAIL`. Do not install while Wan is active.

### 3 — DreamActor-M2

Architecturally relevant benchmark; no current public self-hostable production route confirmed.

### 4 — Kling Motion Control

Hosted comparator only.

## Model Exhaustion Protocol — LOCKED

A candidate reaches `EXHAUSTED_FAIL` only after a finite controlled sequence:

1. reproduce official/reference baseline;
2. keep known-good driver/settings and replace only reference with Exilada;
3. test target Internet walking footage;
4. test secondary-motion footage with body bounce/hair/cloth/wind;
5. test only finite high-leverage implementation variants tied to explicit hypotheses;
6. no manual rescue;
7. no seed fishing.

A runtime/loader failure is `INFRASTRUCTURE FAIL`, not evidence about model quality.

## W0 checkpoint-quality decision — LOCKED 2026-09-07

Canonical ComfyUI W0 asset set:

- `diffusion_models/wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `text_encoders/umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `clip_vision/clip_vision_h.safetensors` — ~1.26 GB;
- `vae/Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total: approximately **45.7 GB**.

Excluded from W0: Base INT8 ConvRot, Distilled BF16/INT8, LightX2V distillation LoRA and UMT5 FP8.

If the exact BF16 set cannot execute on 12 GB VRAM + 48 GB RAM, reduce execution one controlled variable at a time rather than silently lowering checkpoint precision.

## Upstream W0 semantics

Repository Base config documents `640×800`, 37 frames, 16 fps, 20 steps, seed `0`, Base BF16, flow/model shift `5.0` and no CFG in the normal Base route.

W0 uses upstream `examples/demo1/reference.png` and `examples/demo1/template.mp4`.

## Runner 35 preparation — PASS 2026-09-07

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Result: **PASS**. Canonical BF16 assets and native ComfyUI schemas are present.

## Runner 36 — W0 OFFICIAL BF16 INFERENCE

Runner: `tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Builder/executor: `tools/wan-animate2-spike/build_and_run_w0.py`

The graph and all model/inference settings remain locked at the official W0 values.

### Attempt 1 — INFRASTRUCTURE FAIL

Observed failure after approximately 74 seconds:

`RuntimeError: hostbuf_file_reader_read failed`

Location: `comfy_aimdo/host_buffer.py`, during ComfyUI host-buffer/dynamic weight streaming.

This is **not** a visual/model failure and does not count against Wan exhaustion. It happened before meaningful denoising/output evaluation.

Current ComfyUI exposes `--disable-pinned-memory`, and contemporary ComfyUI/Wan reports document this same host-buffer failure being resolved by disabling pinned memory while keeping the workflow unchanged.

### Attempt 2 — ACTIVE

Change exactly one variable: launch ComfyUI with:

`--disable-pinned-memory`

Unchanged:

- Base BF16;
- UMT5 FP16;
- CLIP Vision H;
- VAE BF16;
- official reference/driver;
- `640×800`;
- 37 frames;
- 20 steps;
- seed 0;
- Euler/simple;
- shift 5.0;
- all conditioning strengths.

The runner restarts only its own managed ComfyUI server so the new launch flag is definitely applied.

Do not disable Dynamic VRAM, reduce resolution/frame count or quantize unless this narrower retry fails. Those would be subsequent one-variable tests.

## Wan exhaustion order

- W0 official baseline;
- W1 Exilada cross-identity;
- W2 target walking driver;
- W3 secondary-motion stress;
- W4 finite high-leverage variants only.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Complete-character QA

Judge identity/body proportions, motion adherence, hands/feet topology, hair persistence/inertia, cloth lag/folding, body soft motion, restraint/accessory temporal coherence, driver leakage, camera/background extraction suitability, ~128 px game readability, automatic packing suitability and zero routine manual cleanup.

## Cleanup discipline

Large local model files must correspond to an active test hypothesis. Do not keep duplicate quantizations or Distilled checkpoints in advance. Preserve small logs/manifests/result evidence. Keep the current Base BF16 workspace throughout Wan exhaustion unless explicitly abandoned. Retain the SSD workspace temporarily as comparison/fallback evidence until Wan passes W0 or SSD research is explicitly abandoned.