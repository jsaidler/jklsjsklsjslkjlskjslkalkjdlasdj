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

## No manual eight-pose folder

The eight walk targets already exist in the approved C1A guide:

1. 1588 — `left_contact`;
2. 1598 — `left_down`;
3. 1608 — `left_passing`;
4. 1618 — `left_up`;
5. 1628 — `right_contact`;
6. 1638 — `right_down`;
7. 1648 — `right_passing`;
8. 1658 — `right_up`.

Canonical guide:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

Role split:

- SSD generates visible Exilada frames;
- DWPose extracts the reference pose from the Exilada master and future RGB/driving actions;
- C1A supplies the exact eight walk target states.

## Runner 28 execution history

Runner:

`tools/structured-2d-character-pipeline/28_run_ssd_exilada_walk8.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_ssd_prepare_walk8.py`

### Attempt 1 — SCRIPT FAIL

Raw `Start-Process -ArgumentList` split `D:\GOOGLE DRIVE\...`.

### Attempt 2 — SCRIPT FAIL caught before model work

Manually quoted `Start-Process -ArgumentList` still failed the argv preflight.

### Attempt 3 — SCRIPT FAIL caught before model work

Call-operator/array-splatting still delivered the two whitespace-bearing payload paths as one concatenated Python argument. Actual received count was `1`.

No DWPose or SSD generation ran in these failures. They do not invalidate any installed model/dependency/support PASS gate.

## Windows transport rule — LOCKED V3

Do not carry project paths containing spaces through native Python argv at all.

Runner 28 now uses JSON request transport:

- request: `Z:\AI\SpriteSheetDiffusionSpike\ssd_walk8_prepare_request.json`;
- local helper copy: `Z:\AI\SpriteSheetDiffusionSpike\g3s_ssd_prepare_walk8.py`;
- local request wrapper: `Z:\AI\SpriteSheetDiffusionSpike\g3s_ssd_walk8_request.py`;
- Python receives only paths under `Z:\AI` with no spaces;
- real project-root/master/guide/model-training/marker values are decoded from JSON;
- preflight requires Python to write the decoded values back and PowerShell to match them exactly before any DWPose/model work.

New source wrapper:

`tools/structured-2d-character-pipeline/g3s_ssd_walk8_request.py`

## Current runner — FIX V3 / RETRY READY

After JSON preflight PASS it runs:

- Exilada master -> DWPose reference pose;
- C1A guide -> 8 clean target maps;
- SSD -> 8 visible Exilada frames at 512×512, 25 steps, CFG 3.5, fp16;
- FILM disabled;
- contact sheet + GIF.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\28_run_ssd_exilada_walk8.ps1"
```

Expected early output:

- `[PREFLIGHT] Verifying JSON control-plane transport of the actual Windows paths...`
- `SSD-WALK8-REQUEST-PROBE: PASS`
- `[OK] JSON path transport preflight PASS.`
- `[PREP] Extracting Exilada reference pose with DWPose and building 8 clean target pose maps...`

Successful technical end state:

- `SSD-WALK8: OUTPUT READY FOR VISUAL QA`;
- eight generated PNGs;
- contact sheet;
- GIF;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

Do not declare visual PASS until the user reviews identity, anatomy/proportions, hair, cloth/shackles/chains, pose obedience and temporal coherence.

SSD route remains ACTIVE. No cleanup applies.
