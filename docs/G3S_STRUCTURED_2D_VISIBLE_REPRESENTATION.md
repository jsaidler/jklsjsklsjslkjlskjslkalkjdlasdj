# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR CURRENT / B4C REAL VISUAL ADAPTER REVIEW NEXT**

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

## Closed B4B procedural route

- V1 extraction — **FAIL/CLOSED PRE-RUN**: hidden rear hair absent from master.
- V2 authored — **FAIL/CLOSED VISUAL / STRUCTURAL PASS**.
- V3 authored — **FAIL/CLOSED VISUAL + ALIGNMENT METHOD** because fixed master-like coordinates ignored the production body's pose.
- V4 pose-anchored authored — **FAIL/CLOSED VISUAL + METHOD**.

V4 failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchor_failure.json`

Reviewed V4 contact sheet SHA256:

`50dd663cbbeb0bb1a9865f2ac95daedc7990ceaf7a98ae6a968c8b7eacb4a8a5`

The V4 sheet exposed the key failure: `shoulder_span=6.36 px` for a `37 px`-wide body. More fundamentally, heuristic anchor scalars do not encode the 3/4 anatomy/occlusion needed for hair placement. Therefore **heuristic pose anchors + hard-coded Pillow polygons/lines are closed as visual-authoring methods**.

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1` remains disabled.

## B4C real visual authoring/adaptation — CURRENT

The project now separates **visual adaptation capability** from **final layer ownership**.

B4C uses a real local visual model only as a one-shot static authoring/adaptation gate. It must first prove that the Exilada's canonical hair identity can be adapted convincingly to the actual B3B production pose. Only after that proof may the project ask the same visual adapter for separate rear/front passes and persist validated native 2D hair assets.

This is not a return to per-frame diffusion ownership. B4C is a static source-authoring step; final runtime/export ownership remains persistent sprite layers.

### Narrow local runtime reuse

User instruction `faça` authorizes B4C to reuse the already-retained `Z:\AI\Flux2RefControlSpike` workspace **only for this static visual gate**, if its FLUX.2 Klein files still exist. It does not reopen the old animation/refcontrol route and does not authorize broad model hunting.

Spec:

`tools/structured-2d-character-pipeline/g3s_b4c_flux2_visual_adapter_spec.json`

Runner:

`tools/structured-2d-character-pipeline/18_run_g3s_b4c_flux2_visual_hair_adapter.ps1`

Supporting tools:

- `tools/structured-2d-character-pipeline/g3s_b4c_prepare_flux2_visual_adapter.py`
- `tools/structured-2d-character-pipeline/g3s_b4c_build_flux2_visual_review.py`

B4C conditions on:

1. exact canonical B3B body = authoritative pose/proportion/scale/camera/placement;
2. canonical master = hair identity/style/material only.

It explicitly rejects transfer of the master's clothes, chains, restraints, accessories or pose.

It downloads nothing, uses no paid API, submits one fixed-seed generation only, and promotes nothing automatically.

Generated B4C pixels are **review evidence only**, not production hair-layer ownership.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter\g3s_b4c_flux2_contact_sheet.png`

If visual adaptation passes, the next gate is controlled separate visual authoring of `rear_hair` and `front_hair`, followed by persistent native-2D validation/promotion. If B4C fails, close that narrow method without affecting B3.

No B5/G3S-C starts before B4 passes.
