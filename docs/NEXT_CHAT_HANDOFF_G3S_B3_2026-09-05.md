# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
4. `docs/G1_CAMERA_SCALE_LOG.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`

## Locked production direction

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed `640×360` orthographic camera, pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- no isometric north/south character-family multiplication;
- final runtime = conventional deterministic spritesheet playback;
- runtime/world locomotion is separate from baked sprite root translation.

## Local authoring stack

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Environment/support PASS:

- env `ssd`, Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- DWPose available;
- FILM available but not default;
- released SSD denoising/reference UNets present;
- baseline AnimateAnyone pose guider + motion module present.

## Canonical C1A walk8

Approved states:

1. 1588 — `left_contact`;
2. 1598 — `left_down`;
3. 1608 — `left_passing`;
4. 1618 — `left_up`;
5. 1628 — `right_contact`;
6. 1638 — `right_down`;
7. 1648 — `right_passing`;
8. 1658 — `right_up`.

Guide:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

No manual pose folder is required.

## Exact upstream SSD — BLOCKED

The public SSD release does not include the custom multi-scale `pose_guider.pth` required by the current SSD graph. The available Moore/AnimateAnyone baseline checkpoint is structurally incompatible with that custom pose guider.

Runner 28 exact-upstream route remains BLOCKED/CLOSED. Do not run it again and do not fake compatibility with loose loading.

## Runner 29 Moore-compatible fallback — TECHNICAL PASS / VISUAL FAIL

Fallback route:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion + released SSD fine-tuned denoising/reference UNets`

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

Runner 29 generated all eight `512×512` frames successfully at 25 steps, CFG `3.5`, seed `42`, fp16. Model/checkpoint loading was technically coherent for the fallback graph.

The supplied contact sheet/GIF then failed visual QA for production use:

- Exilada identity remained partly stable;
- pose progression was too weak;
- contact/down/passing/up phases were not clearly differentiated;
- lower legs/ankles/feet became unstable;
- detached dark ground artifacts appeared;
- apparent temporal stability came partly from under-animation.

Therefore runner 29 is not approved for production expansion.

## Concrete prep defect found after QA

Current target-pose preparation maps locked C1A `640×360` coordinates to `512×512` using independent axis normalization:

- X scale `0.8`;
- Y scale `1.4222...`;
- relative vertical stretch `1.7778×`.

The target skeleton is therefore distorted and not explicitly registered to the master DWPose body footprint.

This is the single bounded hypothesis selected for the next A/B test.

## CURRENT GATE — runner 30 pose-registration discriminant

Helper:

`tools/structured-2d-character-pipeline/g3s_ssd_align_walk8_poses.py`

Runner:

`tools/structured-2d-character-pipeline/30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1`

Runner 30:

- rebuilds the same canonical Exilada + C1A package;
- measures the DWPose body footprint from the master reference pose;
- reconstructs all eight target poses directly from original C1A coordinates with one uniform scale;
- registers pelvis X to reference-body center and lowest ankle Y to reference-body bottom;
- removes target-pose root travel only for in-place sprite authoring;
- hard-fails on clipping, duplicate maps or poor body-height registration;
- emits a 3×3 pose-alignment review;
- reruns the exact same Moore+SSD inference parameters as runner 29.

No crop, FILM, model swap, new action, CFG/seed sweep or resolution sweep is allowed.

## EXACT NEXT OPERATOR ACTION

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1"
```

Expected terminal marker:

`SSD-MOORE-POSE-ALIGNED: OUTPUT READY FOR A/B VISUAL QA`

Then share these three artifacts:

1. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_pose_aligned_inputs\exilada_walk8_pose_alignment_review.png`
2. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat_pose_aligned\exilada_walk8_moore_compat_contact_sheet.png`
3. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat_pose_aligned\exilada_walk8_moore_compat.gif`

## Decision rule

Runner 30 passes only if it clearly improves **both** C1A pose readability and lower-limb/foot topology over runner 29, without materially degrading Exilada identity.

If those two classes are not clearly better, close the Moore-compatible SSD salvage route instead of beginning parameter sweeps.

## Future exact SSD condition

Exact SSD remains blocked until a trustworthy compatible custom pose-guider checkpoint is released/found, or the project explicitly decides to retrain the missing custom pose stack.

No cleanup before runner 30 is reviewed.
