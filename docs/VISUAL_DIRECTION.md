# Visual Direction — Living Document

Status: **production constraints locked; final aesthetic pending visual spike**

## Core production constraint

The project is developed end-to-end by ChatGPT with the user directing and approving decisions. Therefore the visual language must be achievable, maintainable, and extensible through code, procedural generation, generated source imagery, shaders, parametric geometry, reusable rigs, and data-driven composition.

The project must not depend on a conventional external art team or on a pipeline that requires large quantities of bespoke manual assets.

This is not merely a budget constraint. It is a design constraint and must inform every visual-system decision.

## Consequences

### Avoid as foundational pipelines

- High-detail realistic or semi-realistic 3D requiring manual sculpting and retopology per creature.
- Large libraries of hand-painted character sprites.
- Frame-by-frame animation as the main animation system.
- Unique rigs and bespoke animation sets for every species.
- Visual variation that requires producing a new complete asset for every equipment, body, age, culture, mutation, or state combination.
- Photorealistic materials whose quality depends on large hand-authored texture sets.
- A visual identity dependent on illustration quality that cannot be reproduced systematically in runtime assets.

### Prefer

- Stylized 3D built from modular and parametric geometry.
- Strong silhouettes and readable proportions.
- Low-to-moderate geometric complexity.
- Reusable skeleton families rather than one skeleton per creature.
- Procedural body proportion changes within controlled anatomical rules.
- Equipment assembled from modular parts and attachment points.
- Vertex colors, palettes, compact texture atlases, procedural masks, and shader-driven material variation.
- Animation built from reusable clips plus procedural posing, additive layers, IK, gait parameters, and behavioral state.
- Environmental assets constructed from modular kits and procedural composition.
- Lighting, atmosphere, weather, particles, material response, and world state as major sources of visual richness.

## Working direction

The strongest candidate is currently **systemic stylized 3D**.

The intended formula is:

> simple geometry + strong silhouette + economical materials + sophisticated lighting + expressive motion + systemic variation

"Low poly" is not itself the desired aesthetic. Polygon economy is a production technique. The final identity must not resemble generic asset-store low-poly art.

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

An elevated 3D perspective remains the leading candidate because it supports tactical readability, large groups, verticality, modular world construction, and systemic variation without sprite explosion.

The exact camera pitch, field of view, rotation policy, zoom limits, and occlusion strategy are **not locked** yet.

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
8. a representative gameplay-camera capture.

Only visual languages that survive this test with an acceptably small authoring burden are valid candidates.

## Current decision

**Locked:** the visual direction must be producible and extensible end-to-end by the project's AI-driven development pipeline.

**Leading candidate:** systemic stylized 3D using modular/parametric geometry, reusable rigs, procedural posing, economical materials, and simulation-driven visible state.

**Not yet locked:** exact aesthetic, proportions, palette, surface treatment, camera specification, and degree of geometric abstraction.
