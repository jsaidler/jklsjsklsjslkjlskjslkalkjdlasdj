# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
4. `docs/G1_CAMERA_SCALE_LOG.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

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
- gameplay depth movement does not require north/south/isometric sprite families;
- true isometric multi-directional character production remains closed unless explicitly reopened.

## Runtime animation representation — LOCKED

`approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary runtime sprite playback`

Runtime does not require a 3D skeleton, segmented puppet or diffusion model.

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

## Retained motion control

C1A skeleton-only walk: PASS/CLOSED.

- motion: CMU `105_34 NormalWalk`;
- rig: `G2_CANONICAL_RIG`;
- guide: `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`;
- approved states: `1588,1598,1608,1618,1628,1638,1648,1658`;
- first visible family: screen-left/front-three-quarter.

The user is not expected to supply eight manual pose images.

## Local SSD/authoring environment — PASS

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- Miniconda / env `ssd` PASS;
- Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- SSD import graph PASS;
- DWPose available;
- FILM available, optional/not default;
- released SSD denoising/reference UNets present;
- baseline AnimateAnyone pose guider + motion module present.

## Walk8 input preparation — PASS

Runner 28 V3 successfully passed the JSON path-control plane and reached real model inference.

This confirms:

- Exilada master path handling;
- DWPose reference-pose extraction;
- conversion of approved C1A states into eight clean target pose maps;
- dedicated first-walk SSD input config/preparation.

## Exact upstream SSD inference — BLOCKED

The first actual SSD model execution failed while loading `pose_guider.pth` into SSD's current custom `PoseGuider`.

Installed checkpoint architecture:

- Moore/AnimateAnyone baseline: `conv_in`, `blocks`, `conv_out`.

Current SSD code requires:

- custom multi-scale `conv_layers*`, `final_proj`, `cross_attn*`, `scale` architecture;
- strict checkpoint loading;
- multiple indexed pose features consumed by modified `unet_3d.py`.

The public SSD model release does not include that custom trained `pose_guider.pth`. Upstream issue #3 records the same missing-checkpoint blocker.

Therefore exact current-upstream SSD inference is **not reproducible from the public checkpoint set**. This is not a DWPose, CUDA or RTX 3060 failure.

The earlier project assumption that the baseline AnimateAnyone pose guider was a drop-in exact SSD checkpoint has been corrected in:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Current manifest status:

`EXACT_UPSTREAM_INFERENCE_BLOCKED_POSE_GUIDER_UNRELEASED`

Do not run runner 28 again and do not fake compatibility by loading the wrong checkpoint loosely into SSD's custom PoseGuider.

## CURRENT GATE — Moore-compatible empirical fallback

Purpose: salvage a meaningful local test using only architecture/checkpoint combinations that actually match.

Route:

`original Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD fine-tuned denoising/reference UNets`

This route is **not the exact published SSD graph**. It tests whether the released SSD UNets remain useful for Exilada sprite generation in the compatible parent graph.

Pinned Moore source commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

Helper:

`tools/structured-2d-character-pipeline/g3s_ssd_moore_compat_walk8.py`

Runner:

`tools/structured-2d-character-pipeline/29_run_ssd_moore_compat_exilada_walk8.ps1`

Runner 29 reuses all heavyweight models already present and fetches only Moore source code. It performs checkpoint-signature/graph compatibility checks before generation and labels the result `exact_upstream_ssd: false`.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\29_run_ssd_moore_compat_exilada_walk8.ps1"
```

Target:

- `SSD-MOORE-COMPAT: OUTPUT READY FOR VISUAL QA`;
- 8 PNG frames;
- contact sheet;
- GIF;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_moore_compat.json`.

Technical success is not visual approval. Review identity, anatomy/proportions, long hair, cloth/shackles/chains, pose obedience and temporal coherence before any expansion to more actions or sheet packing.

## Exact SSD future condition

Exact SSD remains blocked unless a trustworthy compatible custom pose-guider checkpoint becomes available or the project explicitly decides to retrain the missing stage-1/custom pose stack.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- Flux2 independent per-frame redraw — FAIL/CLOSED;
- segmented 2D puppet — PAUSED/HISTORICAL;
- runner 28 exact-upstream SSD attempt — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## No cleanup

The SSD workspace and released fine-tuned models remain useful for the active fallback investigation. No cleanup applies.
