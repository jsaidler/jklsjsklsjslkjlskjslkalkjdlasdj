# Local Video Studio — Current Project State

Status date: **2026-09-15**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
3. `docs/VIDEO_STUDIO.md`
4. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
5. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
6. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
7. `docs/VIDEO_STUDIO_GAME_PAYLOAD_CLEANUP_2026-09-15.md`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Active objective — LOCKED

Build a tool that lets João write dialogue, choose a scenario and optionally specify appearance/framing, then generate a realistic video of himself speaking the new text with convincing identity, voice and natural movement, without recording a new performance.

Target program length: up to approximately one minute, eventually assembled from short shots.

**The only active product focus is João's video production.** Game/sprite/character-runtime work is historical only.

## Cleanup policy — LOCKED

Retired Roguelite material must not consume active local AI storage or clutter the current `main` working tree.

Game-only AI roots classified for deletion:

- `Z:\AI\RogueliteAssetStudio`
- `Z:\AI\SpriteSheetDiffusionSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\QwenImageEditSpike`
- `Z:\AI\Flux2RefControlSpike`

Protected video/reusable roots:

- `Z:\AI\WanAnimate2`
- `Z:\AI\MiniMaxH3`
- `Z:\AI\QwenImageEdit`
- `Z:\AI\Flux2Klein`
- `Z:\AI\FluxKontext`
- `Z:\AI\VideoStudioRuns`

Old game material remains recoverable from Git history; Git history is not rewritten.

## Current hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`

## H3 conclusion — LOCKED

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

H3 proved the architecture but failed the user's production-quality bar, especially effective detail/resolution, anatomy/hands, texture stability, and generic presenter-like visual behavior. Do not resume H3 Base50 / SeedVR2 as the main strategy without new evidence.

## Active renderer direction — Wan2.2-S2V-14B

Target architecture:

```text
written text + target scene + optional appearance
        |
        +--> voice synthesis / cloning (CosyVoice candidate)
        |
        +--> high-quality identity / scene still preparation
        |
        v
Wan2.2-S2V-14B
        |
        v
short validated shot
        |
        v
multi-shot assembly only after quality pass
```

Do not require one monolithic model to solve identity, voice generation, scene generation, body performance and final resolution simultaneously.

## Wan S2V preparation — COMPLETED

Installed/verified:

- `wan2.2_s2v_14B_fp8_scaled.safetensors` (~16.4 GB);
- `wav2vec2_large_english_fp16.safetensors` (~631 MB).

Reused:

- `umt5_xxl_fp16.safetensors`;
- `Wan2_1_VAE_bf16.safetensors`.

Native S2V nodes are present. Benchmark reference image/audio and pinned official template are prepared under `Z:\AI\WanAnimate2`.

CosyVoice remains intentionally deferred until the renderer clears the visual-quality gate.

## First Wan result — COMPLETED / REVIEWED 2026-09-15

First result used:

- Wan2.2 S2V 14B FP8 scaled;
- 480x832 vertical;
- intended 77-frame single chunk at 16 fps;
- 10 steps;
- CFG 6;
- `uni_pc` / `simple`;
- shift 8;
- seed 0;
- real recorded João speech audio;
- no upscaler;
- no CosyVoice.

Uploaded viewing copy metadata:

- 480x832;
- 16 fps;
- 4.5 s;
- 72 encoded video frames.

The 72-frame MP4 was caused by the old runner using FFmpeg `-shortest` against 4.5 s audio. Runner v2 pads audio to the full generated-frame duration and no longer truncates the generated sequence.

### Visual result

Canonical classification:

**WAN S2V 10-STEP FP8: STRUCTURALLY PROMISING / PRODUCTION QUALITY FAIL / QUALITY GATE STILL OPEN.**

Promising relative to H3:

- stable body topology/shoulders;
- substantially better hand behavior;
- asymmetric, more natural conversational gesture pattern;
- stable background;
- stable clothing;
- stable framing/camera;
- face broadly coherent after the opening transient.

Still failing production quality:

- insufficient effective detail at 480x832;
- opening-frame transient;
- subtle eyeglass geometry/reflection drift;
- beard/hairline/facial texture crawl;
- mouth/teeth/jaw softness/synthetic deformation in some positions;
- moving-hand detail loss;
- diffusion-style skin smoothing/temporal texture instability.

AV sync requires playback review and is not automatically promoted to PASS from frame inspection.

## Critical sampling correction — LOCKED

The earlier project state incorrectly treated 10 steps as the documented non-Lightning quality path. That claim is retired.

Current ComfyUI Wan2.2-S2V documentation states:

- with 4-step Lightning LoRA: 4 steps / CFG 1;
- without Lightning LoRA: **20 steps / CFG 6**;
- Lightning significantly reduces generation time but also causes significant dynamic/quality loss;
- if quality is insufficient, use the original 20-step workflow.

Therefore the completed 10-step render was **under-sampled relative to the documented ComfyUI non-Lightning quality baseline**.

Canonical runner v2 now exposes `-Steps` and defaults to 20.

## Native resolution headroom

Wan2.2 S2V-14B officially supports **480P and 720P**. Wan therefore has a native higher-resolution path that H3 local did not give us.

Do not launch 720p blindly on RTX 3060 12 GB. First determine whether a proper 20-step 480x832 run gives enough quality gain to justify the increased cost.

## Immediate decision gate

Before another GPU-heavy inference, recover `elapsed_seconds` from the completed 10-step run's `manifest.json`.

Decision rule:

- if 10-step runtime was reasonably short, run a controlled **20-step** A/B with the same seed/reference/audio/resolution;
- if 10-step was already close to an hour or otherwise impractical, do not blindly double local inference time; proceed to another renderer comparison;
- only if 20-step materially improves quality and remains practical should 720p be tested;
- do not download BF16 automatically; FP8 remains the 12 GB VRAM path unless evidence justifies the much heavier BF16 route.

## Secondary renderer benchmarks

If Wan S2V does not clear the quality/time bar:

1. HunyuanVideo-Avatar — quality comparison candidate;
2. EchoMimicV3-Flash — lower-compute fallback.

Do not switch engines randomly. Compare against the same short-shot quality gate.

## Video Studio implementation direction

`tools/video-studio/` remains the orchestration prototype and should evolve toward:

- persistent identity/profile assets;
- separate voice stage;
- optional scene/look still generation;
- interchangeable renderer backend;
- run manifests/evidence/timing;
- final assembly.

Do not resume one-minute workflow/UI polish until a single short shot is genuinely publishable.

## Immediate next action

Inspect the completed Wan run's manifest for actual inference time. Do not start a 20-step or 720p render until that cost is known.

Canonical procedure: `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`.