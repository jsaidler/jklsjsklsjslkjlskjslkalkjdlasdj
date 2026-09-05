# G3S-A1 — Facial / Anatomy Lock

Status date: **2026-09-05**

Gate status: **READY TO RERUN AFTER HARNESS FIX**

## Why this gate exists

`G3S-A authored native V1` produced a coherent macro silhouette and acceptable gameplay-scale body, but visual review rejected the face because the mouth was still not readable. The V1 helper had a defective guard: it only verified that mouth patch pixels were opaque, which is not equivalent to anatomical readability.

Canonical failure marker:

`tools/structured-2d-character-pipeline/g3s_a_authored_v1_failure.json`

Decision: **no animation and no G3S-B decomposition until native facial/anatomical readability passes.**

## Locked principle

Anatomical details are production-critical. A feature is not considered present merely because pixels exist at nominal coordinates. It must read semantically at native 1× scale and in explicit nearest-neighbor diagnostic zooms.

## Inputs

Design/scaffold provenance only:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Pinned SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

Native scaffold geometry remains:

- canvas: `128×128` RGBA;
- source subject bbox: `[582,40,814,705]`;
- normalized native subject size: `43×122`;
- native placement: `[42,3]`;
- scaffold reduction: nearest-neighbor, provenance/scaffold only.

## V2 authored anatomy patch

Patch:

`tools/structured-2d-character-pipeline/g3s_a_anatomy_patch_v2.json`

The V2 patch is a complete deterministic native-grid patch derived from the same pinned control. It does not invoke a generative model.

Facial changes:

- explicit lower-plane/nose separation;
- five-pixel dark mouth opening;
- a second lower-lip row;
- center lower-lip highlight;
- chin separation below the mouth.

Existing canonical restraints remain explicitly authored:

- both wrist cuffs;
- both ankle cuffs;
- short broken-chain remnants.

## Technical guards

The old alpha-only mouth guard is rejected.

G3S-A1 requires:

- mouth spans two distinct semantic rows;
- mouth core has explicit local RGB contrast against neighboring facial skin;
- face diagnostic region is non-empty;
- both hand regions are non-empty;
- both foot regions are non-empty;
- candidate remains native `128×128`;
- visible body height remains within the locked source range;
- final visual review remains authoritative.

## Harness incident — sibling import failure

The first G3S-A1 invocation stopped before any anatomy work with:

`ModuleNotFoundError: No module named 'g3s_a_authored_native_v1'`

Root cause: `g3s_a1_facial_anatomy_lock.py` imported the sibling helper by bare module name. The ComfyUI embeddable Python does not guarantee that the script directory is on `sys.path`, so the helper could not resolve its sibling module.

This was a harness bug, not an anatomy-patch failure. No model inference occurred and no G3S-A1 candidate was generated.

Fix:

- `g3s_a1_facial_anatomy_lock.py` now loads `g3s_a_authored_native_v1.py` by absolute sibling file path using `importlib.util.spec_from_file_location`;
- no dependency on cwd, `PYTHONPATH` or embeddable-Python import behavior remains for this sibling;
- fix commit: `bf5fe174165ee9cd08ed2f50a09e3ca7563f8658`;
- marker: `tools/structured-2d-character-pipeline/g3s_a1_import_failure.json`.

This fix changes no art coordinates, gate thresholds or model state.

## Review artifacts

Runner:

`tools/structured-2d-character-pipeline/08_run_g3s_a1_facial_anatomy_lock.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_a1_facial_anatomy_lock.py`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a1_anatomy_lock`

Expected artifacts:

- `g3s_a1_candidate_v2.png`
- `g3s_a1_face_zoom.png`
- `g3s_a1_extremities_zoom.png`
- `g3s_a1_gameplay_preview.png`
- `g3s_a1_contact_sheet.png`
- `g3s_a1_result.json`

The contact sheet deliberately exposes six views: design provenance, pre-lock scaffold, V2 native candidate, face diagnostic, hands/feet diagnostic and 1:1 gameplay preview.

## PASS criteria

Topology first:

1. exactly one head/torso;
2. two arms/hands;
3. two legs/feet;
4. no duplicated or fused major anatomy.

Facial/anatomical lock:

5. mouth is visibly readable at native 1× and in face zoom;
6. face reads as a human face rather than an undifferentiated skin cluster;
7. hands and feet remain identifiable and structurally plausible;
8. restraints remain on the correct wrists/ankles;
9. no patch creates obvious anatomy artifacts.

Identity/gameplay:

10. Exilada identity remains coherent: long heavy black hair, olive-brown skin, degraded beige cloth, restraints, bare feet;
11. gameplay preview remains readable at `640×360` with `1 asset pixel = 1 screen pixel`.

## FAIL handling

If facial/anatomical review fails, revise the explicit native patch data. Do not search another image model and do not begin animation.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\08_run_g3s_a1_facial_anatomy_lock.ps1"
```

Then STOP and review `g3s_a1_contact_sheet.png`.
