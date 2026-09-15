# Local Video Studio — Wan2.2 S2V benchmark

Date: **2026-09-15**  
Status: **FIRST RENDER COMPLETE / PROMISING STRUCTURAL RESULT / PRODUCTION QUALITY NOT APPROVED**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

The project returned to the pre-H3 modular architecture. The active renderer candidate is **Wan2.2-S2V-14B**, with voice generation kept as a separate stage. CosyVoice remains deferred until the renderer itself clears the visual-quality gate.

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
- intended 77-frame single chunk at 16 fps;
- **10 steps**;
- CFG 6;
- `uni_pc` / `simple`;
- ModelSamplingSD3 shift 8;
- seed 0;
- real recorded speech audio;
- no CosyVoice;
- no upscaler.

The uploaded MP4 itself was 480x832, 16 fps, 4.5 s, 72 encoded video frames. The 72-frame viewing copy was caused by the runner's previous FFmpeg `-shortest` mux: the 4.5 s audio truncated the 77-frame video sequence. This is a muxing bug, not a model-quality finding. Runner v2 now pads audio to the full generated-frame duration.

### Visual verdict

**WAN S2V FIRST RESULT: STRUCTURALLY PROMISING / PRODUCTION QUALITY FAIL.**

Positive findings relative to the failed H3 direction:

- face remains broadly coherent through the shot after the opening transient;
- body topology and shoulders are stable;
- hand behavior is materially better: no obvious catastrophic finger collapse in the reviewed sequence;
- gestures are asymmetric and more conversational rather than repetitive mirrored presenter motion;
- background geometry is stable;
- clothing is stable;
- camera/framing are stable.

Remaining blockers:

- 480x832 effective detail is not sufficient for the user's production standard;
- first frames show a visible transient before stabilizing;
- subtle eyeglass geometry/reflection drift remains;
- beard, hairline and facial texture show temporal crawl/drift;
- mouth/teeth/jaw remain soft and synthetic in some open-mouth positions;
- moving hands lose finger detail through motion blur/generative softness;
- skin still has diffusion-style smoothing/temporal texture behavior;
- overall output is not yet publishable without qualification.

AV sync was not promoted to PASS from static/sequential frame inspection alone. It requires playback review.

## Sampling correction — IMPORTANT

The earlier repository state incorrectly described 10 steps as the documented non-Lightning quality path. That interpretation is retired.

Current ComfyUI documentation for Wan2.2-S2V states:

- **with 4-step Lightning LoRA:** 4 steps / CFG 1;
- **without Lightning LoRA:** **20 steps / CFG 6**;
- the Lightning LoRA significantly reduces generation time but also causes significant dynamic and quality loss;
- when quality is insufficient, ComfyUI recommends the original 20-step workflow.

Reference: `https://docs.comfy.org/tutorials/video/wan/wan2-2-s2v`

Therefore the first 10-step render was **under-sampled relative to the documented ComfyUI non-Lightning quality baseline**. It remains useful as a first structural test, but it is not the correct final Wan quality gate.

The current benchmark runner now exposes `-Steps`; default is 20.

## Resolution headroom

Wan2.2 S2V is not inherently limited to 480p. The official Wan2.2 repository lists S2V-14B as supporting **480P and 720P**.

Reference: `https://github.com/Wan-Video/Wan2.2`

This makes Wan materially different from the local H3 path: there is a native higher-resolution operating point to test if the 480p/20-step gate demonstrates enough quality improvement to justify the cost.

Do **not** jump directly to 720p on RTX 3060 12 GB. First establish the cost/benefit of the documented 20-step sampling path at the current resolution.

## FP8 / BF16 rule

ComfyUI documents the FP8 S2V checkpoint as the lower-VRAM option and notes that BF16 can reduce quality degradation. BF16 is not the next automatic test on a 12 GB RTX 3060 because its checkpoint/runtime cost is much higher. Do not download it unless the FP8 path gives evidence that BF16 is worth the cost.

## Current controlled gate

Before launching another long inference, inspect the first run's `manifest.json` and recover the actual `elapsed_seconds`.

Decision rule:

- if the 10-step 480x832 run was reasonably short, run **the same seed/reference/audio/resolution at 20 steps**;
- if 10-step was already close to an hour or otherwise impractical, do not blindly double the local inference cost; move to the next renderer comparison instead;
- only if 20-step materially improves detail/stability should a 720p Wan test be considered.

## Runtime / output strategy

Canonical runner:

- `tools/video-studio/run_wan_s2v_benchmark.ps1`
- `tools/video-studio/run_wan_s2v_benchmark.py`

Runner v2:

- default `Steps = 20`;
- `-Steps` is explicit and recorded in the manifest;
- output filename records the step count;
- ComfyUI saves lossless PNG frames;
- FFmpeg assembles H.264 CRF 14 viewing copy;
- audio is padded to the generated-frame duration instead of truncating the video to the source audio length.

Output root:

`Z:\AI\VideoStudioRuns\wan-s2v-gates\<timestamp>\`

## Quality gate

Judge full-size and in motion:

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

## Benchmark order

1. recover the actual runtime of the completed 10-step 480x832 run;
2. if runtime justifies it, controlled 20-step FP8 A/B at the same resolution/seed/reference/audio;
3. if 20-step materially improves quality and remains practical, consider the native 720p operating point;
4. only after renderer quality passes, add CosyVoice;
5. if Wan quality/time remains insufficient, compare HunyuanVideo-Avatar;
6. keep EchoMimicV3-Flash as the lower-compute fallback.

## H3 status

MiniMax H3 remains preserved as functional evidence/baseline. It is not the active renderer optimization target. Do not resume H3 Base50 / SeedVR2 work without new evidence.