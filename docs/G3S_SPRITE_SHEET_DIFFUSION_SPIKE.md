# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — ENVIRONMENT PASS / DEPENDENCIES PASS / CORE MODELS PASS / AUTHORING SUPPORT PASS / RUNNER 28 PATH-ARGUMENT BUG FIXED / RETRY REQUIRED**

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

## Runner 28 first execution — FAIL due path argument corruption

Runner:

`tools/structured-2d-character-pipeline/28_run_ssd_exilada_walk8.ps1`

Actual first execution reached:

`[PREP] Extracting Exilada reference pose with DWPose and building 8 clean target pose maps...`

then Python reported:

`can't open file 'D:\\GOOGLE': [Errno 2] No such file or directory`

and the runner ended:

`SSD-WALK8: FAIL - input preparation exited with code 2`

This is a **runner defect**, not an SSD, DWPose, CUDA or model-quality failure.

### Root cause

Windows PowerShell 5.1 `Start-Process -ArgumentList` was given a raw string array containing the helper path under:

`D:\GOOGLE DRIVE\DEV\Roguelite\...`

The array was flattened into a command line without preserving the whitespace-bearing script path as one argv item. Python therefore received only `D:\GOOGLE` as the script path.

## Native process rules — LOCKED

Existing rule remains: expected native failures must not be raw control flow under `$ErrorActionPreference='Stop'`; use structured diagnostics and explicit exit-code handling.

Additional Windows argument-boundary rule:

1. **never pass a raw string array containing whitespace-bearing paths to Windows PowerShell 5.1 `Start-Process -ArgumentList`;**
2. build one explicitly quoted argument line, or use another transport that preserves argv boundaries;
3. any runner that depends on space-bearing paths must preflight argv transport before expensive/model work;
4. `D:\GOOGLE DRIVE\DEV\Roguelite` and the canonical Exilada master path are regression-test inputs for runner 28.

## Runner 28 — FIXED / RETRY REQUIRED

Runner 28 now:

1. verifies environment/dependency/core-model/support PASS markers;
2. verifies the canonical C1A guide and Exilada master;
3. routes every Python child process through one controlled invocation helper;
4. explicitly quotes whitespace-bearing arguments before `Start-Process`;
5. uses PowerShell splatting instead of fragile line-continuation syntax;
6. runs a tiny Python argv transport preflight and confirms the full project-root and master paths arrive intact;
7. refuses to continue if that preflight fails;
8. runs DWPose on the master and saves a 512×512 reference-pose map;
9. converts the eight approved C1A states to clean 512×512 OpenPose-style body maps;
10. writes a dedicated SSD config and local patched inference copy;
11. runs SSD at `512×512`, 8 frames, 25 steps, CFG 3.5, fp16, FILM disabled;
12. verifies exactly eight generated PNGs;
13. creates an unaltered 4×2 contact sheet and review GIF;
14. writes `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

No reinstall or redownload is required. The failed first run did not invalidate any prior PASS gate.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\28_run_ssd_exilada_walk8.ps1"
```

Expected early sequence after the fix:

- `[PREFLIGHT] Verifying native argument transport for paths containing spaces...`
- `[OK] Native argument quoting preflight PASS.`
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
