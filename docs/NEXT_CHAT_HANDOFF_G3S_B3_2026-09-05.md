# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
4. `docs/G1_CAMERA_SCALE_LOG.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G3S_C1B_SEGMENTED_PUPPET.md`

## Locked production direction

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed `640×360` orthographic camera, pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- no north/south/isometric sprite-family multiplication;
- final runtime = conventional deterministic spritesheet playback.

Runtime does not require 3D, a segmented puppet or diffusion.

## Current source-authoring route

**Sprite Sheet Diffusion (SSD)** validation spike.

Canonical doc:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Purpose: test whether SSD can produce a coherent Exilada action sequence from the complete master plus pose/motion guidance, after which accepted frames are frozen into ordinary spritesheets.

## Verified upstream facts

Repo:

`chenganhsieh/Sprite-Sheet-Diffusion`

- inference: `ModelTraining/inference.py`;
- config: `ModelTraining/configs/prompts/inference.yaml`;
- actual dependency file: `ModelTraining/requirements.txt`;
- no root requirements file despite README command;
- model paths required later: SD1.5 base, VAE, CLIP image encoder, SSD denoising/reference UNets, AnimateAnyone pose guider and motion module.

## Actual local state — environment PASS

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

- upstream clone: SUCCESS;
- Miniconda: SUCCESS;
- conda: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- env `ssd`: PASS;
- Python: `3.10.21`;
- pip: `26.2.1`;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`.

No model weights downloaded yet.

## Current dependency decisions

Project Windows inference lock:

`tools/structured-2d-character-pipeline/ssd_windows_inference_requirements.txt`

- torch `2.0.1` + torchvision `0.15.2` installed from official CUDA 11.8 wheels;
- `xformers` deferred because it is optional for inference and the upstream `0.0.22` pin is not a clean CPython 3.10 Windows-wheel path;
- upstream `av==11.0.0` replaced for this Windows spike by `av==12.0.0`, which has a CPython 3.10 Windows wheel and supports the APIs SSD uses;
- training/UI-only packages are omitted;
- `matplotlib` and `scikit-image` are included because the real local OpenPose import graph needs them.

## CURRENT RUNNER

`tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

It installs the inference stack, checks dependency consistency, verifies CUDA and imports the real upstream `inference.py` graph without loading model weights.

Local outputs on PASS:

- `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_probe.json`;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\25_bootstrap_ssd_dependencies.ps1"
```

PASS target:

- `SSD-DEPS: PASS`;
- CUDA available;
- torch 2.0.1 / CUDA build 11.8;
- NVIDIA GPU reported;
- `SSD_INFERENCE_IMPORT=PASS`.

If it fails, use the complete console and correct only the concrete dependency/Windows compatibility issue. Do not download models first.

## After PASS

Prepare a separate model/checkpoint download runner with exact source, path, size/hash verification. No model download has been authorized or completed yet.

## Historical routes

- segmented-puppet runner 23: historical/paused;
- Flux2 independent full-body frame redraw: FAIL/CLOSED;
- isometric multi-directional character production: CLOSED unless explicitly reopened.

SSD route is ACTIVE. No cleanup applies.
