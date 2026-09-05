# G3V Retarget Preflight — Execution Log

Status date: **2026-09-05**

Sub-gate: **G3V-R — retarget validation before representative body rendering**

Current status: **PASS / CLOSED.**

## Purpose

G3V-R isolated retargeting from the final body render after raw transform transfer visibly collapsed the MPFB character in later gait phases.

Source: `G2_CANONICAL_RIG`.
Target: MPFB `cmu_mb` weighted rig.

## Structural facts — LOCKED

Deterministic rest-rig audit measured:

- source rig type: `cmu_mb`;
- target rig type: `cmu_mb`;
- parent mismatches: `0`;
- mean source/target rest-orientation delta: **83.1874 deg**;
- max rest-orientation delta: **180.0289 deg**;
- gait period: `80` frames at 120 fps;
- quarter-cycle frames: `1568,1588,1608,1628`.

Conclusion: bone naming and hierarchy match, but local/rest-axis conventions are not interchangeable.

## Rejected retarget methods

### Raw Action copy

Rejected. The MPFB body remained frozen across distinct source phases.

### Raw `matrix_basis` copy

Rejected. It produced distinct phases but severe pelvis/leg/trunk collapse because source and target rest spaces differ.

### Local-axis `REST_COMPENSATED_FK`

V1 result:

- unique poses: `4`;
- mean elbow/knee error: `25.0101 deg`;
- max error: `43.6810 deg`;
- old endpoint RMS: `0.27541`.

Rejected.

### `MPFB_POSE_API`

After correcting Pose Mode context, V2 result was:

- unique poses: `4`;
- mean elbow/knee error: `25.4032 deg`;
- max error: `44.3890 deg`;
- old endpoint metric: `0.23865`.

Rejected for this source/target pair.

## Accepted method — `DIRECTION_SPACE_FK`

V2 articulation result:

- unique target poses: `4`;
- mean elbow/knee error: **0.0000 deg**;
- max elbow/knee error: **0.0001 deg**.

The old endpoint metric was then identified as invalid because it subtracted each rig's incompatible rest-pose endpoint positions. V3 retained the same solver and replaced only that metric with rest-independent `CHAIN_UNIT_DIRECTION_RMS`; thresholds were not relaxed.

The V3 runner only generates the review sheet after its numeric audit passes. The reviewed sheet therefore represents a numerically accepted run.

## Visual review — PASS

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v_retarget\g3v_retarget_contact_sheet.png`

Rows:

- A: approved G2 source skeleton;
- B: retargeted MPFB `cmu_mb` skeleton.

Frames:

`1568, 1588, 1608, 1628`.

Topology-first review:

- no duplicate or missing major limbs;
- no pelvis/leg/trunk collapse;
- source and target preserve the same four gait phases;
- left/right alternation is preserved;
- knees and elbows preserve the corresponding articulation;
- remaining differences are target proportions/placement, not motion-phase or topology failure.

**Decision: G3V-R PASS / CLOSED.**

Canonical approval marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

## Production consequence

The G3V body renderer must no longer use raw `Action`, raw `matrix_basis`, or local-axis transfer.

Canonical G3V motion binding is now:

`G2 posed bone directions -> target armature-space direction matching -> MPFB own hierarchy/lengths/weights`

Implementation:

`tools/deterministic-character-pipeline/g3v_motion_binding_patch.py`

Expected body-run marker:

`G3V_MOTION_BINDING=DIRECTION_SPACE_FK_VALIDATED_G3V_R`

## Next action

Return to G3V representative body rendering once, using the validated retarget. Then visually decide the actual G3V kill switch: whether the coherent animated representative human has enough headroom for intentional modern pixel art or still reads merely as blocky/filtered 3D.

G4 remains blocked until that G3V visual decision.
