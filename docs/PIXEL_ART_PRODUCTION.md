# Pixel Art Production — Living Document

Status: **true modern pixel art remains the final gameplay target. No Production Pixel Master is approved. The current FLUX/RefControl work is an upstream pose/identity experiment, not final sprite generation. The immediate dependency is the V2 walk-pose correction; gameplay-scale/native-raster validation resumes after V2.**

## Core distinction

The project uses two visual reference layers:

1. **Identity master** — who the Exilada is.
2. **Production Pixel Master** — how she exists on the actual gameplay pixel grid.

Identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It must not be converted into the final sprite merely by resize, quantization or a pixel-style postprocess.

## Locked visual target

Final gameplay art uses **true modern pixel art**:

- deliberate native-grid construction;
- readable silhouettes and connected pixel clusters;
- controlled palette/value grouping;
- material separation through authored shapes;
- stable animation at actual gameplay scale;
- mature, severe, physical sword-and-sorcery presentation;
- no dependence on illustrative microtexture.

References such as Conan, Frank Frazetta, Heavy Metal and Julie Bell inform physicality, mass and adult fantasy shape language; they are translated into gameplay raster design rather than copied as paintings.

## Rejected final-art routes

### High-resolution image generation -> resize/quantize

**FAIL as final Production Pixel Master route.**

High-resolution generation can be useful upstream for identity, pose or motion reference, but cannot prove:

- final pixel clusters;
- final palette;
- gameplay-scale readability;
- native-grid frame stability.

### Primitive Python/Pillow artistic authoring

**FAIL visually.**

Native-grid technical correctness was demonstrated, but the generated character was procedural/mannequin-like and below the required art quality.

Python/Pillow remains useful for deterministic QA, masks, packing, palette checks and export.

## Gameplay projection

Locked baseline:

**elevated 2D belt-scroller / false 3D**

Consequences:

- old high-oblique/360° eight-direction assumptions are superseded;
- old ~64 px visible height, `96×96` idle canvas and `128×128` melee canvas are no longer locks;
- left/right or limited three-quarter facing families may be sufficient, but this must be validated in gameplay;
- character scale must be derived from combat composition rather than chosen in isolation.

## Current high-resolution animation evidence

The current relevant evidence is the **V1 RefControl four-pose run at 768×1024**, not older unrelated walk-cycle experiments.

V1 is useful as an upstream pose/identity test because it preserved the Exilada much better than previous routes. It is not approved as final gameplay raster.

Observed V1 defects that must be corrected before scale testing:

- reversed/mirrored toe orientation in at least one foot;
- left-arm inconsistency;
- subtle body drift;
- chain/shackle continuity drift.

Therefore the order is now:

`identity master -> controlled V2 re-posing correction -> V1/V2 QA -> gameplay-scale test -> Production Pixel Master -> definitive native-grid walk`

Not:

`high-res generated poses -> direct downscale -> final sprites`

## Native gameplay raster

Provisional scene raster remains:

**640 × 360**

It is not yet locked. It will be tested after V2 against the selected belt-scroller composition.

Candidate character screen heights such as 112/128/144 px remain only future comparison samples, not requirements.

## Exilada identity priorities at gameplay scale

1. dominant long black hair mass;
2. adult lean/compact anatomy;
3. severe physical presence;
4. clear skin/hair value separation;
5. asymmetrical degraded beige cloth;
6. readable limbs and grounded bare feet;
7. restraint-history markers where legible;
8. facial microdetail last.

Weapons are variable equipment, not identity anchors.

## Cluster rules

Required:

- large connected clusters before accents;
- stable silhouettes across animation;
- one-pixel marks only when functional;
- material separation through shape/value;
- controlled detail at 1×.

Avoid:

- random speckling;
- hair-strand soup;
- pseudo-photographic skin texture;
- dense fabric noise;
- automatic dithering as default;
- smooth-gradient dependence;
- uniform heavy black sticker outlines.

## Palette

Initial Exilada target remains approximately **24–32 visible base colors** excluding transparency/state overlays. This is guidance, not a quota.

Hair should remain the darkest dominant material. Skin, cloth and metal must separate immediately at gameplay scale.

## Final sprite runtime integrity

Final production sprites must use:

- nearest-neighbor scaling;
- integer positioning where needed for stability;
- no bilinear filtering;
- no antialiased transform bake;
- no arbitrary rotation of finished bitmaps;
- stable world scale across frames.

## Production-authoring candidate class

The preferred final-authoring class remains an **agent-operated native pixel editor / structured native-grid source** with iterative inspection:

`identity + validated motion reference -> native pixel document -> draw/edit -> 1× gameplay preview -> critique/repair -> deterministic export`

Aseprite MCP remains a promising architecture; LibreSprite MCP remains fallback; structured code-as-pixelart ideas remain useful for semantic parts/anchors/export. None is approved yet as the final artistic pipeline.

## Current decision / next gate

**PASS:** identity master separated from Production Pixel Master.

**PASS:** high-resolution RefControl output may be used as upstream pose/motion reference.

**FAIL:** direct high-resolution generation as final pixel-sprite authoring.

**FAIL:** primitive procedural pixel drawing as final art authoring.

**SUPERSEDED:** old ~64 px / `96×96` / eight-direction assumptions.

**CURRENT DEPENDENCY:** complete the controlled RefControl V2 correction and V1-vs-V2 QA first.

**NEXT PIXEL-ART GATE AFTER V2:** place the accepted motion/reference set in a representative elevated belt-scroller composition at native 1×, determine actual on-screen character height and scene raster, then author the first true native-grid Production Pixel Master and definitive base walk.
