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

## Runner 28 first execution — SCRIPT FAIL / CLOSED

Helper:

`tools/structured-2d-character-pipeline/g3s_ssd_prepare_walk8.py`

Runner:

`tools/structured-2d-character-pipeline/28_run_ssd_exilada_walk8.ps1`

Actual first error:

`C:\Users\jsaid\miniconda3\envs\ssd\python.exe: can't open file 'D:\\GOOGLE': [Errno 2] No such file or directory`

Root cause: Windows PowerShell 5.1 `Start-Process -ArgumentList` flattened a raw string array and split the helper path under `D:\GOOGLE DRIVE\...` at the first space.

This was a runner bug only. No SSD/DWPose/model gate was invalidated.

## Windows native argument rule — LOCKED

- never pass raw string arrays containing whitespace-bearing paths to Windows PowerShell 5.1 `Start-Process -ArgumentList`;
- explicitly quote the constructed native argument line, or use an argv-preserving transport;
- runners using paths with spaces must preflight argument transport before expensive/model work;
- actual project-root and Exilada master paths are regression-test cases.

## Current runner — FIXED / RETRY READY

Runner 28 now:

- uses one controlled Python invocation function;
- explicitly quotes whitespace-bearing arguments;
- uses PowerShell splatting, not fragile continuation syntax;
- performs a Python argv transport preflight before DWPose/model work;
- verifies the complete project-root and master paths arrive intact;
- applies the same controlled quoting to preparation, inference and review.

After the preflight it automatically runs DWPose on the master, creates the eight target control maps, handles the upstream reference-pose assumption via a generated local inference copy, runs SSD at 512×512 / 8 frames / 25 steps / CFG 3.5 / fp16, and builds a contact sheet + GIF.

FILM remains disabled for this first proof.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\28_run_ssd_exilada_walk8.ps1"
```

Expected early output:

- `[PREFLIGHT] Verifying native argument transport for paths containing spaces...`
- `[OK] Native argument quoting preflight PASS.`
- `[PREP] ...`

Successful technical end state:

- `SSD-WALK8: OUTPUT READY FOR VISUAL QA`;
- eight generated PNGs;
- contact sheet;
- GIF;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

Do not declare visual PASS until the user reviews identity, anatomy/proportions, hair, cloth/shackles/chains, pose obedience and temporal coherence.

## PowerShell rules

Expected native failures cannot be raw control flow under `$ErrorActionPreference='Stop'`. Use controlled child processes, structured diagnostics and explicit exit-code handling. Space-bearing paths additionally require argv transport preflight.

SSD route remains ACTIVE. No cleanup applies.
