# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — ENVIRONMENT PASS / DEPENDENCIES PASS / CORE MODELS PASS / AUTHORING SUPPORT PASS / RUNNER 28 TRANSPORT FIX V3 READY / RETRY REQUIRED**

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
- authoring-support models PASS;
- DWPose available;
- FILM available, optional/not default.

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

### Attempt 1 — raw `Start-Process -ArgumentList`

Python received only `D:\GOOGLE` for the helper path and failed before preparation.

### Attempt 2 — manually quoted `Start-Process -ArgumentList`

The argv preflight failed before DWPose/model work. Manual quoting around `Start-Process` is rejected.

### Attempt 3 — PowerShell call-operator array splatting

The user supplied the exact preflight result:

- expected two payload arguments;
- received count: `1`;
- received value: `D:\GOOGLE DRIVE\DEV\Roguelite D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png`.

Therefore `& $PythonExe @Arguments` through the runner's function/parameter path also failed to preserve the two whitespace-bearing Windows paths as separate native argv entries in this Windows PowerShell 5.1 environment.

This third failure was again caught before DWPose or SSD inference. No model, CUDA, dependency or quality gate failed.

## Windows native transport rule — LOCKED V3

Do **not** keep trying to solve this by adding another quoting layer.

For project Python control-plane data under Windows PowerShell 5.1:

1. whitespace-bearing project paths are **not transported through native argv**;
2. project-root, master path, guide path and markers are serialized into a UTF-8 JSON request file under `Z:\AI\SpriteSheetDiffusionSpike`, whose path contains no spaces;
3. the Python helper and request wrapper are copied to the same no-space SSD workspace before native invocation;
4. Python receives only no-space script/request paths plus scalar literals;
5. a Python request probe reads the JSON and writes the decoded values back; PowerShell compares them byte-for-string with the expected actual paths before DWPose/model work;
6. `Start-Process` and dynamic native argument-array splatting are no longer used by runner 28.

This removes the failing transport class instead of attempting to quote around it.

## Runner 28 — FIX V3 / RETRY REQUIRED

New request wrapper:

`tools/structured-2d-character-pipeline/g3s_ssd_walk8_request.py`

Runner 28 now:

1. verifies environment/dependency/core-model/support PASS markers;
2. verifies canonical guide/master/helper sources;
3. copies `g3s_ssd_prepare_walk8.py` and `g3s_ssd_walk8_request.py` to `Z:\AI\SpriteSheetDiffusionSpike`;
4. writes `Z:\AI\SpriteSheetDiffusionSpike\ssd_walk8_prepare_request.json` containing all real project paths;
5. invokes the local request wrapper using only no-space argv;
6. verifies a Python-decoded request probe against the exact project root/master/model-training/guide/marker values;
7. only after probe PASS runs DWPose on the master and builds the eight clean target maps;
8. writes a dedicated SSD config and local patched inference copy;
9. runs SSD at `512×512`, 8 frames, 25 steps, CFG 3.5, fp16, FILM disabled;
10. verifies exactly eight generated PNGs;
11. creates an unaltered 4×2 contact sheet and review GIF;
12. writes `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_inference.json`.

No reinstall or redownload is required.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\28_run_ssd_exilada_walk8.ps1"
```

Expected early sequence:

- `[PREFLIGHT] Verifying JSON control-plane transport of the actual Windows paths...`
- `SSD-WALK8-REQUEST-PROBE: PASS`
- `[OK] JSON path transport preflight PASS.`
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

## Cleanup

SSD is ACTIVE. No cleanup applies.
