# Local Video Studio — HunyuanVideo-Avatar direct comparison

Date: **2026-09-15**  
Status: **PAYLOAD PREPARED / DIRECT RENDER GATE NEXT / WAN 20-STEP A/B PAUSED**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

After the first Wan2.2-S2V render, do **not** spend another ~1 hour on the 20-step Wan A/B before seeing whether a stronger avatar renderer can beat it.

The next comparison target is **HunyuanVideo-Avatar** using the same João reference image and the same recorded 4.5 s speech audio.

The Wan 20-step path is **paused, not rejected**. If Hunyuan is worse, return to Wan and run the proper 20-step quality baseline.

## Runtime strategy

Use:

**DeepBeepMeep WanGP -> Hunyuan Video Avatar 720p 13B -> quantized INT8 payload**.

WanGP is the practical implementation route for Windows 11 + RTX 3060 12 GB.

Runtime bootstrap validated on 2026-09-15:

- Python 3.11.14;
- Torch 2.10.0+cu130;
- CUDA 13.0 available;
- RTX 3060 detected;
- WanGP local footprint: **7.4 GB**.

## Disk and preparation state

The earlier free-space blocker was resolved by retiring approved H3-only payloads. The Hunyuan preparation was then completed successfully.

Successful preparation run:

- report: `D:\GOOGLE DRIVE\DEV\Roguelite\tools\video-studio\reports\hunyuan_avatar_prepare_20260915_234228.txt`;
- manifest: `Z:\AI\WanGP\hunyuan_avatar_benchmark_prepare_manifest.json`;
- downloaded files: **26**;
- reused files: **0**;
- free space on `Z:` after payload: **40.63 GB**.

Canonical preparation classification:

**HUNYUAN AVATAR: RUNTIME PASS / PAYLOAD PREPARED / DIRECT RENDER GATE PENDING.**

## Validated payload

The successful preparer validation reported:

- `hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — **12.486 GB** — PASS;
- `llava-llama-3-8b/llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors` — **8.785 GB** — PASS;
- `clip_vit_large_patch14/model.safetensors` — **1.593 GB** — PASS;
- `whisper-tiny/model.safetensors` — **0.141 GB** — PASS;
- `det_align/detface.pt` — **0.174 GB** — PASS;
- `hunyuan_video_custom_VAE_fp32.safetensors` — **0.918 GB** — PASS;
- `hunyuan_video_custom_VAE_config.json` — PASS.

The current WanGP Hunyuan handler also requires tokenizer/config and supporting dependency assets under `ckpts/`; the preparer downloaded the full required set rather than the full Tencent repository.

Important correction retained: **Hunyuan Avatar uses the custom Hunyuan VAE**, not only the standard Hunyuan VAE:

- `hunyuan_video_custom_VAE_fp32.safetensors`;
- `hunyuan_video_custom_VAE_config.json`.

## Direct comparison inputs — LOCKED

Reuse exactly the Wan benchmark source assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

The preparer pins copies under:

- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_ref.png`
- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_test_4p5s.wav`

Do not introduce CosyVoice yet. Do not change João's identity reference between engines. Do not upscale, face-retouch or otherwise post-process the first Hunyuan render in a way that hides renderer defects.

## Hunyuan timing/shape facts to preserve

The previously inspected WanGP Hunyuan Avatar handler indicated:

- **25 fps**;
- default **129-frame** segment;
- reference-image + audio conditioning;
- guidance scale 7.5;
- flow shift 5;
- one 128-frame processing segment even when a shorter output is requested.

A 129-frame segment at 25 fps is about **5.16 s**, close enough to the Wan ~4.8 s gate for direct visual comparison.

Before the direct runner hardcodes these values, its programmatic WanGP entrypoint and current argument/schema path must be verified against the installed/upstream runtime. Do not invent a CLI or browser-automation layer when a supported programmatic path exists.

## First Hunyuan gate

The first render should answer only:

> Is HunyuanVideo-Avatar materially closer to publishable João video than the completed Wan 10-step render?

Use the same quality criteria:

1. effective detail/resolution;
2. identity stability;
3. glasses/eyes/beard/hair;
4. mouth/teeth/jaw;
5. hands/arms/shoulders;
6. skin/clothing temporal stability;
7. naturalness of body performance;
8. AV sync;
9. runtime practicality;
10. overall publishability without manual repair.

## Decision after Hunyuan render

- **If Hunyuan clearly beats Wan 10-step:** make Hunyuan the active renderer candidate and optimize/integrate it.
- **If Hunyuan is roughly tied:** compare runtime and native resolution headroom before choosing.
- **If Hunyuan is worse:** return immediately to Wan and run the proper 20-step FP8 A/B.

Do not keep changing models without completing this controlled direct comparison.

## Payload preparer

Repository files:

- `tools/video-studio/prepare_hunyuan_avatar_benchmark.ps1`
- `tools/video-studio/prepare_hunyuan_avatar_benchmark.py`

The preparer:

- uses WanGP's own Python environment;
- downloads directly into `Z:\AI\WanGP\ckpts`;
- redirects global Hugging Face/Xet caches to `%LOCALAPPDATA%\VideoStudio\huggingface` so `Z:` is not consumed by duplicate cache payloads;
- reuses already-present files when available;
- validates the critical payload;
- can optionally SHA-256-check the largest pinned files;
- pins the benchmark image/audio;
- writes `Z:\AI\WanGP\hunyuan_avatar_benchmark_prepare_manifest.json`.

## Immediate action

Preparation is complete. **Do not rerun the payload download.**

Next:

1. verify the current WanGP programmatic/headless generation entrypoint and exact Hunyuan Avatar job schema against upstream/runtime code;
2. add a repository-backed direct benchmark runner;
3. execute exactly one Avatar render with the pinned reference image and 4.5 s real speech audio;
4. preserve output, parameters, logs and elapsed time;
5. compare the result directly with the completed Wan 10-step baseline.

No Hunyuan renderer result has been produced yet; only runtime and payload preparation have passed.
