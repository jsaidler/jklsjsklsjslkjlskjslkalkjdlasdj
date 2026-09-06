# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR CURRENT / B4B V4 POSE-ANCHORED REVIEW NEXT**

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
2. **B4 hair** — **CURRENT**.
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

Canonical hair master is identity/style/material inspiration only. **Its pose is not a geometry-placement template.**

## B4B history

- V1 extraction — **FAIL/CLOSED PRE-RUN**: hidden rear hair absent from master.
- V2 authored — **FAIL/CLOSED VISUAL / STRUCTURAL PASS**.
- V3 authored — **FAIL/CLOSED VISUAL + ALIGNMENT METHOD** because fixed master-like coordinates ignored the production body's different pose.

V3 failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_pose_mismatch_failure.json`

Reviewed V3 contact sheet SHA256:

`9d922756f8815ea55cf55bed26d2bc0d24f51f93f89b3f47392126e027573f33`

## B4B V4 — CURRENT

V4 establishes a new invariant for visible-layer authoring:

**When a reference/master pose differs from the production sprite pose, placement geometry must be anchored to the actual production sprite, not to reference-image coordinates.**

V4 measures from the canonical body alpha/silhouette:

- head center/bounds;
- shoulder row/span;
- torso center;
- facing bias.

New `rear_hair` and `front_hair` geometry is authored relative to those body-pose anchors. The contact sheet exposes the detected anchors for review.

Spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchored_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_pose_anchored_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

No B5/G3S-C starts before B4 passes.
