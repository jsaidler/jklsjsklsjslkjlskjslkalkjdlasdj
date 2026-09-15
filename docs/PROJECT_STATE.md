# Local Video Studio — Current Project State

Status date: **2026-09-15**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO.md`
3. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
4. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
5. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Active objective — LOCKED

Build a tool that lets the user write dialogue, choose a scenario and optionally specify appearance/framing, then generate a short realistic video of themselves speaking the new text with convincing identity, voice and natural movement, without recording a new performance.

Target program length: up to approximately one minute.

## Critical direction reset — 2026-09-15

The local MiniMax H3 path proved the architecture but did **not** reach the user's production-quality standard.

Canonical classification:

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

The user specifically identified the effective visual resolution as persistently poor. The Turbo4 and Base20 comparison did not justify continuing to spend hours on progressively slower local inference and post-upscaling.

Therefore the following are paused:

- Base50 as an automatic next step;
- SeedVR2 or other heavy temporal upscaling as the presumed solution;
- further local H3 sampler-chasing;
- productizing the current H3 output as if it were nearly production-ready.

The problem is architectural: the currently open/local H3-Base path is fundamentally a 768p-class base renderer, while MiniMax's official H3-Regenerate-2K stage is not currently open-sourced for local use. Conventional upscaling cannot be assumed to recover the missing generative detail.

## Constraint correction — QUALITY OVERRIDES LOCAL-ONLY

The old `local-first` rule is retired as a hard constraint for the final renderer.

New rule:

> Keep orchestration, assets, references, prompts, manifests and optional preprocessing local where useful, but allow a hosted/cloud render backend when that is what is required to reach production quality in practical time.

A local backend remains desirable when it can meet the quality/time bar. It is no longer allowed to force a visibly inferior result simply to remain local.

## Current hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`

This hardware remains useful for image preparation, reference management, prompt planning, local experiments and some video tasks. It is not treated as sufficient evidence that the final photorealistic avatar renderer must also run locally.

## What H3 proved and what it did not

H3 proved locally:

- recognizable identity from still references;
- user-approved voice behavior from a voice reference;
- useful lip sync;
- autonomous motion without a driving video;
- scene separation using cropped identity references;
- fully local execution.

H3 did not prove:

- production-grade spatial detail;
- production-grade hands/gestures/anatomy;
- production-grade temporal texture stability;
- a practical path to high-resolution finished output on the RTX 3060.

The H3 infrastructure remains preserved as research/fallback evidence. Do not delete it yet.

## New target architecture — ACTIVE DIRECTION

The Video Studio becomes **backend-agnostic**:

```text
local UI / orchestrator
    -> persistent identity + voice profile
    -> optional high-quality still / look generation
    -> render-backend adapter
         -> production hosted avatar/video engine
         -> optional local research backend (H3 etc.)
    -> final assembly / captions / manifests
```

The first production benchmark should use a renderer designed specifically for high-quality personal avatars rather than forcing a general-purpose local video model to approximate one.

## Preferred first production benchmark

**HeyGen Digital Twin / Avatar V if available to the account, otherwise Avatar IV Digital Twin** is the first candidate because it is directly aligned with the user's actual goal:

- trained from the user's own video footage;
- script-adaptive body language and expressions;
- full-body support;
- high-resolution output;
- API integration;
- no need to record each new script.

For arbitrary scene/appearance changes, use a two-stage production architecture when useful:

1. create a high-quality canonical look/still of the user in the target scene;
2. animate that look with the avatar backend using cloned/referenced voice and the script.

**Kling Avatar 2.0 Pro** is the second benchmark candidate for image+audio driven scene-specific shots if it provides better whole-body/scene behavior.

## Open-source alternatives — RESEARCH, NOT FIRST PRACTICAL CHOICE

Current open models remain relevant for comparison, but their hardware/runtime cost matters:

- LongCat-Video-Avatar 1.5 has strong 2026 quality claims and 8-step distilled inference, but practical reference implementations still target much larger GPUs than 12 GB;
- HunyuanVideo-Avatar can be made to run on lower VRAM through community low-memory paths, but it remains a slow 720p-class route and is not the obvious answer to the user's resolution complaint;
- InfiniteTalk is useful for long audio-driven generation but does not by itself resolve the quality/time mismatch on this hardware.

Do not start downloading another 20–50+ GB local model merely to continue the same pattern.

## Local Video Studio implementation

`tools/video-studio/` remains the orchestration prototype.

It should now evolve toward a provider/renderer adapter architecture instead of assuming MiniMax H3 is the permanent backend.

The current H3 quality/resolution runners are retained as evidence and diagnostics, not as the active production path.

## Immediate next action

Do not run Base50 or the resolution/upscaling gate as the next production step.

Next decision gate:

1. benchmark one short personal-avatar clip on a production hosted engine using the user's real footage and the same script;
2. judge it against the existing H3 output;
3. if the quality jump is large enough, integrate that renderer into Video Studio behind an adapter;
4. only then optimize cost, scene generation and multi-shot assembly.

The benchmark should be short enough to cost little and answer the quality question quickly.
