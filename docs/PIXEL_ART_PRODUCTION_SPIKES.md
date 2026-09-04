# Pixel Art Production Spikes — Living Test Log

Status: **native-grid authoring method technically validated; current Exilada S-view candidate visually rejected.**

This file records pixel-art production experiments. It complements `docs/PIXEL_ART_PRODUCTION.md`; it is not a parallel art-direction document.

## 2026-09-04 — Native-grid Exilada S-view spike

### Goal

Test whether ChatGPT can produce a true production-raster sprite without relying on diffusion output, image downscaling, antialiasing, or a superficial pixel filter.

### Method

- renderer: Python + Pillow;
- native canvas: **96 × 96 RGBA**;
- authored directly on the target pixel grid;
- no diffusion bitmap used in the final sprite;
- no downscale;
- no antialiasing;
- controlled palette;
- semantic construction of hair, body, cloth, restraints, shadows/highlights and scars;
- nearest-neighbor previews generated separately for inspection.

### Outputs

Two passes were produced locally during the spike:

- `exilada_S_96x96.png` — first pass;
- `exilada_S_96x96_v2.png` — second pass;
- corresponding silhouettes, enlarged nearest-neighbor previews and JSON source metadata.

These local artifacts are **not canonical production assets** and have not been committed as character art.

### Result

**Technical gate: PASS.**

The method proves that the project can create a real 96×96 RGBA sprite where one source pixel equals one production pixel, with controlled palette and no hidden high-resolution illustration step.

**Visual-quality gate: FAIL.**

Observed problems in the two passes:

- silhouette is too generic;
- anatomy still trends too broad/stubby for the intended adult Exilada;
- face loses too much identity;
- hair mass is readable but not yet distinctive enough;
- overall authored-raster quality is below the project's best-in-class modern pixel-art target;
- the result does not yet carry enough of the Conan / Frazetta / Heavy Metal physicality and design authority.

### Decision

Keep **native-grid authoring** as the correct architectural direction, but reject these specific sprite passes as Production Pixel Master candidates.

The next iteration must improve authored cluster design and character-specific silhouette rather than returning to direct image generation.

### Next gate

Produce a stronger `S` view on the same 96×96 native grid, preserving:

- adult lean anatomy;
- long heavy black hair as the primary silhouette anchor;
- minimal degraded clothing;
- compact restraint markers;
- weaponless state;
- high-oblique gameplay projection;
- controlled palette and cluster economy;
- readability at 1×.

Only after an `S` view passes should the project proceed to `NE` and `N`.
