# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — LOCAL SSD INSTALLATION / ENVIRONMENT BOOTSTRAP BLOCKED ONLY ON ANACONDA TOS OPT-IN**

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

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Upstream clone:

`Z:\AI\SpriteSheetDiffusionSpike\repo`

## Actual bootstrap history

Initial user result:

- upstream clone: **SUCCESS**;
- 887/887 objects received;
- approximately 289.63 MiB transferred;
- `conda` initially not installed / not on PATH;
- `cd /d ...` failed because `/d` is CMD syntax, not PowerShell;
- `pip install -r requirements.txt` failed from `C:\Users\jsaid` and the upstream root requirements file is absent.

Bootstrap runner was then added:

`tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

Latest actual user result on 2026-09-07:

- Miniconda installation: **SUCCESS**;
- resolved `conda.exe`: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- `conda create -n ssd python=3.10 pip -y`: **BLOCKED BEFORE PACKAGE TRANSACTION**;
- blocker: `CondaToSNonInteractiveError` because Anaconda Terms of Service were not yet accepted for default channels:
  - `https://repo.anaconda.com/pkgs/main`;
  - `https://repo.anaconda.com/pkgs/r`;
  - `https://repo.anaconda.com/pkgs/msys2`.

This is not an SSD/model failure. The environment has not yet been created.

## ToS handling decision — EXPLICIT OPT-IN ONLY

The project runner must **not silently accept legal terms on the user's behalf**.

Runner 24 now supports:

`-AcceptAnacondaTos`

Supplying that switch is the user's explicit opt-in to let the runner execute the exact `conda tos accept` commands for the three required default channels before creating the environment.

Without that switch, if environment creation is needed, runner 24 stops and prints the required action rather than accepting terms automatically.

## Environment bootstrap runner

Runner:

`tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

Current behavior:

1. verifies the existing upstream clone and actual inference/config paths;
2. locates existing `conda.exe` or installs Miniconda through WinGet if absent;
3. probes for an already-working `ssd` Python 3.10 environment;
4. if no environment exists, requires explicit `-AcceptAnacondaTos` before accepting Anaconda default-channel terms;
5. creates env `ssd` with Python 3.10 + pip;
6. verifies Python 3.10 and pip through `conda run`;
7. writes `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`;
8. downloads **no model weights** and installs **no large SSD dependency stack** in this gate.

## Current exact next gate

**Environment bootstrap only.**

If the user agrees to the Anaconda Terms of Service for the three channels above, run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\24_bootstrap_ssd_environment.ps1" `
  -AcceptAnacondaTos
```

Using `-AcceptAnacondaTos` is explicit acceptance authorization for the runner; it is not implied by project participation.

Do not download model weights or install the large dependency stack until this environment gate passes.

## PASS

Environment bootstrap PASS requires:

- `conda.exe` resolvable;
- environment `ssd` exists;
- `conda run -n ssd python --version` reports Python 3.10.x;
- local bootstrap marker is written.

## FAIL

Environment bootstrap FAIL if Terms are not accepted, Miniconda cannot be used, or Python 3.10 environment creation fails.

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

Environment, if later created:

```powershell
& "C:\Users\jsaid\miniconda3\Scripts\conda.exe" env remove -n ssd -y
```

This cleanup applies only if the SSD route is explicitly closed.
