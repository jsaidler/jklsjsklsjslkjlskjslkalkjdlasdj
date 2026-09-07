# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — ENVIRONMENT PASS / DEPENDENCIES PASS / CORE MODELS PASS / AUTHORING SUPPORT PASS / RUNNER 28 argv TRANSPORT FIX V2 READY / RETRY REQUIRED**

## Decision

The character-production target is a conventional **2D spritesheet**: approved persistent frames arranged by action in rows/blocks or equivalent atlas regions, with metadata for timing, pivots, hitboxes and events as needed.

The active offline source-authoring spike is **Sprite Sheet Diffusion (SSD)**, using the complete Exilada master as appearance reference plus pose/motion guidance. SSD is a production tool under validation, not a runtime dependency.

The workstation setup includes all assets genuinely useful/necessary for the best practical spritesheet-authoring workflow while excluding unrelated audio/portrait assets and unsuitable legacy components.

## Presentation/runtime lock retained

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime is ordinary spritesheet playback, not 3D, puppet assembly or diffusion.

## Local SSD stack — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- RTX 3060 detected;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real upstream `ModelTraining/inference.py` import graph PASS;
- core generation models PASS;
- authoring-support models PASS.

Latest user-supplied support result:

- `SSD-SUPPORT: PASS`;
- DWPose available;
- FILM available, optional/not default;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_bootstrap.json`;
- probe `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_probe.json`.

## Correct role of the downloaded AIs

### SSD

**Sprite Sheet Diffusion generates the visible Exilada frames.** It consumes an appearance/reference image, a reference pose for that image and a target pose sequence.

### DWPose

**DWPose is the downloaded AI pose extractor.** It converts RGB character/action images or driving video frames into body/hand/face pose maps.

For the first walk proof, DWPose extracts the pose of `exilada_master.png`, so the appearance reference has a matching pose-control image.

### C1A walk guide

The eight walk targets already exist as exact project-owned motion control. Re-running an AI detector over those eight states would add detection error for no benefit. Therefore those target maps are rendered deterministically from approved C1A joint coordinates using the SSD repo's OpenPose-style drawing convention.

Correct split:

`Exilada master --DWPose--> reference pose`

`approved C1A guide --deterministic conversion--> 8 target pose maps`

`master + reference pose + 8 targets --SSD--> 8 visible Exilada frames`

No manual/external pose folder is required from the user.

## Canonical eight-state walk

| Index | Source frame | Event | Support foot |
|---:|---:|---|---|
| 0 | 1588 | `left_contact` | left |
| 1 | 1598 | `left_down` | left |
| 2 | 1608 | `left_passing` | left |
| 3 | 1618 | `left_up` | left |
| 4 | 1628 | `right_contact` | right |
| 5 | 1638 | `right_down` | right |
| 6 | 1648 | `right_passing` | right |
| 7 | 1658 | `right_up` | right |

Canonical local guide:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

Existing C1A review PNGs must not be used as SSD control images because they contain labels, ground graphics, support-foot rings and review colors.

## Upstream inference issue handled

Upstream `ModelTraining/inference.py` assumes the first target pose is also the reference-image pose. That assumption is false for our master: the Exilada master is standing while target frame 1 is `left_contact`.

Project runner 28 leaves upstream `inference.py` untouched and generates a deterministic local copy with one narrow patch: a separate `reference_pose_path` is read from config while the target list stays exactly eight walk frames.

## Runner 28 execution history — SCRIPT FAILURES, NOT SSD FAILURES

Runner:

`tools/structured-2d-character-pipeline/28_run_ssd_exilada_walk8.ps1`

### Attempt 1 — `Start-Process -ArgumentList` raw array

Python reported:

`can't open file 'D:\\GOOGLE': [Errno 2] No such file or directory`

Root cause: Windows PowerShell 5.1 flattened the raw `Start-Process -ArgumentList` array and split the helper path `D:\GOOGLE DRIVE\...`.

### Attempt 2 — manually quoted `Start-Process -ArgumentList`

The added argv preflight correctly stopped the runner before DWPose/model work:

`SSD-WALK8: FAIL - native argument quoting preflight failed; refusing to run preparation with corrupted path arguments.`

This proves that manually constructing a quoted argument string around `Start-Process` is still not a reliable argv transport for this project on the operator's Windows PowerShell 5.1 environment.

No DWPose inference or SSD generation ran in either failed attempt. All prior PASS gates remain valid.

## Windows native process rule — LOCKED V2

For project Python invocations under Windows PowerShell 5.1:

1. **do not use `Start-Process -ArgumentList` for Python commands that contain paths with spaces**, whether supplied as a raw string array or manually reconstructed quoted string;
2. invoke Python directly with the PowerShell call operator and an argument array: `& $PythonExe @Arguments`;
3. temporarily use non-terminating native stderr handling and inspect `$LASTEXITCODE` explicitly;
4. route stdout/stderr to the console but never use stderr text as control flow;
5. keep the argv preflight using the actual project root and Exilada master path before any expensive model work;
6. if the preflight fails, print the received argv values before aborting.

## Runner 28 — FIX V2 / RETRY REQUIRED

Runner 28 now:

1. verifies environment/dependency/core-model/support PASS markers;
2. verifies the canonical C1A guide and Exilada master;
3. **does not use `Start-Process` for Python at all**;
4. invokes Python with `& $PythonExe @Arguments`, preserving array-item argv boundaries;
5. uses the same direct invocation path for preflight, preparation, SSD inference and review;
6. explicitly checks `$LASTEXITCODE` after every Python process;
7. preflights the exact `D:\GOOGLE DRIVE\DEV\Roguelite` and canonical Exilada master paths;
8. runs DWPose on the master and saves a 512×512 reference-pose map;
9. converts the eight approved C1A states to clean 512×512 OpenPose-style body maps;
10. writes a dedicated SSD config and local patched inference copy;
11. runs SSD at `512×512`, 8 frames, 25 steps, CFG 3.5, fp16, FILM disabled;
12. verifies exactly eight generated PNGs;
13. creates an unaltered 4×2 contact sheet and review GIF;
14. writes `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

No reinstall or redownload is required.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\28_run_ssd_exilada_walk8.ps1"
```

Expected early sequence:

- `[PREFLIGHT] Verifying native argument transport for paths containing spaces...`
- `[OK] Native argument transport preflight PASS.`
- `[PREP] Extracting Exilada reference pose with DWPose and building 8 clean target pose maps...`

## PASS semantics

Runner success means **output ready for visual QA**, not visual PASS.

Visual PASS requires review of:

- Exilada identity persistence;
- anatomy/proportion persistence;
- hair persistence;
- cloth/shackles/chains consistency;
- pose obedience;
- temporal coherence;
- suitability for native spritesheet production.

Only after visual PASS do we proceed to alpha cleanup, pivot/root alignment and sheet packing.

## Explicit exclusions

- wav2vec2 / AniPortrait audio models — unrelated;
- legacy CMU OpenPose body/hand/face weights — not a production dependency; DWPose is preferred;
- AnimateAnyone baseline denoising/reference UNets — must not replace SSD fine-tuned sprite UNets;
- xformers — optimization only if measured VRAM behavior requires it.

## Cleanup

SSD is ACTIVE. No cleanup applies.
