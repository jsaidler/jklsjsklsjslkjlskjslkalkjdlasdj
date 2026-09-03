# Visual Direction — Living Document

Status: **production constraints and baseline gameplay camera locked; final aesthetic pending visual spike**

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

### Prefer

- **Stylized rather than realistic rendering.** Stylization is a production strategy as well as an aesthetic choice: it must reduce authoring burden while preserving a strong, adult visual identity.
- Systemic stylized 3D built from modular and parametric geometry.
- Strong silhouettes and readable proportions.
- Low-to-moderate geometric complexity.
- Reusable skeleton families rather than one skeleton per creature.
- Procedural body proportion changes within controlled anatomical rules.
- Equipment assembled from modular parts and attachment points.
- Vertex colors, palettes, compact texture atlases, procedural masks, and shader-driven material variation.
- Animation built from reusable clips plus procedural posing, additive layers, IK, gait parameters, and behavioral state.
- Environmental assets constructed from modular kits and procedural composition.
- Lighting, atmosphere, weather, particles, material response, and world state as major sources of visual richness.
- Visual systems in which code and simulation create richness that would otherwise require large quantities of manually authored art.

## Working direction

The strongest candidate is currently **systemic stylized 3D**.

The intended formula is:

> simple geometry + strong silhouette + economical materials + sophisticated lighting + expressive motion + systemic variation

"Low poly" is not itself the desired aesthetic. Polygon economy is a production technique. The final identity must not resemble generic asset-store low-poly art.

The target should be visually mature and atmospheric rather than cute, toy-like, or dependent on photorealism.

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

The goal is to obtain a very large phenotype space from a tractable number of primitives and modules.

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

### Materials

Materials should favor reproducibility and runtime variation:

- palette-driven base colors;
- vertex color masks;
- procedural wear/dirt/blood/wetness/frost masks;
- small reusable texture sets where texture information is genuinely needed;
- shader-driven surface differentiation.

### World

The environment should derive richness from composition and state rather than asset count:

- modular architecture;
- procedural terrain and settlement composition;
- vegetation families with controlled variation;
- dynamic weather and lighting;
- persistent or semi-persistent evidence of events;
- simulation-driven settlement condition and resource use.

## Camera

The baseline gameplay camera is now **locked as a high oblique top-down camera**, chosen specifically to balance tactical readability, character readability, free movement, verticality, and an AI-manageable production pipeline.

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

The final art direction must not be selected from concept art alone.

Before locking it, we must produce a small **visual production spike** containing at minimum:

1. one humanoid generated from the intended modular character pipeline;
2. several visibly different individuals generated from the same family;
3. at least two equipment states;
4. one non-human body-family test;
5. one small environment tile/scene;
6. lighting/weather variation of the same scene;
7. basic locomotion or procedural pose test;
8. a representative gameplay-camera capture using the locked high-oblique top-down camera.

The spike must also demonstrate that ChatGPT can reproduce and extend the assets without manual art intervention from the user or an external artist.

Only visual languages that survive this test with an acceptably small authoring burden are valid candidates.

## Current decision

**Locked:** the visual direction must be producible, maintainable, and extensible end-to-end by ChatGPT without requiring the user to create art or requiring hired artists.

**Locked:** the baseline gameplay camera is high oblique top-down, approximately 60–70° relative to the ground plane, with continuous 360° movement and no rigid isometric projection requirement.

**Preferred aesthetic direction:** stylized, mature, atmospheric, systemic, and intentionally non-photorealistic unless a future spike demonstrates that a more realistic treatment is equally maintainable by the solo AI pipeline.

**Leading production architecture:** systemic stylized 3D using modular/parametric geometry, reusable rigs, procedural posing, economical materials, and simulation-driven visible state.

**Not yet locked:** exact character proportions, palette, surface treatment, degree of geometric abstraction, precise camera FOV/distance, and final material/shader language.
