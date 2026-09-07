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

## Canonical Exilada references

Complete design/master reference:

`assets/source/characters/exilada/reference/exilada_master.png`

Earlier approved body-base artifact remains retained for provenance:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

The active SSD spike uses the **complete master** as appearance reference.

## Retained offline motion source

- G2 PASS/CLOSED;
- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- C1A skeleton walk PASS/CLOSED;
- approved eight-state cycle `1588,1598,1608,1618,1628,1638,1648,1658`.

This may be reused as offline pose/motion control only.

## Closed / historical visible routes

- direct visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid body partition — CLOSED;
- whole-body chain/cage warp -> gait — CLOSED;
- MPFB skinned body as mandatory guide — CLOSED;
- independent Flux2 full-body redraw per frame — FAIL/CLOSED;
- segmented 2D puppet runner 23 — PAUSED/HISTORICAL, NOT CURRENT.

## CURRENT — SPRITE SHEET DIFFUSION LOCAL VALIDATION

Canonical doc:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Goal:

Determine whether Sprite Sheet Diffusion can generate a coherent Exilada action sequence from the master plus pose/motion guidance strongly enough that accepted frames can be frozen into conventional spritesheets.

### Verified upstream layout

Repo:

`chenganhsieh/Sprite-Sheet-Diffusion`

- inference: `ModelTraining/inference.py`;
- config: `ModelTraining/configs/prompts/inference.yaml`;
- real upstream dependency file: `ModelTraining/requirements.txt`;
- there is no root `requirements.txt` despite the README command;
- config requires SD1.5 base, VAE, CLIP image encoder, SSD denoising/reference UNets, AnimateAnyone pose guider and motion module.

### Environment gate — PASS

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Actual user result:

- upstream clone: SUCCESS;
- Miniconda: SUCCESS;
- `conda.exe`: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- env `ssd`: PASS;
- Python: `3.10.21`;
- pip: `26.2.1`;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`.

No model weights were downloaded by the environment gate.

## CURRENT RUNNER — Windows inference dependencies

Requirements lock:

`tools/structured-2d-character-pipeline/ssd_windows_inference_requirements.txt`

Runner:

`tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

Key compatibility decisions:

- install `torch==2.0.1` + `torchvision==0.15.2` from official CUDA 11.8 wheels;
- do not blindly install the full mixed training/UI upstream requirements;
- defer optional `xformers` for the first proof;
- use `av==12.0.0` on Windows because upstream `av==11.0.0` is source-only on PyPI and the required APIs are compatible;
- include `matplotlib`/`scikit-image` because the imported local OpenPose graph requires them.

Runner 25 performs package install, `pip check`, CUDA probe and a real import of upstream `ModelTraining/inference.py` without loading models. It writes local dependency marker/probe/freeze files and downloads no checkpoints.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\25_bootstrap_ssd_dependencies.ps1"
```

PASS target:

- `SSD-DEPS: PASS`;
- CUDA available;
- torch 2.0.1 / CUDA build 11.8;
- RTX/NVIDIA GPU reported;
- real SSD inference import graph PASS.

After dependency PASS, prepare the separate model/checkpoint download gate. No model download before then.

## No cleanup

SSD is ACTIVE. Do not delete `Z:\AI\SpriteSheetDiffusionSpike`.
