# G3V Retarget Preflight — Execution Log

Status date: **2026-09-05**

Sub-gate: **G3V-R — retarget validation before representative body rendering**

Current status: **V1 FAIL / V2 READY TO RUN.**

## Why this exists

The G3V body render now proves that the source motion reaches the MPFB character, but direct transform transfer deforms the target incorrectly in later gait phases. Retargeting is isolated as its own skeleton-only gate before any further body/pixel-art work.

Source: `G2_CANONICAL_RIG`.
Target: MPFB `cmu_mb` weighted rig.

## V1 measured facts

The first deterministic preflight reported:

- source rig type: `cmu_mb`;
- target rig type: `cmu_mb`;
- parent mismatches: `0`;
- mean source/target rest-orientation delta: **83.1874 deg**;
- max rest-orientation delta: **180.0289 deg**;
- measured gait period: `80` frames at 120 fps;
- quarter-cycle frames: `1568,1588,1608,1628`.

This is the important structural result: the rigs share naming/hierarchy but **not compatible rest-axis conventions**.

### MPFB pose API attempt

V1 did not actually test MPFB's pose path. `RigService.set_pose_from_dict()` failed because it was invoked outside Pose Mode:

`bpy.ops.pose.select_all.poll() failed, context is incorrect`

MPFB's own pose-loading UI enters Pose Mode before calling `set_pose_from_dict()`. V2 now reproduces that contract explicitly in background mode.

### REST_COMPENSATED_FK result

V1 fallback result:

- unique poses: `4`;
- mean elbow/knee angle error: **25.0101 deg**;
- max angle error: **43.6810 deg**;
- normalized endpoint-motion RMS: **0.27541 body heights**.

It failed all quality limits that matter. **Do not relax thresholds.** This local-axis method is closed.

## V2 implementation — CURRENT

New file:

`tools/deterministic-character-pipeline/g3v_retarget_preflight_v2.py`

The existing operator command remains:

`tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`

`g3v_retarget_bootstrap.py` automatically routes the preflight through V2.

V2 evaluates two principled routes:

### 1. MPFB_POSE_API — context corrected

- activate source armature;
- enter Pose Mode before pose capture;
- activate target armature;
- enter Pose Mode before `RigService.set_pose_from_dict()`;
- score the result against the same numerical benchmark.

### 2. DIRECTION_SPACE_FK — axis independent

This method exists specifically because rest orientation differs by ~83 deg on average.

It does **not** transfer source Euler values, quaternions, `Action`, `matrix_basis`, or source local axes.

Instead, parent-first for every matching bone:

1. read the currently posed source bone direction;
2. convert that direction through world space into the target armature space;
3. swing the target bone until its bone direction matches the source direction;
4. preserve the MPFB target's own hierarchy, bone length, skin weights and roll/twist convention.

Root translation is excluded from articulation scoring and remains a separate deterministic gameplay channel.

Expected markers:

- `G3V_RETARGET_BOOTSTRAP_SOLVER=V2`
- `G3V_RETARGET_V2=BOUND`
- `G3V_RETARGET_MPFB_API_CONTEXT=POSE_MODE`
- `G3V_RETARGET_AXIS_INDEPENDENT_METHOD=DIRECTION_SPACE_FK`
- scores for the methods that execute;
- `G3V_RETARGET_NUMERIC_AUDIT=PASS` only if the chosen method genuinely passes.

## Numeric PASS thresholds — unchanged

- at least `3` distinct target poses;
- mean elbow/knee angle error `<= 15 deg`;
- max elbow/knee angle error `<= 35 deg`;
- normalized endpoint-motion RMS `<= 0.18` body heights.

Only after numeric PASS is the 2-row source-vs-target skeleton sheet generated for visual review.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03d_run_g3v_retarget_preflight.ps1"
```

Then STOP. If it reaches `G3V RETARGET PREFLIGHT: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3v_retarget\g3v_retarget_contact_sheet.png`

If it fails, share the full console output. Do not rerun the G3V body render and do not start G4.
