# Local Video Studio — Wan2.2 S2V benchmark

Date: **2026-09-15**  
Status: **READY TO RUN FIRST RENDERER QUALITY TEST**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

The project returned to the pre-H3 modular architecture. The primary renderer benchmark is **Wan2.2-S2V-14B**, with voice generation kept as a separate stage. CosyVoice remains deferred until the renderer itself clears the visual-quality gate.

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

## First benchmark settings — LOCKED

The first gate intentionally follows the official native sampling settings instead of doubling work without evidence of benefit.

- diffusion: Wan2.2 S2V 14B FP8 scaled;
- text encoder: reused UMT5 FP16;
- VAE: reused Wan2.1 VAE BF16;
- audio encoder: wav2vec2 large English FP16;
- resolution: **480x832 vertical**;
- frame count: **77**;
- frame rate: **16 fps**;
- duration: ~4.81 s;
- steps: **10**;
- CFG: **6**;
- sampler: **uni_pc**;
- scheduler: **simple**;
- ModelSamplingSD3 shift: **8**;
- seed: **0** unless explicitly changed;
- single-chunk batch size: **1**;
- no CosyVoice;
- no long-form extension;
- no upscaler.

The official ComfyUI template shows 10 sampling steps / CFG 6 / `uni_pc` / `simple` for the native S2V path. The earlier 20-step assumption came from misreading the seed value in the workflow and is retired.

The 480x832 frame has approximately the same pixel budget as the official 640x640 template while matching the intended vertical-video use.

## First-frame VAE workaround

The official template duplicates each chunk's first latent before VAE decode and then removes the corresponding overbaked decoded frame. The template's `Batch sizes` value is also used as the `ImageFromBatch` start index: a three-chunk example uses index 3.

Our benchmark has exactly **one chunk**, so the correct `ImageFromBatch` start index is **1**, not 3.

## Runtime strategy

The benchmark reuses a protected current ComfyUI portable runtime, preferring:

1. `Z:\AI\Flux2Klein\ComfyUI_windows_portable`;
2. MiniMaxH3 portable fallback;
3. QwenImageEdit portable fallback.

Wan models stay in `Z:\AI\WanAnimate2\models` and are exposed to the selected runtime with a generated `extra_model_paths` YAML. Models are not duplicated.

The runner uses a dedicated local ComfyUI port (`8192` by default), validates required nodes and model visibility, submits the graph through the API, records timing/evidence, and shuts down the ComfyUI process if it started it.

## Quality-preserving output path — LOCKED

The first quality gate must not be contaminated by an uncertain ComfyUI MP4 encoder configuration.

Therefore the ComfyUI graph ends in **`SaveImage`**, preserving the decoded result as lossless PNG frames. After inference, the runner assembles those exact frames with system FFmpeg:

- H.264 / libx264;
- preset `slow`;
- CRF 14;
- `yuv420p`;
- AAC 192 kb/s;
- source benchmark audio preserved.

This makes the renderer comparison depend on the generated frames rather than on a low-bitrate intermediary MP4.

Canonical runner:

- `tools/video-studio/run_wan_s2v_benchmark.ps1`
- `tools/video-studio/run_wan_s2v_benchmark.py`

Output root:

`Z:\AI\VideoStudioRuns\wan-s2v-gates\<timestamp>\`

Expected evidence:

- `frames\frame_0001.png` ... lossless generated frames;
- `wan_s2v_fp8_10step.mp4` — CRF14 viewing copy;
- `api_graph.json`;
- `manifest.json`;
- `comfy_server.log`.

## Quality gate

Judge the actual MP4 at full size and in motion, with the PNG frames available to distinguish renderer defects from encoding defects:

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
4. Keep **EchoMimicV3-Flash** as lower-compute fallback.

## H3 status

MiniMax H3 remains preserved as functional evidence and a baseline comparison. It is not the active renderer optimization target. Do not resume Base50 / SeedVR2 work unless a later comparison creates a specific reason to do so.
