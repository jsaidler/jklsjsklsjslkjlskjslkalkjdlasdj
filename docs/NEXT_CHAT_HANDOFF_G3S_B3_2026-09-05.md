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

`Start-Process -ArgumentList` with a raw array split `D:\GOOGLE DRIVE\...`; Python received `D:\GOOGLE`.

### Attempt 2 — SCRIPT FAIL caught before model work

The manually quoted `Start-Process -ArgumentList` approach still failed the argv preflight:

`SSD-WALK8: FAIL - native argument quoting preflight failed; refusing to run preparation with corrupted path arguments.`

This second failure is also a runner defect, not SSD/DWPose/CUDA/model failure. The preflight prevented any expensive work from starting.

## Windows Python invocation rule — LOCKED V2

For Windows PowerShell 5.1 project runners:

- do not use `Start-Process -ArgumentList` for Python invocations containing whitespace-bearing paths;
- invoke Python with `& $PythonExe @Arguments`;
- display native output but use `$LASTEXITCODE` and structured marker files for control flow;
- keep a preflight using the exact project-root and Exilada-master paths;
- on mismatch, print actual argv before aborting.

## Current runner — FIX V2 / RETRY READY

Runner 28 now uses no `Start-Process` for Python. The same direct argv-preserving invocation is used for:

1. path transport preflight;
2. DWPose/reference + C1A target-map preparation;
3. SSD inference;
4. contact-sheet/GIF review generation.

After preflight PASS it runs:

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

- `[PREFLIGHT] Verifying native argument transport for paths containing spaces...`
- `[OK] Native argument transport preflight PASS.`
- `[PREP] Extracting Exilada reference pose with DWPose and building 8 clean target pose maps...`

Successful technical end state:

- `SSD-WALK8: OUTPUT READY FOR VISUAL QA`;
- eight generated PNGs;
- contact sheet;
- GIF;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

Do not declare visual PASS until the user reviews identity, anatomy/proportions, hair, cloth/shackles/chains, pose obedience and temporal coherence.

SSD route remains ACTIVE. No cleanup applies.
