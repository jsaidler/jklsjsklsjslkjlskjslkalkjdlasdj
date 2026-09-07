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

Retained source: `G2_CANONICAL_RIG`, CMU `105_34 NormalWalk`, eight approved phases `1588..1658`. C1A proves coherent gait timing/support progression and intact skeletal chains. It is not the final gameplay locomotion master.

## SSD status

Exact upstream SSD remains BLOCKED by the missing custom multi-scale `pose_guider.pth`. Moore-compatible fallback remains technically runnable. Runner 29 visually failed; runner 30 fixed the `1.7778×` target-pose distortion and improved pose response, but the source locomotion still failed the game's animation-art-direction target.

**Do not run SSD again yet.**

## Runner 31 — facing audit CLOSED

`60 deg` rejected as too frontal, `84 deg` rejected as too profile-thin, **`72 deg` selected and locked**.

## Runner 32 — gameplay walk overlay V1 VISUAL FAIL / CLOSED

V1 reduced bob/stride/arm pendulum and stabilized the head, but remained generic mocap/human locomotion and did not achieve the expected feminine Exilada gait. The missing class was support-side weight transfer and pelvis/torso/shoulder counter-motion.

## CURRENT GATE — runner 33 feminine gameplay walk V2

Runner:

`tools/structured-2d-character-pipeline/33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_feminine_walk_overlay_v2.py`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1c_gameplay_walk_overlay_v2_feminine_spec.json`

V2 is skeleton-only at the locked `72 deg` facing. It adds restrained phase-weighted pelvic obliquity, mild pelvic yaw, torso/shoulder counterbalance, compact arm pendulum, moderate stride compression, swing-leg clearance and head stabilization. The target is adult feminine Exilada locomotion without catwalk exaggeration.

## First real runner 33 execution — technical guard failure RESOLVED

The fresh `72 deg` baseline built successfully (`C1_TRAVEL_TOTAL_DX_PX=-61.1472`, `C1_MAX_SKELETON_HEIGHT_PX=128.000`). The helper then failed with:

`V2 pelvic obliquity exceeded safety limit: 10.12px`

This was a faulty safety calculation: it compared the **absolute final projected hip-Y separation** against `8 px`, even though the source `72 deg` gait already contains substantial projected hip separation from real pose/depth geometry.

The helper and runner are corrected. They now measure only the **additional hip-Y separation introduced by V2 compared with the same source frame**. Allowed additive separation = authored maximum `3.2 px` + `0.25 px` numerical tolerance. The marker records source max, authored max, added max and allowed added max. No V2 artistic parameter was changed.

Technical failure is CLOSED/RESOLVED. Runner 33 must simply be rerun after pulling main.

## EXACT NEXT OPERATOR ACTION

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1"
```

Expected terminal marker:

`G3S-C1C-FEMININE-V2: A/B SKELETON REVIEW PACKAGE READY`

Share contact sheet + zoom GIF from:

1. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\baseline_az72`
2. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\overlay_v2_feminine`

## Decision rule

PASS only if V2 reads clearly more feminine without hair/costume carrying the read, remains grounded/action-ready rather than runway-like, preserves contact/down/passing/up and support-foot clarity, improves pelvis/torso/shoulder weight transfer naturally, and shows no anatomical/cartoon break.

Only after the skeleton locomotion master passes should visible body authoring resume.

## Layering

Base gait is body motion first. Hair, clothing, bindings, shackles/chains and secondary masses remain downstream layer/authoring problems.

No cleanup applies. SSD assets are retained but computation is paused.
