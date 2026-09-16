# Local Video Studio — Wan2.2 S2V benchmark

Date: **2026-09-16**  
Status: **FIRST RENDER COMPLETE / STRUCTURALLY PROMISING / WAN 20-STEP A/B RESUMED AFTER HUNYUAN LOCAL PRACTICALITY FAIL**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

Wan2.2-S2V remains the strongest validated local renderer candidate.

The 20-step repeat had been paused while HunyuanVideo-Avatar was tested first. Hunyuan's local 720p quality path timed out after approximately three hours while still at `0/30` denoising steps on the RTX 3060 12 GB. That branch is now classified as a **local practicality failure**, not a visual-quality result.

Therefore the controlled Wan 20-step FP8 test is **resumed and is the next GPU-heavy local action**.

CosyVoice remains deferred until a renderer clears the visual-quality gate.

## Preparation — COMPLETED 2026-09-15 17:55

Machine/runtime checks passed:

- NVIDIA RTX 3060 12 GB;
- 47.7 GB system RAM;
- FFmpeg available;
- native `WanSoundImageToVideo`, `AudioEncoderLoader`, and `AudioEncoderEncode` support present.

Downloaded and SHA-256 verified:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan2.2_s2v_14B_fp8_scaled.safetensors` (~16.4 GB);
- `Z:\AI\WanAnimate2\models\audio_encoders\wav2vec2_large_english_fp16.safetensors` (~631 MB).

Reused:

- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors`;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors`.

Prepared benchmark assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`;
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`;
- pinned official template: `Z:\AI\WanAnimate2\video_wan2_2_14B_s2v_official_pinned.json`;
- preparation manifest: `Z:\AI\WanAnimate2\wan_s2v_benchmark_prepare_manifest.json`.

## First generated result — REVIEWED 2026-09-15

The first uploaded viewing copy used:

- Wan2.2 S2V 14B FP8 scaled;
- UMT5 FP16;
- Wan2.1 VAE BF16;
- wav2vec2 large English FP16;
- 480x832 vertical;
- 77-frame single chunk at 16 fps;
- **10 steps**;
- CFG 6;
- `uni_pc` / `simple`;
- ModelSamplingSD3 shift 8;
- seed 0;
- real recorded speech audio;
- no CosyVoice;
- no upscaler.

Measured inference time:

- **1713.2926 s = 28.55 min**.

The original viewing MP4 contained only 72 frames because the old FFmpeg mux used `-shortest` against the 4.5 s audio. The evidence folder contains all 77 generated PNG frames. Runner v2 pads audio and preserves the complete generated sequence.

### Visual verdict

**WAN S2V 10-STEP FP8: STRUCTURALLY PROMISING / PRODUCTION QUALITY FAIL.**

Positive findings relative to H3:

- stable body topology and shoulders;
- materially better hand behavior;
- asymmetric, more natural conversational gestures;
- stable background, clothing and framing;
- broadly coherent face after the opening transient.

Remaining blockers:

- insufficient effective detail at 480x832;
- opening transient;
- eyeglass geometry/reflection drift;
- beard/hairline/facial texture crawl;
- mouth/teeth/jaw softness;
- moving-hand detail loss;
- diffusion-style skin smoothing/temporal instability;
- overall result not yet publishable.

AV sync was not promoted to PASS from frame inspection alone.

## Sampling correction — LOCKED

Current ComfyUI documentation for Wan2.2-S2V states:

- 4-step Lightning path: 4 steps / CFG 1;
- non-Lightning quality path: **20 steps / CFG 6**;
- Lightning reduces generation time but also reduces dynamics/quality;
- when quality is insufficient, use the original 20-step workflow.

Reference: `https://docs.comfy.org/tutorials/video/wan/wan2-2-s2v`

Therefore the completed 10-step render is under-sampled relative to the documented non-Lightning quality baseline.

Runner v2 exposes `-Steps` and defaults to 20.

Based on the measured 28.55 min 10-step run, the 20-step run is expected to take roughly **55–60 minutes**, though scaling is not guaranteed perfectly linear.

## Hunyuan comparison result

The Hunyuan branch did not produce a visual comparison.

At 720x1280 / 129 frames / 30 steps / profile 4 / SDPA, WanGP repeatedly shuttled Hunyuan transformer blocks between RAM and VRAM. The watchdog cancelled the run at 180 minutes while progress still showed `0/30` steps completed.

Canonical Hunyuan classification:

**HUNYUAN AVATAR LOCAL 720P: FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / PRACTICALITY FAIL ON RTX 3060 12 GB.**

This is sufficient to end the Hunyuan local branch without reducing its quality target merely to force an output.

Procedure and evidence: `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`.

## Resolution headroom

Wan2.2 S2V officially supports 480P and 720P.

Do **not** jump to 720p yet. First determine whether the corrected 20-step sampling meaningfully improves face/beard, mouth, glasses, temporal texture and moving-hand definition at the already measured 480x832 gate.

## Current benchmark order

1. keep the completed Wan 10-step result as baseline;
2. run exactly one **Wan 20-step FP8** repeat with the same seed/input/settings except step count;
3. compare the 20-step result directly with the 10-step evidence;
4. if improvement is small, stop local Wan escalation and evaluate high-VRAM/cloud renderer execution rather than spending on 720p/upscale;
5. if improvement is large, then investigate native Wan 720p feasibility on RTX 3060 before changing the runner;
6. only after renderer quality passes, integrate CosyVoice.

## 20-step decision threshold

The 20-step result must improve **clearly**, not marginally, in:

- facial detail and beard stability;
- mouth/teeth/jaw behavior;
- eyeglass stability;
- temporal skin/hair texture;
- moving-hand/finger definition;
- overall publishability.

If the difference is small, local Wan is technically stronger than H3 but not efficient enough for the intended one-minute multi-shot production workflow.

## Immediate action

Run the existing benchmark runner with the original seed and **20 steps**. Do not enable `-LowVram` unless an actual OOM occurs.