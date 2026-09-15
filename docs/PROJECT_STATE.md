# Local Video Studio — Current Project State

Status date: **2026-09-15**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO.md`
3. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
4. `tools/video-studio/README.md`

All Roguelite/game-design, sprite, character-asset and game-runtime documents created before the 2026-09-15 pivot are now **historical evidence only**. They do not define the active product, implementation gate or production defaults.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Project pivot — LOCKED

The Roguelite game has been abandoned as the active objective because the visual-production burden is not useful enough for the user's current needs.

The repository is retained and repurposed rather than replaced.

Active objective:

> Build a local tool that lets the user write dialogue, choose a scenario and optionally specify appearance/framing, then generate a short realistic video of themselves speaking that new text with their own recognizable identity and voice, without recording a new video performance.

Target normal program length: **up to approximately 60 seconds**, assembled automatically from short generated shots.

Working title: **Local Video Studio**.

## Hardware / local runtime — LOCKED

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- AI root: `Z:\AI`
- active H3 runtime: `Z:\AI\MiniMaxH3`
- ComfyUI: `Z:\AI\MiniMaxH3\ComfyUI_windows_portable\ComfyUI`
- normal ComfyUI port: `8188`
- Video Studio UI port: `8765`
- generated-run root: `Z:\AI\MiniMaxH3\VideoStudioRuns`

The old repository-local path remains whatever checkout the user currently uses; old docs referenced `D:\GOOGLE DRIVE\DEV\Roguelite`. Do not make runtime media dependent on that historical folder name.

## Local-first production — HARD LOCK

Routine production must work locally after installation. Hosted video/avatar services may be evaluated as optional comparisons or accelerators, but they are not mandatory dependencies for normal use.

Normal authoring must not require direct ComfyUI graph editing.

## Main engine — MiniMax H3 Ref2VA / ACTIVE PROVEN

The already-installed MiniMax H3 stack is the active engine.

Installed core payload:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors`
- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`

H3 is now promoted from a game-motion specialist to the production speaking-video engine because the new use case was directly validated.

Canonical validation: `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`.

## Personal profile inputs — LOCKED FOR CURRENT USER

Current validated identity references:

- `joao_id_face.png`
- `joao_id_shoulders.png`
- `joao_id_upperbody.png`

Current validated voice reference:

- `joao_ref_voice.wav`

These files currently live under the H3 ComfyUI input directory and are configured in `tools/video-studio/config.example.json`.

The identity images are intentionally cropped. Their role is **identity/anatomy only**, not environment/style authority.

## Validated generation chain — HARD LOCK

The 2026-09-15 experiments proved:

```text
cropped identity stills
+ standalone voice reference
+ written Portuguese dialogue
+ target scene
+ optional clothing/framing
--------------------------------
MiniMax H3 Ref2VA
--------------------------------
recognizable user + generated voice + lip sync + autonomous movement + new environment
```

A driving/motion video is **not required** for the normal talking-video path.

### Test 1 — video + voice reference

`MiniMax_H3_00001_.mp4`

Passed identity, voice and basic lip sync, but inherited substantial gesture/motion trajectory from the driving video. This was insufficient for the final product goal.

### Test 2 — full-frame identity stills + voice / no video

`MiniMax_H3_00002_.mp4`

Passed identity, voice and autonomous motion with no driving video. Failed scene separation: H3 reproduced much of the room contained in the identity images.

### Test 3 — cropped identity stills + voice / no video / new scene

`MiniMax_H3_00003_.mp4`

Passed the required gate:

- identity preserved;
- voice preserved and explicitly approved by the user;
- new written dialogue spoken;
- lip synchronization acceptable;
- autonomous blinking/head/body/hand motion;
- no driving video;
- clearly different requested environment;
- local RTX 3060 execution.

## Reference-role contract — HARD LOCK

For normal jobs:

- `<Picture 1..N>` = identity only;
- `<Audio 1>` = voice identity only;
- scenario field = environment authority;
- appearance field = clothing/appearance authority;
- framing field = camera crop authority;
- there is no `<Video 1>` movement authority.

Prompts must explicitly reject carrying the identity references' room, furniture, windows, bottles, equipment, colors, lighting and composition into the new scene.

Full-frame room images are not canonical identity inputs.

## Current production preset — ACTIVE

The first production default is the **validated high-resolution Turbo4 avatar path**:

- task: Ref2VA;
- output: 768×1344 vertical;
- 24 fps;
- Ref2V Turbo 4-step LoRA at 1.0;
- 4 steps;
- sampler: `res_multistep`;
- scheduler: `simple`;
- `ref_image_size=max`;
- H3 sigma shifts: video 12 / audio 3;
- deterministic seed supplied by the Studio, incremented per shot.

This does **not** revoke the historical finding that Turbo4 was inadequate for the old game-motion-master task. That finding was task-specific. For the present talking-video task, the 4-step route passed the practical gate and is therefore the correct current default until a controlled comparison proves otherwise.

Available controlled alternatives:

- `draft`: Turbo4 at 480×864;
- `quality`: Base20, 768×1344, `res_multistep/beta`;
- `max`: Base50, 768×1344, `res_multistep/beta`.

Base20/Base50 are not yet declared superior for the present use case.

## Long-form strategy — LOCKED

Do not ask H3 to generate a continuous one-minute clip.

For ~15–60 second programs:

1. sentence-aware script segmentation;
2. estimate speech duration per segment;
3. keep generated shots <= ~12.5 s;
4. align each shot to H3's valid 24 fps `17k+5` frame structure;
5. generate serially on the single GPU;
6. concatenate automatically with FFmpeg;
7. preserve per-shot prompts/API graphs and a final job manifest.

Multiple scene descriptions may be separated by `---`; the Studio maps them to successive shots.

## Current implementation — Local Video Studio MVP / ACTIVE

New active tool:

`tools/video-studio/`

Normal launch:

```powershell
.\tools\video-studio\start_video_studio.ps1
```

Normal UI:

`http://127.0.0.1:8765/`

Implemented architecture:

`local web UI -> Video Studio orchestrator -> ComfyUI HTTP API -> H3 Ref2VA -> native video+audio -> FFmpeg shot assembly -> final MP4 + manifest`

The backend is Python-standard-library-only and is designed to run with the existing H3 portable embedded Python. It automatically starts the current ComfyUI launcher when needed and serializes GPU jobs.

Normal user controls:

- text to speak;
- scenario;
- optional clothing/appearance;
- framing;
- quality preset;
- seed;
- Generate.

Normal users should not touch the ComfyUI graph.

## Evidence / reproducibility contract

Each Video Studio job records locally:

- request JSON;
- compiled H3 prompt per shot;
- ComfyUI API graph per shot;
- prompt id;
- elapsed time;
- local copy of each shot;
- SHA-256 of profile references, shots and final video;
- final manifest.

Generated media and local mutable configuration are not committed to Git.

## Supporting image tools — RETAIN

These remain useful because scenario/reference preparation and identity-pack refinement may benefit from still-image generation/editing:

- `Z:\AI\QwenImageEdit`
- `Z:\AI\Flux2Klein`
- `Z:\AI\FluxKontext` — retain until Qwen/Klein fully replace any useful role.

They are support tools, not required by the first Video Studio MVP path.

## Former game-only local payload — RETIRED / CLEANUP CANDIDATES

The following are no longer active production infrastructure for the new project:

- `Z:\AI\RogueliteAssetStudio`
- `Z:\AI\SpriteSheetDiffusionSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\QwenImageEditSpike`
- game-specific contents of `Z:\AI\Flux2RefControlSpike`

`Z:\AI\WanAnimate2` is not required for the current Video Studio path and may be removed when disk cleanup is performed; preserve only evidence/configuration that is useful historically before deleting large weights.

`PowerPaint`, `LaMaInpaint` and `SDXLInpaint` have no active role in the Video Studio MVP and should not be expanded further. Delete only after confirming there is no unrelated personal use for those local folders.

Repository history is not mass-deleted. Old tools/docs remain historical evidence unless they obstruct active development.

## Current gate

**VIDEO-STUDIO-MVP-01**

Goal: make the validated H3 configuration usable without manual ComfyUI work.

PASS requires:

1. one-command local launcher;
2. localhost form for text/scenario/appearance/framing/preset;
3. automatic profile injection;
4. automatic script splitting for longer text;
5. serial H3 generation;
6. automatic final MP4 assembly;
7. local run manifest/evidence;
8. no manual node-graph editing during normal operation.

Implementation has been committed under `tools/video-studio/`. The next operational step is running `start_video_studio.ps1 -PreflightOnly`, then generating the first end-to-end video through the new interface.

## Next quality gate

After MVP execution is confirmed, run one controlled A/B on identical identity/voice/text/scene/seed:

- validated `production` Turbo4;
- Base20 `quality`;
- Base50 `max` only if Base20 suggests a meaningful improvement.

Judge:

- facial identity;
- temporal stability;
- voice/lip synchronization;
- naturalness of autonomous gesture;
- hands;
- scene compliance;
- visual detail;
- elapsed time.

Do not replace H3 or install another avatar model before this finite comparison unless a concrete blocker appears.
