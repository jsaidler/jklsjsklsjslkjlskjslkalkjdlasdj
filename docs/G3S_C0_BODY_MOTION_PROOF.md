# G3S-C0 — Body-Only Motion Proof

Status date: **2026-09-06**

Gate status: **CURRENT / RUNNER READY / REVIEW REQUIRED**

## Why this gate exists

The user explicitly paused hair work and requested to see the already-approved Exilada body implemented in motion now.

G3S-C0 is therefore a **diagnostic exception to the full layered gate order**. It does not claim that B4 hair or B5 clothing/restraints are complete, and it does not approve the final layered G3S-C animation architecture.

Its only question is:

> Can the promoted native 2D Exilada body be driven by the already-approved real-motion infrastructure and visibly walk as the same persistent sprite asset?

## Inputs — LOCKED

Canonical body:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- visible owner remains persistent native 2D pixels.

Motion evidence:

- G2 = PASS using CMU `105_34 NormalWalk`;
- source rig = `G2_CANONICAL_RIG`;
- G3V-R = PASS with `DIRECTION_SPACE_FK`;
- validated phase frames = `1568, 1588, 1608, 1628`;
- eight review samples use `1568, 1578, 1588, 1598, 1608, 1618, 1628, 1638`, preserving the real captured sequence between validated phases.

## C0 representation

The C0 body is a deterministic **2D articulated cutout/deformation diagnostic**.

Pipeline:

`real G2 motion -> projected joints/depth -> direction deltas -> persistent body-part pixel ownership -> deterministic nearest-neighbor 2D transforms -> depth-aware composition -> GIF/contact-sheet review`

The native body is partitioned once into persistent regions:

- torso;
- head;
- left/right upper arm;
- left/right forearm;
- left/right thigh;
- left/right shin;
- left/right foot.

The source image is not redrawn. A one-pixel source overlap is allowed at region boundaries only to reduce visible cutout seams; the overlap copies existing canonical body pixels and creates no new painted anatomy.

Per-frame ordering comes from G2 camera-space joint depth.

## Important scope limit

C0 is intentionally **not final skinning quality**.

The first review is allowed to expose:

- rigid-part/cutout seams;
- imperfect joint continuity;
- inadequate source-rig pivot calibration;
- depth-order problems;
- cadence/grounding problems.

Those are precisely the next deformation problems to solve if the basic motion mapping is viable.

C0 may not:

- invent extra limbs;
- use per-frame diffusion;
- use hidden-3D RGB/masks as visible output;
- modify the canonical B3B PNG;
- silently promote its GIF frames as final production animation.

## Runner

`tools/structured-2d-character-pipeline/19_run_g3s_c0_body_walk_proof.ps1`

Supporting tools:

- `tools/structured-2d-character-pipeline/g3s_c0_extract_g2_motion.py`;
- `tools/structured-2d-character-pipeline/g3s_c0_body_puppet_walk.py`;
- `tools/structured-2d-character-pipeline/g3s_c0_body_motion_spec.json`.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk`

Expected review artifacts:

- `g3s_c0_body_walk_in_place.gif`;
- `g3s_c0_body_walk_travel.gif`;
- `g3s_c0_body_walk_contact_sheet.png`;
- `g3s_c0_motion_projection.json`;
- `g3s_c0_body_walk_report.json`.

No model download, paid API or visual generation model is used in C0.

## Current exact action

Run the C0 runner once and review the animated GIFs/contact sheet. Hair remains deferred until the user explicitly resumes it.
