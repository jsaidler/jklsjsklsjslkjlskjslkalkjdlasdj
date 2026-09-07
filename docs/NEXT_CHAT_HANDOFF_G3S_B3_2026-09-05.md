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

Canonical doc: `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Purpose: generate a coherent Exilada action sequence from the complete master plus pose/motion guidance, then freeze approved frames into ordinary spritesheets.

## Local state — ENV + DEPENDENCIES PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Environment:

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`.

Dependency gate validated by user:

- `SSD-DEPS: PASS`;
- GPU `NVIDIA GeForce RTX 3060`;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD inference import graph PASS;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
- freeze `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`.

The previous PowerShell `NativeCommandError` class is explicitly locked out of future runner design: expected native failures cannot be raw control flow under `ErrorActionPreference=Stop`.

## CURRENT — model download runner ready

Manifest:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/26_download_ssd_models.ps1`

Destination:

`Z:\AI\SpriteSheetDiffusionSpike\repo\ModelTraining\pretrained_model`

Estimated download: ~13.7 GB.

Minimal set:

- SD1.5 UNet;
- MSE VAE;
- CLIP vision image encoder;
- SSD fine-tuned denoising/reference UNets;
- AnimateAnyone pose guider + motion module.

Known large-file hashes are enforced. Downloads use resumable `.part` files and avoid a duplicate Hugging Face cache copy.

Intentionally deferred:

- wav2vec2;
- DWPose detector models;
- FILM interpolation model;
- xformers.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\26_download_ssd_models.ps1"
```

PASS target:

- `SSD-MODELS: PASS`;
- verified model-set marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_models_bootstrap.json`.

## After model PASS

Prepare the first 8-frame Exilada walk smoke test:

- complete `exilada_master.png` as reference;
- approved 8-state walk pose sequence;
- no large multi-action sheet yet;
- first question is identity/temporal consistency, then sheet packing.

## Historical routes

- segmented-puppet runner 23: historical/paused;
- Flux2 independent full-body frame redraw: FAIL/CLOSED;
- isometric multi-directional character production: CLOSED unless explicitly reopened.

SSD route is ACTIVE. No cleanup applies.
