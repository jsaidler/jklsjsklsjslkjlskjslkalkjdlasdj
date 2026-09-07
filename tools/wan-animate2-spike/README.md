# Wan-Animate-2 validation spike — CLI only

Status: **HISTORICAL / REJECTED FOR PRODUCTION / WORKSPACE CLEANED UP.**

This directory preserves reproducible research tooling only. It must **not** be treated as the current Roguelite animation route and must not imply that a local Wan workspace still exists.

## Historical hardware / tested route

The 2026-09-04 validation ran on:

- Windows 11;
- NVIDIA RTX 3060 12 GB;
- 48 GB RAM.

The tested model route was:

- official Wan-Animate-2 Base INT8 ConvRot;
- `wan_animate_2_int8_convrot.safetensors`;
- native ComfyUI `WanAnimate2ToVideo` support;
- FP8 UMT5 text encoder;
- CLIP Vision H;
- Wan 2.1 VAE;
- no LightX2V/distillation LoRA;
- 384×576;
- 17 frames;
- seed 42;
- Euler;
- 20 steps;
- CPU model cache.

The generation completed and produced evaluable output.

## Production rejection

The Exilada spike was rejected for two decisive reasons:

1. **Driving-motion transfer was too weak.** The driver visibly walked while the generated Exilada remained largely planted with only modest weight/limb change.
2. **The required modern-pixel-art/game-art language was not preserved.** Output read as smooth painted/video-diffusion imagery rather than deliberate discrete pixel art.

Identity and coarse anatomy were comparatively stable, but that did not compensate for the motion/style failures.

Result: **Wan-Animate-2 Base INT8 is CLOSED as the production animation foundation.**

Do not rescue or silently revive this exact route through:

- seed fishing;
- CFG/step cosmetics;
- stronger reference strength;
- prompt-only changes;
- a synthetic richer driving video;
- post-generation pixel filters;
- manual frame-by-frame repair.

A future Wan-family revisit would require a **materially different checkpoint/integration/model behavior** with evidence that both locomotor adherence and native/discrete game-art preservation are solved.

## Workspace cleanup

The isolated local Wan runtime/model workspace used for this rejected experiment was deleted after rejection.

Therefore:

- do not assume `D:\AI\WanAnimate2` exists;
- do not instruct the operator to run `inspect.ps1`/`run_spike.ps1` against that path without an explicit new installation gate;
- do not treat missing Wan weights as an infrastructure regression — the deletion was intentional cleanup of a rejected route.

## Historical scripts

The scripts in this directory remain only so the prior experiment is auditable:

- `bootstrap.ps1`
- `make_driver.ps1`
- `inspect.ps1`
- `build_workflow.py`
- `run_spike.ps1`

They are **research history**, not current operator actions.

## Rejection record

Historical rejection commit:

`402dc4a3c4684312af33bbc00f903bad7b708a58` — `record Wan Animate 2 spike rejection`

Post-Wan research commit:

`2277777c91bdd553ef7d9ee882c378226e36f842` — `Document post-Wan pixel-native animation research`
