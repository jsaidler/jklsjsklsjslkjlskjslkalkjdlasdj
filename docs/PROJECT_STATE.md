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

Runtime does not require a 3D skeleton, segmented puppet or diffusion model. World-space locomotion/root translation is a runtime concern and does not require baked root travel in the sprite frames.

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

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

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

## Exact upstream SSD inference — BLOCKED

Exact current-upstream SSD inference remains blocked because the public release does not contain the custom trained multi-scale `pose_guider.pth` required by SSD's current `PoseGuider` and modified `unet_3d.py`.

The installed baseline Moore/AnimateAnyone pose-guider checkpoint is structurally different and is retained only for the compatible Moore fallback. Do not run runner 28 again and do not fake exact compatibility with loose loading.

Manifest status:

`EXACT_UPSTREAM_INFERENCE_BLOCKED_POSE_GUIDER_UNRELEASED`

## Runner 29 Moore-compatible fallback — TECHNICAL PASS / VISUAL FAIL

Route:

`original Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD fine-tuned denoising/reference UNets`

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

Runner:

`tools/structured-2d-character-pipeline/29_run_ssd_moore_compat_exilada_walk8.ps1`

Technical execution passed:

- 8 frames generated at `512×512`, 25 steps, CFG `3.5`, seed `42`, fp16;
- SSD denoising checkpoint produced 0 unexpected Moore keys;
- the 588 missing denoising keys are covered by the SD1.5 + motion-module initialization before the partial SSD overlay;
- reference UNet and baseline Moore pose guider loaded successfully;
- PNGs, contact sheet, GIF and result marker were written.

Visual QA of the supplied contact sheet/GIF **failed for production use**:

- Exilada identity/hair silhouette remained partly stable;
- the eight C1A gait phases were insufficiently differentiated;
- pose obedience was weak;
- lower legs, ankles and feet became unstable/deformed;
- detached dark accessory/foot-like artifacts appeared near the ground;
- temporal stability came partly from insufficient motion rather than a convincing walk.

Therefore runner 29 is **not** approved for new actions, sheet packing or production expansion.

## Concrete input defect discovered after runner 29 QA

`g3s_ssd_prepare_walk8.py` converts C1A coordinates from the locked `640×360` projection to a `512×512` pose canvas by normalizing X and Y independently:

- X scale = `512/640 = 0.8`;
- Y scale = `512/360 = 1.4222...`;
- relative vertical stretch = `1.7778×` compared with horizontal geometry.

The target skeleton is therefore spatially distorted before it reaches the pose guider and is not explicitly registered to the DWPose body footprint extracted from the Exilada master.

This is now the single bounded hypothesis to test before closing the Moore-compatible salvage route.

## CURRENT GATE — runner 30 pose-scale registration discriminant

New helper:

`tools/structured-2d-character-pipeline/g3s_ssd_align_walk8_poses.py`

New runner:

`tools/structured-2d-character-pipeline/30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1`

Runner 30 changes **only target-pose spatial registration**:

- rebuilds the same canonical Exilada + C1A package;
- measures the DWPose body footprint from the master reference pose;
- reconstructs the eight C1A OpenPose maps directly from original `640×360` joint coordinates using one uniform geometry scale;
- registers pelvis X to the reference-body center and the lowest ankle Y to the reference-body bottom;
- removes per-frame root travel for this in-place sprite-authoring test; runtime locomotion remains separate;
- hard-fails on clipping, non-unique pose maps or poor reference-height registration;
- emits a 3×3 pose-alignment review before inference;
- then uses the **same** Moore graph, weights, `512×512`, 25 steps, CFG `3.5`, seed `42`, fp16 as runner 29.

No master crop, FILM, CFG/seed sweep, resolution change, model change or new action is allowed in this A/B test.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1"
```

Expected technical terminal marker:

`SSD-MOORE-POSE-ALIGNED: OUTPUT READY FOR A/B VISUAL QA`

Then share:

1. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_pose_aligned_inputs\exilada_walk8_pose_alignment_review.png`;
2. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat_pose_aligned\exilada_walk8_moore_compat_contact_sheet.png`;
3. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat_pose_aligned\exilada_walk8_moore_compat.gif`.

## Runner 30 decision rule — LOCKED

PASS requires a **clear A/B improvement over runner 29** in both:

1. readable C1A contact/down/passing/up pose progression and left/right alternation;
2. lower-leg/ankle/foot topology and ground contact;

while not materially degrading Exilada identity/proportions.

If runner 30 does **not** clearly improve those two failure classes, close the Moore-compatible SSD salvage route instead of beginning parameter sweeps.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- Flux2 independent per-frame redraw — FAIL/CLOSED;
- segmented 2D puppet — PAUSED/HISTORICAL;
- runner 28 exact-upstream SSD attempt — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## No cleanup

The SSD workspace and released fine-tuned models remain useful for the current bounded runner-30 investigation. No cleanup applies yet.
