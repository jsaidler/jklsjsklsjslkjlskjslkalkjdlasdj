# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR CURRENT OPEN / NO APPROVED B4 RUNNER**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets/guides -> persistent 2D pixel assets -> deterministic 2D transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D may own motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB, alpha or final sprite silhouette.

## Production constraints

- final visible character art is owned by persistent native 2D assets;
- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no beauty-render shrink/pixel-filter route;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer.

## Staged build

1. **B3 complete body base** — **PASS/CLOSED**.
2. **B4 hair** — **CURRENT / OPEN**.
3. **B5 clothing/restraints/accessories** — **BLOCKED UNTIL B4 PASS**.
4. **G3S-C layered motion proof** — **BLOCKED UNTIL B3/B4/B5**.

## Canonical B3 body

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing body height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

## B4 hair ownership — LOCKED

Minimum representation:

`rear_hair -> body -> front_hair`

- `rear_hair`: behind head/neck/shoulders/back/body;
- `front_hair`: scalp/framing/front-crossing locks;
- body remains byte/pixel unchanged underneath;
- additional sublayers may be added later only for real occlusion/secondary-motion needs.

Canonical hair master is identity/style/material inspiration only. Its pose is not a geometry-placement template.

## B4B history

- V1 extraction — **FAIL/CLOSED PRE-RUN**: hidden rear hair absent from master.
- V2 authored — **FAIL/CLOSED VISUAL / STRUCTURAL PASS**.
- V3 authored — **FAIL/CLOSED VISUAL + ALIGNMENT METHOD** because fixed master-like coordinates ignored the production body's different pose.
- V4 pose-anchored authored — **FAIL/CLOSED VISUAL + METHOD**.

V4 failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchor_failure.json`

Reviewed V4 contact sheet SHA256:

`50dd663cbbeb0bb1a9865f2ac95daedc7990ceaf7a98ae6a968c8b7eacb4a8a5`

## Procedural hair-authoring route closure — LOCKED

The V4 contact sheet exposes the key failure: `shoulder_span=6.36 px` was reported for the canonical `37 px`-wide body. The detector therefore did not recover a credible shoulder geometry.

More importantly, the entire abstraction is insufficient. Head center/bounds, shoulder row/span, torso center and a binary facing flag cannot encode the actual 3/4 relationship of head tilt, shoulder slope, torso rotation, arm occlusion, back contour and local depth.

Therefore **heuristic pose anchors + hard-coded Pillow polygons/lines are not a viable visual author for production hair**.

Do not iterate this route with more hand-tuned anchors or procedural locks. The runner `tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1` is intentionally disabled.

The next B4 solution must use real visual 2D authoring/adaptation to the canonical B3B pose while preserving separate `rear_hair` and `front_hair` ownership.

No B5/G3S-C starts before B4 passes.
