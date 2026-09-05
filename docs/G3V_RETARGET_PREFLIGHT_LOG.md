# G3V Retarget Preflight — Execution Log

Status date: **2026-09-05**

Sub-gate: **G3V-R — retarget validation before representative body rendering**

Current status: **V1 FAIL / V2 SOLVER PASS ON ARTICULATION BUT METRIC INVALID / V3 READY TO RUN.**

## Why this exists

The G3V body render proved that source motion reaches the MPFB character, but direct transform transfer deformed the target incorrectly. Retargeting is isolated as a skeleton-only gate before any further body/pixel-art work.

Source: `G2_CANONICAL_RIG`.
Target: MPFB `cmu_mb` weighted rig.

## Structural facts — LOCKED

The deterministic preflight measured:

- source rig type: `cmu_mb`;
- target rig type: `cmu_mb`;
- parent mismatches: `0`;
- mean source/target rest-orientation delta: **83.1874 deg**;
- max rest-orientation delta: **180.0289 deg**;
- gait period: `80` frames at 120 fps;
- quarter-cycle frames: `1568,1588,1608,1628`.

Conclusion: naming/hierarchy are compatible, but source/target rest-axis conventions are not.

## V1 — CLOSED

The local-axis `REST_COMPENSATED_FK` result was:

- unique poses: `4`;
- mean elbow/knee angle error: **25.0101 deg**;
- max angle error: **43.6810 deg**;
- old endpoint-motion RMS: **0.27541**.

The first MPFB pose-API attempt was invalid because `set_pose_from_dict()` was invoked outside Pose Mode.

## V2 measured result

V2 corrected the MPFB API context and added `DIRECTION_SPACE_FK`, which transfers posed bone directions rather than incompatible source local axes.

Measured:

### DIRECTION_SPACE_FK

- unique poses: `4`;
- mean elbow/knee angle error: **0.0000 deg**;
- max elbow/knee angle error: **0.0001 deg**;
- old endpoint metric: **0.24744**;
- result: failed only the endpoint threshold.

### MPFB_POSE_API

- unique poses: `4`;
- mean elbow/knee angle error: **25.4032 deg**;
- max elbow/knee angle error: **44.3890 deg**;
- old endpoint metric: **0.23865**.

Therefore `DIRECTION_SPACE_FK` is decisively better for articulation.

## Why the V2 endpoint failure is not a solver failure

The old endpoint function measured:

`(posed endpoint - hips) - (rest endpoint - hips)`

for each rig, then compared source and target.

That metric assumes source and target share a comparable rest pose. They do not: mean rest-orientation difference is ~83 deg and max is ~180 deg. The rest subtraction therefore injects a large constant disagreement even when the posed articulation matches.

The near-zero elbow/knee errors from `DIRECTION_SPACE_FK` prove that the V2 solver itself is reproducing the sampled articulation. **Thresholds are not being relaxed; the invalid metric is being replaced.**

## V3 — CURRENT

New wrapper:

`tools/deterministic-character-pipeline/g3v_retarget_preflight_v3.py`

The canonical runner remains:

`tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`

Bootstrap now prefers V3 automatically.

V3 keeps the V2 solvers unchanged and replaces only the endpoint fidelity metric with:

**`CHAIN_UNIT_DIRECTION_RMS`**

For torso, left/right arms and left/right legs it:

1. reads each posed bone direction in world space;
2. normalizes every segment to unit length;
3. averages the segment directions within each chain;
4. compares source vs target chain shape.

This metric is independent of:

- rest-pose orientation;
- bone roll/local-axis convention;
- target limb lengths/proportions.

Those target proportions remain owned by MPFB and are visually checked later in the body gate.

## PASS thresholds

The existing guard values remain numerically unchanged:

- at least `3` distinct target poses;
- mean elbow/knee angle error `<= 15 deg`;
- max elbow/knee angle error `<= 35 deg`;
- endpoint/chain-shape RMS `<= 0.18`.

The legacy manifest key for the endpoint value is retained for runner compatibility, but V3 marks its metric kind explicitly as `CHAIN_UNIT_DIRECTION_RMS`.

Expected V3 markers:

- `G3V_RETARGET_BOOTSTRAP_SOLVER=V3`
- `G3V_RETARGET_V2=BOUND`
- `G3V_RETARGET_V3=BOUND`
- `G3V_RETARGET_ENDPOINT_METRIC=CHAIN_UNIT_DIRECTION_RMS`
- `G3V_RETARGET_ENDPOINT_METRIC_REST_INDEPENDENT=TRUE`
- `G3V_RETARGET_THRESHOLDS=UNCHANGED`

Only after numeric PASS is the source-vs-target skeleton contact sheet generated for visual review.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03d_run_g3v_retarget_preflight.ps1"
```

Then STOP. If it reaches `G3V RETARGET PREFLIGHT: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3v_retarget\g3v_retarget_contact_sheet.png`

If it fails, share the full console output. Do not rerun the G3V body render and do not start G4.
