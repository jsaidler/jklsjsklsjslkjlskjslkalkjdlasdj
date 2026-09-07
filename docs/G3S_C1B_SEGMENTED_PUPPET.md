# G3S-C1B — Segmented 2D Skeletal Puppet

Status date: **2026-09-06**

Gate status: **FLUX2 PER-FRAME REDRAW FAIL/CLOSED / MINIMAL BEAT-EM-UP SEGMENTED PUPPET RUNNER READY / REVIEW REQUIRED**

## Why this route exists

The project deliberately moved away from true isometric character production to an elevated **arcade beat'em-up / belt-scroller** presentation because that is the viable 2D production problem.

That decision must simplify animation directly:

- fixed orthographic `640×360` camera;
- pitch `26°`;
- protagonist standing body around `128 px`;
- one screen-left front-three-quarter visible family first;
- gameplay depth does not imply north/south/isometric character directions;
- one persistent 2D doll is driven by one hidden skeleton.

## Closed visible redraw route

The C1B Flux2 eight-frame proof is FAIL/CLOSED. It regenerated the woman independently each frame and drifted in face, skin tone, anatomy, proportions, silhouette and pixel treatment.

Reviewed evidence:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_visual_failure.json`

Do not tune or revive that runner for locomotion.

## Current architecture

`CMU real walk -> approved hidden skeleton -> persistent B3B-derived 2D parts -> bind landmarks + overlap -> projected bone transforms -> camera-space depth sort -> composited sprite`

The hidden skeleton supplies motion/spatial control only. Visible RGB/alpha remain persistent native-2D pixels.

## First proof — deliberately minimal

The first proof now uses an even smaller part set than the earlier design:

- `head_neck`;
- one continuous `core` containing torso + pelvis;
- bilateral upper arms;
- bilateral forearms;
- bilateral hands;
- bilateral thighs;
- bilateral shins;
- bilateral feet.

Keeping torso and pelvis as one `core` avoids inventing a waist seam before evidence says it is needed.

The canonical source remains unchanged:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

SHA256:

`702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`

## Difference from failed C0 V1

This is not the old nearest-segment exclusive partition with exposed rigid joints.

The current builder:

- fits explicit bind landmarks to the actual B3B alpha silhouette;
- creates overlapping capsule masks for adjacent limb segments;
- restores shoulder, hip and neck cap pixels into the persistent core;
- keeps elbow/knee/wrist/ankle overlap between neighboring pieces;
- transforms each reusable part from its bind segment to the approved projected skeleton segment;
- sorts all parts far-to-near using C1A camera-space joint depth;
- uses the same exact persistent source parts in every gait state.

No per-frame image model is involved.

## Simplification contract

For this proof:

- screen-left family only;
- no extra isometric/north/south directions;
- no preemptive foreshortening/orientation variants;
- no high-resolution redraw stage;
- no MPFB body;
- no diffusion/model/API/download;
- no user frame-by-frame repair;
- hair remains deferred.

A new persistent part variant may be added later only if a specific visible defect demonstrates that one base part cannot represent an important projection.

## Current implementation

Spec:

`tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`

Builder:

`tools/structured-2d-character-pipeline/g3s_c1b_build_segmented_puppet.py`

Runner:

`tools/structured-2d-character-pipeline/23_run_g3s_c1b_segmented_puppet_walk.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1b_segmented_puppet`

## Review outputs

The runner generates in one pass:

- `g3s_c1b_segmented_part_atlas.png`;
- `g3s_c1b_puppet_bind_manifest.json`;
- eight transparent body-frame PNGs;
- `g3s_c1b_puppet_walk_in_place.gif`;
- `g3s_c1b_puppet_walk_zoom.gif`;
- `g3s_c1b_puppet_walk_travel.gif`;
- `g3s_c1b_puppet_contact_sheet.png`;
- `g3s_c1b_puppet_contact_sheet_skeleton_overlay.png`.

## PASS requirement

The proof passes only if the result reads as **the same persistent B3B doll moving** through the eight approved gait states, with connected joints, recognizable identity, usable left-facing walk and no catastrophic layer ordering.

If it fails, diagnose the concrete seam/part/projection defect. Do not change presentation or reopen isometric complexity by default.
