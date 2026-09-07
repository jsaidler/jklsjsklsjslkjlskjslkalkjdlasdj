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

## Current source-authoring route

**Sprite Sheet Diffusion (SSD)** validation spike.

All installation/model/support gates are PASS:

- env `ssd` PASS;
- Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- SSD import graph PASS;
- core generation models PASS;
- `SSD-SUPPORT: PASS`;
- DWPose available;
- FILM available, optional/not default.

## Critical correction — no manual eight-pose folder

The earlier placeholder `YOUR_8_POSE_IMAGES` instruction was wrong and must not recur.

The eight walk targets already exist in the approved C1A guide:

1. 1588 — `left_contact`;
2. 1598 — `left_down`;
3. 1608 — `left_passing`;
4. 1618 — `left_up`;
5. 1628 — `right_contact`;
6. 1638 — `right_down`;
7. 1648 — `right_passing`;
8. 1658 — `right_up`.

Canonical local guide:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

Role split:

- SSD generates visible Exilada frames;
- DWPose extracts pose from RGB/reference/driving images/video;
- C1A already owns the exact walk target motion.

For walk8:

`Exilada master --DWPose--> reference pose`

`C1A guide --deterministic OpenPose-style conversion--> 8 target maps`

`master + reference pose + targets --SSD--> 8 visible frames`

This avoids both manual pose authoring and unnecessary AI re-detection of exact motion data.

## Current runner — READY

Helper:

`tools/structured-2d-character-pipeline/g3s_ssd_prepare_walk8.py`

Runner:

`tools/structured-2d-character-pipeline/28_run_ssd_exilada_walk8.ps1`

It automatically prepares the inputs, runs DWPose on the master, creates the eight target control maps, handles the upstream reference-pose assumption via a generated local inference copy, runs SSD at 512×512 / 8 frames / 25 steps / CFG 3.5 / fp16, and builds a contact sheet + GIF.

FILM remains disabled for this first proof.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\28_run_ssd_exilada_walk8.ps1"
```

Successful technical end state:

- `SSD-WALK8: OUTPUT READY FOR VISUAL QA`;
- eight generated PNGs;
- contact sheet;
- GIF;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

Do not declare visual PASS until the user reviews identity, anatomy/proportions, hair, cloth/shackles/chains, pose obedience and temporal coherence.

## PowerShell rule

Expected native failures cannot be raw control flow under `$ErrorActionPreference='Stop'`. Use controlled child processes, structured diagnostics and explicit exit-code handling.

SSD route remains ACTIVE. No cleanup applies.
