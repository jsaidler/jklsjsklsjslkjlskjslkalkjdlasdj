# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — ENVIRONMENT PASS / DEPENDENCIES PASS / CORE MODEL DOWNLOAD IN PROGRESS / PRODUCTION SUPPORT QUEUED**

## Decision

The character-production target is a conventional **2D spritesheet**: approved persistent frames arranged by action in rows/blocks or equivalent atlas regions, with metadata for timing, pivots, hitboxes and events as needed.

The active offline source-authoring spike is **Sprite Sheet Diffusion (SSD)**, using the complete Exilada master as appearance reference plus pose/motion guidance. SSD is a production tool under validation, not a runtime dependency.

The user explicitly directed that the local authoring stack should not stop at the smallest smoke-test download: **download everything actually useful/necessary to create spritesheets at the best practical quality**, while still excluding unrelated assets that do not improve this workflow.

## Presentation/runtime lock retained

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime is ordinary spritesheet playback, not 3D, puppet assembly or diffusion.

## Verified upstream layout

Upstream: `https://github.com/chenganhsieh/Sprite-Sheet-Diffusion`

- inference entry point: `ModelTraining/inference.py`;
- prompt config: `ModelTraining/configs/prompts/inference.yaml`;
- actual dependency file: `ModelTraining/requirements.txt`;
- no root `requirements.txt` despite the README command;
- upstream `pretrained_model/download.sh` confirms the SD1.5 UNet, SD VAE and CLIP vision image encoder layout used by inference;
- SSD config also requires `denoising_unet.pth`, `reference_unet.pth`, `pose_guider.pth` and `motion_module.pth`.

`inference.py` loads the VAE, SD1.5 UNet architecture, SSD fine-tuned denoising/reference UNets, pose guider, motion module and CLIP image encoder. It accepts a directory of pose images and can optionally load FILM frame interpolation when `--accelerate` is used. The imported OpenPose/DWPose code is not required when pose images are already prepared, but it is useful for production because it can turn arbitrary driving footage/actions into whole-body pose maps.

## Environment bootstrap — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Runner: `tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

Validated state:

- clone: PASS;
- Miniconda: PASS;
- `conda.exe`: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- env `ssd`: PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`.

## Windows inference dependencies — PASS

Runner: `tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

Validated user result:

- `SSD-DEPS: PASS`;
- GPU: `NVIDIA GeForce RTX 3060`;
- Torch: `2.0.1+cu118`;
- CUDA build: `11.8`;
- real SSD inference import graph: PASS;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
- freeze: `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`.

No model/checkpoint was downloaded by the dependency gate.

## Native-process scripting rule — LOCKED

For subsequent project PowerShell runners:

1. do not use an expected native-process failure as raw control flow under `$ErrorActionPreference='Stop'`;
2. do not depend on native STDERR/`2>&1` to decide expected states;
3. Python probes must catch expected exceptions and emit structured diagnostics;
4. native calls must have explicitly inspected exit codes;
5. project failure must end as a controlled `FAIL`, not an unhandled `NativeCommandError`.

## Core SSD generation models — CURRENT DOWNLOAD

Manifest:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/26_download_ssd_models.ps1`

Destination:

`Z:\AI\SpriteSheetDiffusionSpike\repo\ModelTraining\pretrained_model`

Estimated download: **~13.7 GB**.

Core generation set:

1. Stable Diffusion v1.5 UNet config + weights;
2. Stability AI MSE VAE config + weights;
3. Lambda CLIP vision image encoder config + weights;
4. SSD fine-tuned `denoising_unet.pth`;
5. SSD fine-tuned `reference_unet.pth`;
6. AnimateAnyone baseline `pose_guider.pth`;
7. AnimateAnyone baseline `motion_module.pth`.

Known large-file SHA256 values are enforced by the manifest. Downloads are resumable through `.part` files and avoid a duplicate Hugging Face cache.

### Current operator state

The user reported on 2026-09-07 that **runner 26 is currently downloading**. Do not interrupt or restart it merely because the production-support plan has been expanded. Let runner 26 finish and report its PASS/FAIL normally.

## Production-authoring support decision — QUEUED AFTER CORE PASS

The first model manifest was intentionally the smallest complete inference set. The user has now clarified that the workstation should also hold the support assets needed for the **best practical spritesheet-authoring workflow**, not merely the minimum smoke test.

A second controlled asset gate is therefore prepared.

Manifest:

`tools/structured-2d-character-pipeline/ssd_authoring_support_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/27_download_ssd_authoring_support.ps1`

Additional download: approximately **0.42 GB**.

### 1. DWPose — production pose extraction

Download:

- `ModelTraining/models/openpose/yolox_l.onnx`;
- `ModelTraining/models/openpose/dw-ll_ucoco_384.onnx`.

Purpose:

- extract whole-body pose from arbitrary driving video/action references;
- body, hands and face are available through the repo's DWPose path;
- useful when authoring future walk/run/attack/dodge/hit/death actions instead of manually drawing pose maps;
- DWPose is the preferred detector path for this project.

The repo's DWPose implementation uses OpenCV DNN on CPU, so the already-installed OpenCV stack is enough; a separate ONNX Runtime install is not required for this path.

### 2. FILM interpolation — available but not default

Download:

- `ModelTraining/pretrained_model/film_net_fp16.pt`.

Purpose:

- make upstream `--accelerate` / interpolation mode available;
- produce optional in-between frames where it helps timing or source review.

Production rule:

**FILM is available, but not automatically used for final sprite frames.** Pixel-art silhouettes and hand-authored timing take priority; interpolated frames must pass visual QA because interpolation can soften or deform crisp sprite geometry.

### 3. MediaPipe task assets — already bundled, verify only

The upstream clone already contains:

- `utils/mp_models/blaze_face_short_range.tflite`;
- `utils/mp_models/face_landmarker_v2_with_blendshapes.task`;
- `utils/mp_models/pose_landmarker_heavy.task`.

Runner 27 verifies them instead of downloading duplicate copies.

## Intentionally excluded even from the full spritesheet-authoring kit

### wav2vec2 / AniPortrait audio models

Not downloaded. They support audio-driven portrait animation and do not improve action spritesheets for the Exilada.

### Legacy CMU OpenPose body/hand/face weights

Not downloaded. The bundled OpenPose preprocessor explicitly carries a non-commercial-use restriction, while DWPose provides a more appropriate whole-body extraction path for this project. Avoid making the production pipeline depend on legacy CMU OpenPose weights.

### AnimateAnyone baseline denoising/reference UNets

Not downloaded. They must not replace the SSD fine-tuned sprite UNets; doing so would reduce the point of this spike.

### xformers

Not installed by default. It is a memory/performance optimization rather than a model asset. Only add it if measured VRAM behavior on the RTX 3060 shows that the first real inference needs it, and only through a compatibility-verified Windows wheel/test gate.

## Runner 27 behavior

After runner 26 PASS, runner 27:

1. requires environment, dependency and core-model PASS markers;
2. downloads DWPose detector + whole-body ONNX models;
3. downloads FILM TorchScript interpolation model;
4. validates known SHA256 hashes;
5. verifies the three bundled MediaPipe task assets;
6. loads both DWPose ONNX files through OpenCV DNN as a structural probe;
7. loads FILM through `torch.jit.load(..., map_location='cpu')` as a structural probe;
8. writes:
   - `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_bootstrap.json`;
   - `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_probe.json`;
9. executes no actual SSD inference.

## Current exact operator sequence

### Right now

Let the already-running runner 26 finish.

### After `SSD-MODELS: PASS`

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\27_download_ssd_authoring_support.ps1"
```

Expected final support status:

- `SSD-SUPPORT: PASS`;
- DWPose available;
- FILM available;
- support marker/probe written.

## First real inference after support PASS

Then prepare **Exilada master + approved 8-state walk pose sequence + first real SSD inference**.

The first quality gate remains an 8-frame action, not a giant multi-action sheet. The purpose is to validate:

- identity persistence;
- body/proportion persistence;
- hair/clothing/equipment persistence from the complete master;
- temporal coherence;
- pose obedience;
- whether 512×512 / 8 frames fits the RTX 3060 12 GB;
- whether the generated RGB/background can be converted cleanly to transparent native sprite frames without damaging pixel edges.

Only after that PASS do we expand to the conventional multi-action sheet and automate frame packing/alpha/pivot metadata.

## Cleanup if SSD is explicitly discarded

```powershell
Remove-Item -LiteralPath "Z:\AI\SpriteSheetDiffusionSpike" -Recurse -Force -ErrorAction SilentlyContinue
& "C:\Users\jsaid\miniconda3\Scripts\conda.exe" env remove -n ssd -y
```

SSD is ACTIVE, so no cleanup applies now.
