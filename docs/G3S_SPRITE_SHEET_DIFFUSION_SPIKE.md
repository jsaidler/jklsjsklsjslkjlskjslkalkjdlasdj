# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — ENVIRONMENT PASS / WINDOWS DEPENDENCY RUNNER FIXED / RETRY REQUIRED**

## Decision

The character-production target is a conventional **2D spritesheet**: approved persistent frames arranged by action in rows/blocks or equivalent atlas regions, with metadata for timing, pivots, hitboxes and events as needed.

The active offline source-authoring spike is **Sprite Sheet Diffusion (SSD)**, using the complete Exilada master as appearance reference plus pose/motion guidance. SSD is a production tool under validation, not a runtime dependency.

## Presentation/runtime lock retained

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime is ordinary spritesheet playback, not 3D, puppet assembly or diffusion.

## Upstream repository — verified layout

Upstream:

`https://github.com/chenganhsieh/Sprite-Sheet-Diffusion`

Verified implementation facts:

- README requests a Python 3.10 conda environment;
- README says `pip install -r requirements.txt`, but there is **no root** `requirements.txt`;
- actual dependency file: `ModelTraining/requirements.txt`;
- inference entry point: `ModelTraining/inference.py`;
- prompt config: `ModelTraining/configs/prompts/inference.yaml`;
- inference config later requires SD1.5 base, VAE, CLIP image encoder, SSD denoising/reference UNets, AnimateAnyone pose guider and motion module.

## Environment bootstrap — PASS

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Runner:

`tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

Actual result supplied by the user on 2026-09-07:

- upstream clone: PASS;
- Miniconda: PASS;
- `conda.exe`: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- env `ssd`: PASS;
- Python: `3.10.21`;
- pip: `26.2.1`;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`;
- no model weights downloaded.

## Windows dependency strategy

Project inference lock:

`tools/structured-2d-character-pipeline/ssd_windows_inference_requirements.txt`

Decisions for this spike:

- install `torch==2.0.1` + `torchvision==0.15.2` from official CUDA 11.8 wheels;
- do not blindly install the mixed training/UI upstream requirements;
- defer optional `xformers`;
- use `av==12.0.0` on Windows instead of upstream `av==11.0.0` because the latter is source-only for this Python/Windows target while the APIs SSD uses remain available;
- include import-time dependencies actually needed by the real local graph, including `matplotlib` and `scikit-image`.

## Dependency runner — first execution FAIL / SCRIPT BUG

Runner:

`tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

The first execution failed at the old Torch preflight probe around line 98 with PowerShell reporting:

`NativeCommandError / RemoteException`

The user correctly identified this as the same recurring class of script error seen in earlier work.

### Root cause

The runner combined:

- `$ErrorActionPreference = 'Stop'`;
- a native command expected to fail when Torch was not yet installed;
- native STDERR redirected through `2>&1`.

Windows PowerShell promoted native STDERR into a terminating PowerShell error before the runner could inspect `$LASTEXITCODE` and decide that the preflight simply meant "Torch is not installed yet".

This was a **PowerShell control-flow defect in our runner**, not a Torch, CUDA, SSD or model-quality failure.

## Native-process scripting rule — LOCKED

For new project PowerShell runners:

1. do not execute expected-failure native probes directly under `$ErrorActionPreference='Stop'`;
2. do not depend on raw `2>&1` native tracebacks as control flow;
3. native calls must temporarily isolate themselves from the global Stop policy, then explicitly inspect `$LASTEXITCODE`;
4. expected Python probes should catch their own exceptions and emit structured JSON while exiting cleanly;
5. a probe failure must be reported as a project `FAIL` with a preserved diagnostic file, not as an unhandled PowerShell `NativeCommandError`.

This rule is intended to prevent this exact recurring failure class from appearing again in subsequent SSD runners.

## Runner 25 — FIXED

Runner 25 was rewritten after the failure.

Changes:

- dependency work now resolves the environment interpreter directly (`...\miniconda3\envs\ssd\python.exe`) instead of relying on `conda run` for every Python action;
- all native calls use wrappers that temporarily set `ErrorActionPreference=Continue`, record the exit code, then restore the project-wide Stop policy;
- Torch preflight now catches import failure inside Python and writes `ssd_torch_probe.json`; missing Torch is data, not a process error;
- incompatible existing Torch triggers deterministic reinstall from the official CUDA 11.8 wheel index;
- the real `ModelTraining/inference.py` import probe catches Python exceptions and writes a structured `ssd_dependency_probe.json` instead of throwing a raw traceback into PowerShell;
- no model/checkpoint download occurs in this gate.

## Current exact operator action

Pull the fixed runner and rerun the dependency gate:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\25_bootstrap_ssd_dependencies.ps1"
```

## Dependency gate PASS

PASS requires:

- `SSD-DEPS: PASS`;
- CUDA available;
- torch 2.0.1 / torchvision 0.15.2 with CUDA build 11.8;
- RTX/NVIDIA GPU reported;
- `pip check` passes;
- real SSD `inference.py` import graph passes;
- marker/freeze files written.

Primary local outputs:

- `Z:\AI\SpriteSheetDiffusionSpike\ssd_torch_probe.json`;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_probe.json`;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`.

If the import graph fails, the runner must now end with a clean `SSD-DEPS: FAIL` and preserve the Python traceback in `ssd_dependency_probe.json`.

## Model assets — NOT YET DOWNLOADED

Only after dependency PASS, prepare a separate controlled model-bootstrap gate for:

- Stable Diffusion v1.5 base model;
- SSD `denoising_unet.pth`;
- SSD `reference_unet.pth`;
- AnimateAnyone `pose_guider.pth`;
- AnimateAnyone `motion_module.pth`;
- `stabilityai/sd-vae-ft-mse`;
- CLIP vision `image_encoder/`.

## Cleanup if SSD is explicitly discarded

```powershell
Remove-Item -LiteralPath "Z:\AI\SpriteSheetDiffusionSpike" -Recurse -Force -ErrorAction SilentlyContinue
& "C:\Users\jsaid\miniconda3\Scripts\conda.exe" env remove -n ssd -y
```

SSD is ACTIVE, so no cleanup applies now.
