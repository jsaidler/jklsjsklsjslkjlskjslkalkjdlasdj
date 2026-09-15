# Local Video Studio — HunyuanVideo-Avatar direct comparison

Date: **2026-09-15**  
Status: **ACTIVE NEXT BENCHMARK / WAN 20-STEP A/B PAUSED**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

After the first Wan2.2-S2V render, do **not** spend another ~1 hour on the 20-step Wan A/B before seeing whether a stronger avatar renderer can beat it.

The next comparison target is **HunyuanVideo-Avatar** using the same João reference image and the same recorded 4.5 s speech audio.

Reason:

- Wan 10-step already showed a useful structural improvement over H3 but still has a large production-quality gap;
- measured Wan runtime was **1713.29 s = 28.55 min** for the 10-step 480x832 test;
- a 20-step Wan repeat is expected to cost roughly twice that;
- HunyuanVideo-Avatar is purpose-built for audio-driven human avatar video and is therefore the more informative next benchmark.

The Wan 20-step path is **paused, not rejected**. If Hunyuan is worse, return to Wan and run the proper 20-step quality baseline.

## Runtime strategy

Do not use Tencent's original native low-memory path directly on this Windows 11 / RTX 3060 12 GB machine as the first implementation.

Tencent's repository states that the original single-GPU path needs at least about 24 GB VRAM for its documented 704x768x129f case and is tested on Linux. The same repository explicitly points to **WanGP / Wan2GP** for a 10 GB VRAM path.

Therefore the practical route is:

**DeepBeepMeep WanGP -> Hunyuan Video Avatar 720p 13B -> quantized INT8 payload**.

WanGP supports Windows/RTX 30-series and exposes API/settings paths, so final Video Studio integration does not require manual ComfyUI graph operation.

## Candidate payload

Primary checkpoint:

- `hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — about **13.4 GB**.

Core dependencies used by the WanGP Hunyuan handler include approximately:

- LLaVA/VLM INT8 text encoder — about **9.43 GB**;
- Hunyuan VAE — about **0.99 GB**;
- CLIP ViT-L/14 — about **1.71 GB**;
- Whisper Tiny — about **0.15 GB**;
- face alignment / tokenizer / configs — comparatively small;
- WanGP Python environment and caches — additional several GB.

Treat **35 GB free** as a conservative preparation reserve. Do not download the full 80+ GB Tencent repository.

## Direct comparison inputs

Reuse exactly:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

Do not introduce CosyVoice yet. Do not change João's identity reference between engines.

## Hunyuan timing/shape facts

WanGP's Hunyuan Avatar handler uses:

- **25 fps**;
- default **129-frame** segment;
- reference-image + audio conditioning;
- guidance scale 7.5;
- flow shift 5;
- one 128-frame processing segment even when a shorter output is requested.

A 129-frame segment at 25 fps is about **5.16 s**, close enough to the Wan 4.8 s gate for direct visual comparison.

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
10. overall publishability without manual frame repair.

## Decision after Hunyuan render

- **If Hunyuan clearly beats Wan 10-step:** make Hunyuan the active renderer candidate and optimize/integrate it.
- **If Hunyuan is roughly tied:** compare runtime and native resolution headroom before choosing.
- **If Hunyuan is worse:** return immediately to Wan and run the proper 20-step FP8 A/B.

## Immediate action

Run `tools/video-studio/preflight_hunyuan_avatar.ps1` before any new model download. It checks disk, runtime prerequisites, benchmark assets and any Hunyuan/WanGP payload already present.
