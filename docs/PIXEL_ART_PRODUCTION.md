# Pixel Art Production — Living Document

Status: **modern pixel-art production target locked; no Production Pixel Master approved. Direct image generation and hand-authored Python/Pillow geometry have both been tested and rejected as final-authoring routes. The next gate is a true native-grid agent/editor workflow with visual iteration.**

This document is the canonical record for final raster production. It must be updated after every material pixel-art experiment, pass/fail result, production-method change or approval.

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
- consistent character identity across directions, equipment and states;
- no dependence on high-resolution illustrative detail.

The target is mature, severe, physical and atmospheric. Sword-and-sorcery references such as Conan, Frank Frazetta, Heavy Metal and Julie Bell inform mass, physicality, adult fantasy, body presence and dramatic shape language. They are **not** to be copied literally and they must be translated into the constraints of gameplay pixel art rather than imitated as high-resolution painting.

Useful pixel-art quality references include titles such as *Children of Morta*, *Blasphemous*, *Eastward* and *Sea of Stars* for discipline, silhouette, palette and authored raster quality; the project does not copy any one game's style.

## What is explicitly rejected

### Rejected: high-resolution image generation pretending to be pixel art

The direct image-generation attempts produced visually plausible Exilada-like characters but remained high-resolution generative illustrations with visible blocky treatment.

Observed failure:

- generated files around `1024 × 1536`, not actual production canvases;
- excessive surface detail on skin, cloth and hair;
- apparent pixels were an image style, not the actual production grid;
- no trustworthy palette/cluster control;
- no reliable 1× gameplay evaluation;
- no evidence that directional frames would remain the same character.

**Status: FAIL.** Do not rescue this route by prompt iteration. Image generation remains useful only as identity, composition or pose reference.

### Rejected: Python/Pillow geometric drawing as the artistic authoring method

A native `96 × 96` Exilada spike was then constructed directly with Pillow using polygons, rectangles, lines and a controlled palette.

Technical properties passed:

- true 96×96 RGBA canvas;
- no antialiasing;
- no downscale;
- actual native pixels;
- controlled palette;
- transparent background.

Visual result failed decisively:

- generic/procedural mannequin quality;
- weak authored anatomy;
- crude silhouettes and clusters;
- no convincing translation of the Exilada's design or the project's sword-and-sorcery references;
- far below best-in-class modern pixel art;
- formal similarity to the already rejected idea of simple procedural primitives being mistaken for final visual art.

**Status: FAIL as an art-authoring route.** Python/Pillow remains valid for deterministic export, validation, palette checks, packing, masks and QA, but not as the system that invents the final character art through primitive geometry.

## Production principle now locked

**Native grid is necessary but not sufficient.**

A valid production route must provide both:

1. **true native-grid pixel control**, and
2. **high-level visual authorship capable of producing professional modern pixel art.**

The project must not confuse technical raster correctness with artistic quality again.

## Current production architecture candidate

The next route is **agent-native pixel editing**.

The AI should operate a real pixel-art document/editor or structured pixel source and iterate visually:

`identity/pose reference -> native pixel canvas -> draw/edit -> preview at 1× -> critique -> repair clusters -> validate -> save`

The agent must be able to:

- create the exact canvas size;
- control individual pixels and connected regions;
- maintain a fixed palette;
- inspect the actual canvas after each material edit;
- alter silhouette and clusters deliberately;
- preserve layers/frames/anchors;
- export deterministic PNG/spritesheets;
- run automated checks without replacing visual judgment.

### External tooling researched

#### Aseprite MCP — promising architecture, not yet adopted

Current public implementation can operate Aseprite through native pixel-level primitives, layers, frames, palette control, canvas preview, silhouette export, standards checks and iterative `draw -> preview -> analyze -> fix` loops.

Advantages:

- the editor owns a real pixel canvas;
- AI operations are actual edits, not a diffusion bitmap pretending to be pixel art;
- animation/layer/palette infrastructure already exists;
- implementation is MIT licensed.

Constraint:

- requires a local Aseprite installation.

**Status: candidate for a controlled spike, not yet approved.**

#### LibreSprite-MCP — free alternative, currently less trustworthy

A LibreSprite MCP exists and is GPL-2.0, but its own documentation describes the implementation as hacky/brittle and not extensively tested, with low-quality/unclear MCP resources.

**Status: research fallback, not preferred production foundation at present.**

#### code-as-pixelart — useful structured-source reference

This MIT project treats characters as structured source with semantic colors, named parts, directional views, cels, poses, anchors and deterministic animation/export.

Useful architectural ideas:

- source-of-truth separate from exported PNG;
- diffable character documents;
- validated operations;
- deterministic render/export;
- semantic parts/anchors.

**Status: architectural reference/candidate component, not yet proven to create the required art quality by itself.**

#### Spriteloom — not suitable as Production Pixel Master authoring foundation

Although local and convenient, its workflow still uses FLUX.2 diffusion followed by post-processing such as crop, palette quantization, background removal and fit-to-canvas.

That is fundamentally still the route the project has rejected for the canonical master.

**Status: not a Production Pixel Master foundation.**

## Native gameplay raster — provisional locked starting target

Internal gameplay grid:

**640 × 360 native pixels**

Why:

- 3× integer scale to 1920×1080;
- 4× integer scale to 2560×1440;
- sufficient tactical field while retaining meaningful pixel structure.

This value may only change after a real gameplay-composition test.

### Exilada sprite scale

Starting body/silhouette target:

**~64 native pixels from highest visible hair mass to grounded foot**

Tuning band during composition validation:

**56–72 px**

Idle/locomotion canvas starting point:

**96 × 96 px**

Ordinary melee/action canvas starting point:

**128 × 128 px**

The character is not a 64×64 box; the visible body is approximately 64 px high inside a larger transparent canvas.

## Gameplay projection

All production character references must be designed for the actual gameplay camera:

- high-oblique top-down;
- viewing axis approximately 60–70° relative to the horizontal ground plane;
- continuous 360° movement;
- not vertical top-down;
- not rigid 2:1 isometric.

Front/profile catalogue art is not sufficient production evidence.

## Exilada production reference pack

The Production Pixel Master is a directional reference family, not one oversized portrait.

Required final neutral turntable:

- S
- SW
- W
- NW
- N
- NE
- E
- SE

All views must preserve:

- same scale;
- same anatomy/proportion logic;
- same dominant hair mass;
- same initial clothing state;
- same captivity-marker logic;
- same lighting assumption;
- same ground/pivot convention;
- weaponless base state.

Before all eight views, the first visual gate remains only:

1. `S`
2. `NE`
3. `N`

Do not create a walk cycle until these three static views are convincingly the same character and pass at 1×.

## Exilada — pixel-art identity priorities

At gameplay scale, priority order is:

1. large black hair mass;
2. adult lean/compact body proportion;
3. severe, alert physical presence;
4. skin/hair value separation;
5. minimal asymmetrical degraded cloth;
6. readable limbs and grounded bare feet;
7. broken-restraint history markers where legible;
8. facial microdetail.

Weapons are variable gameplay equipment and are not an identity anchor.

## Sword-and-sorcery translation rules

The visual references must influence **shape language**, not become decorative filters.

Desired translation:

- Frazetta: decisive dark/light masses, bodily weight, dangerous silhouette, physical immediacy;
- Conan/sword-and-sorcery: brutality, scarcity, primitive/material world logic, exposed body without modern costume cleanliness;
- Heavy Metal: adult freedom, sensual/material physicality, strangeness and less sanitized fantasy design;
- Julie Bell: anatomical confidence and sculptural physical presence, without drifting into polished bodybuilding or chrome-like glamour.

For the Exilada specifically:

- avoid fitness-model musculature;
- favor lean functional anatomy, tendon/bone/weight;
- clothing should look like residue of captivity, not a designed barbarian costume;
- nudity/skin exposure is acceptable when materially/narratively coherent and should not be converted into pin-up framing;
- hair should be a violent dominant mass rather than hundreds of tiny strands;
- asymmetry and damaged material state should feel lived rather than decorated.

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

The number is not a quota. Value clarity matters more than counting colors.

Guidelines:

- hair remains the darkest dominant material;
- skin, cloth and restraint metal separate immediately at 1×;
- do not add near-identical shades merely to fake smooth rendering;
- blood, dirt, wetness, burns, frost and similar states should be systematic overlays/palette modifications rather than arbitrary baked noise.

## Pixel integrity / runtime rules

Final production sprites must use:

- nearest-neighbor scaling;
- integer sprite positioning where required for pixel stability;
- no bilinear filtering;
- no antialiased transform bake;
- no arbitrary rotation of finished bitmaps;
- fixed world scale across frames unless a real gameplay mechanic changes size.

## QA gate

A Production Pixel Master candidate fails if:

- it looks good only enlarged;
- it reads as a shrunk illustration;
- it is technically native but visually procedural/generic;
- anatomy becomes juvenile or mannequin-like;
- hair loses its designed mass;
- clothing becomes generic fantasy-barbarian costuming;
- directions look like different people;
- palette expands without structural reason;
- routine manual pixel repair by the user would be required.

A candidate passes only if **both** are true:

1. it is technically native, controllable and reproducible;
2. it is artistically convincing at the quality level of the project's modern pixel-art target.

## Current decision / next gate

**PASS:** separation of identity master from Production Pixel Master.

**PASS:** 96×96 native-grid construction is technically feasible.

**FAIL:** direct high-resolution image generation as final sprite authoring.

**FAIL:** primitive Python/Pillow drawing as final artistic authoring.

**PAUSED:** mass animation production until a convincing Production Pixel Master exists.

**NEXT GATE:** validate an **agent-operated native pixel editor/source workflow**, beginning with a single `S` Exilada sprite at the real target grid. The first candidate should allow the agent to inspect and revise the actual pixels iteratively rather than outputting one generated bitmap.