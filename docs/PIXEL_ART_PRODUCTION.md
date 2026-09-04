# Pixel Art Production — Living Document

Status: **modern pixel-art production target locked; no Production Pixel Master approved. Direct high-resolution generation and primitive Python/Pillow authoring are rejected as final-art routes. The gameplay projection is an elevated 2D belt-scroller / false-3D baseline. The current blocking gate is now the relationship between the existing high-resolution walk-cycle tests and the actual gameplay-scale raster: validate motion/readability at gameplay scale before locking a new Production Pixel Master size or authoring the final native-grid walk cycle.**

This document is the canonical record for final raster production. It must be updated after every material pixel-art experiment, PASS/FAIL result, production-method change or approval.

## Core distinction

The project uses two different character-reference layers:

1. **Identity master** — defines who the character is.
2. **Production Pixel Master** — defines how that character actually exists on the final gameplay pixel grid.

For the Exilada, the identity master remains:

`assets/source/characters/exilada/reference/exilada_master.png`

It is intentionally richer than the final gameplay sprite. It must never be treated as final sprite art merely by resizing, quantizing or adding visible pixel texture.

## Locked visual target

The final game uses **true modern pixel art**.

This explicitly means:

- deliberate native-grid construction;
- strong silhouettes;
- readable pixel clusters;
- controlled values and palette;
- material separation through authored shapes rather than microtexture;
- animation readability at actual gameplay scale;
- consistent character identity across equipment and states;
- no dependence on high-resolution illustrative detail.

The target is mature, severe, physical and atmospheric. Sword-and-sorcery references such as Conan, Frank Frazetta, Heavy Metal and Julie Bell inform mass, physicality, adult fantasy, body presence and dramatic shape language. They are not to be copied literally and must be translated into gameplay pixel art rather than imitated as high-resolution painting.

Useful pixel-art quality references include titles such as *Children of Morta*, *Blasphemous*, *Eastward* and *Sea of Stars* for discipline, silhouette, palette and authored raster quality; the project does not copy any one game's style.

## Rejected authoring routes

### Direct high-resolution image generation as final pixel art — FAIL

Observed failure:

- outputs around `1024 × 1536`, not actual production canvases;
- excessive surface detail on skin, cloth and hair;
- apparent pixels were an image style rather than the production grid;
- no trustworthy cluster/palette control;
- no reliable 1× gameplay evaluation;
- no evidence of repeatable state/equipment consistency.

**Decision:** do not rescue this route through prompt iteration. Image generation may remain useful for identity, composition or pose reference, but not as the final sprite-authoring foundation.

### Python/Pillow primitive geometry as artistic authoring — FAIL visually

A real native `96 × 96` RGBA Exilada spike was constructed with polygons, rectangles and lines.

Technical raster properties passed:

- native RGBA canvas;
- no antialiasing;
- no downscale;
- controlled palette;
- transparent background.

Visual result failed:

- generic/procedural mannequin quality;
- weak authored anatomy;
- crude silhouette and clusters;
- poor translation of the Exilada identity and sword-and-sorcery references;
- far below the project's modern pixel-art quality target.

**Decision:** Python/Pillow remains valid for deterministic export, validation, palette checks, packing, masks and QA, but not as the system that invents the final art through primitive geometry.

## Production principle — LOCKED

**Native grid is necessary but not sufficient.**

A valid production route requires both:

1. **true native-grid pixel control**, and
2. **high-level visual authorship capable of professional modern pixel art.**

Technical raster correctness must never again be confused with artistic adequacy.

## Gameplay projection dependency

The production sprite cannot be sized independently from gameplay composition.

The current gameplay baseline is:

**elevated 2D belt-scroller / false 3D**

See `docs/VISUAL_DIRECTION.md` and `docs/GAME_VISION.md`.

This replaces the earlier high-oblique/360° character-presentation assumption.

Consequences:

- a mandatory eight-direction neutral turntable is no longer assumed;
- `S`, `NE`, `N` are no longer the first required directional master set;
- the old ~64 px body target is no longer locked;
- `96 × 96` idle/locomotion and `128 × 128` melee canvases are no longer locked;
- the Exilada may be significantly larger on screen if that better serves anatomy, silhouette and combat readability;
- left/right action families and mirroring may reduce animation multiplication, but the exact facing model must be validated rather than assumed.

## Recovered walk-cycle checkpoint — 2026-09-04

Before the production-raster question interrupted the animation work, two high-resolution eight-frame walk-cycle artifacts had already been produced for the Exilada:

- **smoke:** `8` frames, `8 fps`, `384 × 576` pixels per frame;
- **quality:** `8` frames, `8 fps`, `512 × 768` pixels per frame.

These are **high-resolution motion/reference artifacts**, not approved production sprites.

The unresolved methodological question is now explicit:

> How much does generating/evaluating the walk cycle at `384 × 576` or `512 × 768` alter what survives when the character is viewed at the real gameplay raster and screen height?

The project must not answer this by assuming that a high-resolution frame can simply be downscaled into final pixel art.

### Locked separation: motion proxy versus final raster

High-resolution frames may be used upstream to evaluate or derive:

- pose sequence;
- stride timing;
- foot-contact phases;
- body mechanics;
- hair/clothing secondary motion;
- identity continuity at the reference/rendering stage.

They **cannot** by themselves validate:

- final pixel clusters;
- final palette;
- gameplay-scale silhouette quality;
- readability of facial/clothing details;
- final native-grid animation stability.

Therefore:

`high-resolution motion/reference -> gameplay-scale readability test -> native-grid Production Pixel Master -> native-grid walk cycle`

is valid as a staged production architecture.

`high-resolution generated frames -> simple downscale/quantization -> final sprites`

remains rejected.

## Native gameplay raster

Provisional internal raster remains:

**640 × 360 native pixels**

Reasons retained for testing:

- 3× integer scale to 1920×1080;
- 4× integer scale to 2560×1440;
- a useful balance between authored pixel structure and scene area.

However, this is explicitly **subject to the current motion-aware gameplay-composition test**. It may change if the belt-scroller framing proves too coarse or too dense.

## Current motion-aware scale gate

The next validation must use the already-existing eight-frame walk cycle as a **motion proxy**, not as final art.

At the provisional `640 × 360` gameplay raster, preview the same cycle at several candidate visible character heights. Initial comparison points may include approximately:

- `112 px`;
- `128 px`;
- `144 px`.

These are **test samples, not locked production sizes**.

The preview should include a minimal representative belt-scroller space so that the cycle can be judged in context rather than against an empty background.

Evaluate at native `1×`:

1. whether the stride remains readable;
2. whether heel/toe/foot-contact phases remain visually distinct;
3. whether the body appears grounded rather than sliding;
4. whether the Exilada's large hair mass still reads coherently in motion;
5. whether arms/legs separate clearly during passing/contact poses;
6. whether the character occupies too much or too little of the combat field;
7. whether 3–5 enemies could coexist legibly around her;
8. whether normal weapons/attack arcs have sufficient screen space;
9. whether the belt depth still allows useful foreground/background positioning;
10. whether `640 × 360` remains a viable native scene raster.

This gate judges **motion readability and gameplay scale**, not final pixel-art quality. No result from this gate can be promoted directly to the Production Pixel Master merely because it looks acceptable after resize.

## Current production architecture candidate

The preferred final art-authoring class remains **agent-native pixel editing / structured native-grid editing**.

Desired loop after the motion-aware scale gate:

`identity + validated motion references -> native pixel document -> draw/edit -> preview at 1× in gameplay composition -> critique -> repair clusters -> validate -> save`

The agent must be able to:

- create exact native canvases;
- control individual pixels and connected regions;
- maintain controlled palettes;
- inspect the actual canvas after material edits;
- alter silhouette and clusters deliberately;
- preserve layers/frames/anchors;
- export deterministic PNG/spritesheets;
- run automated checks without replacing visual judgment.

### Aseprite MCP — promising architecture, not yet adopted

Advantages:

- real pixel canvas;
- pixel-level operations;
- layers/frames/palette support;
- iterative preview/analysis/fix loop;
- animation infrastructure.

Constraint:

- requires a local Aseprite installation.

**Status:** candidate for a controlled spike, not yet approved.

### LibreSprite-MCP — free fallback

A LibreSprite MCP route exists, but previous research found its implementation less trustworthy/brittle.

**Status:** fallback research route, not preferred foundation.

### code-as-pixelart — architectural reference

Useful concepts:

- structured source of truth separate from exported PNG;
- semantic colors/parts;
- named views/cels/poses;
- anchors;
- deterministic export;
- diffable/validated operations.

**Status:** useful component/reference, not proven sufficient for artistic authorship by itself.

### Spriteloom — not accepted as Production Pixel Master foundation

Its diffusion-plus-postprocess structure remains too close to the rejected route of generating an illustration and converting it afterward.

**Status:** not the canonical pixel-master authoring foundation.

## Exilada pixel-art identity priorities

At gameplay scale, priority order remains:

1. large black hair mass;
2. adult lean/compact body proportion;
3. severe, alert physical presence;
4. skin/hair value separation;
5. minimal asymmetrical degraded cloth;
6. readable limbs and grounded bare feet;
7. broken-restraint history markers where legible;
8. facial microdetail.

Weapons are gameplay-variable equipment and are not an identity anchor.

## Sword-and-sorcery translation rules

Desired translation:

- Frazetta: decisive dark/light masses, bodily weight, dangerous silhouette, physical immediacy;
- Conan/sword-and-sorcery: brutality, scarcity, primitive/material world logic, exposed body without modern costume cleanliness;
- Heavy Metal: adult freedom, sensual/material physicality, strangeness and less sanitized fantasy design;
- Julie Bell: anatomical confidence and sculptural physical presence without polished bodybuilding/chrome glamour.

For the Exilada:

- avoid fitness-model musculature;
- favor lean functional anatomy, tendon/bone/weight;
- clothing must read as residue of captivity rather than a designed barbarian costume;
- nudity/skin exposure is acceptable when materially/narratively coherent and not converted into pin-up framing;
- hair should be a dominant mass rather than strand soup;
- asymmetry and damaged material state should feel lived rather than decorative.

## Cluster rules

Required:

- connected clusters explain volume;
- large masses before accents;
- one-pixel marks have a clear function;
- stable clusters between animation frames;
- material separation through shape/value.

Avoid:

- random speckling;
- hair strand soup;
- pseudo-photographic skin texture;
- dense fabric noise;
- default dithering;
- smooth gradient dependence;
- uniform heavy black sticker outlines.

## Palette

Initial Exilada target remains approximately **24–32 visible base colors**, excluding transparency and transient state overlays.

The number is not a quota. Value clarity matters more than color count.

Guidelines:

- hair remains the darkest dominant material;
- skin, cloth and restraint metal separate immediately at 1×;
- avoid near-identical shades used only to fake smooth rendering;
- blood, dirt, wetness, burns, frost and similar states should be systematic overlays/palette modifications rather than arbitrary baked noise.

## Pixel integrity / runtime rules

Final production sprites must use:

- nearest-neighbor scaling;
- integer sprite positioning where required for pixel stability;
- no bilinear filtering;
- no antialiased transform bake;
- no arbitrary rotation of finished bitmaps;
- fixed world scale across frames unless a gameplay mechanic intentionally changes size.

## QA gate

A Production Pixel Master candidate fails if:

- it looks good only enlarged;
- it reads as a shrunk illustration;
- it is technically native but visually procedural/generic;
- anatomy becomes juvenile/mannequin-like;
- hair loses its designed mass;
- clothing becomes generic fantasy-barbarian costuming;
- palette expands without structural reason;
- routine manual pixel repair by the user would be required;
- it cannot sit convincingly inside the actual belt-scroller gameplay composition.

A candidate passes only if both are true:

1. technically native, controllable and reproducible;
2. artistically convincing at actual gameplay scale in the selected projection.

## Current decision / next gate

**PASS:** separation of identity master from Production Pixel Master.

**PASS:** native-grid sprite construction is technically feasible.

**PASS:** high-resolution walk-cycle artifacts are valid as **motion proxies/reference**, not as final pixel sprites.

**FAIL:** direct high-resolution image generation as final sprite authoring.

**FAIL:** primitive Python/Pillow drawing as final artistic authoring.

**SUPERSEDED:** previous ~64 px / `96 × 96` / eight-direction baseline assumptions.

**PAUSED:** final Production Pixel Master authoring until gameplay-scale walk readability is measured under the belt-scroller projection.

**NEXT GATE:** run a **motion-aware belt-scroller composition/scale test** using the existing eight-frame walk-cycle artifact as a temporary motion proxy at several candidate screen heights. Lock the actual gameplay-scale character height only from that evidence. Then author the native-grid Production Pixel Master and the definitive base walk cycle at that scale.
