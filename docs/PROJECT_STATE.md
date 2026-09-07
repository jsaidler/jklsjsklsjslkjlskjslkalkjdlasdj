# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
4. `docs/G1_CAMERA_SCALE_LOG.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
7. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
8. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families.

True isometric multi-directional character production remains closed unless explicitly reopened.

## Runtime animation representation — LOCKED

`approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary runtime sprite playback`

Runtime does not require a 3D skeleton, MPFB, segmented puppet, diffusion model or per-frame generation.

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

The active SSD spike uses the complete master as appearance reference.

## Retained offline motion source

- G2 PASS/CLOSED;
- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- C1A skeleton walk PASS/CLOSED;
- approved eight-state cycle `1588,1598,1608,1618,1628,1638,1648,1658`.

This may be reused only as offline pose/motion control.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp -> gait — CLOSED;
- MPFB skinned body as mandatory guide — CLOSED;
- Flux2 independent full-body redraw per frame — FAIL/CLOSED;
- segmented 2D puppet runner 23 — PAUSED/HISTORICAL.

## CURRENT — SPRITE SHEET DIFFUSION LOCAL VALIDATION

Canonical doc:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Goal: determine whether Sprite Sheet Diffusion can generate a coherent Exilada action sequence strongly enough that accepted frames can be frozen into conventional spritesheets.

### Upstream verified layout

Repo: `chenganhsieh/Sprite-Sheet-Diffusion`

- inference: `ModelTraining/inference.py`;
- config: `ModelTraining/configs/prompts/inference.yaml`;
- actual dependency file: `ModelTraining/requirements.txt`;
- no root requirements file despite README command;
- model paths required later: SD1.5 base, VAE, CLIP image encoder, SSD denoising/reference UNets, AnimateAnyone pose guider and motion module.

### Environment gate — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

- clone: PASS;
- Miniconda: PASS;
- `conda.exe`: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- env `ssd`: PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- environment marker written;
- no model weights downloaded.

## CURRENT GATE — Windows inference dependencies

Requirements lock:

`tools/structured-2d-character-pipeline/ssd_windows_inference_requirements.txt`

Runner:

`tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

### First run — FAIL due runner control-flow bug

The first runner 25 execution aborted at its old Torch preflight probe with `NativeCommandError / RemoteException`.

Root cause was PowerShell-native process handling:

- global `$ErrorActionPreference='Stop'`;
- expected missing-Torch traceback written to native STDERR;
- `2>&1` redirected STDERR into the PowerShell pipeline;
- Windows PowerShell terminated before `$LASTEXITCODE` could be inspected.

This is not a Torch/CUDA/SSD failure.

### Scripting rule now locked

Expected-failure native probes must not be used as raw control flow under `ErrorActionPreference=Stop`. Native calls must isolate STDERR/error preference and explicitly inspect exit codes. Expected Python probes should catch exceptions and emit structured JSON.

### Runner 25 — FIXED / RETRY READY

The runner now:

- resolves env Python directly rather than repeatedly using `conda run`;
- wraps all native calls so native STDERR cannot prematurely terminate PowerShell;
- performs Torch preflight via a clean JSON probe;
- repairs incompatible Torch deterministically from official CUDA 11.8 wheels;
- performs the real SSD `inference.py` import through a structured diagnostic probe;
- downloads no models.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\25_bootstrap_ssd_dependencies.ps1"
```

PASS target:

- `SSD-DEPS: PASS`;
- torch 2.0.1 / torchvision 0.15.2;
- CUDA build 11.8;
- RTX/NVIDIA GPU detected;
- `pip check` PASS;
- real SSD inference import graph PASS.

If it fails, use the clean runner message plus `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_probe.json`; do not improvise package/model installation.

## Next after PASS

Prepare a separate model/checkpoint download gate with exact sources, paths and verification. No model download before dependency PASS.

## No cleanup

SSD is ACTIVE. Do not delete `Z:\AI\SpriteSheetDiffusionSpike`.
