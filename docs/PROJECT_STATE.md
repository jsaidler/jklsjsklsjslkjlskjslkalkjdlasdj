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

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

## Retained offline motion source

- G2 PASS/CLOSED;
- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- C1A skeleton walk PASS/CLOSED;
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`.

This is the exact source of the first eight SSD walk targets. Do not ask the user for eight new pose images.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp -> gait — CLOSED;
- MPFB skinned body as mandatory guide — CLOSED;
- Flux2 independent full-body redraw per frame — FAIL/CLOSED;
- segmented 2D puppet runner 23 — PAUSED/HISTORICAL.

## CURRENT — SPRITE SHEET DIFFUSION LOCAL VALIDATION

Canonical doc: `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Goal: determine whether Sprite Sheet Diffusion can generate a coherent Exilada action sequence strongly enough that accepted frames can be frozen into conventional spritesheets.

## Installation / model / authoring-support gates — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- RTX 3060 detected;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD inference import graph PASS;
- core generation models PASS;
- authoring support PASS;
- DWPose available;
- FILM available, optional/not default.

## Correct role split — LOCKED

- **SSD** generates visible Exilada frames.
- **DWPose** extracts pose from RGB/reference/driving frames.
- **C1A** already owns the exact eight walk target poses.

First walk proof:

`Exilada master --DWPose--> matching reference pose`

`approved C1A guide --deterministic OpenPose-style render--> 8 clean target pose maps`

`master + reference pose + 8 targets --SSD--> 8 visible Exilada frames`

## CURRENT GATE — runner 28 first real Exilada inference

Helper:

`tools/structured-2d-character-pipeline/g3s_ssd_prepare_walk8.py`

Runner:

`tools/structured-2d-character-pipeline/28_run_ssd_exilada_walk8.ps1`

### Attempt 1 — SCRIPT FAIL

Error:

`can't open file 'D:\\GOOGLE': [Errno 2] No such file or directory`

Cause: raw `Start-Process -ArgumentList` array split `D:\GOOGLE DRIVE\...`.

### Attempt 2 — SCRIPT FAIL caught by preflight

Actual user result:

- `[PREFLIGHT] Verifying native argument transport for paths containing spaces...`
- `SSD-WALK8: FAIL - native argument quoting preflight failed; refusing to run preparation with corrupted path arguments.`

The preflight did its job: it prevented DWPose/SSD work from starting with corrupted argv. The manually quoted `Start-Process -ArgumentList` strategy is therefore also rejected for this project on Windows PowerShell 5.1.

Neither attempt invalidated environment/model/support PASS gates. No reinstall/redownload is required.

## Windows native Python invocation rule — LOCKED V2

Under Windows PowerShell 5.1:

- **do not use `Start-Process -ArgumentList` for project Python invocations containing paths with spaces**;
- invoke directly with the PowerShell call operator and array splatting: `& $PythonExe @Arguments`;
- temporarily prevent native stderr from becoming terminating control flow;
- show stdout/stderr but decide success only from `$LASTEXITCODE` and structured markers;
- preflight the actual project-root and Exilada-master paths before expensive model work;
- print received argv values on any future mismatch.

Runner 28 has been updated to follow this rule for preflight, input preparation, SSD inference and review. `Start-Process` is no longer used for Python in runner 28.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\28_run_ssd_exilada_walk8.ps1"
```

Expected early sequence:

- `[PREFLIGHT] Verifying native argument transport for paths containing spaces...`
- `[OK] Native argument transport preflight PASS.`
- `[PREP] Extracting Exilada reference pose with DWPose and building 8 clean target pose maps...`

Expected successful end state:

- `SSD-WALK8: OUTPUT READY FOR VISUAL QA`;
- eight generated PNGs;
- contact sheet;
- GIF;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

Visual PASS still requires review of identity, anatomy/proportions, hair, cloth/shackles/chains, pose obedience and temporal coherence.

## No cleanup

SSD is ACTIVE. Do not delete `Z:\AI\SpriteSheetDiffusionSpike`.
