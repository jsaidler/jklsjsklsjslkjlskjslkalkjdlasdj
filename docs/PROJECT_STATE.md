# Local Video Studio — Current Project State

Status date: **2026-09-15**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO.md`
3. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
4. `docs/VIDEO_STUDIO_GAME_PAYLOAD_CLEANUP_2026-09-15.md`
5. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
6. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
7. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Active objective — LOCKED

Build a tool that lets the user write dialogue, choose a scenario and optionally specify appearance/framing, then generate a short realistic video of themselves speaking the new text with convincing identity, voice and natural movement, without recording a new performance.

Target program length: up to approximately one minute.

**The only active product focus is now João's video production.** Game/sprite/character-runtime work is historical only.

## Cleanup policy — LOCKED

The retired Roguelite objective must not consume active local AI storage or clutter the current `main` working tree.

Local game-only AI roots classified for deletion:

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

The active repository working tree is intentionally limited to Video Studio material plus root metadata. Old game material remains recoverable from Git history; Git history is not rewritten.

## H3 conclusion — LOCKED

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

H3 remains preserved as video evidence/baseline. Do not delete it in the game cleanup.

## Current hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`

## Active renderer direction — Wan2.2-S2V-14B

The project has returned to the original modular plan that existed before the H3 detour.

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

## Wan S2V preparation — COMPLETED 2026-09-15 17:55

Machine/runtime checks passed:

- RTX 3060 12 GB;
- 47.7 GB RAM;
- FFmpeg available;
- native `WanSoundImageToVideo`, `AudioEncoderLoader`, and `AudioEncoderEncode` support present.

Downloaded and SHA-256 verified:

- `wan2.2_s2v_14B_fp8_scaled.safetensors` (~16.4 GB);
- `wav2vec2_large_english_fp16.safetensors` (~631 MB).

Reused without duplicate download:

- `umt5_xxl_fp16.safetensors`;
- `Wan2_1_VAE_bf16.safetensors`.

Prepared benchmark assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`;
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`;
- pinned official ComfyUI S2V template;
- preparation manifest.

CosyVoice remains intentionally deferred until the renderer itself clears the visual-quality gate.

## First Wan quality gate — READY TO RUN

Canonical runner:

- `tools/video-studio/run_wan_s2v_benchmark.ps1`
- `tools/video-studio/run_wan_s2v_benchmark.py`

Locked first-test settings:

- Wan2.2 S2V 14B FP8 scaled;
- reused UMT5 FP16;
- reused Wan2.1 VAE BF16;
- wav2vec2 audio encoder;
- **480x832 vertical**;
- 77 frames;
- 16 fps;
- ~4.8 seconds;
- 20 steps;
- CFG 6;
- `uni_pc` / `simple`;
- ModelSamplingSD3 shift 8;
- seed 0;
- real João speech audio;
- no upscaler;
- no CosyVoice;
- no long-form extension.

The 480x832 frame has approximately the same pixel budget as the official 640x640 template but matches the intended vertical-video use.

The runner prefers the current Flux2Klein ComfyUI portable runtime, exposes `Z:\AI\WanAnimate2\models` through `extra_model_paths`, copies only the prepared benchmark inputs into the runtime input root, validates node/model visibility, runs on dedicated port 8192, records timing/evidence, and shuts down the server process it started.

Output root:

`Z:\AI\VideoStudioRuns\wan-s2v-gates\<timestamp>\`

Expected MP4:

`wan_s2v_fp8_20step.mp4`

Judge:

1. effective detail/resolution;
2. identity stability;
3. glasses/eyes/beard/hair;
4. mouth/teeth/jaw;
5. hands/arms/shoulders;
6. skin/clothing texture stability;
7. naturalness of body performance;
8. AV sync;
9. runtime practicality;
10. overall publishability without manual frame repair.

Inference completion does not equal production approval.

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

Run the prepared Wan2.2-S2V single-shot benchmark and evaluate the resulting MP4 against the production visual-quality gate before installing CosyVoice or any additional renderer.

Canonical procedure:

`docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
