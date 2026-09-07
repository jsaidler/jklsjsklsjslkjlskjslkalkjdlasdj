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
- final runtime = conventional deterministic spritesheet playback.

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

## Canonical walk8 inputs

No manual pose folder is needed.

Approved C1A states:

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

Runner 28 V3 successfully completed JSON path transport and input preparation, so DWPose reference-pose extraction + eight clean C1A target maps are operational.

## Critical current fact — exact upstream SSD is BLOCKED

Runner 28 reached actual model initialization and failed at strict loading of `pose_guider.pth`.

The downloaded baseline checkpoint is Moore/AnimateAnyone architecture:

`conv_in / blocks / conv_out`

Current SSD expects its own custom multi-scale architecture:

`conv_layers* / final_proj / cross_attn* / scale`

SSD's modified UNet consumes multiple pose-feature scales; Moore's original UNet consumes one. The checkpoints are therefore not interchangeable.

The SSD authors' public weights do not include the required custom trained pose guider. Upstream issue #3 reports the same missing-file blocker.

Consequences:

- runner 28 exact-upstream route is BLOCKED/CLOSED;
- do not run it again;
- do not load the baseline checkpoint `strict=False` into the custom SSD PoseGuider;
- no CUDA/DWPose/environment reinstall is required;
- `ssd_model_manifest.json` has been corrected so baseline pose guider is labelled fallback-only, not exact-SSD compatible.

## CURRENT route — Moore-compatible empirical fallback

Use the compatible parent graph:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion + released SSD fine-tuned denoising/reference UNets`

This is explicitly **not** the exact published SSD graph. It is a bounded empirical test of the useful released SSD weights.

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

New helper:

`tools/structured-2d-character-pipeline/g3s_ssd_moore_compat_walk8.py`

New runner:

`tools/structured-2d-character-pipeline/29_run_ssd_moore_compat_exilada_walk8.ps1`

Runner 29:

- rebuilds the canonical Exilada walk8 inputs automatically;
- fetches only pinned Moore source code under `Z:\AI\SpriteSheetDiffusionSpike\moore_animateanyone`;
- reuses all downloaded heavyweight models;
- checks baseline pose-guider checkpoint signature;
- loads Moore matching PoseGuider/UNet/pipeline;
- loads released SSD denoising/reference weights;
- runs 512×512, 8 frames, 25 steps, CFG 3.5, seed 42, fp16;
- writes PNG frames, contact sheet, GIF and result marker with `exact_upstream_ssd: false`.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\29_run_ssd_moore_compat_exilada_walk8.ps1"
```

Expected technical success:

- `SSD-MOORE-COMPAT: OUTPUT READY FOR VISUAL QA`;
- eight PNG frames;
- contact sheet;
- GIF;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_moore_compat.json`.

If it fails, diagnose the exact Moore/SSD checkpoint/import/VRAM error. Do not broaden the architecture or begin another model search before closing that failure.

If it succeeds, inspect visual identity, anatomy/proportions, long hair, cloth/shackles/chains, pose obedience and temporal coherence before expanding to any more actions.

## Future exact SSD condition

Exact SSD remains blocked until a trustworthy compatible custom pose-guider checkpoint is released/found, or the project explicitly decides to retrain the missing custom stage-1 pose stack.

SSD workspace remains active. No cleanup applies.
