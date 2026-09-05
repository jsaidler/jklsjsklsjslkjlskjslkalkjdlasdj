# G1 Camera / Native Scale — Execution Log

Status date: **2026-09-04**

Gate: **G1 — camera/native gameplay scale**

Current status: **PASS / CLOSED.**

## First execution defect

The first 3×3 matrix exposed a calibration bug: `pitch18 / hero112` rendered massively zoomed/cropped despite the manifest reporting 112 px. Root cause was stale Blender dependency-graph/camera evaluation before the first render.

Hardening implemented:

- explicit view-layer updates before/after camera changes;
- four calibration iterations;
- pre-render tolerance <= `0.5 px`;
- post-render re-measurement;
- hard failure if post-render height differs from target by more than `1.0 px`;
- corrected ASCII `deg` labels for PowerShell 5.1.

Relevant commits:

- `93aeae6e42496e450dc0b603efd0cf07c1c72e9e`
- `8135b4bbc66cbac8e71e0e1c79995b54220187bb`

## Corrected matrix review

The corrected matrix rendered all nine candidates consistently at native `640×360`.

Locked validation baseline:

- camera: orthographic;
- pitch: **26 deg**;
- protagonist reference visible height: **128 px**;
- native gameplay raster: **640×360**.

Rationale:

- `18 deg` reads too flat and weakens belt-scroller depth;
- `34 deg` is a useful upper reference but leans too far toward top-down;
- `112 px` is too small for the intended Exilada identity/equipment/gore readability;
- `144 px` remains an upper reference but consumes more combat/composition space;
- `26 deg / 128 px` is the best current balance of lateral combat readability, walkable depth and character detail budget.

Machine-readable baseline:

`tools/deterministic-character-pipeline/g1_baseline.json`

This baseline is locked for G2/G3 validation and may only change through an explicit later gate decision.
