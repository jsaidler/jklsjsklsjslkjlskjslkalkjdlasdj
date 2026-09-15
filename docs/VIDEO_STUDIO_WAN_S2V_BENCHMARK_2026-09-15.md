# Local Video Studio — Wan2.2 S2V benchmark

Date: **2026-09-15**  
Status: **FIRST RENDER COMPLETE / STRUCTURALLY PROMISING / WAN 20-STEP A/B PAUSED FOR HUNYUAN COMPARISON**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

Wan2.2-S2V remains a viable renderer candidate, but the next GPU-heavy action is no longer the 20-step Wan repeat. The user chose to compare **HunyuanVideo-Avatar first** because the completed Wan render still has a large production-quality gap and a proper 20-step repeat is expected to cost close to an hour.

The Wan 20-step path is **paused, not rejected**. If Hunyuan is worse, return to Wan immediately and run the proper 20-step FP8 baseline.

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

The first uploaded viewing copy was generated with:

- diffusion: Wan2.2 S2V 14B FP8 scaled;
- reused UMT5 FP16;
- reused Wan2.1 VAE BF16;
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

Measured inference time from the run manifest:

- `elapsed_seconds`: **1713.2926 s**;
- equivalent: **28.55 min** for the 10-step 480x832 generation.

The original viewing MP4 was 480x832, 16 fps, 4.5 s, 72 encoded video frames because the old runner used FFmpeg `-shortest` against 4.5 s audio. The generated evidence folder contains all 77 lossless PNG frames. Runner v2 pads audio to the full generated-frame duration and no longer truncates the video.

### Visual verdict

**WAN S2V FIRST RESULT: STRUCTURALLY PROMISING / PRODUCTION QUALITY FAIL.**

Positive findings relative to H3:

- face remains broadly coherent through the shot after the opening transient;
- body topology and shoulders are stable;
- hand behavior is materially better with no catastrophic finger collapse in the reviewed sequence;
- gestures are asymmetric and more conversational rather than repetitive mirrored presenter motion;
- background geometry is stable;
- clothing is stable;
- camera/framing are stable.

Remaining blockers:

- 480x832 effective detail is not sufficient for the user's production standard;
- first frames show a visible transient before stabilizing;
- subtle eyeglass geometry/reflection drift remains;
- beard, hairline and facial texture show temporal crawl/drift;
- mouth/teeth/jaw remain soft and synthetic in some positions;
- moving hands lose finger detail through motion blur/generative softness;
- skin still has diffusion-style smoothing/temporal texture behavior;
- overall output is not publishable yet.

AV sync requires playback review and is not promoted to PASS from static/sequential frame inspection alone.

## Sampling correction

The earlier repository state incorrectly described 10 steps as the documented non-Lightning quality path. That interpretation is retired.

Current ComfyUI documentation for Wan2.2-S2V states:

- with 4-step Lightning LoRA: 4 steps / CFG 1;
- without Lightning LoRA: **20 steps / CFG 6**;
- the Lightning LoRA reduces generation time but also reduces dynamics/quality;
- when quality is insufficient, use the original 20-step workflow.

Reference: `https://docs.comfy.org/tutorials/video/wan/wan2-2-s2v`

Therefore the first 10-step render was under-sampled relative to the documented non-Lightning quality baseline.

Runner v2 exposes `-Steps` and defaults to 20, but **do not run it yet**. At the measured 28.55 min for 10 steps, a 20-step repeat is expected to be approximately 55–60 min on this machine.

## Resolution headroom

Wan2.2 S2V officially supports 480P and 720P. Native 720p remains available if a later 20-step gate proves worthwhile.

Do not launch 720p before comparing HunyuanVideo-Avatar.

## Current benchmark order

1. keep the completed Wan 10-step result as the direct baseline;
2. benchmark **HunyuanVideo-Avatar** with the same João identity image and the same recorded speech audio;
3. if Hunyuan clearly beats Wan, promote Hunyuan and stop spending time on Wan sampling escalation;
4. if Hunyuan is tied or worse, return to Wan and run the controlled 20-step FP8 A/B;
5. only after renderer quality passes, add CosyVoice;
6. keep EchoMimicV3-Flash as lower-compute fallback.

Hunyuan procedure: `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`.

## H3 status

MiniMax H3 remains preserved as functional evidence/baseline. It is not the active renderer optimization target.
