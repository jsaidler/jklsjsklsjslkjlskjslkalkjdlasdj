# Local Video Studio

This is the active local prototype for the current project.

It hides the ComfyUI graph behind a localhost interface and turns the MiniMax H3 Ref2VA workflow into:

`text + scene + optional appearance -> identity refs + voice ref -> H3 clips -> MP4`

## Current status

**Functional architecture: validated.**  
**Production visual quality: NOT approved.**

The 2026-09-15 tests proved that the installed local H3 stack can:

- preserve recognizable identity from still references;
- use the user's voice reference for new Portuguese dialogue;
- generate autonomous motion without a driving video;
- generate a scene different from the source-reference room when cropped identity references are used.

They did **not** prove that the visual result is good enough for publication. The active gate is `../../docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`.

Do not describe the current Turbo4 result as `production validated` or `production-ready`.

## Current architecture contract

- local-first;
- engine candidate: MiniMax H3 Ref2VA through `Z:\AI\MiniMaxH3`;
- identity: `joao_id_face.png`, `joao_id_shoulders.png`, `joao_id_upperbody.png`;
- voice: `joao_ref_voice.wav`;
- no driving video required for the normal recording-free hypothesis;
- normal authoring should not require ComfyUI graph editing;
- quality work on one short shot takes precedence over one-minute/multi-shot polish.

## Start / preflight

From the repository root:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File `
'.\tools\video-studio\start_video_studio.ps1' `
-PreflightOnly
```

The launcher creates `config.json` from `config.example.json` on first run.

To open the prototype UI:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File `
'.\tools\video-studio\start_video_studio.ps1'
```

Interface:

```text
http://127.0.0.1:8765/
```

## Preset status

The first MVP backend still contains the key name `production` for compatibility. **That key name is historical and does not mean production quality.**

### `draft`

Turbo4 at 480×864. Smoke test only.

### `production` — legacy key / fast baseline

- 768×1344;
- MiniMax H3 Ref2VA INT8;
- Ref2V Turbo LoRA;
- 4 steps;
- `res_multistep` + `simple`;
- `ref_image_size=max`.

Functionally successful, visually **not accepted as production quality**.

### `quality`

- 768×1344;
- Base H3, no Turbo LoRA;
- 20 steps;
- `res_multistep` + `beta`;
- `ref_image_size=max`.

First active quality candidate.

### `max`

- 768×1344;
- Base H3, no Turbo LoRA;
- 50 steps;
- `res_multistep` + `beta`;
- `ref_image_size=max`.

Maximum defined H3 quality candidate; potentially very slow on the RTX 3060.

## Active task: controlled visual-quality benchmark

Run the quality gate before treating the Studio as a production tool.

The benchmark keeps identity references, voice, text, scenario, framing and seed fixed while changing only the sampling preset.

Canonical criteria include:

- face/identity stability;
- eyes/glasses/hair/beard;
- mouth/teeth/jaw;
- hands/fingers/wrists/arms;
- natural body performance;
- skin/detail texture;
- clothing stability;
- background geometry stability;
- lighting/camera coherence;
- voice/AV synchronization;
- overall publishability without manual frame repair.

## Interface

The existing UI exposes:

- dialogue;
- scenario;
- optional clothing/appearance;
- framing;
- quality preset;
- seed.

It is currently a prototype harness. Productization resumes only after the visual-quality gate passes.

## Output/evidence

Default output root:

```text
Z:\AI\MiniMaxH3\VideoStudioRuns
```

Jobs preserve prompts, API graphs, hashes and manifests. Generated media stays local and is not committed to Git.

## Files

- `video_studio.py` — existing backend/orchestrator;
- `index.html` — local UI;
- `config.example.json` — machine/profile defaults;
- `start_video_studio.ps1` — Windows launcher;
- `run_quality_gate.py` — controlled single-shot H3 quality comparison;
- `run_quality_gate.ps1` — PowerShell entry point for that comparison.

Canonical state: `../../docs/PROJECT_STATE.md`.