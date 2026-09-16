# Local Video Studio — Current Project State

Status date: **2026-09-16**

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

H3 proved the architecture but failed the production-quality bar, especially effective detail/resolution, anatomy/hands, texture stability, and generic presenter-like visual behavior. Do not resume H3 Base50 / SeedVR2 as the main strategy without new evidence.

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

A 20-step repeat is expected to cost roughly **55–60 min** on this RTX 3060 based on the measured 28.55 min 10-step run.

**Decision: PAUSE the Wan 20-step A/B until HunyuanVideo-Avatar is tested.**

If Hunyuan is worse, return directly to Wan and run the controlled 20-step FP8 test. Do not discard Wan before that comparison.

## Active renderer benchmark — HunyuanVideo-Avatar

Current classification:

**HUNYUAN AVATAR: RUNTIME PASS / PAYLOAD PREPARED / DRY-RUN PASS / DIRECT RENDER READY.**

Candidate:

**Hunyuan Video Avatar 720p 13B via DeepBeepMeep WanGP, quantized INT8 path.**

WanGP runtime bootstrap completed successfully on 2026-09-15:

- Python 3.11.14;
- Torch 2.10.0+cu130;
- CUDA 13.0 available;
- RTX 3060 detected;
- WanGP local footprint: **7.4 GB**.

### Payload preparation — PASS

Validated critical payload:

- `hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — **12.486 GB**;
- `llava-llama-3-8b/llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors` — **8.785 GB**;
- `clip_vit_large_patch14/model.safetensors` — **1.593 GB**;
- `whisper-tiny/model.safetensors` — **0.141 GB**;
- `det_align/detface.pt` — **0.174 GB**;
- `hunyuan_video_custom_VAE_fp32.safetensors` — **0.918 GB**;
- `hunyuan_video_custom_VAE_config.json`.

Preparation result:

- downloaded: **26 files**;
- reused: **0 files**;
- free space on `Z:` after payload: **40.63 GB**;
- manifest: `Z:\AI\WanGP\hunyuan_avatar_benchmark_prepare_manifest.json`;
- report: `D:\GOOGLE DRIVE\DEV\Roguelite\tools\video-studio\reports\hunyuan_avatar_prepare_20260915_234228.txt`.

Important correction retained: **Hunyuan Avatar uses `hunyuan_video_custom_VAE_fp32.safetensors` + `hunyuan_video_custom_VAE_config.json`.**

### Programmatic execution path — VERIFIED

Current upstream WanGP provides a supported Python API at `shared/api.py`. The benchmark uses `session.submit_task(settings)` rather than Gradio/browser automation or guessed internal callbacks.

Verified settings contract for Hunyuan Avatar:

- `image_refs` with model-exposed `video_prompt_type="KI"` for the single reference image;
- `audio_guide` with `audio_prompt_type="A"` for speech conditioning;
- 25 fps model metadata;
- default 129 frames;
- CFG 7.5;
- flow shift 5;
- common default 30 inference steps;
- background removal off;
- `skip_steps_cache_type=""` disables step-skipping cache such as TeaCache/MagCache.

Repository runner:

- `tools/video-studio/run_hunyuan_avatar_benchmark.ps1`
- `tools/video-studio/run_hunyuan_avatar_benchmark.py`

The runner dynamically discovers the installed Avatar model, reads local defaults/schema/availability and refuses to submit if the installed runtime no longer exposes the required image/audio modes.

### Initial runner compatibility error — FIXED / NO INFERENCE SUBMITTED

At the first direct execution on 2026-09-16, WanGP initialization failed immediately with:

```text
wgp.py: error: unrecognized arguments: --teacache 0
```

This was a runner compatibility bug, not a renderer/model failure. The runner had incorrectly treated TeaCache as a WanGP startup CLI switch.

Correction applied:

- removed startup `--teacache 0`;
- retained supported startup `--profile 4` and `--attention sdpa`;
- TeaCache remains disabled correctly at task level through `skip_steps_cache_type=""`;
- patch commit: `7d77ce33c0d21b5259b8d21a2f8b95caf521197c`.

Because the failure occurred before task submission, **no Hunyuan GPU inference time or visual result was produced by that attempt**.

### Compatibility dry-run — PASS

The patched runner completed a zero-inference compatibility gate on 2026-09-16.

Evidence:

`Z:\AI\VideoStudioRuns\hunyuan-avatar-gates\20260916_003617`

Observed runtime state:

- WanGP v13.02 initialized;
- model discovery: PASS;
- model type: `hunyuan_avatar`;
- availability: `available`;
- reference mode: `KI`;
- audio mode: `A`;
- runtime default frames: 129;
- runtime default steps: 30;
- runtime default CFG: 7.5;
- runtime default flow shift: 5;
- dry-run: **PASS, no generation submitted**.

WanGP downloaded an FFmpeg 9.0.1 essentials package during initialization; this was a runtime dependency setup action, not renderer inference.

The API/schema compatibility gate is now closed. Do not rerun preparation or another dry-run unless the WanGP runtime changes.

### Direct benchmark settings — LOCKED

- same pinned reference image and real 4.5 s speech audio used for Wan;
- 720x1280 portrait;
- 129 frames at native 25 fps (~5.16 s);
- 30 steps;
- CFG 7.5;
- flow shift 5;
- seed 0;
- WanGP profile 4;
- SDPA attention;
- TeaCache off through `skip_steps_cache_type=""`;
- no CosyVoice;
- no spatial/temporal upscale;
- no face retouch;
- no film grain or audio post-processing.

The first Hunyuan run is intentionally 720p-class rather than matching Wan's lower 480x832 pixel count. The product question is whether this local engine can produce a publishable result at its intended quality level. Runtime is part of the verdict.

Evidence root:

`Z:\AI\VideoStudioRuns\hunyuan-avatar-gates\<timestamp>\`

The runner preserves settings, model metadata/defaults/schema/availability, log, result, manifest and final video. Default watchdog ceiling is **180 minutes**; reaching it is a local-practicality failure.

No Hunyuan renderer output has been produced yet.

## Direct comparison inputs — LOCKED

Source assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

Pinned WanGP copies:

- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_ref.png`
- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_test_4p5s.wav`

## Hunyuan decision rule

Evaluate the same production criteria as Wan/H3:

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

- if Hunyuan clearly beats Wan 10-step, promote Hunyuan and move to CosyVoice integration;
- if tied, compare runtime and resolution headroom;
- if worse, stop Hunyuan tuning and return to Wan 20-step;
- if it OOMs or exceeds the runtime ceiling, treat the local route as impractical and evaluate hosted/rented-GPU execution before degrading quality.

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

Do **not** rerun Hunyuan payload preparation or the dry-run.

Pull `main` and execute exactly one full direct Hunyuan Avatar benchmark with `tools/video-studio/run_hunyuan_avatar_benchmark.ps1`, using the locked 720x1280 / 129-frame / 30-step / seed 0 settings. Then inspect the generated video against the completed Wan 10-step baseline and update the canonical verdict.

Canonical Hunyuan procedure: `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`.
