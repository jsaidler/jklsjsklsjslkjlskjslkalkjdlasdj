# Local Video Studio — Current Project State

Status date: **2026-09-15**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO.md`
3. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
4. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
5. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
6. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Active objective — LOCKED

Build a tool that lets the user write dialogue, choose a scenario and optionally specify appearance/framing, then generate a short realistic video of themselves speaking the new text with convincing identity, voice and natural movement, without recording a new performance.

Target program length: up to approximately one minute.

## H3 conclusion — LOCKED

The local MiniMax H3 path proved the architecture but did **not** reach the user's production-quality standard.

Canonical classification:

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

H3 proved:

- recognizable identity from still references;
- user-approved voice behavior;
- useful lip sync;
- autonomous motion without driving video;
- scene separation using cropped identity references;
- fully local execution.

It did not prove:

- production-grade spatial detail;
- production-grade hands/gestures/anatomy;
- production-grade temporal texture stability;
- a practical path to high-resolution finished output on the RTX 3060.

The user explicitly judged the effective visual resolution/detail as persistently poor. Turbo4 and Base20 did not justify continuing into Base50 or heavy upscaling as the next main strategy.

H3 remains preserved as evidence/baseline. Do not delete it yet.

## Current hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`

## Active renderer direction — Wan2.2-S2V-14B

The project has returned to the original modular plan that existed before the H3 detour.

Active next benchmark:

**Wan2.2-S2V-14B + separate voice stage.**

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

## Wan local preflight — COMPLETED 2026-09-15 17:14

Machine/runtime result:

- RTX 3060 12 GB detected;
- 47.7 GB RAM;
- FFmpeg available;
- `Z:\AI\WanAnimate2` exists;
- current Wan installation is **Animate-oriented**, not S2V-oriented.

Current Wan payload:

- `wan_animate_2_bf16.safetensors` — 30.54 GB;
- `umt5_xxl_fp16.safetensors` — 10.59 GB;
- `clip_vision_h.safetensors` — 1.18 GB;
- `Wan2_1_VAE_bf16.safetensors` — 0.24 GB.

Missing for native Wan2.2 S2V:

- S2V diffusion checkpoint;
- wav2vec2 audio encoder;
- CosyVoice components.

Important discovery: current ComfyUI template packages already contain the official native `video_wan2_2_14B_s2v.json` workflow.

## Download minimization — LOCKED FOR FIRST S2V TEST

Do **not** download the entire stock bundle blindly.

First benchmark will use:

- `wan2.2_s2v_14B_fp8_scaled.safetensors` (~16.4 GB) — download;
- `wav2vec2_large_english_fp16.safetensors` (~631 MB) — download;
- existing `umt5_xxl_fp16.safetensors` — reuse first;
- existing `Wan2_1_VAE_bf16.safetensors` — reuse first.

Only download the stock-template FP8 UMT5 / standard VAE if the local loaders reject the existing compatible components.

## CosyVoice status

CosyVoice remains the intended local text-to-speech / voice-cloning candidate, but it is intentionally deferred by one gate.

The first Wan benchmark will use an already-recorded João audio sample to isolate **video renderer quality**.

Reason: if Wan S2V itself is visually inadequate or impractically slow on the RTX 3060, there is no reason to spend another cycle installing and debugging the voice stage first.

## First Wan quality gate

Use approximately one native 77-frame S2V chunk:

- 16 fps;
- ~4.8 seconds;
- one high-quality João upper-body reference;
- real João speech audio;
- no long-form extension;
- no upscaler;
- no CosyVoice yet.

Judge:

1. effective detail/resolution;
2. identity stability;
3. glasses/eyes/beard/hair;
4. mouth/teeth/jaw;
5. hands/arms/shoulders;
6. skin/clothing texture stability;
7. naturalness of body performance;
8. AV sync;
9. runtime practicality.

If Wan S2V materially beats H3 and runtime is acceptable, then add CosyVoice and scene/look preparation.

## Secondary renderer benchmarks

If Wan S2V does not clear the quality/time bar:

1. HunyuanVideo-Avatar — quality comparison candidate;
2. EchoMimicV3-Flash — lower-compute fallback.

Do not switch engines randomly. Compare them against the same short-shot quality gate.

## Video Studio implementation direction

`tools/video-studio/` remains the orchestration prototype.

It should evolve toward a backend-adapter architecture:

- persistent profile assets;
- separate voice stage;
- optional scene/look still generation;
- interchangeable video renderer backend;
- evidence / timing / model manifests;
- FFmpeg assembly.

Do not resume one-minute workflow/UI polish until a single short shot is genuinely publishable.

## Immediate next action

Prepare the Wan S2V runtime without redundant downloads, verify native node support, download only the FP8 S2V checkpoint + wav2vec2 audio encoder, and prepare one ~4.8 s benchmark asset set.

Canonical procedure: `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`.
