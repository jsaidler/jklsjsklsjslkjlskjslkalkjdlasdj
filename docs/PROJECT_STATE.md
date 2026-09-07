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
- first canonical locomotion family is screen-left / mostly lateral-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- true isometric multi-directional character production remains closed unless explicitly reopened.

### Locomotion-facing lock — 2026-09-07

Runner 31 compared the retained real gait at `60`, `72` and `84 deg` azimuth from travel heading.

Decision:

- `60 deg` rejected as too frontal/depth-oriented;
- `84 deg` rejected as the baseline because it sacrifices too much projected torso/face/body mass;
- **`72 deg` selected as the first gameplay locomotion facing baseline**.

In this convention `90 deg` is pure side profile. The old C1A `45 deg` projection remains valid only as a historical mechanical sanity view, not the production locomotion baseline.

## Runtime animation representation — LOCKED

`approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary sprite playback`

Runtime does not require a 3D skeleton, segmented puppet or diffusion model. World-space locomotion/root translation is a runtime concern and does not require baked root travel in sprite frames.

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

## C1A retained motion control — MECHANICAL PASS ONLY

- motion: CMU `105_34 NormalWalk`;
- rig: `G2_CANONICAL_RIG`;
- guide: `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`;
- approved states: `1588,1598,1608,1618,1628,1638,1648,1658`.

C1A proves gait timing, left/right alternation, support-foot sequencing and intact joint chains. It does **not** approve final gameplay locomotion art direction.

## SSD/visible-authoring status

Local SSD authoring environment remains available and technically validated.

Exact upstream SSD inference remains **BLOCKED** because the public release omits the custom multi-scale `pose_guider.pth` required by the current SSD graph. Do not run runner 28 again.

Moore-compatible fallback remains technically runnable:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion + released SSD fine-tuned denoising/reference UNets`

### Runner 29

- technical PASS;
- visual FAIL;
- weak pose obedience;
- unstable feet/lower legs;
- detached accessory/ground artifacts.

### Runner 30

Runner 30 corrected the concrete pose-registration defect from runner 29: the old `640×360 -> 512×512` target-pose conversion introduced `1.7778×` relative vertical stretch. Uniform geometry scaling + DWPose-body registration produced a clear improvement in pose articulation and lower-limb reconstruction.

However runner 30 still failed as a production walk because the source locomotion itself was too generic/frontal/under-authored for the game.

Do not rerun SSD yet.

## Runner 31 gameplay-facing audit — PASS / CLOSED

Runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Result:

**`72 deg` azimuth selected as gameplay locomotion facing baseline.**

The camera/facing problem is therefore sufficiently isolated. The remaining primary problem is animation authorship, not model tuning.

## CURRENT GATE — RUNNER 32 GAMEPLAY WALK OVERLAY V1

Canonical thematic doc:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_gameplay_walk_overlay.py`

Runner 32 performs no diffusion. It creates a fresh `72 deg` skeleton baseline and a deterministic authored overlay that keeps real gait timing/support order while changing the projected animation language:

- compact projected stride;
- reduced pelvis/root bob;
- mild screen-left upper-body intent;
- reduced casual/civilian arm pendulum;
- stabilized head offset.

Current V1 control values are documented in `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md` and in the generated marker.

### Runner 32 PASS criteria

The overlay must be clearly better than the fresh `72 deg` raw baseline in naturality and game fit while preserving:

- human gait phase readability;
- grounded support contacts;
- left/right alternation;
- non-cartoon anatomy and physicality.

Do not proceed to visible body generation until the skeleton walk itself passes.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1"
```

Expected terminal marker:

`G3S-C1C-OVERLAY: A/B SKELETON REVIEW PACKAGE READY`

Share these four artifacts:

1. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\baseline_az72\g3s_c1_skeleton_walk_contact_sheet.png`
2. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\baseline_az72\g3s_c1_skeleton_walk_zoom.gif`
3. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\overlay_v1\g3s_c1_skeleton_walk_contact_sheet.png`
4. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\overlay_v1\g3s_c1_skeleton_walk_zoom.gif`

## Layering consequence

Base locomotion is defined on body motion first. Hair, clothing, bindings, shackles/chains and other secondary masses remain downstream animation/authoring layers and must not be allowed to obscure gait validation.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- Flux2 independent per-frame redraw — FAIL/CLOSED;
- segmented 2D puppet — PAUSED/HISTORICAL;
- runner 28 exact-upstream SSD attempt — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## No cleanup

SSD assets remain retained because runner 30 proved useful pose response after correct registration. Visible generation is paused while gameplay locomotion is authored. No cleanup applies now.
