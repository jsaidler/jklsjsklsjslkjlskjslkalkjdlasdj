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
- **locomotion-facing baseline selected at `72 deg` azimuth from travel heading** (`90 deg` = pure side);
- no isometric north/south character-family multiplication;
- final runtime = conventional deterministic spritesheet playback;
- runtime/world locomotion is separate from baked sprite root translation.

## C1A status — mechanical pass only

Retained source:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight approved phases `1588..1658`;
- existing guide `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`.

C1A proves coherent human gait timing/support progression and intact skeletal chains. It is **not** the final gameplay locomotion master.

## SSD status

Exact upstream SSD remains BLOCKED because the public release omits the custom multi-scale `pose_guider.pth` required by current upstream code.

Moore-compatible fallback remains technically runnable with the released SSD denoising/reference UNets plus baseline Moore pose guider/motion module.

Runner 29: technical PASS / visual FAIL.

Runner 30: fixed the `1.7778x` target-pose stretch/registration defect and clearly improved visible pose response, but the user rejected the walk as still far below the intended game quality. This proved the next bottleneck is locomotion art direction, not another diffusion parameter sweep.

Do not run SSD again yet.

## Runner 31 — facing audit CLOSED

Runner 31 compared `60`, `72`, `84 deg` skeleton projections with all other motion/camera variables fixed.

Decision:

- `60 deg` rejected as too frontal;
- `84 deg` rejected as too profile-thin for the baseline;
- **`72 deg` selected** as the gameplay locomotion facing baseline.

The remaining primary problem is the generic raw `NormalWalk` pose language.

## CURRENT GATE — runner 32 gameplay walk overlay V1

Canonical doc:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_gameplay_walk_overlay.py`

Runner 32 performs **no diffusion**. It rebuilds a fresh `72 deg` skeleton baseline and applies one bounded authored overlay:

- stride compression;
- pelvis/root bob reduction;
- mild forward upper-body intent;
- reduced casual arm pendulum;
- head stabilization;
- real gait timing/support order retained.

It outputs an A/B review package so the raw `72 deg` gait and authored V1 can be compared directly.

## EXACT NEXT OPERATOR ACTION

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1"
```

Expected terminal marker:

`G3S-C1C-OVERLAY: A/B SKELETON REVIEW PACKAGE READY`

Share:

1. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\baseline_az72\g3s_c1_skeleton_walk_contact_sheet.png`
2. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\baseline_az72\g3s_c1_skeleton_walk_zoom.gif`
3. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\overlay_v1\g3s_c1_skeleton_walk_contact_sheet.png`
4. `Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1\overlay_v1\g3s_c1_skeleton_walk_zoom.gif`

## Decision rule

Approve overlay V1 only if it is clearly more natural and game-authored than the raw `72 deg` baseline while preserving:

- human phase readability;
- grounded support contacts;
- left/right alternation;
- mature/non-cartoon physicality;
- anatomical coherence.

If V1 is directionally right but one specific control is visibly over/under-corrected, revise only that control in the next bounded skeleton pass. Do not open a broad parameter sweep.

Only after the skeleton locomotion master passes should visible body authoring resume.

## Layering

Base gait is body motion first. Hair, clothing, bindings, shackles/chains and secondary masses remain downstream layer/authoring problems.

No cleanup applies. SSD assets are retained but computation is paused.
