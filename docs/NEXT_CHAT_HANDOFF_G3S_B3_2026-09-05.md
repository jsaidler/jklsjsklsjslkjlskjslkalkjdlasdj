# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G1_CAMERA_SCALE_LOG.md`

## Locked production direction

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed `640×360` orthographic camera, pitch `26 deg`;
- protagonist about `128 px` tall;
- first screen-left locomotion family is mostly lateral / slight three-quarter;
- **locomotion-facing baseline = `72 deg` azimuth from travel heading** (`90 deg` = pure side);
- no isometric north/south character-family multiplication;
- final runtime = conventional deterministic spritesheet playback;
- runtime/world locomotion is separate from baked sprite root translation.

## C1A status — mechanical pass only

Retained source:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight approved phases `1588..1658`.

C1A proves coherent gait timing/support progression and intact skeletal chains. It is **not** the final gameplay locomotion master.

## SSD status

Exact upstream SSD remains BLOCKED because the public release omits the custom multi-scale `pose_guider.pth` required by current upstream code.

Moore-compatible fallback remains technically runnable. Runner 29 visually failed. Runner 30 fixed the `1.7778x` target-pose distortion and clearly improved pose response, but the visible walk still failed because the locomotion itself was not sufficiently authored for the game.

**Do not run SSD again yet.**

## Runner 31 — facing audit CLOSED

Decision:

- `60 deg` rejected as too frontal;
- `84 deg` rejected as too profile-thin for the baseline;
- **`72 deg` selected and locked**.

## Runner 32 — gameplay walk overlay V1 VISUAL FAIL / CLOSED

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

V1 reduced bob/stride/arm pendulum and stabilized the head. Visual review showed only modest improvement. It still read as a generic human/mocap walk and specifically did not achieve the expected feminine Exilada locomotion read.

The missing class was support-side weight transfer and coordinated pelvis/torso/shoulder motion, not another image-model parameter.

## CURRENT GATE — runner 33 feminine gameplay walk V2

Canonical doc:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Runner:

`tools/structured-2d-character-pipeline/33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_feminine_walk_overlay_v2.py`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1c_gameplay_walk_overlay_v2_feminine_spec.json`

V2 remains skeleton-only and keeps the real eight-phase timing/support order. It adds restrained feminine body-language controls at the locked `72 deg` facing:

- phase-weighted pelvic obliquity;
- mild pelvic yaw;
- torso/shoulder counterbalance;
- compact arm pendulum;
- moderate stride compression;
- small swing-leg clearance boost;
- head stabilization;
- no catwalk exaggeration or cartoon sway.

This is an Exilada-specific animation art-direction target, not a claim that all women share one gait.

## EXACT NEXT OPERATOR ACTION

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

## Decision rule

PASS only if V2:

- reads clearly more feminine without costume/hair carrying the read;
- remains grounded and action-ready, not runway-like;
- preserves contact/down/passing/up and support-foot clarity;
- improves pelvis/torso/shoulder weight transfer naturally;
- has no anatomy break or cartoon exaggeration;
- is materially better than runner 32 V1.

Only after the skeleton locomotion master passes should visible body authoring resume.

## Layering

Base gait is body motion first. Hair, clothing, bindings, shackles/chains and secondary masses remain downstream layer/authoring problems.

No cleanup applies. SSD assets are retained but computation is paused.
