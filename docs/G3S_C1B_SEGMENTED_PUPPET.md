# G3S-C1B — Segmented 2D Skeletal Puppet

Status date: **2026-09-06**

Gate status: **FLUX2 PER-FRAME FULL-BODY REDRAW FAIL/CLOSED / SEGMENTED 2D SKELETAL PUPPET CURRENT**

## Why this route exists

The project deliberately moved away from true isometric character production to an elevated **arcade beat'em-up / belt-scroller** presentation because that is the viable 2D production problem.

That decision must directly simplify animation:

- fixed elevated camera;
- one lateral/front-three-quarter visible family first;
- walkable gameplay depth without north/south/isometric character directions;
- persistent 2D body parts driven by one hidden skeleton;
- no per-frame reinvention of the woman.

The segmented puppet is therefore not an attempt to reproduce unrestricted 3D articulation in 2D. It is a deliberately constrained character system built for the locked belt-scroller camera.

## Why the Flux2 walk proof is closed

The reviewed C1B visual proof did not read as one persistent woman. Across the eight gait states it changed face, skin tone, proportions, shading, silhouette and pixel-art treatment. The motion control was usable, but the visible character was regenerated independently every frame.

Reviewed evidence:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_visual_failure.json`

Closed method:

`approved skeleton pose -> independent full-body generative redraw for each gait frame`

This route is not to be tuned further for production locomotion.

## Current architecture

The visible body is a persistent segmented 2D puppet attached to the already-approved hidden skeleton:

`CMU walk -> hidden 3D skeleton -> reusable native-2D body parts -> joint pivots/bindings -> projected bone transform -> skeleton depth order -> composited sprite`

The 3D remains hidden and supplies only motion/spatial control. The visible pixels remain persistent 2D assets.

## Persistent body parts — first proof

Use the smallest practical body-only partition:

- head/neck;
- torso;
- pelvis;
- left/right upper arm;
- left/right forearm;
- left/right hand;
- left/right thigh;
- left/right shin;
- left/right foot.

The canonical B3B body remains the identity/style source:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

Its original file remains unchanged.

## Critical difference from failed C0 V1

This must **not** repeat the old `nearest-segment hard partition + independent rigid rotation` method.

C0 V1 failed because pieces were assigned mechanically from one still, rotated independently and exposed gaps/disconnected joints.

The current puppet requires:

- explicit anatomical pivots;
- deliberate overlap hidden under every joint;
- continuous torso/pelvis connection;
- optional joint cover/cap sprites only where a seam is actually visible;
- depth order from the hidden skeleton rather than fixed draw order;
- projected bone direction/length driving each part.

## Belt-scroller simplification contract

Do **not** add complexity before the first composed walk proves that it is necessary.

First proof rules:

- screen-left family only;
- same persistent part assets across all eight walk states;
- no frame-specific redraw;
- no extra north/south/isometric directions;
- no pre-authored foreshortening libraries;
- no generative model;
- no high-resolution redraw stage;
- no manual frame repair required from the user.

Gameplay movement into/out of the screen uses the same visible lateral family while world position and runtime depth sorting handle the gameplay-depth axis.

Screen-right is not part of this proof. It can later be mirrored or separately authored only after the left family works.

## 2.5D binding model

Each limb part is attached to one projected skeleton chain:

1. proximal joint gives the pivot;
2. distal joint gives direction and projected length;
3. the part is positioned/rotated to the chain;
4. camera-space skeleton depth determines draw order;
5. intentional overlap hides the joint seam.

Head, torso and pelvis follow the central chain with the minimum transformation needed for this fixed camera family.

## Variant rule — only after evidence

A reusable variant may be introduced **only if the first left-facing composed walk demonstrates a specific projection that cannot be represented acceptably by the base part**.

Examples could eventually include a strongly foreshortened foot or hand, but these are not assumed in advance.

Any accepted variant must be:

- persistent;
- reusable across multiple frames/actions;
- selected deterministically from skeleton orientation/depth;
- never a frame-specific generative redraw.

## Current spec

`tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`

## First proof

The next implementation must produce, in one runner:

- segmented body-part atlas;
- pivot/binding manifest;
- eight composited body-only walk frames driven by the approved C1A cycle;
- in-place GIF;
- travel GIF;
- contact sheet with optional skeleton overlay for debugging.

PASS requires one recognizable persistent Exilada body throughout the cycle with intact joints, stable identity, correct left-facing motion and no per-frame redesign.

Hair remains deferred.
