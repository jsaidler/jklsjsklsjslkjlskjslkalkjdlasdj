# G3S-A1 — Facial / Anatomy Lock

Status date: **2026-09-05**

Gate status: **FAIL / CLOSED**

## Why this gate existed

`G3S-A authored native V1` had a coherent macro body but the mouth was not visually readable. G3S-A1 attempted a bounded deterministic native-grid correction before any animation work.

V1 failure marker:

`tools/structured-2d-character-pipeline/g3s_a_authored_v1_failure.json`

## Input / provenance

Design scaffold only:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Pinned SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

Native scaffold geometry:

- canvas `128×128` RGBA;
- source subject bbox `[582,40,814,705]`;
- normalized subject size `43×122`;
- placement `[42,3]`;
- nearest-neighbor scaffold reduction only.

## Harness incident — fixed

The first G3S-A1 invocation stopped before anatomy work with:

`ModuleNotFoundError: No module named 'g3s_a_authored_native_v1'`

Root cause: bare sibling-module import under the ComfyUI embeddable Python.

Fix: `g3s_a1_facial_anatomy_lock.py` loads the sibling helper by absolute file path through `importlib.util.spec_from_file_location`.

Fix commit:

`bf5fe174165ee9cd08ed2f50a09e3ca7563f8658`

Incident marker:

`tools/structured-2d-character-pipeline/g3s_a1_import_failure.json`

## V2 result — FAIL

The corrected harness produced the requested candidate and anatomy diagnostics.

Visual review found:

- macro body remained usable as a provisional structural source;
- hands and feet were readable enough to continue structural work;
- the face remained unresolved;
- the new mouth became an exaggerated dark/red block and was visually worse than an unresolved minimal mouth;
- therefore **G3S-A1 V2 does not pass facial anatomy**.

Canonical V2 failure marker:

`tools/structured-2d-character-pipeline/g3s_a1_v2_failure.json`

## Operator decision after V2

The user explicitly chose to **continue the planned structured-2D pipeline** rather than spend another whole-character iteration on the mouth.

Locked consequences:

1. the macro body source is accepted **provisionally for decomposition**, not as a finished character master;
2. `head_face` becomes an **unresolved replaceable persistent part**;
3. future facial correction must replace/refine only that part rather than force whole-character redraws;
4. broken chain segments are **not** permanent body pixels;
5. broken chains become initial accessory state with independent sockets/art/state;
6. G3S-B is unblocked;
7. G3S-C remains blocked until G3S-B visual review.

## Critical lesson

Anatomical details are semantically important, but solving a localized defect by repeatedly patching the entire static character is the wrong production architecture. Structured decomposition must make face, hands, feet, hair, cloth and accessories independently replaceable/controllable.

The historical fact of captivity remains canonical. Moving chains into the accessory layer is a production-layer decision, not a narrative retcon.

## Next gate

**G3S-B — Persistent 2D Part Decomposition**

Canonical log:

`docs/G3S_B_PERSISTENT_PART_DECOMPOSITION_LOG.md`

Runner:

`tools/structured-2d-character-pipeline/09_run_g3s_b_decomposition.ps1`

No image model is used by G3S-B.
