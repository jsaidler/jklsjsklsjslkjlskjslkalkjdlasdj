# Visual Direction — Living Document

Status: **modern pixel art remains the final gameplay target. The current Exilada master is the canonical high-detail identity/design reference, not the final sprite. Gameplay presentation baseline is now an elevated 2D belt-scroller / false-3D camera rather than the previously assumed high-oblique 360° top-down system. Production execution remains under validation.**

## Process rule — living documentation

All material visual-direction decisions, production-pipeline changes, accepted/rejected approaches and validation results must be recorded here or in the relevant linked canonical document as they occur. When a decision changes, edit the living document rather than creating parallel versions or relying on chat history.

The high-level game vision is defined in `docs/GAME_VISION.md`.

## Core production constraint

The project is developed end-to-end by ChatGPT, with the user directing and approving decisions.

The user will **not produce game art manually and will not hire an external art/animation team**. Therefore the complete production visual pipeline — characters, creatures, environments, animation, effects, variation, maintenance and future expansion — must be executable by ChatGPT and project tooling without routine bespoke manual frame work.

A visual direction is invalid if it can produce an attractive isolated concept but cannot be reproduced, animated, varied, maintained and expanded by the same production system used to build the game.

## Locked final visual language: modern pixel art

The final game uses **modern pixel art as an actual image-making language**, not merely a pixel texture or post-process applied to another rendering style.

At production gameplay scale this means:

- pixel clusters, silhouette, value grouping, palette, edge treatment and animation readability are primary design concerns;
- the final image must not read as conventional painted/3D imagery simply downsampled, quantized or covered with a pixel filter;
- pixel density and detail must be intentional and coherent at gameplay scale;
- the style may be detailed and contemporary, but detail must remain organized into readable raster structures rather than noisy microtexture;
- controlled palettes, clean clusters and strong silhouettes are preferred over decorative texture for its own sake;
- the target is mature, severe, atmospheric, physical and systemic rather than nostalgic, cute or cartoonish.

## Identity reference versus production sprite

Canonical Exilada identity reference:

`assets/source/characters/exilada/reference/exilada_master.png`

The current master is richer and more detailed than the final production sprite should be. It remains approved because it establishes the Exilada's identity, proportions, face, long black hair mass, clothing state, captivity markers and overall visual character.

It must therefore be treated as a **high-detail canonical design/identity reference**, not as evidence that its current raster density already satisfies final gameplay pixel art.

Consequences:

- the source must not simply be resized/quantized and declared a finished sprite;
- final pixel-art compliance must be solved at actual gameplay scale;
- the project requires an automatic/scalable production method without manual frame repainting;
- the source design must not be redesigned merely to make a particular generation model easier to use.

## Explicitly rejected as final visible art

- simple procedural primitives or generic low-poly geometry presented directly;
- the same geometry hidden behind outlines, hatching, fog or cosmetic shaders;
- conventional rendered imagery with superficial pixelation/post-processing as the final solution;
- fake pixel texture that does not survive inspection as coherent gameplay-scale raster construction;
- large libraries of manually painted frame-by-frame sprites;
- production approaches that require routine manual frame repair.

3D or procedural geometry may still be useful internally for blockout, collision, navigation, pose generation, lighting reference or hidden production tooling, but it is not the locked visible art direction.

## Character visual principles

Characters must be identifiable first through **silhouette, large masses, posture and controlled contrast**, then through secondary detail.

At gameplay scale:

- hair masses, body proportions, clothing asymmetry and large equipment shapes must remain readable;
- facial microdetail cannot carry identity by itself;
- weapons are gameplay-variable equipment and are not permanent identity anchors unless explicitly defined for another character;
- clothing/equipment may evolve without erasing underlying body, hair and posture identity;
- anatomy remains adult and materially grounded;
- exposed skin, partial nudity and full adult nudity are valid parts of the visual language when appropriate to character, scene and state;
- dirt, wounds, blood, scars and wear should preferably express actual simulated history/state rather than arbitrary decoration.

The protagonist-specific rules live in `docs/CHARACTERS.md`.

## Erotic charge and adult-body language — LOCKED 2026-09-05

The project does **not** treat erotic charge as something to be automatically removed or sanitized.

The principal visual references invoked for this universe — **Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell** — repeatedly use idealized adult bodies, sensuality, nudity, sexual confidence, fetishized materials, dramatic poses and erotic tension as part of their sword-and-sorcery / fantasy vocabulary. Avoiding that dimension by default would move the project away from its own reference lineage.

Locked interpretation:

- eroticism is an allowed and intentional part of the mature visual vocabulary;
- adult characters may be beautiful, sensual, sexualized, nude or partially nude without this being treated as a defect;
- nudity does not need to be visually neutralized or disguised merely because it is nudity;
- erotic charge is not mandatory in every scene or every character state;
- heroic, violent, grotesque, vulnerable, erotic and matter-of-fact body readings may coexist in the same universe;
- the direction should preserve adult agency and scene intent rather than impose a blanket rule of either desexualization or sexualization;
- captivity, violence and coercion may be depicted directly, but the project should distinguish the erotic charge of an adult character/body from making coercion itself the only erotic subject unless that is an explicit narrative/art-direction choice.

For the Exilada specifically, her body may carry erotic charge even when the state is harsh, wounded, dirty, deprived or minimally clothed. The production rule is therefore **not “avoid erotic framing”; it is “do not sanitize the mature body language of the project, and make framing intentional.”**

## Systemic visual rule

Whenever feasible, visually relevant state should be a consequence of simulation rather than random decoration.

Examples:

- scars reflect survived injuries/history;
- equipment wear reflects use/material condition;
- population clothing and equipment reflect resources, culture, climate, trade and conflict;
- looted equipment may propagate between factions after warfare;
- hunger, disease, age, fatigue, status, occupation and injury may affect silhouette, posture, animation, material condition or clothing;
- blood, dirt, wetness, burns, frost and other transient states correspond to gameplay/environmental causes.

Procedural variation must therefore be **causal and constrained**, not arbitrary noise.

## Character production architecture

Broad character variation should come from tractable systems rather than bespoke manual drawing for every individual.

Useful controlled parameters may include:

- height;
- limb/torso proportions;
- mass/volume;
- posture;
- head/facial structure;
- hair families;
- age-related transforms;
- injury/state transforms;
- clothing layers;
- equipment states;
- species-specific anatomy.

The final visible output must still satisfy the locked gameplay raster language. Production efficiency does not excuse generic forms or incoherent pixels.

## Environment direction

The environment should derive richness from composition, state and systemic consequence rather than an excessive number of one-off assets.

Preferred structure:

- modular architecture;
- connected dense gameplay spaces rather than empty traversal acreage;
- procedural/systemic settlement composition where appropriate;
- vegetation families with controlled variation;
- dynamic weather and lighting;
- persistent or semi-persistent evidence of events;
- simulation-driven settlement condition/resource use;
- pixel-art materials and shapes designed for the actual gameplay projection;
- foreground/background layering, occlusion and depth cues that sell a false-3D world while remaining fundamentally 2D.

## Gameplay projection — LOCKED BASELINE

### Elevated 2D belt-scroller / false 3D

The previous baseline of a high-oblique top-down camera with continuous 360° character presentation is **superseded**.

The current locked baseline is:

**an elevated 2D belt-scroller / 2.5D false-3D presentation inspired by the spatial language of arcade beat'em ups, updated for a contemporary systemic action game.**

This is **not** a pure side-scrolling platformer.

Core principles:

- the screen has a strong lateral travel axis;
- the player also moves continuously along a walkable depth axis;
- the camera is elevated enough to expose the ground plane and make depth ordering legible;
- the protagonist remains large and readable in a mostly lateral / three-quarter action presentation;
- characters may pass in front of/behind each other and environmental elements;
- foreground and background layers reinforce depth;
- doors, paths, stairs, bridges, interiors, ledges and other structures may use false-3D spatial cues;
- combat readability has priority over geometric purity;
- the game need not obey strict 2:1 isometric projection;
- the camera does not need to reproduce the full freedom of the world simulation: it needs to make local gameplay spaces readable and satisfying.

### Why this baseline was chosen

Relative to an eight-direction isometric/top-down character system, this approach should materially reduce production complexity while improving:

- full-body readability;
- impact and melee readability;
- animation reuse;
- equipment variation feasibility;
- scalability to many NPCs, races and creatures;
- ability to keep the Exilada visually large enough for the desired mature, anatomical pixel-art language.

### Consequences for old assumptions

The following earlier production assumptions are **no longer locked**:

- eight-direction neutral character turntable as a mandatory baseline;
- `S / NE / N` as the first three required directional masters;
- ~64 px visible Exilada height;
- `96 × 96` idle/locomotion canvas;
- `128 × 128` ordinary melee canvas.

Those values belonged to the previous high-oblique/360° composition hypothesis. They must now be recalculated from an actual belt-scroller gameplay-composition test.

### Still to tune

- exact camera elevation/pitch;
- exact walkable depth-band size;
- orthographic-like versus perspective treatment;
- camera distance/zoom;
- protagonist screen occupancy;
- vertical/elevation traversal rules;
- camera follow/damping/combat framing;
- number of distinct facing families required beyond left/right mirroring;
- whether the provisional `640 × 360` native raster remains ideal.

## Animation direction

Mass animation production remains paused until the Production Pixel Master and gameplay projection are sufficiently defined.

Existing animation research is preserved in `docs/ANIMATION_PIPELINE.md`, including the FLUX.2 Klein + RefControl spike. That work remains technically useful, but it must not force the game into the older eight-direction/top-down assumptions.

The new projection should be exploited to minimize directional multiplication where visually acceptable — likely emphasizing left/right action families with depth movement handled without requiring a complete new body rendering for every travel vector. Exact facing rules remain a downstream validation item.

## Visual validation gate

Artwork is not approved because a concept sheet is attractive. Production art must be judged at actual game scale and in gameplay context.

A representative visual validation sequence must eventually demonstrate:

1. one protagonist with a distinctive silhouette at gameplay scale;
2. deliberate modern pixel-art construction rather than shrunk illustration;
3. convincing placement inside the elevated belt-scroller / false-3D scene;
4. readable locomotion and combat across lateral and depth movement;
5. at least one representative environment composition;
6. dynamic state such as light, injury, dirt, blood, weather or equipment without destroying readability;
7. reproducibility through project tooling without manual frame-by-frame repainting.

## Current decision

**LOCKED:** modern pixel art remains the final visible gameplay language.

**LOCKED:** `exilada_master.png` remains the canonical high-detail identity/design master, not the final sprite.

**LOCKED:** mature, severe, physical, atmospheric and systemic presentation.

**LOCKED:** erotic charge, sensuality and adult nudity are legitimate parts of the visual language and must not be automatically sanitized away.

**LOCKED:** gameplay projection baseline is elevated 2D belt-scroller / false 3D, not pure side-scroller and not the previous high-oblique 360° character system.

**LOCKED:** visually relevant character/world state should be causal whenever feasible.

**LOCKED:** character production must remain scalable without manual art labor from the user or hired artists.

**NEXT VISUAL GATE:** continue the G3S structured-2D body-first pipeline: complete nude/hairless body base first, then hair, clothing and accessories as separate layers before layered motion proof.
