# G1 Camera / Native Scale — Execution Log

Status date: **2026-09-04**

Gate: **G1 — camera/native gameplay scale**

Current status: **RE-RUN REQUIRED AFTER CALIBRATION FIX.** Do not advance to G2 yet.

## First execution

The first G1 run completed technically and produced nine `640×360` diagnostic renders plus `g1_contact_sheet.png`.

Test matrix:

- camera pitch: `18 / 26 / 34 deg`;
- target protagonist height: `112 / 128 / 144 px`;
- orthographic camera;
- five enemy proxies;
- walkable depth band and attack/depth markers.

## Visual QA result

The first contact sheet is **not valid enough to close G1**.

Observed critical defect:

- candidate `pitch18 / hero112` is massively zoomed/cropped and clearly does not correspond to a 112 px protagonist, despite the manifest reporting the requested height.

This proves that the original pre-render calibration path could report a stale camera/projection state on the first candidate of a fresh headless Blender session.

The remaining eight cells are useful as qualitative evidence. Provisional visual reading only, not yet locked:

- `18 deg` exposes less useful ground/depth information and is not the current front-runner;
- `26–34 deg` better communicates the belt-scroller depth band;
- `128–144 px` better supports the intended large, mature full-body pixel character than `112 px`;
- `26 deg / 128 px` is currently the strongest provisional balance between character presence, lateral combat room and visible ground depth;
- `26 deg / 144 px` and `34 deg / 128 px` remain credible alternatives;
- no candidate is canonical until the corrected matrix is reviewed.

## Root cause / hardening

`g1_camera_scale_blockout.py` originally queried projected bounding boxes without explicitly synchronizing Blender's dependency graph before camera/orthographic measurements.

The first render can force Blender to evaluate camera/parent transforms after the pre-render measurement, producing a mismatch between reported and actually rendered scale.

Fix implemented:

1. explicitly call `bpy.context.view_layer.update()` before projection queries and after camera / `ortho_scale` changes;
2. run four calibration iterations;
3. enforce a pre-render tolerance of `0.5 px`;
4. after each actual render, re-measure the protagonist projection;
5. hard-fail if post-render height differs from target by more than `1.0 px`;
6. store both pre- and post-render measurements in the manifest;
7. replace the degree symbol in PowerShell contact-sheet labels with ASCII `deg` to avoid Windows PowerShell 5.1 mojibake (`Â°`).

Relevant commits:

- `93aeae6e42496e450dc0b603efd0cf07c1c72e9e` — dependency-graph synchronization + post-render framing validation;
- `8135b4bbc66cbac8e71e0e1c79995b54220187bb` — ASCII contact-sheet labels.

## Next action

Re-run the same G1 command once with the fixed tooling and review only the new `g1_contact_sheet.png`.

Do not start G2 until G1 is explicitly recorded PASS with a selected baseline camera pitch and protagonist screen height.
