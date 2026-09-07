# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/G1_CAMERA_SCALE_LOG.md`
6. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
7. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

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
- first visible family remains screen-left / mostly lateral-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- true isometric multi-directional character production remains closed unless explicitly reopened.

The exact horizontal facing angle inside that mostly-lateral family is **reopened for locomotion art-direction review**. The previous `45 deg` azimuth from motion heading was sufficient for a mechanical C1A sanity proof but is not automatically the production gameplay angle.

## Runtime animation representation — LOCKED

`approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary sprite playback`

Runtime does not require a 3D skeleton, segmented puppet or diffusion model. World-space locomotion/root translation is a runtime concern and does not require baked root travel in the sprite frames.

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

## Retained motion control — C1A MECHANICAL PASS, NOT PRODUCTION LOCOMOTION MASTER

C1A skeleton-only walk remains a valid mechanical motion/control proof:

- motion: CMU `105_34 NormalWalk`;
- rig: `G2_CANONICAL_RIG`;
- guide: `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`;
- approved states: `1588,1598,1608,1618,1628,1638,1648,1658`.

It still proves real gait timing, left/right alternation, support-foot sequencing and intact joint chains. It does **not** by itself approve the final gameplay locomotion pose language.

The user is not expected to supply eight manual pose images.

## Local SSD/authoring environment — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- Miniconda / env `ssd` PASS;
- Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- SSD import graph PASS;
- DWPose available;
- FILM available, optional/not default;
- released SSD denoising/reference UNets present;
- baseline AnimateAnyone pose guider + motion module present.

## Exact upstream SSD inference — BLOCKED

Exact current-upstream SSD inference remains blocked because the public release does not contain the custom trained multi-scale `pose_guider.pth` required by SSD's current `PoseGuider` and modified `unet_3d.py`.

The installed baseline Moore/AnimateAnyone pose-guider checkpoint is structurally different and is retained only for the compatible Moore fallback. Do not run runner 28 again and do not fake exact compatibility with loose loading.

Manifest status:

`EXACT_UPSTREAM_INFERENCE_BLOCKED_POSE_GUIDER_UNRELEASED`

## Runner 29 Moore-compatible fallback — TECHNICAL PASS / VISUAL FAIL

Route:

`original Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD fine-tuned denoising/reference UNets`

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

Runner:

`tools/structured-2d-character-pipeline/29_run_ssd_moore_compat_exilada_walk8.ps1`

Technical execution passed, but visual QA failed:

- the eight C1A phases were insufficiently differentiated;
- pose obedience was weak;
- lower legs, ankles and feet became unstable/deformed;
- detached dark accessory/foot-like artifacts appeared near the ground;
- temporal stability came partly from insufficient motion rather than a convincing walk.

## Runner 30 pose registration — CLEAR DIAGNOSTIC IMPROVEMENT / STILL VISUAL FAIL FOR PRODUCTION

Runner:

`tools/structured-2d-character-pipeline/30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1`

Runner 30 corrected the concrete runner-29 input defect:

- old pose conversion mapped `640×360` to `512×512` with independent X/Y scaling;
- old relative vertical stretch was `1.7778×`;
- runner 30 rebuilt the eight poses using uniform geometry scale and registered them to the master DWPose body footprint;
- inference parameters/model stack otherwise remained unchanged.

Supplied runner-30 output showed a **clear A/B improvement**:

- body/leg articulation responded much more visibly to the target poses;
- left/right phase differentiation improved;
- feet/legs were materially more coherent than runner 29;
- the correction therefore validated pose-scale registration as a real defect.

However the user correctly rejected the result as still far below the intended game quality:

- walking lacks convincing naturality;
- the body presentation/pose language is not yet authored for the elevated belt-scroller gameplay style;
- several phases still read awkwardly rather than as a polished locomotion cycle;
- accessory/restraint artifacts remain, reinforcing that complete-master secondary masses should not define the base gait.

Therefore runner 30 is **not a production PASS**. It is retained as a successful diagnostic correction only.

## Key diagnosis after runner 30

The project was conflating two independent questions:

1. can a visible authoring model obey a pose sequence?;
2. is the pose sequence itself the correct production locomotion for this game?

Runner 30 improved #1 enough to expose #2. The original C1A source uses generic CMU `NormalWalk` viewed at `45 deg` from travel heading. That was acceptable for mechanical gait sanity, but it has never been art-directed as a contemporary arcade belt-scroller locomotion master.

Do not ask diffusion to invent the missing animation art direction.

## CURRENT GATE — G3S-C1C GAMEPLAY LOCOMOTION MASTER

Canonical document:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

First bounded test:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Runner 31 performs **no diffusion inference**. It reprojects the same validated real gait at three increasingly lateral camera azimuths while keeping all other camera/motion controls fixed:

- `60 deg` — 30 deg off pure side profile;
- `72 deg` — 18 deg off pure side profile;
- `84 deg` — 6 deg off pure side profile.

Purpose: determine whether the old `45 deg` projection is the major reason the locomotion reads too frontal/awkward for the belt-scroller, before authoring additive gait changes.

Review criteria:

- natural gait readability;
- screen-left travel clarity;
- near/far leg separation;
- body/face readability;
- fit with the elevated arcade belt-scroller presentation.

If one facing is selected but the gait remains too neutral, the next gate will author a deterministic gameplay-locomotion overlay on the retained real gait timing: stride compression, root bob, torso inclination, shoulder orientation, arm swing/elbow flexion, head stabilization and foot-lift amplitude.

No SSD rerun is authorized before the locomotion pose master itself passes skeleton-only review.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\31_run_g3s_c1c_gameplay_facing_audit.ps1"
```

Then share the three `g3s_c1_skeleton_walk_contact_sheet.png` files and, preferably, the three `g3s_c1_skeleton_walk_zoom.gif` files from:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_facing_audit\az60`

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_facing_audit\az72`

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_facing_audit\az84`

## Layering consequence

The visible runner-30 accessory/restraint failures reinforce the body-first production principle. The locomotion master is therefore defined on the body motion first. Hair, clothing, bindings, shackles/chains and other secondary masses remain downstream layer/authoring problems rather than part of gait definition.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- Flux2 independent per-frame redraw — FAIL/CLOSED;
- segmented 2D puppet — PAUSED/HISTORICAL;
- runner 28 exact-upstream SSD attempt — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## No cleanup

SSD assets remain retained because runner 30 proved useful pose response after correct registration. The Moore-compatible visible route is paused while gameplay locomotion is authored; no cleanup applies yet.
