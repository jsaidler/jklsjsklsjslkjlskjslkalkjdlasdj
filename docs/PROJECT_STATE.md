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

Runner 31 compared `60`, `72` and `84 deg` azimuth from travel heading. `60 deg` was too frontal, `84 deg` too profile-thin, and **`72 deg` is locked as the first gameplay locomotion facing baseline**. `90 deg` is pure side profile. The old C1A `45 deg` projection is historical/mechanical only.

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

Exact upstream SSD remains **BLOCKED** because the public release omits the custom multi-scale `pose_guider.pth`. The Moore-compatible fallback remains technically runnable. Runner 29 visually failed. Runner 30 fixed the `1.7778×` pose distortion/registration defect and materially improved pose response, but still failed as a production walk because the locomotion itself was too generic and under-authored.

**SSD visible authoring remains paused.** Do not rerun it until C1C provides an approved skeleton locomotion master.

## Runner 31 gameplay-facing audit — PASS / CLOSED

Runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Result: **`72 deg` selected and locked.**

## Runner 32 gameplay walk overlay V1 — VISUAL FAIL / CLOSED

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

V1 reduced bob/stride/arm pendulum and stabilized the head, but visual review showed only modest improvement. It still read as generic human/mocap locomotion and did not achieve the expected feminine Exilada gait. The missing class was support-side weight transfer and coordinated pelvis/torso/shoulder motion.

## CURRENT GATE — RUNNER 33 FEMININE GAMEPLAY WALK V2

Canonical thematic doc:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Runner:

`tools/structured-2d-character-pipeline/33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_feminine_walk_overlay_v2.py`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1c_gameplay_walk_overlay_v2_feminine_spec.json`

### V2 intent

The Exilada's walk must read as adult and feminine, natural rather than catwalk-like, grounded/action-ready, compatible with the locked `72 deg` family and faithful to real contact/down/passing/up timing/support semantics.

V2 uses restrained phase-weighted pelvic obliquity, mild pelvic yaw, torso/shoulder counterbalance, moderate stride compression, compact arm pendulum, small swing-leg clearance and head stabilization. No diffusion runs in this gate.

### First real runner 33 execution — TECHNICAL FAIL / RESOLVED

The baseline build passed cleanly at `72 deg` with `C1_TRAVEL_TOTAL_DX_PX=-61.1472` and `C1_MAX_SKELETON_HEIGHT_PX=128.000`. The V2 helper then stopped at:

`V2 pelvic obliquity exceeded safety limit: 10.12px`

Diagnosis: the safety guard incorrectly treated **absolute final projected left/right hip Y separation** as if it were entirely authored by V2. The `72 deg` source gait already contains projected hip-Y separation from real pose/depth geometry. Thus `10.12 px` was not the V2-authored pelvic obliquity amount.

Fix: the helper now compares each V2 frame with its corresponding source frame and guards only the **additional projected hip-Y separation introduced by V2**. The allowed additive amount is the intended maximum `pelvic_obliquity_total_px=3.2` plus `0.25 px` numerical tolerance. The result marker records source maximum, authored maximum, added maximum and allowed added maximum. Runner 33 validates this additive metric. **No artistic V2 parameter was reduced or changed.**

This technical failure is CLOSED/RESOLVED; runner 33 is ready to rerun.

## Runner 33 PASS criteria

PASS requires:

- clearly more feminine skeleton read than raw `72 deg` baseline without relying on hair/costume;
- grounded action-game locomotion rather than runway locomotion;
- readable contact/down/passing/up phases;
- stable support-foot contacts and left/right alternation;
- natural pelvis/torso/shoulder counter-motion;
- no anatomical break or cartoon exaggeration;
- material improvement over runner 32 V1 sufficient to justify returning to visible body authoring.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1"
```

Expected terminal marker:

`G3S-C1C-FEMININE-V2: A/B SKELETON REVIEW PACKAGE READY`

Share the contact sheet + zoom GIF from both:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\baseline_az72`
- `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\overlay_v2_feminine`

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
