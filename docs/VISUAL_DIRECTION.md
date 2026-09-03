# Visual Direction — Living Document

Status: **production constraints and baseline gameplay camera locked; final aesthetic still unproven**

## Core production constraint

The project is developed end-to-end by ChatGPT, with the user directing and approving decisions.

The user will **not produce game art manually and will not hire external artists**. Therefore the complete production visual pipeline — characters, creatures, environments, animation, materials, effects, variation, maintenance, and future expansion — must be executable by ChatGPT without depending on a conventional art team or on bespoke manual artwork supplied by the user.

This is a hard design constraint, not merely a budget preference.

A visual direction is invalid if it can produce an attractive concept image but cannot be reproduced, animated, varied, maintained, and expanded by the same AI-driven production pipeline used to build the game.

Generated concept imagery may be used for exploration and reference, but it must not be mistaken for production-ready modular assets unless those assets can actually be generated and integrated reproducibly.

## Consequences

### Avoid as foundational pipelines

- Any pipeline that requires the user to model, draw, paint, rig, retopologize, animate, or manually repair production assets.
- Any pipeline whose quality depends on hiring external artists.
- Realistic or semi-realistic rendering as a primary target when maintaining that fidelity requires large amounts of bespoke modeling, sculpting, texturing, or animation work.
- High-detail realistic 3D requiring manual sculpting and retopology per creature.
- Large libraries of hand-painted character sprites.
- Frame-by-frame animation as the main animation system.
- Unique rigs and bespoke animation sets for every species.
- Visual variation that requires producing a new complete asset for every equipment, body, age, culture, mutation, or state combination.
- Photorealistic materials whose quality depends on large hand-authored texture sets.
- A visual identity dependent on illustration quality that cannot be reproduced systematically in runtime assets.
- Treating generated full-scene illustrations or character sheets as if they were automatically usable production assets.
- Treating simple runtime primitives plus lighting/shaders as proof of production-quality art.

### Prefer

- **Stylized rather than realistic rendering.** Stylization is a production strategy as well as an aesthetic choice: it must reduce authoring burden while preserving a strong, adult visual identity.
- Strong silhouettes and readable proportions.
- Low-to-moderate geometric complexity when hidden by or compatible with the final rendering language.
- Reusable skeleton families rather than one skeleton per creature.
- Procedural body proportion changes within controlled anatomical rules.
- Equipment assembled from modular parts and attachment points.
- Palette-driven rendering, procedural masks, shader-driven material variation, controlled pixelation/dithering, compact reusable textures where needed, and simulation-driven visual state.
- Animation built from reusable clips plus procedural posing, additive layers, IK, gait parameters, and behavioral state.
- Environmental assets constructed from modular kits and procedural composition.
- Lighting, atmosphere, weather, particles, material response, and world state as major sources of visual richness.
- Visual systems in which code and simulation create richness that would otherwise require large quantities of manually authored art.

## Failed visual-production attempts

The project has now tested and **rejected** a specific production approach:

> direct rendering of simple procedural 3D primitives / parametric low-detail geometry, with flat materials, outlines, hatching, lighting, fog, and procedural animation, presented as the final visible art.

This approach proved that the technical architecture is programmable, but **did not prove that ChatGPT can produce sufficiently strong final game art using that rendering language**.

Observed failure mode:

- characters read as procedural mannequins rather than authored protagonists;
- environments read as technical compositions of primitives rather than a distinctive world;
- shader changes, outlines, hatching, or lighting did not materially solve the underlying form-design problem;
- repeating the same geometric strategy with a different renderer or shader is not considered a new visual-production experiment.

Therefore **plain runtime primitive/low-poly rendering is rejected as the final art direction**. It may still be used internally for blockout, collision, navigation, prototyping, or hidden geometry, but not as the visible production target unless transformed by a substantially different rendering pipeline.

## Next candidate: pixel-rendered systemic 3D

The next visual-production candidate changes the final image formation rather than merely changing the shader on the same visible geometry.

The hypothesis to test is:

> systemic 3D geometry and continuous skeletal/procedural animation rendered internally at low resolution, then transformed into a deliberately pixel-art-like final image through palette quantization, ordered dithering, controlled edge treatment, hard value grouping, and low-resolution lighting.

The intent is **not** to imitate conventional frame-by-frame sprite production. The character remains continuously animated and can rotate freely in 3D; the final raster presentation is pixel-driven.

This candidate is attractive because it may simultaneously provide:

- continuous 360° movement and facing;
- reusable 3D rigs and modular equipment;
- no frame-by-frame animation burden;
- a non-realistic, mature visual language;
- reduced need for detailed sculpting because the final image is intentionally resolution-limited;
- lighting, particles, weather, injuries, equipment state, and world simulation that remain dynamic;
- a plausible route toward detailed-looking pixel art without hand-authoring thousands of sprite frames.

This remains **unproven** and must not be treated as the selected art direction until a visual spike demonstrates sufficient quality.

## Systemic visual rule

Whenever feasible, visually relevant state must be represented as a consequence of the simulation rather than as random decoration.

Examples:

- Scars should preferably reflect survived injuries or history.
- Equipment wear should reflect use and material condition.
- Population clothing and equipment should reflect available resources, culture, climate, trade, and conflict.
- Looted equipment may visually propagate between factions after warfare.
- Hunger, disease, age, fatigue, status, occupation, and injuries may affect silhouette, posture, animation, material condition, or clothing.

Procedural variation must therefore be **causal and constrained**, not arbitrary noise.

## Visual production architecture candidate

### Characters

Characters should be assembled from a limited number of anatomical families. Each family may expose parameters such as:

- height;
- limb proportions;
- torso proportion;
- mass/volume;
- posture;
- head and facial structural variants;
- species-specific appendages;
- age-related transforms;
- injury/state transforms;
- clothing layers;
- equipment attachment points.

The goal is to obtain a very large phenotype space from a tractable number of modules.

The visible result must be judged **after final raster treatment**, not from raw geometry alone.

### Animation

Animation should favor systemic reuse:

- shared base locomotion by skeleton family;
- speed and stride adaptation;
- additive posture layers;
- procedural aim/look direction;
- inverse kinematics where useful;
- injury/fatigue/age modifiers;
- behavioral animation modifiers;
- weapon-dependent overrides rather than wholly separate animation libraries.

Continuous motion is mandatory. Pixel presentation must not imply frame-by-frame or turn-stepped locomotion.

### Materials and final image formation

The next spike should prioritize final image formation over conventional PBR fidelity:

- deliberately low internal render resolution;
- limited or controlled palette;
- palette quantization by luminance/material family;
- ordered dithering where it improves tonal richness;
- hard value grouping for readability;
- restrained silhouettes/edge treatment;
- dynamic lights calculated before raster reduction;
- low-resolution particles and atmospheric effects;
- procedural blood, wetness, dirt, frost, wear, and state masks where readable at gameplay scale;
- nearest-neighbor scaling to the display resolution.

The target is not nostalgic pixel art by default. The target is a coherent modern pixel-rendered language that can support the game's adult tone and systemic world.

### World

The environment should derive richness from composition and state rather than asset count:

- modular architecture;
- procedural terrain and settlement composition;
- vegetation families with controlled variation;
- dynamic weather and lighting;
- persistent or semi-persistent evidence of events;
- simulation-driven settlement condition and resource use.

The next spike must determine whether low-resolution final rasterization can make economical geometry visually convincing without exposing generic primitive construction.

## Camera

The baseline gameplay camera is **locked as a high oblique top-down camera**, chosen specifically to balance tactical readability, character readability, free movement, verticality, and an AI-manageable production pipeline.

### Locked camera principles

- The camera is elevated and strongly top-down, but **not vertical**.
- The viewing axis should descend at approximately **60–70° relative to the horizontal ground plane** (roughly 20–30° away from a purely vertical top-down view). The exact value may be tuned inside this band during the visual spike.
- The camera must show the character's full body clearly enough for posture, equipment, weapon state, injuries, and animation to remain readable.
- Movement is continuous and free in **360°**, not grid-stepped and not simulated turn-by-turn movement.
- The presentation is **not constrained to a rigid 2:1 isometric projection**.
- The camera must preserve useful visibility of walls, doors, props, elevation changes, and vertical structures.
- Character facing, locomotion direction, torso orientation, look direction, and weapon aim may be partially independent.
- The camera is a production constraint: character and environment assets must be designed for this actual gameplay projection rather than generated in unrelated front/profile/catalog views.

### Still to tune

The following remain implementation parameters rather than art-direction reversals:

- exact pitch within the 60–70° target band;
- field of view / orthographic-vs-perspective evaluation if needed by the spike;
- camera distance and zoom limits;
- azimuth and whether any rotation is exposed to the player;
- occlusion handling for walls and tall objects;
- camera follow damping and combat framing.

Any change to these parameters must preserve the locked high-oblique top-down gameplay language rather than drifting toward a conventional isometric ARPG camera or a nearly vertical overhead view.

## Decision gate

The final art direction must not be selected from concept art or technical architecture alone.

The next valid test is deliberately narrow before rebuilding the larger production spike.

### Immediate proof required

Produce one representative gameplay-camera scene containing only:

1. one protagonist with a distinctive silhouette and readable equipment;
2. one small environment composition;
3. continuous locomotion and rotation;
4. one dynamic light source and shadow response;
5. final low-resolution raster / palette / dithering treatment.

The test passes only if the resulting **final gameplay image** is visually convincing enough to justify expanding the pipeline.

If it passes, only then expand the proof to:

1. several visibly different individuals generated from the same family;
2. at least two equipment states;
3. one non-human body-family test;
4. lighting/weather variation;
5. systemic visual-state variation;
6. a representative gameplay capture under load.

The spike must demonstrate that ChatGPT can reproduce and extend the assets without manual art intervention from the user or an external artist.

## Current decision

**Locked:** the visual direction must be producible, maintainable, and extensible end-to-end by ChatGPT without requiring the user to create art or requiring hired artists.

**Locked:** the baseline gameplay camera is high oblique top-down, approximately 60–70° relative to the ground plane, with continuous 360° movement and no rigid isometric projection requirement.

**Rejected as final visible art:** direct presentation of simple procedural runtime primitives / generic low-poly geometry, even with flat shading, outlines, hatching, fog, or sophisticated lighting.

**Preferred aesthetic direction:** stylized, mature, atmospheric, systemic, and intentionally non-photorealistic.

**Next production hypothesis to prove:** pixel-rendered systemic 3D — continuous modular 3D animation rendered at deliberately low resolution with palette quantization, dithering, controlled edges, and dynamic low-resolution lighting.

**Not yet locked:** the final aesthetic itself. No production art direction is approved until the next visual spike demonstrates acceptable final gameplay quality.