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

Repo: `chenganhsieh/Sprite-Sheet-Diffusion`

- inference: `ModelTraining/inference.py`;
- config: `ModelTraining/configs/prompts/inference.yaml`;
- actual dependency file: `ModelTraining/requirements.txt`;
- no root requirements file despite README command;
- later model requirements: SD1.5 base, VAE, CLIP image encoder, SSD denoising/reference UNets, AnimateAnyone pose guider and motion module.

## Actual local state — environment PASS

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

- clone: PASS;
- Miniconda: PASS;
- conda: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- env `ssd`: PASS;
- Python: `3.10.21`;
- pip: `26.2.1`;
- environment marker written;
- no model weights downloaded.

## Dependency decisions

Project Windows inference lock:

`tools/structured-2d-character-pipeline/ssd_windows_inference_requirements.txt`

- torch `2.0.1` + torchvision `0.15.2` from official CUDA 11.8 wheels;
- `xformers` deferred;
- `av==12.0.0` used for this Windows/Python target;
- training/UI-only packages omitted;
- real import-time dependencies such as `matplotlib` and `scikit-image` included.

## Runner 25 first execution — SCRIPT FAIL, NOT SSD FAIL

Runner:

`tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

The first execution aborted around the old Torch preflight with PowerShell `NativeCommandError / RemoteException`.

Root cause:

- `$ErrorActionPreference='Stop'`;
- missing-Torch probe intentionally produced native STDERR;
- `2>&1` promoted that STDERR into a terminating PowerShell error before the runner could inspect `$LASTEXITCODE`.

User explicitly flagged this as the recurring script-error class. Treat that feedback as a hard scripting requirement.

## PowerShell native-process rule — LOCKED

Do not use expected native failure + raw STDERR as control flow under `ErrorActionPreference=Stop`.

For new runners:

- isolate native calls from the global Stop policy;
- inspect exit codes explicitly;
- make expected Python probes catch exceptions and write JSON;
- preserve diagnostics in files and report a clean project `FAIL` instead of an unhandled `NativeCommandError`.

## CURRENT RUNNER — FIXED / RETRY READY

Runner 25 now:

- resolves the env Python directly;
- wraps native invocations safely;
- uses `ssd_torch_probe.json` for Torch preflight;
- deterministically installs/repairs Torch CUDA 11.8;
- uses `ssd_dependency_probe.json` for the real SSD import graph;
- downloads no model weights.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\25_bootstrap_ssd_dependencies.ps1"
```

PASS target:

- `SSD-DEPS: PASS`;
- torch 2.0.1 / torchvision 0.15.2;
- CUDA build 11.8;
- NVIDIA GPU detected;
- `pip check` PASS;
- `SSD_INFERENCE_IMPORT=PASS`.

If it fails, use the runner's clean final message and inspect:

`Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_probe.json`

Do not download models or improvise package changes before diagnosing that concrete output.

## After PASS

Prepare a separate model/checkpoint download runner with exact source, path and verification. No model download has been authorized or completed yet.

## Historical routes

- segmented-puppet runner 23: historical/paused;
- Flux2 independent full-body frame redraw: FAIL/CLOSED;
- isometric multi-directional character production: CLOSED unless explicitly reopened.

SSD route is ACTIVE. No cleanup applies.
