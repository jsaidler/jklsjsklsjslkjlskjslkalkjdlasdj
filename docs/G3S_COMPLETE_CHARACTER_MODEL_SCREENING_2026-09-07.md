# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN-ANIMATE-2 BASE BF16 W0 INFERENCE ACTIVE / SCAIL-2 NEXT OPEN LOCAL CANDIDATE**

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

A production candidate must:

- accept a complete reference image plus a separate driving video;
- consume richer motion information than a body skeleton;
- preserve the target character appearance as strongly as possible;
- infer locomotion/weight transfer automatically;
- infer body jiggle/soft response automatically;
- infer long-hair inertia/follow-through automatically;
- infer cloth deformation/lag/material response automatically;
- infer wind response where appropriate;
- keep shackles/chains/accessories attached and temporally coherent;
- require no routine manual keyframing, rigging, cloth simulation, hair bones, repainting, per-frame cleanup, hand compositing or manual mask repair;
- permit automatic preprocessing;
- output the whole visible character per frame for automatic spritesheet packing;
- remain recognizable as the approved Exilada/game-art language at gameplay scale.

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

A bad single run is `CONFIGURATION FAIL` or `INTEGRATION FAIL`, not automatic model death.

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

Repository Base config documents:

- `640×800`;
- `37` frames;
- `16 fps`;
- `20` steps;
- base seed `0`;
- Base BF16;
- flow/model sampling shift `5.0`;
- no CFG in the normal Base route.

The separate upstream Diffusers example demonstrates Base BF16 at `640×800` with 40 steps. The project W0 deliberately follows the repository-YAML/20-step route first rather than mixing both paths.

## W0 official inputs

Use upstream `examples/demo1/reference.png` and `examples/demo1/template.mp4`.

Do not begin W1 with Exilada until W0 establishes credible local motion transfer.

## Runner 35 preparation — PASS 2026-09-07

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Result: **PASS**.

Confirmed terminal markers:

- `WAN BF16 SCHEMA PREFLIGHT: PASS`
- `RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

Proof files:

- `Z:\AI\WanAnimate2\wan_bf16_route.json`
- `Z:\AI\WanAnimate2\object_info_wan_bf16.json`

This proves the canonical BF16 assets and installed native ComfyUI node contract are present. It does **not** prove model quality.

## Runner 36 — W0 OFFICIAL BF16 INFERENCE ACTIVE

Runner:

`tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Builder/executor:

`tools/wan-animate2-spike/build_and_run_w0.py`

The builder queries live `/object_info`, validates the exact installed node contract and creates the API graph dynamically. It uses the raw official driving-video frames directly in the native `WanAnimate2ToVideo` driving/`pose_video` branch and the first driving frame in the dedicated driving CLIP-vision branch. No DWPose/custom preprocessing is installed or inserted into this W0 graph.

Locked W0 inference settings:

- Base BF16 main model;
- UMT5 XXL FP16;
- CLIP Vision H;
- Wan VAE BF16;
- `640×800`;
- 37 frames;
- 16 fps;
- 20 steps;
- CFG `1.0` / no CFG;
- Euler;
- simple scheduler;
- shift `5.0`;
- seed `0`;
- driving/pose strength `1.0`;
- reference-image strength `1.0`.

Expected evidence:

- `Z:\AI\WanAnimate2\object_info_w0_live.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`

Only after visual W0 acceptance may W1 replace the reference with `exilada_master.png`.

## Wan exhaustion order

### W0 — official baseline

Official reference + official driver, Base BF16.

### W1 — Exilada cross-identity

Same known-good driver/settings; replace only reference with `exilada_master.png`.

### W2 — target walking driver

Clean full-body Internet walking clip.

### W3 — secondary-motion stress

Real footage with visible body bounce and non-rigid dynamics such as long hair, loose cloth or wind.

### W4 — finite variants only

Examples: Base vs Distilled, hardware-safe temporal/spatial execution changes, one justified quantization tier, documented viewpoint/reference controls.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Complete-character QA

Judge the whole sequence on:

1. Exilada identity/face/body proportions;
2. motion adherence and grounding;
3. hands/feet/limb topology;
4. hair mass persistence + inertia;
5. cloth topology + lag/folding;
6. body soft motion/jiggle where expected;
7. restraint/chain/accessory attachment and temporal behavior;
8. no leakage of driver identity/clothing/body shape;
9. camera/background compatibility with automatic spritesheet extraction;
10. game-art readability around `128 px` height;
11. automatic frame extraction/packing suitability;
12. zero routine manual cleanup.

## Cleanup discipline

Large local model files must correspond to an active test hypothesis. Do not keep duplicate quantizations or Distilled checkpoints in advance. Preserve small logs/manifests/result evidence. Keep the current Base BF16 workspace throughout Wan exhaustion unless explicitly abandoned. Retain the SSD workspace temporarily as comparison/fallback evidence until Wan passes W0 or SSD research is explicitly abandoned.