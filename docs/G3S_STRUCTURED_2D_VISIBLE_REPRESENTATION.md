# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR DEFERRED / C0 BODY MOTION CURRENT**

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

## Canonical B3 body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing body height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

## B4 hair — DEFERRED

Hair remains structurally separate and later must still satisfy:

`rear_hair -> body -> front_hair`

No hair candidate is approved. B4C produced review evidence only; no generated hair pixels were promoted. The user explicitly paused hair on 2026-09-06.

See `docs/G3S_B4_HAIR_LOG.md`.

## G3S-C0 — BODY-ONLY MOTION DIAGNOSTIC — CURRENT

The user requested to see the approved doll moving before more layer work.

C0 is an intentional diagnostic exception to the full-layer build order. It asks only whether the persistent B3B body can be driven by the already-approved real-motion infrastructure.

Motion inputs:

- G2 real-motion/topology = PASS;
- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- G3V-R `DIRECTION_SPACE_FK` = PASS;
- validated phase frames `1568, 1588, 1608, 1628`.

C0 pipeline:

`G2 real motion -> screen-space joints/depth -> direction deltas -> persistent body pixel regions -> deterministic nearest-neighbor transforms -> per-frame depth ordering -> animated GIF/contact sheet`

The visible source remains the canonical body PNG. Hidden 3D contributes joint/depth data only.

C0 deliberately does **not** use:

- hidden-3D RGB/masks as visible art;
- diffusion or visual models;
- manual final key poses;
- manual user frame repair;
- automatic production promotion.

The first C0 revision is a cutout/deformation diagnostic and may expose seams or rigid-part artifacts. Those are judged as deformation problems; they do not invalidate the real-motion backbone by themselves.

Spec:

`tools/structured-2d-character-pipeline/g3s_c0_body_motion_spec.json`

Runner:

`tools/structured-2d-character-pipeline/19_run_g3s_c0_body_walk_proof.ps1`

Supporting tools:

- `tools/structured-2d-character-pipeline/g3s_c0_extract_g2_motion.py`;
- `tools/structured-2d-character-pipeline/g3s_c0_body_puppet_walk.py`.

Expected review outputs:

- `g3s_c0_body_walk_in_place.gif`;
- `g3s_c0_body_walk_travel.gif`;
- `g3s_c0_body_walk_contact_sheet.png`.

## Full layered motion remains later

C0 does not waive the eventual production requirement for persistent hair, clothing, restraints and equipment. Full G3S-C layered motion approval still waits until those layer families exist.
