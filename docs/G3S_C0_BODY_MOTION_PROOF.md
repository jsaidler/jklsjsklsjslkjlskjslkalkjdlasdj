# G3S-C0 — Body-Only Motion Proof

Status date: **2026-09-06**

Gate status: **V1 FAIL/CLOSED VISUAL DEFORMATION METHOD — V2 CONTINUOUS CHAIN WARP RUNNER READY / REVIEW NEXT**

## Why this gate exists

The user explicitly paused hair work and requested to see the already-approved Exilada body implemented in motion now.

G3S-C0 is a **diagnostic exception to the full layered gate order**. It does not claim that B4 hair or B5 clothing/restraints are complete, and it does not approve the final layered G3S-C animation architecture.

Its question remains:

> Can the promoted native 2D Exilada body be driven by the already-approved real-motion infrastructure and visibly walk as one coherent persistent sprite asset?

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
- eight review samples use `1568, 1578, 1588, 1598, 1608, 1618, 1628, 1638`.

The real motion projection itself is retained. C0 failures concern only the visible 2D deformation method unless explicitly stated otherwise.

## V1 — FAIL/CLOSED VISUAL DEFORMATION METHOD

V1 runner:

`tools/structured-2d-character-pipeline/19_run_g3s_c0_body_walk_proof.ps1`

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk\g3s_c0_body_walk_contact_sheet.png`

Reviewed SHA256:

`730afda6a541db4524671931892685bee7317d8324efe6c9b3eb0c62fbdd5cc4`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`

### What V1 proved

- the approved CMU/G2 motion reaches the 2D body pipeline;
- clear gait-phase progression is visible;
- the canonical B3B body remains the source art and is not modified;
- no hidden-3D RGB, diffusion or paid API is involved.

### Why V1 failed

V1 partitioned the sprite into many hard pieces — upper/lower arms, thighs, shins and feet — and rotated each region independently around estimated pivots.

The reviewed frames expose the method directly:

- joints visibly detach;
- later stride frames create loop-like / arc-like disconnected leg-foot silhouettes;
- knees and ankles do not remain welded;
- extreme poses read as assembled rotating slabs rather than one body;
- the failure is therefore not just polish or seam cleanup.

**Decision:** close `nearest-segment hard partition + independent rigid part rotation` as the C0 body-deformation method. Do not make a V1.1 by adding more overlap or hand-tuning more rigid piece pivots.

No model/runtime was added by V1, so no cleanup command applies.

## V2 — CONTINUOUS CHAIN WARP — CURRENT

V2 preserves the same approved source body and real-motion projection but changes the deformation model.

Instead of rotating separate upper/lower limb slabs, V2 owns six continuous visible regions:

- head;
- torso;
- left arm;
- right arm;
- left leg;
- right leg.

Each arm/leg is warped as one continuous polyline chain. Pixels around elbow/knee/ankle joints blend the mappings of adjacent chain segments, so a limb bends through the joint rather than splitting there.

Source pixel colors remain the visible material. Source pixels are rasterized back to the integer grid as hard nearest-grid quads; no antialiasing, image-model repainting or hidden-3D RGB is used. A one-pixel enclosed raster pinhole may be filled only by copying an immediately adjacent existing source color.

Depth ordering remains derived from hidden G2 camera-space joint depth.

V2 spec:

`tools/structured-2d-character-pipeline/g3s_c0_body_motion_spec_v2.json`

V2 builder:

`tools/structured-2d-character-pipeline/g3s_c0_continuous_warp_v2.py`

V2 runner:

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2`

Expected review artifacts:

- `g3s_c0_v2_body_walk_in_place.gif`;
- `g3s_c0_v2_body_walk_travel.gif`;
- `g3s_c0_v2_contact_sheet.png`;
- `g3s_c0_v2_zoom_contact_sheet.png`;
- `g3s_c0_v2_report.json`.

## V2 PASS requirement

V2 is not required to be final production animation, but it must clear the V1 structural visual failure:

- the body must read as one articulated figure;
- arms/legs must remain visually continuous through elbows/knees/ankles;
- no loop-like detached limb arcs;
- gait alternation must remain recognizable;
- canonical body identity/proportions must remain readable at gameplay scale;
- no automatic promotion.

If continuous chain warping still cannot keep the sprite coherent under the real walk, C0 must move to an actual weighted 2D mesh/cage representation rather than returning to rigid cutout parts.

## Current exact action

Run V2 once and review the **in-place GIF plus zoom contact sheet**. Hair remains deferred until the user explicitly resumes it.
