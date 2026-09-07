# G3S-C1B — Segmented 2D Skeletal Puppet

Status date: **2026-09-06**

Gate status: **HISTORICAL / PAUSED — NOT CURRENT PRODUCTION ROUTE**

## Current disposition

This route is retained for provenance but is no longer the active character-production path.

The project explicitly returned to a conventional spritesheet target:

`offline source-authoring -> approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary runtime sprite playback`

Current source-authoring validation is documented in:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Do not run or continue `23_run_g3s_c1b_segmented_puppet_walk.ps1` unless the segmented-puppet route is explicitly reopened.

## Why this route existed

The project deliberately moved away from true isometric character production to an elevated arcade beat'em-up / belt-scroller presentation because that is the viable 2D production problem.

The segmented puppet attempted to exploit that simplification by driving persistent B3B-derived body parts from the approved hidden skeleton.

## Historical architecture

`CMU real walk -> approved hidden skeleton -> persistent B3B-derived 2D parts -> bind landmarks + overlap -> projected bone transforms -> camera-space depth sort -> composited sprite`

Historical implementation:

- spec: `tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`;
- builder: `tools/structured-2d-character-pipeline/g3s_c1b_build_segmented_puppet.py`;
- runner: `tools/structured-2d-character-pipeline/23_run_g3s_c1b_segmented_puppet_walk.ps1`.

## Why it is not current

The user explicitly chose to return to the conventional production model used by sprite-based arcade games: completed action frames assembled into spritesheets rather than requiring a segmented puppet as the production representation.

The retained puppet code may remain useful as a fallback or debugging experiment, but it must not compete with the active SSD spritesheet spike or silently become the runtime architecture again.

## Still-closed methods

The following failures remain closed:

- C1B Flux2 independent full-body redraw per frame;
- C0 V1 nearest-segment exclusive hard partition with exposed rigid joints;
- single-still whole-body chain/cage warp;
- MPFB skinned body as mandatory hidden guide;
- implicit return to isometric/multi-directional character coverage.

## Presentation lock retained

- elevated beat'em-up / belt-scroller false 3D;
- fixed orthographic `640×360` camera;
- pitch `26 deg`;
- protagonist around `128 px`;
- first visible family screen-left/front-three-quarter;
- gameplay depth does not imply north/south/isometric character sprite families.
