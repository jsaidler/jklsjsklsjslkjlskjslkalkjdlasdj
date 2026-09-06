# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY BASE PASS/CLOSED / B4 HAIR CURRENT / B4B V3 REVIEW NEXT**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets/guides -> persistent 2D pixel assets -> deterministic 2D transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB, alpha or final sprite silhouette.

## Visible-ownership invariant — LOCKED

- 3D may guide anatomy, motion, topology, sockets, contacts, depth and occlusion;
- 3D may not be mechanically promoted into final visible sprite geometry;
- high-resolution 2D reference art may not be mechanically resized/quantized/traced and promoted as production sprite geometry;
- final character pixels are owned by persistent structured 2D assets;
- runtime/export uses sprites.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI work by the user;
- no beauty-render shrink/pixel-filter route as final art;
- recurring work remains scriptable/headless;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer.

## Correct staged character build — LOCKED

1. **B3 — complete body base** — **PASS/CLOSED**.
2. **B4 — hair** — **CURRENT**.
3. **B5 — clothing/restraints/accessories** — **BLOCKED UNTIL B4 PASS**.
4. **G3S-C — layered motion proof** — **BLOCKED UNTIL B3/B4/B5**.

## B3 — PASS/CLOSED

Canonical production body base:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

Promotion commit:

`2deb765c3980d586ef9747340bb48852dedca452`

Recorded production facts:

- `37×128` RGBA;
- visible standing height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- front-three-quarter elevated belt-scroller view;
- adult nude/hairless/barefoot body base;
- persistent 2D visible ownership.

## 128 px clarification — LOCKED

`128 px` is the target visible standing body height in the native `640×360` gameplay raster. It is not a universal source/frame canvas dimension. Hair, weapons and extreme animation bounds may use larger transparent frames while preserving this body scale.

## Current gate — B4 HAIR

Canonical hair direction:

- very long;
- heavy;
- voluminous;
- messy black hair;
- primary silhouette anchor;
- separate from body base;
- persistent across animation;
- eligible for deterministic secondary-motion/wind guides later;
- body visibility/ownership underneath must remain intact.

### Hair depth ownership — LOCKED

Minimum valid representation:

`rear_hair -> body -> front_hair`

- `rear_hair` owns mass behind head, neck, shoulders and back;
- `front_hair` owns framing/locks in front of face, neck, shoulders or chest;
- additional sublayers may be introduced later only if occlusion/secondary motion requires them.

### B4A preflight — PASS/CLOSED DIAGNOSTIC

The canonical master is suitable as identity/mass inspiration and the shared `96×160` review frame is adequate.

### B4B V1 master extraction — FAIL/CLOSED PRE-RUN

The master does not reveal enough rear-hair coverage to reconstruct valid `rear_hair` by extraction/splitting.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

### B4B V2 authored two-layer static candidate — FAIL/CLOSED VISUAL / STRUCTURAL PASS

Reviewed contact sheet SHA256:

`73a9b53d35c158d78079039b4425c94028c8836e82b775ee0ce3e38b8d32a09d`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_visual_failure.json`

Structural architecture passed, but visual massing failed: centered curtain/bell silhouette, excessive front coverage, cape-like rear mass, repetitive equal-width lock rhythm, buried face/head and insufficient asymmetry/hierarchy.

### B4B V3 authored two-layer static candidate — CURRENT / RUNNER READY

V3 retains the valid architecture but rewrites the visible massing:

- rear-dominant asymmetric irregular silhouette;
- sparse front framing;
- face/clavicle/chest/abdomen substantially open;
- broad primary masses and distinct long falls instead of repetitive equal-width locks;
- explicit rear geometry behind head/shoulders/back;
- master used for inspiration only;
- body hash-verified and immutable;
- no external paid API/model;
- no automatic promotion.

Spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_authored_two_layer_hair_spec.json`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

No B5 clothing/restraints/accessories or G3S-C motion begins before B4 passes.
