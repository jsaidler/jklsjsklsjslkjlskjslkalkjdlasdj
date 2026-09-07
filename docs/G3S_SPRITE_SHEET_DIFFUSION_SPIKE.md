# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — WINDOWS INFERENCE DEPENDENCY BOOTSTRAP RUNNER READY**

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
- there **is** an actual dependency file at `ModelTraining/requirements.txt`;
- inference entry point: `ModelTraining/inference.py`;
- prompt config: `ModelTraining/configs/prompts/inference.yaml`;
- inference config requires:
  - `stable-diffusion-v1-5`;
  - `sd-vae-ft-mse`;
  - `image_encoder`;
  - `denoising_unet.pth`;
  - `reference_unet.pth`;
  - `pose_guider.pth`;
  - `motion_module.pth`.

The earlier install plan was corrected twice: first to stop assuming a root requirements file, then after inspection to use the real `ModelTraining/requirements.txt` as the upstream reference rather than the Moore repo alone.

## Environment bootstrap — PASS

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Upstream clone:

`Z:\AI\SpriteSheetDiffusionSpike\repo`

Runner:

`tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

Actual result supplied by the user on 2026-09-07:

- Miniconda: **installed successfully**;
- `conda.exe`: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- Anaconda default-channel ToS: explicitly accepted through runner opt-in;
- env `ssd`: **PASS**;
- Python: **3.10.21**;
- pip: **26.2.1**;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`;
- no model weights downloaded by this gate.

The earlier `CondaToSNonInteractiveError` is resolved and closed as an environment-bootstrap issue.

## Windows dependency strategy — LOCKED FOR THIS SPIKE

Do **not** blindly install all of `ModelTraining/requirements.txt` on Windows.

A project-specific inference-only lock is committed at:

`tools/structured-2d-character-pipeline/ssd_windows_inference_requirements.txt`

Reasons:

1. upstream mixes inference, training, UI and evaluation dependencies;
2. `xformers==0.0.22` is optional in SSD inference code and has no CPython 3.10 Windows wheel on PyPI; it is deferred rather than compiled from source or silently substituted;
3. upstream `av==11.0.0` is source-only on PyPI, while SSD only uses stable `av.open` / `VideoFrame` APIs; the Windows lock uses `av==12.0.0`, which has a CPython 3.10 Windows wheel;
4. training/UI-only packages such as `bitsandbytes`, `wandb`, Gradio and related packages are not installed in this gate;
5. local OpenPose imports require `matplotlib` and `scikit-image`, so they are included even though the upstream requirements are not fully self-consistent for this import graph.

## CUDA/PyTorch decision

Install exactly:

- `torch==2.0.1`;
- `torchvision==0.15.2`;
- from the official **CUDA 11.8** PyTorch wheel index.

This matches the SSD-era dependency family while giving a deterministic Windows CUDA build for the RTX 3060.

`xformers` is intentionally absent from the first inference dependency proof. If 12 GB VRAM later proves insufficient, xformers/offload becomes a separate measured optimization gate rather than an installation prerequisite.

## Current runner — dependency gate

Runner:

`tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

It:

1. requires the environment PASS marker;
2. validates Python 3.10 in env `ssd`;
3. validates the real upstream `ModelTraining/requirements.txt` and the project Windows inference lock;
4. installs PyTorch 2.0.1 + torchvision 0.15.2 CUDA 11.8 from the official PyTorch index;
5. installs the inference-only Windows lock;
6. runs `pip check`;
7. performs a CUDA probe;
8. imports the real upstream `ModelTraining/inference.py` and its local model/OpenPose/pipeline import graph without loading checkpoints;
9. writes:
   - `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_probe.json`;
   - `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`;
   - `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
10. downloads **no model weights**.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\25_bootstrap_ssd_dependencies.ps1"
```

## Dependency gate PASS

PASS requires all of the following:

- `SSD-DEPS: PASS`;
- CUDA available in torch;
- RTX/NVIDIA GPU name reported;
- torch `2.0.1` with CUDA build `11.8`;
- real SSD `inference.py` import graph passes;
- dependency marker and freeze snapshot are written.

## Dependency gate FAIL

Any package-resolution, Windows-wheel, CUDA or real-import failure is a dependency-gate failure only. It is not evidence about SSD image quality. Fix the smallest concrete compatibility defect and rerun this gate before downloading models.

## Model assets — NOT YET DOWNLOADED

Only after dependency PASS, prepare a separate controlled model-bootstrap gate for:

- Stable Diffusion v1.5 base model;
- SSD `denoising_unet.pth`;
- SSD `reference_unet.pth`;
- AnimateAnyone `pose_guider.pth`;
- AnimateAnyone `motion_module.pth`;
- `stabilityai/sd-vae-ft-mse`;
- CLIP vision `image_encoder/` from the SD image-variations model.

No checkpoint/model download is considered complete until exact path, provenance, size/hash when available and local verification are recorded here.

## Cleanup if SSD is explicitly discarded

Workspace:

```powershell
Remove-Item -LiteralPath "Z:\AI\SpriteSheetDiffusionSpike" -Recurse -Force -ErrorAction SilentlyContinue
```

Environment:

```powershell
& "C:\Users\jsaid\miniconda3\Scripts\conda.exe" env remove -n ssd -y
```

SSD is currently ACTIVE, so no cleanup applies now.
