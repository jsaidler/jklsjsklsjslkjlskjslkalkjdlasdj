# G1 Camera / Native Scale — Execution Log

Status date: **2026-09-06**

Gate: **G1 — camera/native gameplay scale**

Current status: **PASS / CLOSED.**

## Presentation simplification decision — LOCKED

The project originally considered a true isometric 2D presentation. That direction was deliberately abandoned because it multiplies character-facing families, pose coverage, occlusion cases and animation-authoring cost.

The locked presentation is instead an **elevated 2D belt-scroller / arcade beat'em-up camera**, preserving a walkable depth band while making character art fundamentally lateral.

This is not a cosmetic preference. It is a production-feasibility decision intended to make the character pipeline possible:

- fixed elevated orthographic camera rather than free/isometric camera coverage;
- first production body family is screen-left front-three-quarter;
- screen-right may later be mirrored or separately authored only if visual QA requires it;
- movement through the walkable depth band does **not** require north/south/isometric directional sprite families;
- the same lateral locomotion family can move through gameplay depth while runtime position/depth sorting handles the world-space Y/depth component;
- hidden 3D exists to drive motion, depth order, sockets and contacts, not to force visible multi-angle 3D coverage.

Any animation proposal that starts rebuilding isometric-style multi-directional coverage, independent per-frame character redraws or unnecessary view families is architectural drift and must be rejected unless the presentation itself is explicitly reopened.

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

This baseline is locked for later validation and may only change through an explicit gate decision.
