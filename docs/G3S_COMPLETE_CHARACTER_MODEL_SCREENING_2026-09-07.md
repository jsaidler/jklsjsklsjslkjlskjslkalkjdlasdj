# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN-ANIMATE-2 BASE BF16 W0 ACTIVE / SCAIL-2 NEXT OPEN LOCAL CANDIDATE**

## Purpose

Select only model classes capable of generating the Exilada as a **complete animated character** from two distinct references:

1. `exilada_master.png` owns appearance/state;
2. an arbitrary real driving video owns movement/performance.

The driving performer does not need matching clothing, hair, body type or identity and may come from Internet video.

## Local workspace lock — 2026-09-07

Project repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model workspace root:

`Z:\AI`

Active Wan workspace:

`Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current tooling. The first BF16 W0 preparation attempt failed before installation because an old hard-code still referenced `D:\AI`. This is classified strictly as an **INFRASTRUCTURE/PATH FAIL** and carries no model-quality conclusion. Runner/bootstrap/inspect were corrected to use `Z:\AI\WanAnimate2`, with comfy-cli working directory derived from the configured workspace parent.

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
- require no manual keyframing, rigging, cloth simulation, hair bones, repainting, per-frame cleanup, hand compositing or manual mask repair;
- permit automatic preprocessing such as crop/resize/segmentation/background removal;
- output the whole visible character per frame for automatic spritesheet packing;
- remain recognizable as the approved Exilada/game-art language at gameplay scale.

## Pose-only methods

Body-pose-only conditioning is not a valid final production foundation under this contract because it discards exactly the non-rigid motion classes now required.

This includes Moore/AnimateAnyone pose-only and the current Moore + released SSD-UNet compatibility reconstruction. They remain research evidence, not final complete-motion candidates.

Exact public SSD remains independently `BLOCKED` by the absent custom SSD pose-guider checkpoint.

## Candidate ranking

### 1 — Wan-Animate-2 / Wan2.2-Animate-2-14B

**Class:** reference image + direct raw driving video.

**Architectural fit:** YES.

Wan-Animate-2 directly consumes the driving video in its animation transformer and therefore belongs to the correct information class for body + non-rigid dynamics.

The old 2026-09-04 project run used a constrained Base INT8/FP8 setup at approximately `384×576`, 17 frames and seed 42. It produced recognizable Exilada identity but weak movement transfer and a painted/smoothed visual result. That remains a configuration-level negative result, not model-family exhaustion.

### 2 — SCAIL-2

**Class:** end-to-end raw driving video + reference image.

**Architectural fit:** YES.

Strongest next open/local candidate if Wan reaches a documented `EXHAUSTED_FAIL`. Do not install while Wan is active.

### 3 — DreamActor-M2

Architecturally excellent pose-free RGB-driving approach, but no current public self-hostable production route confirmed. Benchmark only.

### 4 — Kling Motion Control

Architecturally relevant hosted comparator. Not a current local dependency.

## Model Exhaustion Protocol — LOCKED

A candidate reaches `EXHAUSTED_FAIL` only after a finite controlled sequence:

1. reproduce official/reference baseline in the selected local integration;
2. keep known-good driver/settings and replace only reference with Exilada;
3. test target Internet walking footage;
4. test secondary-motion footage with body bounce/hair/cloth/wind;
5. test only finite high-leverage implementation variants tied to explicit hypotheses;
6. no manual rescue;
7. no seed fishing.

A bad single run is `CONFIGURATION FAIL` or `INTEGRATION FAIL`, not automatic model death.

## W0 checkpoint-quality decision — LOCKED 2026-09-07

The RTX 3060 12 GB does **not** choose the checkpoint.

The canonical W0 model is the highest-quality available Base BF16 checkpoint. Memory concessions happen later in execution, one controlled variable at a time.

Canonical ComfyUI W0 asset set:

- `diffusion_models/wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `text_encoders/umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `clip_vision/clip_vision_h.safetensors` — ~1.26 GB;
- `vae/Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total: approximately **45.7 GB**.

Excluded from W0:

- Base INT8 ConvRot;
- Distilled BF16;
- Distilled INT8 ConvRot;
- LightX2V distillation LoRA;
- UMT5 FP8.

These excluded files are removed from the isolated Wan workspace if found. They may be downloaded later only if W4 explicitly reaches the corresponding controlled comparison.

## Upstream W0 semantics

Repository Base config documents:

- `640×800`;
- `37` frames;
- `16 fps`;
- `20` steps;
- base seed `0`;
- Base BF16.

The upstream Diffusers example separately demonstrates Base BF16 at `640×800` with 40 inference steps. W0 will record which exact documented path is being reproduced rather than mixing settings between paths.

## W0 official inputs

Use upstream `examples/demo1`:

- `reference.png`;
- `template.mp4`.

Do not begin W1 with Exilada until W0 establishes credible local motion transfer.

## Runner 35 preparation — ACTIVE

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Runner 35:

1. requires 70 GB free-space headroom on `Z:`;
2. rebuilds/restores isolated `Z:\AI\WanAnimate2`;
3. cleans superseded Wan INT8/Distilled/LoRA/FP8 assets;
4. downloads only the canonical ~45.7 GB W0 set;
5. downloads official demo1 inputs;
6. copies Exilada master for later W1;
7. removes completed Hugging Face/Xet cache;
8. captures exact fresh ComfyUI node schemas;
9. stops before inference.

This schema-first stop is intentional. The W0 workflow must be generated against the actual installed `WanAnimate2ToVideo` contract, not guessed from a stale template.

## Wan exhaustion order after Runner 35

### W0 — official baseline

Official reference + official driver, Base BF16, as close as practical to one documented upstream inference path.

### W1 — Exilada cross-identity

Same known-good driver/settings; replace only reference with `exilada_master.png`.

### W2 — target walking driver

Clean full-body Internet walking clip. No costume match required.

### W3 — secondary-motion stress

Real footage with visible body bounce and non-rigid dynamics such as long hair, loose cloth or wind.

### W4 — finite variants only

Examples:

- Base vs Distilled;
- official window vs smallest hardware-safe window;
- one justified quantization tier;
- documented viewpoint/reference controls;
- text correction only when tied to a known condition.

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
9. camera/background compatible with automatic spritesheet extraction;
10. game-art readability around `128 px` height;
11. automatic frame extraction/packing suitability;
12. zero manual cleanup.

## Cleanup discipline

Large local model files must correspond to an active test hypothesis.

- Do not keep duplicate quantizations or Distilled checkpoints in advance.
- Remove superseded model-specific material when it is no longer needed.
- Preserve small logs/manifests/result evidence.
- Keep the current Base BF16 workspace throughout Wan exhaustion unless explicitly abandoned.
- Keep the existing SSD workspace temporarily as comparison/fallback evidence until Wan passes W0 or SSD research is explicitly abandoned; do not repeat the earlier premature cleanup mistake.
