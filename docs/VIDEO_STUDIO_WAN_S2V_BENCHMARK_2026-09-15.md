# Local Video Studio — Wan2.2 S2V benchmark

Date: **2026-09-15**  
Status: **ACTIVE NEXT ENGINE TEST**

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
- current `Z:\AI\WanAnimate2` runtime present.

Current Wan payload:

- `wan_animate_2_bf16.safetensors` — 30.54 GB;
- `umt5_xxl_fp16.safetensors` — 10.59 GB;
- `clip_vision_h.safetensors` — 1.18 GB;
- `Wan2_1_VAE_bf16.safetensors` — 0.24 GB.

Confirmed missing:

- Wan2.2 S2V diffusion checkpoint;
- Wan S2V wav2vec2 audio encoder;
- CosyVoice runtime/models.

The existing Wan installation is Animate-oriented, not S2V-oriented.

## Important discovery

A current ComfyUI installation already contains the official native workflow template:

`video_wan2_2_14B_s2v.json`

The official ComfyUI workflow requires:

- diffusion model: `wan2.2_s2v_14B_fp8_scaled.safetensors` or BF16 equivalent;
- text encoder: `umt5_xxl_fp8_e4m3fn_scaled.safetensors` in the stock workflow;
- VAE: `wan_2.1_vae.safetensors` in the stock workflow;
- audio encoder: `wav2vec2_large_english_fp16.safetensors`.

For the RTX 3060 12 GB benchmark, the first model choice is the **FP8 scaled S2V checkpoint**, not BF16.

## Download-minimization rule

Do not download every stock-template dependency blindly.

For the first benchmark:

- **download** `wan2.2_s2v_14B_fp8_scaled.safetensors` (~16.4 GB);
- **download** `wav2vec2_large_english_fp16.safetensors` (~631 MB);
- first attempt to **reuse** the already-installed `umt5_xxl_fp16.safetensors`;
- first attempt to **reuse** the already-installed `Wan2_1_VAE_bf16.safetensors`.

If the native loaders reject either reused component, then download the exact stock-template FP8 text encoder / standard VAE. Do not pre-download them merely for naming symmetry.

## First benchmark scope

The first S2V test is intentionally short and isolates renderer quality.

Inputs:

- one high-quality still reference of João, preferably upper-body;
- approximately 4–5 seconds of real João speech;
- concise prompt describing restrained natural speaking behavior;
- no CosyVoice yet;
- no one-minute extension chain yet;
- no upscaler.

Target questions:

1. Does Wan S2V preserve materially more real image detail than H3 local?
2. Are face, glasses, beard, mouth and skin more stable?
3. Are hands/shoulders/body motion more natural?
4. Does the output look like real video rather than a soft diffusion render?
5. Is runtime on the RTX 3060 remotely practical?

Only after this visual benchmark passes do we add:

- CosyVoice text-to-speech / voice cloning;
- high-quality scene/look preparation;
- multi-shot generation;
- long-form assembly.

## Known native workflow facts

The official ComfyUI S2V workflow is a 16 fps path.

- default chunk length: 77 frames;
- 77 frames at 16 fps ≈ 4.81 seconds;
- additional S2V Extend stages add more 77-frame chunks;
- stock high-quality path is approximately 20 steps / CFG 6;
- Lightning path can use approximately 4 steps / CFG 1.

The first benchmark should stay in a single short chunk where possible. Long audio is deliberately deferred.

## Benchmark order

1. **Wan2.2-S2V-14B FP8 + real João audio** — active next test.
2. If visual quality passes, add **CosyVoice** and test text-only speech generation.
3. Compare against **HunyuanVideo-Avatar** only if Wan quality or runtime is insufficient.
4. Keep **EchoMimicV3-Flash** as the lower-compute fallback, not the default quality target.

## H3 status

MiniMax H3 remains preserved as functional evidence and a baseline comparison. It is not the active renderer optimization target.

Do not resume Base50 / SeedVR2 work unless a later comparison creates a specific reason to do so.
