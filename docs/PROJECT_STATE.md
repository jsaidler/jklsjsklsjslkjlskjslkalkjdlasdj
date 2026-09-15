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

Build a tool that lets João write dialogue, choose a scenario and optionally specify appearance/framing, then generate a realistic video of himself speaking the new text with convincing identity, voice and natural movement, without recording a new performance.

Target program length: up to approximately one minute.

**The only active product focus is João's video production.** Game/sprite/character-runtime work is historical only.

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

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

H3 proved identity preservation, useful voice/lip-sync behavior, autonomous motion without a driving video, scene separation, and local execution. It did not prove production-grade effective detail, anatomy/hands, temporal texture stability, or a practical high-resolution finish on the RTX 3060.

The user explicitly rejected the persistent effective-resolution/detail level. Turbo4/Base20 did not justify continuing into Base50 or heavy upscaling as the next main strategy.

H3 remains preserved as video evidence/baseline.

## Current hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`

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

## Wan S2V preparation — COMPLETED 2026-09-15 17:55

Checks passed:

- RTX 3060 12 GB / 47.7 GB RAM;
- FFmpeg available;
- native `WanSoundImageToVideo`, `AudioEncoderLoader`, `AudioEncoderEncode` support present.

Downloaded and SHA-256 verified:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan2.2_s2v_14B_fp8_scaled.safetensors` (~16.4 GB);
- `Z:\AI\WanAnimate2\models\audio_encoders\wav2vec2_large_english_fp16.safetensors` (~631 MB).

Reused:

- `umt5_xxl_fp16.safetensors`;
- `Wan2_1_VAE_bf16.safetensors`.

Prepared:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`;
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`;
- pinned official ComfyUI S2V template;
- preparation manifest.

CosyVoice remains intentionally deferred until the renderer clears the visual-quality gate.

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
- 77 frames at 16 fps (~4.8 s);
- 20 steps;
- CFG 6;
- `uni_pc` / `simple`;
- ModelSamplingSD3 shift 8;
- seed 0;
- real João speech audio;
- no upscaler;
- no CosyVoice;
- no long-form extension.

The 480x832 frame has approximately the same pixel budget as the official 640x640 template while matching the intended vertical-video use.

The runner prefers the current Flux2Klein ComfyUI portable runtime and exposes `Z:\AI\WanAnimate2\models` through `extra_model_paths`, avoiding model duplication. It runs on dedicated port 8192 and records evidence/timing.

### Quality-preserving output path — LOCKED

For this benchmark, ComfyUI saves the decoded output as **lossless PNG frames** rather than a compressed intermediary MP4. The runner then assembles the exact frames with FFmpeg using libx264 `slow`, CRF 14, `yuv420p`, and AAC 192 kb/s.

This prevents ComfyUI video encoding from obscuring whether a softness/detail defect belongs to Wan itself.

The official first-frame VAE workaround is retained before frame export.

Output root:

`Z:\AI\VideoStudioRuns\wan-s2v-gates\<timestamp>\`

Expected evidence:

- `frames\frame_0001.png` ... lossless frames;
- `wan_s2v_fp8_20step.mp4`;
- `api_graph.json`;
- `manifest.json`;
- `comfy_server.log`.

Judge full-size/in-motion:

1. effective detail/resolution;
2. identity stability;
3. glasses/eyes/beard/hair;
4. mouth/teeth/jaw;
5. hands/arms/shoulders;
6. skin/clothing temporal stability;
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

`tools/video-studio/` remains the orchestration prototype and should evolve toward persistent profile assets, separate voice stage, optional scene/look still generation, interchangeable renderer backend, manifests/evidence, and final assembly.

Do not resume one-minute workflow/UI polish until a single short shot is genuinely publishable.

## Immediate next action

Run the prepared Wan2.2-S2V single-shot benchmark and evaluate its MP4 and lossless PNG frames before installing CosyVoice or any additional renderer.

Canonical procedure: `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`.
