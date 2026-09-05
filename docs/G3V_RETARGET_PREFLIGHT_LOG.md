# G3V Retarget Preflight — Execution Log

Status date: **2026-09-05**

Sub-gate: **G3V-R — rest-pose-aware retarget validation before representative body rendering**

Current status: **READY TO RUN.**

## Why this sub-gate exists

The second coherent G3V contact sheet finally showed four distinct motion phases, but the MPFB body deformed incorrectly in later phases: pelvis/legs/trunk visibly collapsed even though the G2 source motion itself is already validated.

This isolates the failure to motion transfer between:

- source: `G2_CANONICAL_RIG`;
- target: MPFB `cmu_mb` rig.

The failed shortcut was copying source `matrix_basis` values directly into the target rig. Matching bone names do **not** imply matching rest orientation, bone roll, local basis or proportions.

G3V body rendering is therefore paused until retargeting is proven independently.

## Correct validation strategy

Do not debug retargeting through the final body render.

The preflight now:

1. opens the approved G2 motion artifact;
2. creates the same MPFB female body and weighted `cmu_mb` target rig headlessly;
3. compares required source/target bone hierarchy, rest orientation and length ratios;
4. derives the same four real gait phases from G2 foot-contact metadata;
5. evaluates two non-random retarget implementations in one deterministic run:
   - `MPFB_POSE_API`: MPFB's documented `RigService.get_pose_as_dict()` -> `RigService.set_pose_from_dict()` path;
   - `REST_COMPENSATED_FK`: explicit rest-pose-aware FK transfer that converts source local motion through source/target rest bases rather than copying `matrix_basis` blindly;
6. scores both methods from joint-angle fidelity, endpoint-motion residual and distinct-pose count;
7. chooses the objectively better method;
8. refuses review if numeric thresholds fail;
9. renders a skeleton-only 2-row contact sheet: approved G2 source above, retargeted MPFB skeleton below.

This is an automated benchmark, not iterative visual guessing.

## Tooling

- `tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`
- `tools/deterministic-character-pipeline/g3v_retarget_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_retarget_preflight.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3v_retarget`

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v_retarget\g3v_retarget_contact_sheet.png`

## Locked inputs

- G1: `640×360`, orthographic `26 deg`, reference height `128 px`;
- G2: `CMU 105_34 NormalWalk`, 120 fps, PASS/CLOSED;
- measured gait period: derived from G2 contact metadata, not hard-coded indices;
- MPFB: `2.0.17`, pinned verified archive SHA256 `4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87`.

## Numeric PASS thresholds

The chosen retarget method must satisfy all of:

- at least `3` distinct target pose signatures across four phases;
- mean elbow/knee joint-angle absolute error `<= 15 deg`;
- maximum elbow/knee joint-angle error `<= 35 deg`;
- mean normalized endpoint-motion RMS `<= 0.18` body heights.

These thresholds are preflight guards, not production-animation quality targets. Visual skeleton comparison is still required before returning to G3V.

## Review rule

If the source and target skeleton rows preserve the same gait phase, left/right alternation, knee/elbow articulation and overall topology without collapse, record G3V-R PASS and replace the old direct-`matrix_basis` motion binding with the chosen retarget method.

If the preflight fails numerically or visually, do **not** touch renderer, hair, cloth, pixel translation or Exilada identity. The problem remains retargeting only.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03d_run_g3v_retarget_preflight.ps1"
```

Then STOP. Share `g3v_retarget_contact_sheet.png` if the runner reaches `REVIEW REQUIRED`; otherwise share the full console output. Do not rerun `03c_run_g3v.ps1` and do not start G4 until this preflight passes.
