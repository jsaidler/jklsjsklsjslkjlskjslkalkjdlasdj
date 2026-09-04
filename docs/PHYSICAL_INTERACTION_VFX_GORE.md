# Physical Interaction, VFX, Gore and Body-State Pipeline — Living Plan

Status: **canonical planning document.** Wind, liquids, gore, environmental interaction, dynamic lighting and optional unclothed body states are architectural requirements, not post-production decorations. They must be represented in the deterministic rig/material/mask pipeline before broad character content production.

## Core principle

The hidden 3D/physics layer may calculate motion, collision, attachment and simulation, while the final game still renders intentional native-grid pixel art.

The project must distinguish:

1. **physical/source simulation** — deterministic geometry, forces, contacts, fluids, particles, cloth/hair motion;
2. **pixel representation** — palette bands, sprite layers, pixel VFX, masks and runtime composition.

A physically plausible Blender render is not automatically accepted as visible game art.

## Wind architecture

Blender force fields can affect cloth, particles, soft bodies and related secondary systems. Wind is therefore useful as a deterministic production/reference source.

Persistent wind-sensitive structures:

- Exilada hair large masses;
- loose cloth strips;
- capes, banners and flags;
- foliage/grass;
- dust, sparks and lightweight debris;
- smoke/fire flow references.

### Character wind

Do not model the Exilada's hair as thousands of strands. Use persistent large rigged masses / curves / secondary bones that preserve her silhouette.

The system must support a wind vector and strength parameter. Because the final game is sprite-based, do **not** assume arbitrary continuous 3D wind can simply be rendered at runtime.

Preferred scalable strategy to validate:

- body/base motion remains one canonical animation;
- major hair/cloth systems are exported as separate depth-aware pixel layers where possible;
- a small discrete family of wind-response states is generated automatically (for example calm / light / strong and a limited set of screen-relative directions);
- runtime selects/interpolates only where interpolation preserves pixel clusters;
- if layer deformation damages pixel quality, select discrete atlas states rather than smooth bitmap warping.

This avoids multiplying every full-body animation by every wind condition where separate layers are sufficient.

### Environment wind

Environment elements may use runtime procedural motion directly when the visible geometry is simple enough:

- grass/foliage sway;
- banners;
- rain direction;
- dust/snow particle drift;
- smoke direction.

The game simulation provides a causal wind vector; visual systems consume the same state.

## Liquids — environment

Blender's fluid system supports liquid domains and FLIP/APIC methods and can be scripted/baked as a production/reference tool.

However, arbitrary gameplay water should not require an offline Blender bake for every interaction.

Use Blender for:

- reference motion;
- splash/impact atlas generation;
- waterfall/wave studies;
- hero/cinematic or repeated deterministic effects;
- deriving pixel VFX shapes and timing.

Use runtime 2D/systemic effects for ordinary gameplay:

- rain;
- puddles;
- shallow-water ripples;
- water-entry/exit splashes;
- footsteps in water;
- drips;
- small wave propagation;
- wet decals/ground masks.

Potential runtime representation:

- 2D height-field / wave state for surfaces where needed;
- contact-event driven splash emitters;
- pixel-particle systems with discrete palette ramps;
- depth/occlusion masks from the world renderer.

The exact runtime fluid solver is a game-engine decision and is not delegated to Blender.

## Liquids — characters

Character-related fluids include:

- blood;
- water/wetness;
- mud;
- sweat where visually relevant;
- poison/acid/other systemic liquids if introduced later.

Separate **surface state** from **free fluid motion**.

### Surface state

Persistent semantic/body/material masks support:

- wet skin/cloth palette changes;
- blood staining by anatomical region;
- mud/dirt accumulation;
- dried/fresh blood state;
- washed-off state;
- interaction with rain/water.

This should not require redrawing each animation.

### Free liquid motion

Blood spray, splashes and drips are event-driven VFX with known origins, velocities and collision context.

Blender may be used to author/reference complex effect families, but runtime pixel particles/decals are the preferred scalable representation for ordinary combat.

## Gore — LOCKED AS A PRODUCTION REQUIREMENT

The game is allowed to be physically violent; gore must be architected, not improvised as random image generation.

### Body topology for gore

The production body rig should be built with **named anatomical damage/sever zones** from the start.

Initial deterministic zones may include:

- neck/head;
- upper/lower arms;
- hands where useful;
- upper/lower legs;
- torso regions only where gameplay justifies them.

Do not begin with arbitrary real-time mesh slicing. Constrained anatomical zones are more controllable, readable and scalable for pixel art.

### Dismemberment model

When a sever event occurs:

1. canonical body part is hidden/disabled at a known cut boundary;
2. a persistent wound-cap/gore socket becomes visible;
3. detached limb/head becomes a separate rigid/animated object using the same material/body identity;
4. blood emitter is spawned from the named wound socket;
5. detached part receives inherited velocity/angular velocity and world collision;
6. blood decals/pools may accumulate on world surfaces;
7. state persists according to gameplay rules.

This guarantees that a severed limb is the correct limb and that clothing/equipment attached to it can follow deterministic rules.

### Pixel representation of gore

Visible gore uses the same native-grid principles:

- discrete blood palette;
- large readable shapes before droplets;
- deterministic wound-cap shapes by cut zone;
- event-driven sprays/arcs;
- pixel particles for droplets/chunks;
- ground/body decals;
- no smooth high-resolution fluid render simply downsampled.

### Gore QA

Automated/structural checks should verify:

- removed part no longer appears on base body;
- detached part identity matches removed region;
- wound socket is attached to correct anatomical side;
- blood emitter origin matches wound;
- no duplicated limb remains;
- equipment attached to severed part follows the intended rule;
- gore layers respect depth/occlusion.

## Death / fall / recovery motion

Gore depends on good physical motion sources.

The animation library should include or derive:

- hit reactions by direction/force;
- knockback;
- stumble;
- falls forward/back/side;
- collapse;
- ground reactions;
- attempts to rise;
- get-up from back/front/side;
- wounded/limping locomotion;
- death motions.

Where a library lacks a precise transition, deterministic blending/IK/physics can bridge motions, but final gameplay motion is still QA'd as a sequence.

## Dynamic lighting opportunity

The hidden 3D pipeline can provide per-frame metadata such as:

- normals;
- material IDs;
- depth;
- body-part IDs;
- world position / approximate light response;
- occlusion/shadow reference.

The final game should **not** apply smooth photoreal shading directly to pixel sprites.

Preferred runtime lighting strategy:

`light state + hidden normal/material metadata -> discrete palette-band/LUT selection`

Examples:

- skin has a small number of light bands;
- cloth/metal/hair use different ramps;
- point lights can push pixels/parts between discrete bands;
- rim/light effects use thresholded pixel masks;
- weather/day-night modifies palette ramps rather than applying arbitrary smooth gradients.

This preserves pixel-art structure while enabling dynamic lighting.

## Particles and environmental VFX

Blender provides useful simulation/reference tools for particles, force fields and custom Geometry Nodes simulations, but runtime effects must remain scalable.

Candidate systems:

- dust;
- sparks;
- debris;
- smoke;
- fire;
- embers;
- rain/snow;
- blood;
- water splashes;
- weapon trails;
- insects/flocks where useful;
- magical effects.

Preferred workflow:

`Blender/reference simulation -> pixel VFX rule/atlas/parameters -> runtime particle system`

Only special deterministic effects that genuinely benefit from offline simulation are pre-baked.

## Nude/unclothed body states — PIPELINE SUPPORT REQUIRED

The production rig must own a complete persistent body **under clothing**, because clothing is modular and can be removed, damaged or changed.

This requirement is independent of whether every unclothed state is ultimately shown in the game.

Important architectural consequence:

- body mesh and body material exist independently of clothing;
- clothing pieces are separate persistent meshes/material regions;
- removing clothing cannot reveal missing geometry or an arbitrary newly generated body;
- scars/injuries/body state remain attached to the body, not to clothes.

The project does **not** need to depend on generative image synthesis for the unclothed body.

A current candidate for the deterministic base-body layer is **MakeHuman / MPFB** or direct use of their core base assets. Their bundled graphical assets (base mesh, targets, skins and related core data) are published under CC0, and project output/models can be used commercially. Any third-party downloaded asset must be license-checked separately.

The base body can then be parametrically adjusted to the Exilada's approved adult proportions and rendered by the same native-pixel pipeline with or without clothing.

Whether explicit anatomical detail is visually required is a later art-direction decision. The pipeline must not make clothing technically mandatory.

This also avoids depending on any limitations of an image-generation service for nude imagery: the production asset is deterministic local geometry/material data, not a newly generated nude reference image.

## New validation gates added to the character pipeline

These capabilities must be tested before large content multiplication.

### G6A — wind/secondary motion

Test hair/cloth with calm + wind state on one motion.

PASS requires:

- deterministic repeatability;
- no side swapping;
- no unacceptable pixel deformation;
- reasonable modularity without full animation×wind combinatorial explosion.

### G6B — liquid/contact VFX

Test one water splash + wetness state and one blood impact.

PASS requires:

- correct contact origin;
- depth-aware composition;
- pixel-consistent VFX;
- reusable event-driven architecture.

### G6C — gore topology

Test one deterministic sever zone on a generic proxy before Exilada gore content is authored.

PASS requires:

- correct body removal;
- detached part;
- wound socket;
- blood emitter;
- collision/depth behavior;
- no duplicated topology.

### G7 — dynamic state/lighting

Extend existing systemic-state gate to include:

- wetness;
- blood/dirt;
- one dynamic light direction/intensity change;
- wind-driven environmental state.

All must preserve native pixel readability.

## Kill switches

- If wind requires manually repairing hair/cloth frames, reject that wind representation.
- If liquid physics requires per-event offline baking, replace it with runtime 2D VFX for ordinary gameplay.
- If modular gore causes sprite-combination explosion, simplify to fixed sever zones/layers before expanding content.
- If dynamic lighting produces smooth/dirty pixel gradients, reduce it to discrete material/palette-band logic.
- If unclothed body support requires per-frame generative reconstruction, reject that implementation; body geometry must be persistent.
