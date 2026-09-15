# Local Video Studio — Wan2.2 S2V benchmark

Date: **2026-09-15**  
Status: **READY TO RUN FIRST RENDERER QUALITY TEST**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

The project returns to the pre-H3 architecture instead of continuing to spend time trying to rescue MiniMax H3 local output with more steps or heavy upscaling.

Primary next renderer benchmark:

**Wan2.2-S2V-14B + separate voice generation**.

Voice synthesis/cloning will ultimately be a separate stage, with CosyVoice remaining the intended local candidate. However, CosyVoice is **not required for the first Wan S2V visual-quality benchmark**. The first benchmark deliberately uses an already-recorded João voice sample so that we can isolate the video renderer quality before adding another model.

## Preflight result — 2026-09-15 17:14

Machine:

- NVIDIA RTX 3060 12 GB;
- 47.7 GB system RAM;
- FFmpeg available;
- current `Z:\AI\WanAnimate2` payload present.

Original Wan payload before S2V preparation:

- `wan_animate_2_bf16.safetensors` — 30.54 GB;
- `umt5_xxl_fp16.safetensors` — 10.59 GB;
- `clip_vision_h.safetensors` — 1.18 GB;
- `Wan2_1_VAE_bf16.safetensors` — 0.24 GB.

The existing Wan installation was Animate-oriented, not S2V-oriented.

## S2V preparation — COMPLETED 2026-09-15 17:55

The preparation gate completed successfully.

Confirmed available and SHA-256 verified:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan2.2_s2v_14B_fp8_scaled.safetensors` — ~16.4 GB;
- `Z:\AI\WanAnimate2\models\audio_encoders\wav2vec2_large_english_fp16.safetensors` — ~631 MB.

Confirmed reused:

- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors`;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors`.

Confirmed native node support:

- `WanSoundImageToVideo`;
- `AudioEncoderLoader`;
- `AudioEncoderEncode`.

Prepared benchmark assets:

- reference image: `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`;
- speech audio: `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`;
- pinned official template: `Z:\AI\WanAnimate2\video_wan2_2_14B_s2v_official_pinned.json`;
- preparation manifest: `Z:\AI\WanAnimate2\wan_s2v_benchmark_prepare_manifest.json`.

## Official workflow basis

The benchmark runner follows the native ComfyUI Wan2.2 S2V path rather than a custom third-party node stack.

Core path:

```text
UNETLoader -> ModelSamplingSD3 (shift 8)
CLIPLoader (Wan UMT5) -> positive / negative conditioning
LoadAudio -> AudioEncoderLoader -> AudioEncoderEncode
LoadImage
        -> WanSoundImageToVideo
        -> KSampler
        -> VAE decode
        -> CreateVideo + source audio
        -> SaveVideo
```

The official first-frame VAE workaround is retained in the benchmark through `LatentCut` + `LatentConcat` + `ImageFromBatch`.

## First benchmark settings — LOCKED

The first test is a controlled quality test, not a speed preset.

- diffusion: `wan2.2_s2v_14B_fp8_scaled.safetensors`;
- text encoder: reused `umt5_xxl_fp16.safetensors`;
- VAE: reused `Wan2_1_VAE_bf16.safetensors`;
- audio encoder: `wav2vec2_large_english_fp16.safetensors`;
- resolution: **480x832** vertical;
- reason: approximately the same pixel budget as the stock 640x640 template while matching the intended vertical-video use;
- frame count: **77**;
- frame rate: **16 fps**;
- duration: ~4.81 s;
- steps: **20**;
- CFG: **6**;
- sampler: **uni_pc**;
- scheduler: **simple**;
- ModelSamplingSD3 shift: **8**;
- seed: **0** unless explicitly changed;
- input speech: real João audio;
- no CosyVoice;
- no long-form extension;
- no upscaler.

The runner requests high-quality H.264 output at CRF 14 when supported by the active ComfyUI SaveVideo implementation so that compression does not unnecessarily contaminate the renderer-quality judgment.

## Runtime strategy

The benchmark reuses one of the protected current ComfyUI portable runtimes, preferring:

1. `Z:\AI\Flux2Klein\ComfyUI_windows_portable`;
2. MiniMaxH3 portable fallback;
3. QwenImageEdit portable fallback.

Wan models stay in `Z:\AI\WanAnimate2\models` and are exposed to the chosen runtime via a generated `extra_model_paths` YAML. Models are not duplicated into another ComfyUI installation.

The test runs on a dedicated local ComfyUI port (`8192` by default), validates required nodes/model visibility, submits the graph through the ComfyUI API, records timing/evidence, and shuts down the ComfyUI process if the runner started it.

Canonical runner:

- `tools/video-studio/run_wan_s2v_benchmark.ps1`
- `tools/video-studio/run_wan_s2v_benchmark.py`

Outputs:

`Z:\AI\VideoStudioRuns\wan-s2v-gates\<timestamp>\`

Expected final file:

`wan_s2v_fp8_20step.mp4`

## Quality gate

Judge the actual MP4 at full size and in motion:

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

Inference success alone is not a production-quality pass.

## Benchmark order

1. **Wan2.2-S2V-14B FP8 + real João audio** — ready to run.
2. If visual quality passes, add **CosyVoice** and test text-only speech generation.
3. Compare against **HunyuanVideo-Avatar** only if Wan quality or runtime is insufficient.
4. Keep **EchoMimicV3-Flash** as the lower-compute fallback, not the default quality target.

## H3 status

MiniMax H3 remains preserved as functional evidence and a baseline comparison. It is not the active renderer optimization target.

Do not resume Base50 / SeedVR2 work unless a later comparison creates a specific reason to do so.
