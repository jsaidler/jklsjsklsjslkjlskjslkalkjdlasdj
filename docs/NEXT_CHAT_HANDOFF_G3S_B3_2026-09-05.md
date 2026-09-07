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

User clarification on 2026-09-07: the local setup must include **all assets genuinely useful/necessary for the best practical spritesheet-authoring workflow**, not only the smallest smoke-test set. Unrelated audio/portrait assets and legally unsuitable legacy OpenPose weights remain excluded.

## Local state — ENV + DEPENDENCIES PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Environment:

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`.

Dependency gate:

- `SSD-DEPS: PASS`;
- GPU `NVIDIA GeForce RTX 3060`;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD inference import graph PASS;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
- freeze `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`.

Native-process rule remains locked: expected native failures cannot be raw control flow under `ErrorActionPreference=Stop`; use structured probes and explicit exit handling.

## CURRENT — runner 26 core model download IN PROGRESS

Manifest:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/26_download_ssd_models.ps1`

Destination:

`Z:\AI\SpriteSheetDiffusionSpike\repo\ModelTraining\pretrained_model`

Core generation download: ~13.7 GB.

Includes:

- SD1.5 UNet;
- MSE VAE;
- CLIP vision image encoder;
- SSD fine-tuned denoising/reference UNets;
- AnimateAnyone pose guider + motion module.

**Actual current operator state:** user reports runner 26 is downloading now. Do not interrupt it. Wait for `SSD-MODELS: PASS` or a controlled failure.

## QUEUED AFTER runner 26 PASS — full production-authoring support

Manifest:

`tools/structured-2d-character-pipeline/ssd_authoring_support_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/27_download_ssd_authoring_support.ps1`

Additional download: ~0.42 GB.

Adds:

- DWPose detector `ModelTraining/models/openpose/yolox_l.onnx`;
- DWPose whole-body model `ModelTraining/models/openpose/dw-ll_ucoco_384.onnx`;
- FILM interpolation `ModelTraining/pretrained_model/film_net_fp16.pt`.

Runner 27 also verifies upstream-bundled MediaPipe task assets and structurally loads the DWPose ONNX models and FILM TorchScript model without running SSD inference.

### Why

- DWPose allows arbitrary driving-video/actions to be converted into whole-body pose maps for future walk/run/attack/dodge/hit/death rows.
- FILM is available for optional in-between generation but is **not** the default for final sprite timing because interpolated frames may soften/deform crisp pixel silhouettes.

## Explicit exclusions

Do not add unless a later measured gate establishes a need:

- wav2vec2 / audio-driven AniPortrait models — unrelated;
- legacy CMU OpenPose body/hand/face weights — bundled preprocessor is explicitly non-commercial-use-only; DWPose is preferred;
- AnimateAnyone baseline denoising/reference UNets — must not replace SSD fine-tuned sprite UNets;
- xformers — optimization only; install later only if actual VRAM measurements require it.

## Exact next operator action

### Right now

Let runner 26 finish. No new command while it is downloading.

### After `SSD-MODELS: PASS`

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\27_download_ssd_authoring_support.ps1"
```

Support PASS target:

- `SSD-SUPPORT: PASS`;
- DWPose available;
- FILM available;
- `ssd_authoring_support_bootstrap.json` + `ssd_authoring_support_probe.json` written.

## After support PASS

First real SSD proof:

- complete `exilada_master.png`;
- approved 8-state walk pose sequence;
- 8 frames;
- FILM disabled initially;
- validate identity, anatomy, hair/equipment persistence, pose obedience, temporal coherence, 12 GB VRAM fit and clean alpha/background conversion.

Only after this passes do we expand to multi-action sheet production and automate packing/alpha/pivots/events.

## Historical routes

- segmented-puppet runner 23: historical/paused;
- Flux2 independent full-body frame redraw: FAIL/CLOSED;
- isometric multi-directional character production: CLOSED unless explicitly reopened.

SSD route is ACTIVE. No cleanup applies.
