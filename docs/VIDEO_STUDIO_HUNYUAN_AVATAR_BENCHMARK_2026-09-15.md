# Local Video Studio — HunyuanVideo-Avatar direct comparison

Date: **2026-09-16**  
Status: **PAYLOAD PREPARED / DRY-RUN PASS / LOCAL 720P RENDER TIMED OUT BEFORE FIRST DENOISE STEP / LOCAL PRACTICALITY FAIL / WAN 20-STEP RESUMED**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

HunyuanVideo-Avatar was selected to compare directly against the first Wan2.2-S2V result using the same João identity image and the same recorded 4.5 s speech audio.

The local Hunyuan test has now answered the practicality question decisively: **the quality-oriented 720p / 129-frame / 30-step path is not viable on the RTX 3060 12 GB in the current WanGP profile-4 offload configuration.**

This is **not a visual-quality failure** because no frame was completed. It is a **local throughput/practicality failure**.

The Wan 20-step path is therefore unpaused and becomes the next local renderer test. Hunyuan remains relevant only for a future rented/high-VRAM GPU comparison if that is still useful after the Wan result.

## Runtime strategy tested

**DeepBeepMeep WanGP -> Hunyuan Video Avatar 720p 13B -> quantized INT8 payload**.

Validated local runtime:

- Windows 11;
- RTX 3060 12 GB;
- 48 GB RAM;
- Python 3.11.14;
- Torch 2.10.0+cu130;
- CUDA 13.0;
- WanGP v13.02;
- WanGP profile 4;
- SDPA attention.

## Payload preparation — PASS

Validated critical payload:

- `hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — **12.486 GB**;
- `llava-llama-3-8b/llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors` — **8.785 GB**;
- `clip_vit_large_patch14/model.safetensors` — **1.593 GB**;
- `whisper-tiny/model.safetensors` — **0.141 GB**;
- `det_align/detface.pt` — **0.174 GB**;
- `hunyuan_video_custom_VAE_fp32.safetensors` — **0.918 GB**;
- `hunyuan_video_custom_VAE_config.json` — PASS.

Preparation result:

- downloaded files: **26**;
- reused files: **0**;
- free space on `Z:` after payload: **40.63 GB**;
- manifest: `Z:\AI\WanGP\hunyuan_avatar_benchmark_prepare_manifest.json`;
- report: `D:\GOOGLE DRIVE\DEV\Roguelite\tools\video-studio\reports\hunyuan_avatar_prepare_20260915_234228.txt`.

Important correction retained: **Hunyuan Avatar uses the custom Hunyuan VAE**, not only the standard Hunyuan VAE.

## Direct comparison inputs — LOCKED

Source assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

Pinned WanGP copies:

- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_ref.png`
- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_test_4p5s.wav`

No CosyVoice, no upscale, no face retouch and no post-processing were introduced.

## Programmatic interface verification — PASS

The benchmark uses WanGP `shared/api.py` directly, not browser/Gradio automation.

Verified runtime contract:

- model type: `hunyuan_avatar`;
- availability: `available`;
- image reference mode: `KI`;
- audio mode: `A`;
- default frames: **129**;
- default steps: **30**;
- CFG: **7.5**;
- flow shift: **5**;
- native fps: **25**;
- `skip_steps_cache_type=""` disables TeaCache/MagCache at task level.

Repository runner:

- `tools/video-studio/run_hunyuan_avatar_benchmark.ps1`
- `tools/video-studio/run_hunyuan_avatar_benchmark.py`

### Initial CLI compatibility error — FIXED

The first attempt stopped before inference because the runner passed unsupported startup argument `--teacache 0`.

Patch:

- removed startup `--teacache 0`;
- retained `--profile 4` and `--attention sdpa`;
- retained `skip_steps_cache_type=""` in task settings.

This error produced no renderer result and is not part of the Hunyuan performance verdict.

## Compatibility dry-run — PASS

Evidence:

`Z:\AI\VideoStudioRuns\hunyuan-avatar-gates\20260916_003617`

The dry-run initialized WanGP, discovered the model, validated payload availability and confirmed the locked image/audio/sampling schema. No generation was submitted.

## Full local benchmark — TIMEOUT / PRACTICALITY FAIL

Locked settings:

- Hunyuan Video Avatar 720p 13B;
- INT8 transformer/text encoder;
- **720x1280** portrait;
- **129 frames**;
- native **25 fps**;
- **30 steps**;
- CFG **7.5**;
- flow shift **5**;
- seed **0**;
- WanGP profile **4**;
- SDPA attention;
- TeaCache off;
- no spatial/temporal upscale;
- no film grain;
- no audio post-processing.

Observed execution on 2026-09-16:

- WanGP repeatedly loaded, prefetched and unloaded `HYVideoDiffusionTransformer` double blocks between system memory and GPU;
- after approximately **2 h 54 min**, the progress display was still **`0/30`** denoising steps completed;
- the 180-minute watchdog fired and requested cancellation;
- the transformer was unloaded cleanly;
- benchmark exited with timeout;
- **no output video and no completed visual frame were produced**.

Representative terminal evidence:

```text
Loading model transformer/double_blocks.4 (HYVideoDiffusionTransformer) in GPU
Timeout reached after 180 min; requesting WanGP cancellation.
Prefetching model transformer/double_blocks.5 (HYVideoDiffusionTransformer) in GPU
  0%|          | 0/30 [2:54:18<?, ?it/s]
BENCHMARK FAILED: Generation exceeded the 180-minute benchmark timeout and was cancelled.
```

Canonical classification:

**HUNYUAN AVATAR LOCAL 720P: FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / PRACTICALITY FAIL ON RTX 3060 12 GB.**

The failure mechanism is severe model block offload/prefetch churn under the 12 GB VRAM constraint. This is not a near-miss where a small sampling tweak is likely to make the route practical.

## Why no more local Hunyuan tuning now

The purpose of this branch was to test a candidate that might clearly outperform Wan without first spending another hour on Wan sampling. Instead, Hunyuan consumed nearly three hours without completing the first denoising iteration.

Do **not** now force a result by:

- reducing resolution below the intended 720p-class gate;
- reducing the 30-step quality baseline simply to obtain an output;
- enabling aggressive step skipping/cache solely to make the benchmark finish;
- extending the watchdog beyond 180 minutes.

Those changes would answer a different question and would move away from the production-quality target.

WanGP documentation describes Sage2 as materially faster than SDPA on Ampere GPUs, but the observed bottleneck here is so large that an attention-backend optimization does not justify another multi-hour local gate before testing the already-working Wan path.

## High-VRAM/cloud status

Hunyuan itself is **not rejected as a renderer**. The local RTX 3060 path is rejected for the quality-oriented 720p benchmark.

A future high-VRAM comparison can still be useful. A rented 48 GB GPU such as A40/A6000 would remove most of the reason for the repeated block shuttling and can be tested with the same reference/audio/settings. This is optional and comes after the next Wan local gate unless a cloud comparison becomes strategically preferable.

## Next action

Resume the controlled **Wan2.2-S2V 20-step FP8** test using the already validated local pipeline.

Hunyuan local should not be rerun unless new evidence changes the memory/runtime picture.