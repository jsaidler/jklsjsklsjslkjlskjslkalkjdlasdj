# G3S-C1B — Segmented 2D Skeletal Puppet

Status date: **2026-09-06**

Gate status: **FLUX2 PER-FRAME FULL-BODY REDRAW FAIL/CLOSED / SEGMENTED 2D SKELETAL PUPPET CURRENT**

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

The visible body is now a persistent segmented 2D puppet attached to the already-approved hidden skeleton:

`CMU walk -> hidden 3D skeleton -> reusable native-2D body parts -> joint pivots/bindings -> projected bone transform -> skeleton depth order -> composited sprite`

This is the route the project should have followed after the skeleton was validated.

The 3D remains hidden and supplies only motion/spatial control. The visible pixels remain 2D.

## Persistent body parts

Initial body-only partition:

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
- optional joint cover/cap sprites where needed;
- depth order from the hidden skeleton rather than fixed draw order;
- projected bone length/orientation driving each part;
- a small frozen variant set only when one flat part cannot represent strong foreshortening or near/far change.

Variants are reusable persistent assets, not frame-specific redraws.

## 2.5D binding model

Each visible body part behaves like a camera-facing billboard attached to one skeleton chain.

For a limb segment:

1. proximal joint gives the pivot;
2. distal joint gives direction and projected length;
3. the sprite is translated/rotated/scaled to that projected bone;
4. camera-space skeleton depth determines its draw order;
5. joint overlap hides seams.

Head, torso and pelvis are bound to their corresponding central skeleton transforms and may use minimal discrete orientation variants if the walk proves that a single flat part is insufficient.

## Foreshortening rule

Pure rigid rotation of one limb image is not enough when a bone points materially toward/away from the camera.

Therefore a part may have a small authored/frozen set such as:

- normal;
- foreshortened;
- near-side/far-side hand or foot;
- optional pelvis/torso lead-side state.

The selector is deterministic from skeleton orientation/depth. No per-frame diffusion is allowed to own the visible animation.

## Current spec

`tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`

## First proof

The next implementation must produce, in one runner:

- segmented body-part atlas;
- pivot/binding manifest;
- eight composited body-only walk frames driven by the approved C1A cycle;
- in-place GIF;
- travel GIF;
- contact sheet, optionally with skeleton overlay for debugging.

PASS requires one recognizable persistent Exilada body throughout the cycle with intact joints, stable identity, correct left-facing motion and no per-frame redesign.

Hair remains deferred.
