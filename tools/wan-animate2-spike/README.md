# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE AGAIN FOR A CONTROLLED BASE-BF16 MODEL-EXHAUSTION PASS.**

The historical 2026-09-04 Base INT8 run remains valid negative evidence for that constrained configuration, but it no longer counts as a model-family rejection. The current project gate deliberately rebuilds Wan-Animate-2 around the highest-quality Base BF16 checkpoint before making another verdict.

## Hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB RAM

The GPU is **not** used to choose the checkpoint. The canonical checkpoint is Base BF16 even if execution later requires aggressive offload or reduced spatial/temporal settings. Those execution concessions must be isolated one at a time.

## Canonical BF16 W0 asset set

Only these model files belong to the reference-quality W0 route:

- `models/diffusion_models/wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `models/text_encoders/umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `models/clip_vision/clip_vision_h.safetensors` — ~1.26 GB;
- `models/vae/Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total payload is about **45.7 GB**, excluding ComfyUI/runtime/temp files.

The following are deliberately **not** retained in the active W0 workspace:

- Base INT8 ConvRot;
- Distilled BF16;
- Distilled INT8 ConvRot;
- LightX2V distillation LoRA;
- UMT5 FP8.

If they are found in the isolated Wan workspace, `bootstrap.ps1` removes them before the BF16 download. Git history preserves the old experiment; local disk does not need duplicate 16–33 GB checkpoints.

## Official W0 inputs

The bootstrap downloads the current upstream `examples/demo1` assets:

- `reference.png`;
- `template.mp4`.

They are stored under:

`ComfyUI/input/wan_animate2_w0/`

W0 exists only to prove the fresh local integration before testing Exilada.

## Upstream Base reference semantics

The upstream repository config declares approximately:

- Base BF16;
- `640×800`;
- `37` frames;
- `16 fps`;
- `20` steps in the repository YAML;
- base seed `0`.

The upstream Diffusers example also uses `640×800` and 40 inference steps. We will record the exact inference path used in each W0 attempt rather than mixing those two documented paths.

## Scripts

### `bootstrap.ps1`

Active. Rebuilds the isolated `D:\AI\WanAnimate2` ComfyUI workspace if needed, enforces a free-space preflight, deletes superseded Wan-specific weights/materials, downloads only the canonical BF16 W0 asset set, downloads the official demo inputs, copies `exilada_master.png`, writes `wan_bf16_route.json`, and removes the completed Hugging Face download cache.

### `inspect.ps1`

Active. Starts the fresh ComfyUI headlessly, validates the BF16 files/native Wan node classes, proves superseded Wan weights are absent, and stores the exact installed node schemas in:

`D:\AI\WanAnimate2\object_info_wan_bf16.json`

No W0 workflow is authored until this schema exists. This prevents guessing cache/widget semantics across ComfyUI versions.

### Historical scripts

`make_driver.ps1`, `build_workflow.py`, and `run_spike.ps1` document the old 384×576 / 17-frame INT8 experiment. Do **not** use them for the BF16 W0 gate.

## Current operator entry point

Use:

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Runner 35 performs setup + cleanup + download + schema preflight and intentionally stops before inference.

## Cleanup discipline

- Remove model variants and generated material only when they are no longer part of a current diagnostic hypothesis.
- Do not retain duplicate quantizations/Distilled checkpoints “just in case”; download them later only if W4 explicitly calls for that controlled comparison.
- Preserve small manifests/logs/results as evidence.
- Do not delete the current Base BF16 route after one bad output; apply the model-exhaustion protocol first.
