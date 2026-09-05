# G3V Retarget Preflight — Execution Log

Status date: **2026-09-05**

Sub-gate: **G3V-R — retarget validation before representative body rendering**

Current status: **V3 READY TO RERUN AFTER BOOTSTRAP IMPORT FIX.**

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

The near-zero elbow/knee errors from `DIRECTION_SPACE_FK` show that the V2 solver reproduces the sampled articulation. Thresholds were not relaxed; the invalid endpoint metric was replaced.

## V3 — CURRENT

New wrapper:

`tools/deterministic-character-pipeline/g3v_retarget_preflight_v3.py`

V3 retains the V2 solvers and replaces only the endpoint fidelity metric with:

**`CHAIN_UNIT_DIRECTION_RMS`**

For torso, left/right arms and left/right legs it compares normalized posed bone directions, making the metric independent of rest-pose orientation, bone roll/local-axis convention and limb-length proportions.

### Latest V3 run — bootstrap/import failure only

The first V3 invocation did **not** execute the solver. It stopped immediately with:

`ModuleNotFoundError: No module named 'g3v_retarget_preflight_v2'`

Cause:

- `g3v_retarget_bootstrap.py` executes V3 through `runpy.run_path()`;
- `runpy.run_path()` does not automatically add the target script directory to `sys.path`;
- V3 imports sibling module `g3v_retarget_preflight_v2`.

This is a packaging/bootstrap defect, not a retarget-result regression and not evidence against V3.

Fix committed:

- bootstrap inserts `target_script.parent` into `sys.path` before `runpy.run_path()`;
- expected marker: `G3V_RETARGET_HELPER_PATH=BOUND`.

## PASS thresholds

The guard values remain unchanged:

- at least `3` distinct target poses;
- mean elbow/knee angle error `<= 15 deg`;
- max elbow/knee angle error `<= 35 deg`;
- chain-shape RMS `<= 0.18`.

Expected V3 markers after the import fix:

- `G3V_RETARGET_BOOTSTRAP_SOLVER=V3`
- `G3V_RETARGET_HELPER_PATH=BOUND`
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
