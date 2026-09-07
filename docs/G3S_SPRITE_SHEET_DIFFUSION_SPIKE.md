# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-06**

Gate status: **ACTIVE — LOCAL SSD INSTALLATION / ENVIRONMENT BOOTSTRAP RUNNER READY**

## Decision

The character-production target is a conventional **2D spritesheet**, as used by classic arcade beat'em-up production: final gameplay animation is stored as persistent frame images arranged by action in rows/blocks, with metadata for timing/pivots/events as needed.

The current local source-authoring spike is **Sprite Sheet Diffusion (SSD)**, using the Exilada master as the appearance reference and pose/motion guidance to generate a consistent animation sequence. The SSD spike is a production-tool validation only; SSD is not a runtime dependency.

## Presentation lock retained

The project remains an elevated arcade beat'em-up / belt-scroller false 3D, not true isometric character production:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall in gameplay;
- first visible family screen-left/front-three-quarter;
- movement through gameplay depth does not require north/south/isometric sprite families.

## Runtime/output lock

Final runtime representation:

`offline source-authoring -> approved 2D frames -> spritesheet PNG(s) + animation metadata -> ordinary sprite playback`

A hidden rig/mocap sequence may be used offline to create/control source poses, but it is not required at runtime.

A single giant PNG is not mandatory. Conventional grouped sheets are acceptable, e.g. locomotion/combat/damage/contextual, provided actions remain deterministic frame sequences.

## Why SSD is being tested

SSD adapts an AnimateAnyone-style architecture for game-character animation and uses:

- a fine-tuned denoising UNet;
- a fine-tuned reference UNet;
- a pose guider;
- a motion module;
- SD1.5 base model;
- SD VAE;
- CLIP vision image encoder.

The project is testing it specifically because it is trained for sprite/game-character animation rather than independently regenerating unrelated full-body frames.

## Upstream repository reality — VERIFIED

Upstream:

`https://github.com/chenganhsieh/Sprite-Sheet-Diffusion`

Important implementation facts verified on 2026-09-06:

- the README says `conda create -n ssd python=3.10`, `conda activate ssd`, then `pip install -r requirements.txt`;
- **the repository does not actually contain a root `requirements.txt`**;
- actual inference entry point is `ModelTraining/inference.py`;
- actual prompt config is `ModelTraining/configs/prompts/inference.yaml`;
- that config requires these paths:
  - `stable-diffusion-v1-5` base model;
  - `sd-vae-ft-mse`;
  - `image_encoder`;
  - `denoising_unet.pth`;
  - `reference_unet.pth`;
  - `pose_guider.pth`;
  - `motion_module.pth`.

The earlier local-install plan omitted the SD1.5 base model and incorrectly assumed a usable root `requirements.txt`; this is corrected here.

## Dependency baseline

SSD states that it is built directly on Moore-AnimateAnyone. Until a project-specific Windows requirements lock is proven, dependency bootstrap uses the Moore-AnimateAnyone pinned inference-era requirements as the compatibility baseline, with SSD-specific missing imports added only when observed/verified.

The Moore baseline includes Python 3.10-era versions including Torch 2.0.1 / torchvision 0.15.2, diffusers 0.24.0, transformers 4.30.2, xformers 0.0.22 and related packages.

## Local workspace

Expected workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Expected upstream clone:

`Z:\AI\SpriteSheetDiffusionSpike\repo`

Actual user result on 2026-09-06:

- upstream clone: **SUCCESS**;
- received 887/887 objects;
- approximately 289.63 MiB transferred;
- `conda`: **NOT INSTALLED / NOT ON PATH**;
- `conda create -n ssd python=3.10 -y`: FAIL because command not found;
- `conda activate ssd`: FAIL because command not found;
- `cd /d ...`: FAIL because `/d` is CMD syntax, not PowerShell syntax;
- `pip install -r requirements.txt`: FAIL because shell remained in `C:\Users\jsaid` and, independently, upstream does not provide the referenced root requirements file.

These are bootstrap/procedure failures, not an SSD inference/model-quality failure.

## Correct PowerShell rule

Use:

```powershell
Set-Location "Z:\AI\SpriteSheetDiffusionSpike\repo"
```

Do not use CMD-only `cd /d` in PowerShell.

## Environment decision

Because conda is absent and the upstream explicitly targets a Python 3.10 conda environment, the spike will install **Miniconda** and create an isolated environment named `ssd`.

To avoid PowerShell activation/path problems, project automation uses:

`conda run -n ssd <command>`

over relying on `conda activate` in the current shell.

## Environment bootstrap runner

Runner:

`tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

The runner:

1. verifies the existing upstream clone and actual `ModelTraining/inference.py` / config paths;
2. locates an existing `conda.exe` if present;
3. if absent, installs `Anaconda.Miniconda3` through WinGet in user scope;
4. locates `conda.exe` without requiring a PowerShell PATH refresh;
5. creates env `ssd` with Python 3.10 + pip;
6. verifies Python 3.10 and pip through `conda run`;
7. writes local proof marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`;
8. intentionally downloads **no model weights** and installs **no large SSD dependency stack** in this gate.

## Current exact next gate

**Environment bootstrap only.**

Run the committed runner. Do not download model weights or install the large dependency stack until it passes.

## PASS

Environment bootstrap PASS requires:

- `conda.exe` resolvable;
- environment `ssd` exists;
- `conda run -n ssd python --version` reports Python 3.10.x;
- local bootstrap marker is written.

## FAIL

Environment bootstrap FAIL if Miniconda cannot be installed/located or Python 3.10 environment creation fails.

## Later model assets — NOT YET DOWNLOADED

When environment bootstrap passes, the next stage will install dependencies and then fetch, in a controlled order:

- `stable-diffusion-v1-5` base model;
- SSD `denoising_unet.pth`;
- SSD `reference_unet.pth`;
- AnimateAnyone baseline `pose_guider.pth`;
- AnimateAnyone baseline `motion_module.pth`;
- `stabilityai/sd-vae-ft-mse`;
- CLIP vision `image_encoder/` from the SD image-variations model.

No model download is considered complete until path, size and provenance are recorded here.

## Cleanup if SSD is discarded

Workspace:

```powershell
Remove-Item -LiteralPath "Z:\AI\SpriteSheetDiffusionSpike" -Recurse -Force -ErrorAction SilentlyContinue
```

Environment:

```powershell
conda env remove -n ssd -y
```

This cleanup applies only if the SSD route is explicitly closed.
