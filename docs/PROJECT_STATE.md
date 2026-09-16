# Local Video Studio — Current Project State

Status date: **2026-09-15**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`
3. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
4. `docs/VIDEO_STUDIO.md`
5. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
6. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
7. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
8. `docs/VIDEO_STUDIO_GAME_PAYLOAD_CLEANUP_2026-09-15.md`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Active objective — LOCKED

Build a tool that lets João write dialogue, choose a scenario and optionally specify appearance/framing, then generate a realistic video of himself speaking the new text with convincing identity, voice and natural movement, without recording a new performance.

Target program length: up to approximately one minute, eventually assembled from short shots.

**The only active product focus is João's video production.** Game/sprite/character-runtime work is historical only.

## Cleanup policy — LOCKED

Retired Roguelite material must not consume active local AI storage or clutter the current `main` working tree.

Game-only AI roots classified for deletion:

- `Z:\AI\RogueliteAssetStudio`
- `Z:\AI\SpriteSheetDiffusionSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\QwenImageEditSpike`
- `Z:\AI\Flux2RefControlSpike`

Video/reusable roots that remain active or potentially reusable:

- `Z:\AI\WanAnimate2`
- `Z:\AI\QwenImageEdit`
- `Z:\AI\Flux2Klein`
- `Z:\AI\FluxKontext`
- `Z:\AI\VideoStudioRuns`
- `Z:\AI\WanGP`

`Z:\AI\MiniMaxH3` is no longer storage-protected as a renderer payload. H3 remains historically documented; its two large model weights were approved for deletion because H3 failed the production-quality gate and is paused as a final renderer.

Cleanup result on 2026-09-15:

- recovered approximately **34.14 GB**;
- free space on `Z:` after cleanup: **65.66 GB**.

Old game material remains recoverable from Git history; Git history is not rewritten.

## Current hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`

## H3 conclusion — LOCKED

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

H3 proved the architecture but failed the user's production-quality bar, especially effective detail/resolution, anatomy/hands, texture stability, and generic presenter-like visual behavior. Do not resume H3 Base50 / SeedVR2 as the main strategy without new evidence.

## Wan S2V result — COMPLETED / BASELINE PRESERVED

First Wan2.2-S2V result used:

- Wan2.2 S2V 14B FP8 scaled;
- 480x832 vertical;
- 77-frame single chunk at 16 fps;
- 10 steps;
- CFG 6;
- `uni_pc` / `simple`;
- shift 8;
- seed 0;
- real João speech audio;
- no upscaler;
- no CosyVoice.

Measured inference runtime:

- **1713.2926 s = 28.55 min**.

Canonical classification:

**WAN S2V 10-STEP FP8: STRUCTURALLY PROMISING / PRODUCTION QUALITY FAIL.**

Relative strengths over H3:

- more stable body topology/shoulders;
- substantially better hand behavior;
- asymmetric, more natural conversational gestures;
- stable background/clothing/framing;
- broadly coherent face after an opening transient.

Remaining blockers:

- insufficient effective detail at 480x832;
- opening transient;
- eyeglass drift;
- beard/hairline/facial texture crawl;
- mouth/teeth/jaw softness;
- moving-hand detail loss;
- diffusion-style skin smoothing/temporal instability.

The first viewing MP4 contained 72 frames because the old FFmpeg mux used `-shortest` against 4.5 s audio; the evidence folder contains all 77 generated PNG frames. Runner v2 fixes the mux by padding audio.

## Wan quality baseline correction — LOCKED

Current ComfyUI documentation states that the non-Lightning Wan2.2-S2V quality path is **20 steps / CFG 6**. The completed 10-step render is therefore under-sampled relative to the documented quality baseline.

However, a 20-step repeat is expected to cost roughly **55–60 min** on this RTX 3060 based on the measured 28.55 min 10-step run.

**Decision: PAUSE the Wan 20-step A/B until HunyuanVideo-Avatar is tested.**

If Hunyuan is worse, return directly to Wan and run the controlled 20-step FP8 test. Do not discard Wan before that comparison.

## Active renderer benchmark — HunyuanVideo-Avatar

Next candidate:

**Hunyuan Video Avatar 720p 13B via DeepBeepMeep WanGP, quantized INT8 path.**

Why this route:

- HunyuanVideo-Avatar is specialized for reference-image + speech-driven human video;
- Tencent's original single-GPU path is not the practical Windows/12 GB route;
- WanGP is specifically designed to make these models usable on lower-VRAM GPUs;
- the local machine has 12 GB VRAM and Windows 11.

WanGP runtime bootstrap completed successfully on 2026-09-15:

- Python 3.11.14;
- Torch 2.10.0+cu130;
- CUDA 13.0 available;
- RTX 3060 detected;
- WanGP local footprint: **7.4 GB**.

Hunyuan payload disk gate now passes:

- free space on `Z:`: **65.66 GB** after H3 payload cleanup.

Candidate main checkpoint:

- `hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` (~13.4 GB).

INT8 text encoder:

- `llava-llama-3-8b/llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors` (~9.43 GB).

WanGP's current Hunyuan handler also requires CLIP-L, Whisper Tiny, face alignment, tokenizer/config assets and VAE payloads.

Important correction: **Hunyuan Avatar uses `hunyuan_video_custom_VAE_fp32.safetensors` + `hunyuan_video_custom_VAE_config.json`**. The current generic Hunyuan dependency definition also requests the standard VAE pair and the generic INT8 map, so the preparer mirrors that set to prevent additional downloads when the renderer starts.

Do not download the full Tencent repository.

## Direct comparison inputs — LOCKED

Reuse the exact same assets used for Wan:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

No CosyVoice yet.

WanGP's Hunyuan Avatar handler uses 25 fps and a default 129-frame segment, about 5.16 s, which is close enough to the Wan ~4.8 s gate for a useful direct visual comparison.

## Hunyuan decision rule

Use the same quality criteria as Wan/H3:

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

After one Hunyuan render:

- if Hunyuan clearly beats Wan 10-step, promote Hunyuan;
- if tied, compare runtime and resolution headroom;
- if worse, stop Hunyuan tuning and return to Wan 20-step;
- do not keep changing models without completing this direct gate.

## Video Studio implementation direction

`tools/video-studio/` remains the orchestration prototype and should evolve toward:

- persistent identity/profile assets;
- separate voice stage;
- optional scene/look still generation;
- interchangeable renderer backend;
- run manifests/evidence/timing;
- final assembly.

Do not resume one-minute workflow/UI polish until a single short shot is genuinely publishable.

## Immediate next action

Prepare the Hunyuan Avatar payload with the now-present repository-backed scripts:

- `tools/video-studio/prepare_hunyuan_avatar_benchmark.ps1`
- `tools/video-studio/prepare_hunyuan_avatar_benchmark.py`

Run the PowerShell wrapper with `-Download`. It downloads into `Z:\AI\WanGP\ckpts`, redirects Hugging Face/Xet global caches to `%LOCALAPPDATA%\VideoStudio\huggingface`, pins the benchmark image/audio, validates critical files, and writes a preparation manifest.

After payload preparation passes, run one Hunyuan Avatar benchmark using the same image and 4.5 s speech audio used for Wan.

Canonical Hunyuan procedure: `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`.
