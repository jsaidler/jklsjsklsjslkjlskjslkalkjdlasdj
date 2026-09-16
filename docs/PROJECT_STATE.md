# Local Video Studio — Current Project State

Status date: **2026-09-16**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
3. `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`
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

## Current hardware

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`

## Storage cleanup state

H3's two large retired model weights were removed after its production-quality failure.

Cleanup result:

- recovered approximately **34.14 GB**;
- free `Z:` after cleanup: **65.66 GB**.

Hunyuan payload preparation later reduced free `Z:` to approximately **40.63 GB**.

Protected/reusable active roots:

- `Z:\AI\WanAnimate2`
- `Z:\AI\WanGP`
- `Z:\AI\QwenImageEdit`
- `Z:\AI\Flux2Klein`
- `Z:\AI\FluxKontext`
- `Z:\AI\VideoStudioRuns`

`Z:\AI\MiniMaxH3` is no longer storage-protected as a renderer payload.

## H3 conclusion — LOCKED

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

H3 proved the architecture but failed the production-quality bar, especially effective detail/resolution, anatomy/hands, texture stability and generic presenter-like behavior. Do not resume H3 Base50 / SeedVR2 as the main strategy without new evidence.

## Wan2.2-S2V — ACTIVE LOCAL CANDIDATE

Completed baseline:

- Wan2.2 S2V 14B FP8 scaled;
- 480x832;
- 77 generated frames at 16 fps;
- 10 steps;
- CFG 6;
- `uni_pc` / `simple`;
- shift 8;
- seed 0;
- real João speech audio;
- no CosyVoice;
- no upscaler.

Measured graph runtime:

- **1713.2926 s = 28.55 min**.

Canonical classification:

**WAN S2V 10-STEP FP8: STRUCTURALLY PROMISING / PRODUCTION QUALITY FAIL.**

Strengths over H3:

- more stable body topology/shoulders;
- substantially better hand behavior;
- asymmetric, more natural gestures;
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

The old viewing MP4 contained only 72 frames because FFmpeg used `-shortest`; all 77 lossless generated frames exist in evidence. Runner v2 fixes the mux.

### Wan sampling correction — LOCKED

Current ComfyUI documentation identifies the non-Lightning Wan2.2-S2V quality path as **20 steps / CFG 6**. The completed 10-step result is therefore under-sampled relative to the documented baseline.

A 20-step repeat is expected to cost roughly **55–60 min** on this machine based on the measured 10-step run.

**Decision now: RUN the controlled Wan 20-step FP8 A/B.**

The previous pause is retired because the Hunyuan local comparison failed on runtime practicality before producing a visual result.

Do not jump to Wan 720p yet. First determine whether 20-step sampling produces a clearly meaningful visual gain at the existing 480x832 gate.

## HunyuanVideo-Avatar — LOCAL PRACTICALITY FAIL

Candidate tested:

**Hunyuan Video Avatar 720p 13B via DeepBeepMeep WanGP, INT8 path.**

WanGP runtime bootstrap passed:

- Python 3.11.14;
- Torch 2.10.0+cu130;
- CUDA 13.0;
- RTX 3060 detected;
- WanGP v13.02;
- runtime footprint approximately 7.4 GB before model payload.

Payload preparation passed. Critical files include:

- Hunyuan Avatar INT8 transformer: **12.486 GB**;
- LLaVA INT8 text/VLM payload: **8.785 GB**;
- CLIP: **1.593 GB**;
- Whisper Tiny: **0.141 GB**;
- face alignment model: **0.174 GB**;
- custom Hunyuan VAE: **0.918 GB**.

The current Avatar implementation requires the custom Hunyuan VAE.

### API/schema compatibility — PASS

Dry-run evidence:

`Z:\AI\VideoStudioRuns\hunyuan-avatar-gates\20260916_003617`

Runtime confirmed:

- model type `hunyuan_avatar`;
- availability `available`;
- reference mode `KI`;
- audio mode `A`;
- 129 frames;
- 30 steps;
- CFG 7.5;
- flow shift 5;
- native 25 fps.

The earlier unsupported `--teacache 0` startup argument was removed; TeaCache is disabled correctly through task setting `skip_steps_cache_type=""`.

### Full local quality gate — TIMEOUT

Locked full benchmark:

- 720x1280;
- 129 frames;
- 25 fps;
- 30 steps;
- CFG 7.5;
- flow shift 5;
- seed 0;
- profile 4;
- SDPA;
- TeaCache off;
- no upscale or retouch;
- same identity image and real 4.5 s speech audio as Wan.

Observed result on 2026-09-16:

- repeated loading/prefetching/unloading of `HYVideoDiffusionTransformer` double blocks between RAM and GPU;
- after about **2 h 54 min**, progress still showed **`0/30`** denoising steps completed;
- 180-minute watchdog cancelled generation;
- no output video and no completed visual frame were produced.

Canonical classification:

**HUNYUAN AVATAR LOCAL 720P: FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / PRACTICALITY FAIL ON RTX 3060 12 GB.**

This is not a Hunyuan quality rejection. It rejects the local 12 GB quality-oriented route because block offload makes throughput unusable.

Do not attempt to rescue the local Hunyuan gate by lowering resolution, lowering the 30-step baseline, enabling aggressive cache/step skipping, or extending the watchdog. A future rented 48 GB GPU comparison remains valid if needed.

## Direct comparison assets — LOCKED

Wan source assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

Pinned Hunyuan copies:

- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_ref.png`
- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_test_4p5s.wav`

CosyVoice remains deferred until the renderer gate is passed.

## Quality gate — LOCKED

Evaluate renderers on:

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

Any conspicuous blocker is a production failure.

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

Run exactly one controlled **Wan2.2-S2V 20-step FP8** benchmark with the same seed and existing 480x832 settings.

Repository runner:

- `tools/video-studio/run_wan_s2v_benchmark.ps1`
- `tools/video-studio/run_wan_s2v_benchmark.py`

Command parameters:

- seed 0;
- steps 20;
- no `-LowVram` unless an actual OOM occurs.

After the render, compare it directly against the completed 10-step evidence. The 20-step result must improve clearly, not marginally, in face/beard, mouth, glasses, temporal texture and moving-hand definition to justify further local Wan escalation.

Canonical Wan procedure: `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`.