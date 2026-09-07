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

The user has now explicitly required the workstation setup to include **all assets genuinely useful/necessary for the best practical spritesheet-authoring workflow**, not only the smallest smoke-test set. This does not mean downloading unrelated audio/portrait or legally unsuitable legacy assets.

## Environment gate — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

- clone: PASS;
- Miniconda: PASS;
- env `ssd`: PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- environment marker written.

## Windows inference dependency gate — PASS

Validated user console:

- `SSD-DEPS: PASS`;
- GPU `NVIDIA GeForce RTX 3060`;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD `inference.py` import graph PASS;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
- freeze `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`.

The earlier runner 25 `NativeCommandError` was a PowerShell control-flow defect and is closed. Subsequent runners must use controlled native-process execution and structured Python diagnostics.

## CURRENT GATE — core generation model download IN PROGRESS

Manifest:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/26_download_ssd_models.ps1`

Destination:

`Z:\AI\SpriteSheetDiffusionSpike\repo\ModelTraining\pretrained_model`

Estimated core download: **~13.7 GB**.

Core generation set:

- SD1.5 UNet;
- MSE VAE;
- CLIP vision image encoder;
- SSD fine-tuned denoising/reference UNets;
- AnimateAnyone pose guider + motion module.

The user reported on 2026-09-07 that runner 26 **is currently downloading**. Do not interrupt it. Let it complete and report `SSD-MODELS: PASS` or a controlled failure.

## Production-support asset gate — PREPARED / QUEUED AFTER RUNNER 26

Manifest:

`tools/structured-2d-character-pipeline/ssd_authoring_support_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/27_download_ssd_authoring_support.ps1`

Additional download: approximately **0.42 GB**.

It adds:

- DWPose YOLOX detector `models/openpose/yolox_l.onnx`;
- DWPose whole-body pose model `models/openpose/dw-ll_ucoco_384.onnx`;
- FILM interpolation `pretrained_model/film_net_fp16.pt`.

Runner 27 also verifies the MediaPipe face/pose task files already bundled in the upstream clone and structurally loads DWPose through OpenCV DNN plus FILM through TorchScript.

### Why these are included

- **DWPose** gives us a practical route from arbitrary driving footage/actions to body/hand/face pose maps for future walk/run/attack/dodge/hit/death production, instead of requiring manual pose-image authoring for every action.
- **FILM** keeps upstream interpolation available as an optional production tool. It is not the default for final sprite frames because interpolation can damage crisp pixel silhouettes; every interpolated frame must pass QA.

## Explicit exclusions from the full spritesheet-authoring kit

- `wav2vec2` and AniPortrait audio models — unrelated to spritesheet action generation;
- legacy CMU OpenPose body/hand/face weights — not used because the bundled OpenPose path is explicitly non-commercial-use-only and DWPose is the preferred whole-body detector path;
- AnimateAnyone baseline denoising/reference UNets — must not replace SSD fine-tuned sprite UNets;
- `xformers` — not a model download; only add later if measured RTX 3060 VRAM behavior proves it necessary through a compatibility-tested optimization gate.

## Current exact operator sequence

### Now

Do nothing to the already-running model download. Wait for runner 26 to finish.

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
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_bootstrap.json` written;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_probe.json` written.

## Next after support PASS

Prepare the first **8-frame Exilada walk inference** using:

- complete `exilada_master.png`;
- approved eight-state walk pose sequence;
- SSD core generation weights;
- DWPose available for future arbitrary action extraction, but not required for the already-approved walk poses;
- FILM disabled by default for the first identity/temporal-coherence proof.

First quality questions:

- identity persistence;
- anatomy/proportion persistence;
- hair/clothing/equipment persistence;
- pose obedience;
- temporal coherence;
- RTX 3060 12 GB memory fit;
- clean conversion of generated RGB/background to transparent native sprite frames.

Only after this passes do we expand to conventional multi-action sheets and automate sheet packing, alpha cleanup and runtime metadata.

## No cleanup

SSD is ACTIVE. Do not delete `Z:\AI\SpriteSheetDiffusionSpike`.
