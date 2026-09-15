# Local Video Studio

This is the active local production tool for the project.

It hides the ComfyUI graph behind a small localhost interface and turns the validated MiniMax H3 Ref2VA workflow into the normal operation:

`text + scene + optional appearance -> identity refs + voice ref -> H3 clips -> final MP4`

## Current production contract

- local-first: routine generation must work after installation without a hosted generation service;
- engine: MiniMax H3 Ref2VA through the existing `Z:\AI\MiniMaxH3` portable ComfyUI;
- identity: three canonical cropped references, currently `joao_id_face.png`, `joao_id_shoulders.png`, `joao_id_upperbody.png`;
- voice: `joao_ref_voice.wav`;
- no driving video is required for the normal talking-video path;
- output: vertical 9:16, generated in H3-safe short clips and concatenated automatically;
- current job limit: approximately 60 seconds;
- normal user operation must not require editing a ComfyUI graph.

The three-reference + voice + new-scene configuration was validated on 2026-09-15 on Windows 11 / RTX 3060 12 GB / 48 GB RAM. See `../../docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`.

## Start

From the repository root in PowerShell:

```powershell
.\tools\video-studio\start_video_studio.ps1
```

The launcher creates `config.json` from `config.example.json` on first run and opens:

```text
http://127.0.0.1:8765/
```

The default example is already pointed at the current `Z:\AI\MiniMaxH3` installation and the validated identity/voice references.

To validate the installation without opening the UI:

```powershell
.\tools\video-studio\start_video_studio.ps1 -PreflightOnly
```

## Interface

The UI intentionally exposes only production decisions:

- **Texto que será falado** — Brazilian Portuguese dialogue; longer scripts are segmented automatically.
- **Cenário** — target environment. Separate multiple scene descriptions with a line containing only `---`.
- **Roupa / aparência** — optional clothing/appearance instruction.
- **Enquadramento** — close, medium, or American shot.
- **Qualidade** — generation preset.
- **Seed** — deterministic starting seed; subsequent clips increment it by one.

The identity images and voice sample are profile data, not normal per-job inputs.

## Presets

### `production` — default / validated

- 768×1344;
- MiniMax H3 Ref2VA INT8;
- Ref2V Turbo LoRA;
- 4 steps;
- `res_multistep` + `simple`;
- `ref_image_size=max`;
- sigma shifts 12/3.

This is the first production preset because the 2026-09-15 tests validated identity, voice, autonomous movement and scenario separation with the 4-step path at the high-resolution vertical canvas.

### `draft`

Same fast path at 480×864 for cheap composition/script checks.

### `quality`

- 768×1344;
- Base H3, no Turbo LoRA;
- 20 steps;
- `res_multistep` + `beta`.

This is available for controlled A/B testing; it is not yet declared superior to `production` for this talking-video use.

### `max`

- 768×1344;
- Base H3, no Turbo LoRA;
- 50 steps;
- `res_multistep` + `beta`.

Very slow on the RTX 3060. The old game-motion spike proved that Base50 could materially improve a different motion-master use case, but that verdict does not automatically transfer to the present avatar-video task.

## Long videos

MiniMax H3 works best as a short-shot generator. The Studio therefore does not ask it for a continuous 60-second generation.

The backend:

1. splits the script into sentence-aware chunks;
2. estimates a natural duration from the amount of dialogue;
3. snaps each clip to H3's valid `17k+5` frame structure at 24 fps;
4. generates each clip serially on the single GPU;
5. concatenates the resulting MP4 files with FFmpeg;
6. stores prompts, API graphs, hashes and a run manifest under the job directory.

Default output root:

```text
Z:\AI\MiniMaxH3\VideoStudioRuns
```

## Scene contamination rule

Identity references are deliberately cropped. Prompts explicitly state that their backgrounds, furniture, windows, bottles, equipment, lighting and composition are **not** scene references. This is not cosmetic: the full-frame reference test copied the original room, while the cropped-reference test successfully generated a different room.

Do not replace the canonical cropped identity references with full-frame room photographs without treating that as a new experiment.

## CLI

The web UI is only a front-end. The same backend can be called from PowerShell:

```powershell
$py = "Z:\AI\MiniMaxH3\ComfyUI_windows_portable\python_embeded\python.exe"
& $py .\tools\video-studio\video_studio.py `
  --config .\tools\video-studio\config.json `
  generate `
  --text "Este é um teste." `
  --scenario "um laboratório fotográfico escuro e organizado" `
  --preset production
```

## Implementation notes

- Python standard library only; no new venv/pip environment is required.
- ComfyUI is automatically started with the existing `run_nvidia_gpu.bat` when it is not already active.
- The backend submits API-format graphs to `/prompt` and polls `/history/<prompt_id>`.
- GPU jobs are serialized so two browser requests cannot try to run H3 concurrently.
- Each clip uses the installed video VAE and audio VAE and is muxed with native generated audio.
- FFmpeg is used only for final multi-clip assembly.

## Files

- `video_studio.py` — backend, H3 API graph builder, job runner, local HTTP server.
- `index.html` — intentionally small local interface.
- `config.example.json` — current machine/profile defaults without committing mutable `config.json`.
- `start_video_studio.ps1` — Windows launcher.

Canonical state is `../../docs/PROJECT_STATE.md`.
