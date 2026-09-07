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
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`.

This may be reused only as offline pose/motion control.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp -> gait — CLOSED;
- MPFB skinned body as mandatory guide — CLOSED;
- Flux2 independent full-body redraw per frame — FAIL/CLOSED;
- segmented 2D puppet runner 23 — PAUSED/HISTORICAL.

## CURRENT — SPRITE SHEET DIFFUSION LOCAL VALIDATION

Canonical doc: `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Goal: determine whether Sprite Sheet Diffusion can generate a coherent Exilada action sequence strongly enough that accepted frames can be frozen into conventional spritesheets.

### Upstream verified layout

Repo: `chenganhsieh/Sprite-Sheet-Diffusion`

- inference: `ModelTraining/inference.py`;
- config: `ModelTraining/configs/prompts/inference.yaml`;
- actual dependency file: `ModelTraining/requirements.txt`;
- no root requirements file despite README command;
- default `pretrained_model` layout is compatible with the current model bootstrap plan.

## Environment gate — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

- clone: PASS;
- Miniconda: PASS;
- env `ssd`: PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- environment marker written.

## Windows inference dependency gate — PASS

Validated user console on 2026-09-07:

- `SSD-DEPS: PASS`;
- GPU `NVIDIA GeForce RTX 3060`;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD `inference.py` import graph PASS;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
- freeze `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`.

The earlier runner 25 `NativeCommandError` was a PowerShell control-flow defect and is closed. Subsequent runners must use controlled native-process execution and structured Python diagnostics.

## CURRENT GATE — model/checkpoint download

Manifest:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/26_download_ssd_models.ps1`

Destination:

`Z:\AI\SpriteSheetDiffusionSpike\repo\ModelTraining\pretrained_model`

Estimated download: **~13.7 GB**.

Minimal set:

- SD1.5 UNet config + weights;
- Stability AI MSE VAE config + safetensors;
- Lambda CLIP vision encoder config + weights;
- SSD fine-tuned `denoising_unet.pth` + `reference_unet.pth`;
- AnimateAnyone baseline `pose_guider.pth` + `motion_module.pth`.

Known large-file SHA256 values are enforced by the manifest. Downloads use resumable `.part` files and do not create a duplicate Hugging Face model cache.

Intentionally deferred because they are not required for the first selected inference path:

- wav2vec2;
- DWPose detector weights;
- FILM frame interpolation model;
- xformers.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\26_download_ssd_models.ps1"
```

PASS target:

- `SSD-MODELS: PASS`;
- all manifest files verified;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_models_bootstrap.json` written.

## Next after model PASS

Prepare input/config + first **8-frame Exilada walk inference** using the complete master and an approved 8-state pose sequence. No large multi-action sheet until temporal identity is proven.

## No cleanup

SSD is ACTIVE. Do not delete `Z:\AI\SpriteSheetDiffusionSpike`.
