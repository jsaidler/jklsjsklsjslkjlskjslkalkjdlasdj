# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — ENVIRONMENT PASS / DEPENDENCIES PASS / CORE MODELS PASS / AUTHORING SUPPORT PASS / FIRST EXILADA INFERENCE PREPARATION CURRENT**

## Decision

The character-production target is a conventional **2D spritesheet**: approved persistent frames arranged by action in rows/blocks or equivalent atlas regions, with metadata for timing, pivots, hitboxes and events as needed.

The active offline source-authoring spike is **Sprite Sheet Diffusion (SSD)**, using the complete Exilada master as appearance reference plus pose/motion guidance. SSD is a production tool under validation, not a runtime dependency.

The workstation setup must include all assets genuinely useful/necessary for the best practical spritesheet-authoring workflow, while excluding unrelated audio/portrait assets and legally unsuitable legacy components.

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
- inference loads SD1.5 UNet architecture, MSE VAE, CLIP vision encoder, SSD fine-tuned denoising/reference UNets, pose guider and motion module;
- inference consumes a directory of pose images;
- FILM interpolation is optional through `--accelerate`;
- DWPose is retained as the preferred production pose extractor for future arbitrary actions.

## Environment bootstrap — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`.

## Windows inference dependencies — PASS

Validated user result:

- `SSD-DEPS: PASS`;
- GPU `NVIDIA GeForce RTX 3060`;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD `inference.py` import graph PASS;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
- freeze `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`.

## Native-process scripting rule — LOCKED

For subsequent project PowerShell runners:

1. do not use an expected native-process failure as raw control flow under `$ErrorActionPreference='Stop'`;
2. do not depend on native STDERR/`2>&1` to decide expected states;
3. Python probes must catch expected exceptions and emit structured diagnostics;
4. native calls must have explicitly inspected exit codes;
5. project failure must end as a controlled `FAIL`, not an unhandled `NativeCommandError`.

## Core SSD generation models — PASS

Runner: `tools/structured-2d-character-pipeline/26_download_ssd_models.ps1`

Manifest: `tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Core generation set present under `ModelTraining/pretrained_model`:

- SD1.5 UNet;
- Stability AI MSE VAE;
- CLIP vision image encoder;
- SSD fine-tuned `denoising_unet.pth`;
- SSD fine-tuned `reference_unet.pth`;
- AnimateAnyone baseline `pose_guider.pth`;
- AnimateAnyone baseline `motion_module.pth`.

Runner 27 cannot reach PASS without the core-model PASS marker, so the subsequent authoring-support PASS structurally confirms the core model gate completed successfully.

## Production-authoring support — PASS

Runner: `tools/structured-2d-character-pipeline/27_download_ssd_authoring_support.ps1`

Actual user result on 2026-09-07:

- `SSD-SUPPORT: PASS`;
- DWPose available;
- FILM available, optional/not default;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_bootstrap.json`;
- probe `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_probe.json`.

DWPose is the preferred route for extracting pose maps from future driving footage/actions. FILM remains an optional interpolation tool and is not enabled for the first identity/temporal-coherence proof.

## Canonical eight-state walk source — CLARIFIED

The phrase **“8 poses”** does not mean eight new references the user must find or provide.

It refers to the already-approved C1A skeleton-only walk cycle derived from real CMU motion:

| Index | Source frame | Event | Support foot |
|---:|---:|---|---|
| 0 | 1588 | `left_contact` | left |
| 1 | 1598 | `left_down` | left |
| 2 | 1608 | `left_passing` | left |
| 3 | 1618 | `left_up` | left |
| 4 | 1628 | `right_contact` | right |
| 5 | 1638 | `right_down` | right |
| 6 | 1648 | `right_passing` | right |
| 7 | 1658 | `right_up` | right |

Canonical source data:

- guide: `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`;
- source motion: `CMU 105_34 NormalWalk`;
- rig: `G2_CANONICAL_RIG`;
- approved projected direction: screen-left/front-three-quarter;
- review playback: `83 ms` per state.

Existing C1A review PNGs also exist in that workspace as `g3s_c1_skeleton_walk_00_left_contact.png` through the corresponding eight states. **Those review images must not be fed directly into SSD**, because they contain labels, ground graphics, support-foot rings and review-specific colors.

The correct next preparation step is to render **clean SSD/OpenPose-compatible body pose maps** from the existing C1A guide data, with no labels/ground/review annotations. This is project work; the user must not be asked to invent a `YOUR_8_POSE_IMAGES` folder or manually locate new pose references.

## First real SSD inference — CURRENT

Inputs:

- complete `assets/source/characters/exilada/reference/exilada_master.png` as appearance reference;
- eight clean pose-control maps generated from the approved C1A guide;
- 8 frames;
- `512×512` first proof;
- FILM disabled initially.

Quality gate:

- identity persistence;
- anatomy/proportion persistence;
- hair/clothing/equipment persistence;
- pose obedience;
- temporal coherence;
- RTX 3060 12 GB memory fit;
- clean conversion of generated RGB/background to transparent native sprite frames.

Only after this PASS do we expand to conventional multi-action sheet production and automate packing, alpha cleanup, pivots and runtime metadata.

## Explicit exclusions

- wav2vec2 / AniPortrait audio models — unrelated;
- legacy CMU OpenPose body/hand/face weights — do not make production depend on them; DWPose is preferred;
- AnimateAnyone baseline denoising/reference UNets — must not replace SSD fine-tuned sprite UNets;
- xformers — optimization only, add later only if measured VRAM behavior requires it.

## Cleanup if SSD is explicitly discarded

```powershell
Remove-Item -LiteralPath "Z:\AI\SpriteSheetDiffusionSpike" -Recurse -Force -ErrorAction SilentlyContinue
& "C:\Users\jsaid\miniconda3\Scripts\conda.exe" env remove -n ssd -y
```

SSD is ACTIVE, so no cleanup applies now.
