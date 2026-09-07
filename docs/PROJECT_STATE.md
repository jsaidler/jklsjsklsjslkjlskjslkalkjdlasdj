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

### Locomotion-facing lock

Runner 31 compared the retained real gait at `60`, `72` and `84 deg` azimuth from travel heading.

Decision:

- `60 deg` rejected as too frontal/depth-oriented;
- `84 deg` rejected as baseline because it sacrifices too much projected torso/face/body mass;
- **`72 deg` selected and locked as the first gameplay locomotion facing baseline**.

`90 deg` is pure side profile in the current convention. The old C1A `45 deg` projection is historical/mechanical only.

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

## SSD / visible-authoring status

Exact upstream SSD remains **BLOCKED** because the public release omits the custom multi-scale `pose_guider.pth` required by the current SSD graph. Do not run runner 28 again.

The Moore-compatible fallback remains technically runnable:

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

**SSD visible authoring remains paused.** Do not rerun it until C1C provides an approved skeleton locomotion master.

## Runner 31 gameplay-facing audit — PASS / CLOSED

Runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Result:

**`72 deg` azimuth selected as gameplay locomotion facing baseline.**

The camera/facing problem is sufficiently isolated. The remaining primary problem is animation authorship.

## Runner 32 gameplay walk overlay V1 — VISUAL FAIL / CLOSED

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_gameplay_walk_overlay.py`

V1 created a fresh `72 deg` baseline and a deterministic authored overlay with compact stride, reduced root bob, mild upper-body forward intent, reduced casual arm pendulum and head stabilization.

Visual review result:

- somewhat more controlled than the raw baseline;
- difference still too small;
- still read as generic mocap/human locomotion rather than the Exilada's authored walk;
- specifically did **not** achieve the expected feminine locomotion read;
- lacked convincing support-side weight transfer through pelvis/torso/shoulders.

Therefore runner 32 V1 is **FAIL/CLOSED as locomotion master**. This does not reopen broad parameter sweeps.

## CURRENT GATE — RUNNER 33 FEMININE GAMEPLAY WALK V2

Canonical thematic doc:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Runner:

`tools/structured-2d-character-pipeline/33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_feminine_walk_overlay_v2.py`

Machine-readable spec:

`tools/structured-2d-character-pipeline/g3s_c1c_gameplay_walk_overlay_v2_feminine_spec.json`

### V2 intent

The Exilada's walk must read as:

- adult and feminine;
- natural rather than catwalk-like;
- grounded and action-ready;
- compatible with the locked `72 deg` belt-scroller family;
- still faithful to the real contact/down/passing/up timing and support sequence.

This is an art-direction requirement for the Exilada, not a claim that there is one universal female gait.

### V2 bounded controls

Runner 33 performs **no diffusion** and creates a fresh `72 deg` baseline plus V2 authored overlay. V2 adds:

- root/pelvis bob at `62%` of raw amplitude;
- moderate stride compression: hip `0.99`, knee `0.95`, ankle/toe `0.91`;
- phase-weighted pelvic obliquity up to `3.2 px` total;
- subtle pelvic yaw split up to `2.2 px`;
- torso/shoulder counterbalance and shoulder counter-yaw up to `1.4 px`;
- mild forward upper-body shear `2.6 px` at the head;
- compact arm pendulum;
- small swing-leg clearance boost in passing/up;
- head stabilization blend `0.64`.

Guardrails:

- no exaggerated hip sway;
- no catwalk leg crossing;
- no cartoon bounce;
- no change to gait event/support ordering;
- no visible-body/diffusion execution;
- helper hard-fails if projected left/right hip Y separation exceeds `8 px`.

## Runner 33 PASS criteria

PASS requires:

- clearly more feminine skeleton read than raw `72 deg` baseline without relying on hair/costume;
- grounded action-game locomotion rather than runway locomotion;
- readable contact/down/passing/up phases;
- stable support-foot contacts and left/right alternation;
- natural pelvis/torso/shoulder counter-motion;
- no anatomical break or cartoon exaggeration;
- a material improvement over runner 32 V1 sufficient to justify returning to visible body authoring.

If runner 33 fails, diagnose the remaining motion-design defect before any SSD rerun.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1"
```

Expected terminal marker:

`G3S-C1C-FEMININE-V2: A/B SKELETON REVIEW PACKAGE READY`

Share:

1. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\baseline_az72\g3s_c1_skeleton_walk_contact_sheet.png`
2. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\baseline_az72\g3s_c1_skeleton_walk_zoom.gif`
3. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\overlay_v2_feminine\g3s_c1_skeleton_walk_contact_sheet.png`
4. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\overlay_v2_feminine\g3s_c1_skeleton_walk_zoom.gif`

## Layering consequence

Base locomotion is defined on body motion first. Hair, clothing, bindings, shackles/chains and other secondary masses remain downstream animation/authoring layers.

## Historical / closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- Flux2 independent per-frame redraw — FAIL/CLOSED;
- segmented 2D puppet — PAUSED/HISTORICAL;
- runner 28 exact-upstream SSD attempt — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## No cleanup

SSD assets remain retained because runner 30 proved useful pose response after correct registration. Visible generation is paused while gameplay locomotion is authored. No cleanup applies now.
