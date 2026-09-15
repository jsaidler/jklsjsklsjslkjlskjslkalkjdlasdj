# Local Video Studio — Current Project State

Status date: **2026-09-15**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO.md`
3. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
4. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
5. `tools/video-studio/README.md`

All Roguelite/game-design, sprite, character-asset and game-runtime documents created before the 2026-09-15 pivot are historical evidence only. They do not define the active product or current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Project pivot — LOCKED

The Roguelite game is abandoned as the active objective. The repository is retained and repurposed.

Active objective:

> Build a local tool that lets the user write dialogue, choose a scenario and optionally specify appearance/framing, then generate a short realistic video of themselves speaking that new text with their own recognizable identity and voice, without recording a new video performance.

Target normal program length: up to approximately 60 seconds, assembled automatically from short generated shots.

Working title: **Local Video Studio**.

## Hardware / local runtime — LOCKED

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- repo checkout: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active H3 runtime: `Z:\AI\MiniMaxH3`
- ComfyUI: `Z:\AI\MiniMaxH3\ComfyUI_windows_portable\ComfyUI`
- ComfyUI port: `8188`
- Video Studio UI port: `8765`
- generated-run root: `Z:\AI\MiniMaxH3\VideoStudioRuns`

## Critical correction — PRODUCTION QUALITY NOT VALIDATED

The 2026-09-15 H3 tests validated the **functional architecture**, not production visual quality.

Canonical classification:

**FUNCTIONAL / ARCHITECTURAL PASS — PRODUCTION QUALITY FAIL / OPEN GATE.**

The tests proved that the installed local stack can:

- preserve recognizable identity;
- use the user's voice reference for new Portuguese dialogue;
- produce useful lip synchronization;
- generate autonomous body motion without a driving video;
- separate identity references from a newly requested environment when cropped identity references are used;
- execute locally on the RTX 3060.

They did **not** establish that the resulting image quality is acceptable for publication/production.

The user explicitly rejected that interpretation after reviewing the generated videos. Therefore all previous wording such as **production validated**, **production preset**, or **fit for production** is retired until the visual-quality gate passes.

Known visual concerns already observed in discussion include generic "AI presenter" gesture language and hand/pose behavior. Additional visual defects visible in the actual outputs remain part of the open quality review and must not be hand-waved away by the functional pass.

## Active engine — MiniMax H3 Ref2VA / CANDIDATE, NOT YET PRODUCTION-APPROVED

Installed core payload:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors`
- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`

H3 remains the first candidate because it proved the required architecture locally. It is not locked as the final production engine until controlled quality testing is exhausted.

Do not install another avatar/video engine merely because it exists. A replacement becomes justified if the finite H3 quality ladder fails to reach the required visual standard.

## Personal profile inputs — FUNCTIONALLY VALIDATED

Current identity references:

- `joao_id_face.png`
- `joao_id_shoulders.png`
- `joao_id_upperbody.png`

Current voice reference:

- `joao_ref_voice.wav`

The identity images are intentionally cropped. Their role is identity/anatomy evidence only, not environment/style authority.

## Functional generation chain — PROVEN

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

A driving/motion video is not required for the normal talking-video hypothesis.

### Test 1 — video + voice reference

`MiniMax_H3_00001_.mp4`

Passed identity/voice/basic lip-sync behavior but inherited substantial gesture trajectory from the driving video. It did not prove recording-free operation.

### Test 2 — full-frame identity stills + voice / no driving video

`MiniMax_H3_00002_.mp4`

Proved autonomous motion without a driving video but failed scene separation because H3 reproduced much of the room contained in the identity images.

### Test 3 — cropped identity stills + voice / no driving video / new scene

`MiniMax_H3_00003_.mp4`

Passed the functional gate:

- recognizable identity;
- stable-enough identity for the spike;
- voice explicitly judged good by the user;
- new dialogue;
- useful lip synchronization;
- autonomous blinking/head/body/hand motion;
- no driving video;
- different requested environment;
- local execution.

It **did not pass the production visual-quality gate**.

## Reference-role contract — RETAIN

For image-only talking-video experiments:

- `<Picture 1..N>` = identity only;
- `<Audio 1>` = voice identity only;
- scenario field = environment authority;
- appearance field = clothing/appearance authority;
- framing field = camera crop authority;
- no `<Video 1>` movement authority in the normal recording-free path.

Prompts must explicitly reject carrying the identity references' room/composition into the new scene.

## Current presets — EXPERIMENTAL ONLY

No preset is currently called production.

Existing backend keys remain temporarily for compatibility with the first MVP code, but their status is:

- `draft`: Turbo4 at 480×864 — cheap functional/composition test only;
- `production`: **legacy key name only**; Turbo4 at 768×1344 — functional baseline, visually rejected as a production claim;
- `quality`: Base20 at 768×1344, `res_multistep/beta` — unvalidated quality candidate;
- `max`: Base50 at 768×1344, `res_multistep/beta` — unvalidated maximum-quality H3 candidate, very slow.

The UI/documentation must not present the legacy `production` key as approved production quality.

## Current gate — VIDEO-STUDIO-QUALITY-01 / ACTIVE

The next step is **not** general UI polish and not one-minute assembly. First establish a visually acceptable single short shot.

Canonical quality procedure: `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`.

Controlled comparison uses identical:

- identity references;
- voice reference;
- dialogue;
- scenario;
- appearance;
- framing;
- seed;
- output canvas.

Finite H3 ladder:

1. Turbo4 768×1344 as the rejected functional baseline;
2. Base20 768×1344;
3. Base50 768×1344 if Base20 is materially better or still leaves plausible room for improvement;
4. if sampling quality is not enough, improve the canonical identity-reference pack and repeat the best sampler path;
5. only after exhausting those variables consider a different local video/avatar engine.

No result is promoted merely because it is more expensive/slower.

## Production visual acceptance criteria — HARD GATE

A candidate must be reviewed at full size and in motion for:

1. facial identity and facial geometry from first to last frame;
2. eyes, eyelids, eyeglasses, beard/hairline and teeth/mouth stability;
3. lip/jaw motion without rubbery or synthetic deformation;
4. hands/fingers/wrists/elbows and absence of anatomically implausible gestures;
5. natural, non-repetitive body performance without generic AI-presenter choreography;
6. clothing topology/material stability;
7. skin/detail texture without obvious waxy diffusion artifacts;
8. background geometry/object stability and absence of melting/morphing;
9. scene/composition compliance;
10. voice identity and audiovisual synchronization;
11. absence of distracting temporal flicker, identity drift or local warping;
12. overall result being acceptable for public release without manual frame repair.

A failure on a conspicuous defect is a production failure even if identity/voice technically pass.

## Local Video Studio MVP — IMPLEMENTED PROTOTYPE, NOT PRODUCTION TOOL YET

Implementation exists under:

`tools/video-studio/`

Architecture:

`local web UI -> orchestrator -> ComfyUI HTTP API -> H3 Ref2VA -> video+audio -> FFmpeg assembly`

This remains useful infrastructure, but productization is paused behind the active quality gate. Do not spend effort on multi-shot/60-second polish until a single-shot quality preset passes.

Normal authoring must ultimately hide ComfyUI, but the immediate development priority is quality, not interface completeness.

## Supporting image tools — RETAIN

Potentially useful for a stronger canonical identity pack or controlled scene/reference preparation:

- `Z:\AI\QwenImageEdit`
- `Z:\AI\Flux2Klein`
- `Z:\AI\FluxKontext`

## Former game-only payload — RETIRED / CLEANUP CANDIDATES

No longer active for the new project:

- `Z:\AI\RogueliteAssetStudio`
- `Z:\AI\SpriteSheetDiffusionSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\QwenImageEditSpike`
- game-specific contents of `Z:\AI\Flux2RefControlSpike`

`Z:\AI\WanAnimate2` is not part of the current H3 quality ladder. Do not delete it solely to simplify the narrative before the Video Studio engine decision is closed; it may still be useful as retained comparison infrastructure if H3 fails.

Repository history remains intact as evidence.

## Immediate next action

Run the controlled H3 quality benchmark, starting with the high-resolution Turbo4 baseline and Base20 under identical conditions. Review the actual MP4s before deciding whether Base50 is justified.

Do **not** call any result production-ready until the user explicitly approves the visual quality.