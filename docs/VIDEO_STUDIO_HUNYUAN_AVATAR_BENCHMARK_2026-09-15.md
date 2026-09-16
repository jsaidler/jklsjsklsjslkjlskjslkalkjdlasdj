# Local Video Studio — HunyuanVideo-Avatar direct comparison

Date: **2026-09-15**  
Status: **ACTIVE NEXT BENCHMARK / PAYLOAD PREPARATION ACTIVE / WAN 20-STEP A/B PAUSED**

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

## Disk state

After retiring the two large H3-only weights:

- recovered approximately **34.14 GB**;
- free space on `Z:`: **65.66 GB**;
- Hunyuan payload gate: **PASS**.

## Candidate payload

Primary checkpoint:

- `hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — about **13.4 GB**.

INT8 text encoder:

- `llava-llama-3-8b/llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors` — about **9.43 GB**.

The current Wan2GP Hunyuan handler also requires the CLIP-L, Whisper Tiny, face-alignment, tokenizer/config assets and Hunyuan VAE files under `ckpts/`.

Important correction: **Hunyuan Avatar uses the custom Hunyuan VAE**, not only the standard Hunyuan VAE:

- `hunyuan_video_custom_VAE_fp32.safetensors`;
- `hunyuan_video_custom_VAE_config.json`.

Wan2GP's current generic Hunyuan dependency definition also requests the standard VAE pair and the generic INT8 map, so the preparer mirrors that dependency set to prevent surprise downloads at render time.

Do not download the full Tencent repository.

## Direct comparison inputs

Reuse exactly:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

Do not introduce CosyVoice yet. Do not change João's identity reference between engines.

The preparer pins copies under:

- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_ref.png`
- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_test_4p5s.wav`

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
10. overall publishability without manual repair.

## Decision after Hunyuan render

- **If Hunyuan clearly beats Wan 10-step:** make Hunyuan the active renderer candidate and optimize/integrate it.
- **If Hunyuan is roughly tied:** compare runtime and native resolution headroom before choosing.
- **If Hunyuan is worse:** return immediately to Wan and run the proper 20-step FP8 A/B.

## Payload preparer

Repository files:

- `tools/video-studio/prepare_hunyuan_avatar_benchmark.ps1`
- `tools/video-studio/prepare_hunyuan_avatar_benchmark.py`

The preparer:

- uses WanGP's own Python environment;
- downloads directly into `Z:\AI\WanGP\ckpts`;
- redirects global Hugging Face/Xet caches to `%LOCALAPPDATA%\VideoStudio\huggingface` so `Z:` is not consumed by duplicate cache payloads;
- reuses already-present files;
- validates the critical payload;
- can optionally SHA-256-check the largest pinned files;
- writes `Z:\AI\WanGP\hunyuan_avatar_benchmark_prepare_manifest.json`.

## Immediate action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File `
'.\tools\video-studio\prepare_hunyuan_avatar_benchmark.ps1' `
-Download
```

If preparation passes, build/run one Hunyuan Avatar benchmark using the pinned image and 4.5 s speech audio.
