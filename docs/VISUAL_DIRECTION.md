# Visual Direction — Living Document

Status: **modern pixel art remains the final gameplay target; the current Exilada master is reclassified as a high-detail canonical design/identity reference rather than proof of final pixel-art construction. Production execution is still under validation.**

## Process rule — living documentation

All material visual-direction decisions, pipeline changes, accepted/rejected approaches and current validation state must be recorded in this document or the relevant linked canonical document as they occur. These documents are the project memory across chats. When a decision changes, edit the existing canonical document rather than creating parallel versions.

## Core production constraint

The project is developed end-to-end by ChatGPT, with the user directing and approving decisions.

The user will **not produce game art manually and will not hire external artists**. Therefore the complete production visual pipeline — characters, creatures, environments, animation, effects, variation, maintenance and future expansion — must be executable by ChatGPT and project tooling without depending on a conventional art team or bespoke manual frame work.

A visual direction is invalid if it can produce an attractive isolated concept but cannot be reproduced, animated, varied, maintained and expanded by the same production pipeline used to build the game.

## Locked final visual language: modern pixel art

The final game should use **modern pixel art as an actual image-making language**, not merely a pixel texture or post-process applied to another rendering style.

At production gameplay scale this means:

- pixel clusters, silhouette, value grouping, palette, edge treatment and animation readability are primary design concerns;
- the final image should not read as conventional painted/3D imagery simply downsampled, quantized or covered with a pixel filter;
- pixel density and detail must be intentional and coherent at gameplay scale;
- the style may be detailed and contemporary, but detail must remain organized into readable raster structures rather than noisy microtexture;
- controlled palettes, clean clusters and strong silhouettes are preferred over decorative texture for its own sake;
- the target is mature, severe, atmospheric and systemic rather than nostalgic, cute or cartoonish.

### Important clarification: design reference versus production sprite

The current `exilada_master.png` is **more detailed than a strict production pixel-art sprite should be**. It remains approved because it successfully defines the Exilada's identity, proportions, face, hair mass, clothing state, restraint markers and overall visual character.

It must therefore be treated as a **high-detail canonical design/identity reference**, not as evidence that its current raster density is already the final gameplay pixel-art solution.

Consequences:

- a pose/model test should be judged against the source it was given; reproducing the reference's high-detail look is not, by itself, a model failure;
- final pixel-art compliance is a separate production problem that must be solved downstream at actual gameplay scale;
- the project still requires an automatic/scalable method to derive the final production-raster representation from the approved design without manual frame repainting;
- the source design should not be redesigned merely to make a particular animation model look better.

### Explicitly rejected as final visible art

- simple procedural primitives or generic low-poly geometry presented directly;
- the same geometry hidden behind outlines, hatching, fog or more sophisticated shaders;
- conventional rendered imagery with a superficial pixelation/post-process filter as the final solution;
- fake pixel texture that does not survive inspection as coherent gameplay-scale raster construction;
- large libraries of hand-painted frame-by-frame sprites requiring manual art labor from the user;
- production approaches that require routine manual frame repair.

3D or procedural geometry may still be useful internally for blockout, collision, navigation, pose generation, lighting reference or hidden production tooling, but it is not the locked visible art direction.

## Character visual principles

Characters must be identifiable first through **silhouette, large masses, posture and controlled contrast**, then through secondary detail.

At gameplay scale:

- hair masses, body proportions, clothing asymmetry and large equipment shapes must remain readable;
- facial microdetail cannot carry identity by itself;
- weapons are gameplay-variable equipment and must not be treated as permanent identity anchors unless a specific character design explicitly requires it;
- clothing and equipment may evolve without erasing the character's underlying body, hair and posture identity;
- anatomy remains adult and materially grounded;
- exposed skin or nudity may be used when narratively and materially appropriate, without forcing erotic framing;
- dirt, wounds, blood, scars and wear should preferably express actual simulated history/state rather than arbitrary decoration.

The protagonist-specific rules live in `docs/CHARACTERS.md`.

## Systemic visual rule

Whenever feasible, visually relevant state must be represented as a consequence of simulation rather than random decoration.

Examples:

- scars should preferably reflect survived injuries or history;
- equipment wear should reflect use and material condition;
- population clothing and equipment should reflect available resources, culture, climate, trade and conflict;
- looted equipment may visually propagate between factions after warfare;
- hunger, disease, age, fatigue, status, occupation and injuries may affect silhouette, posture, animation, material condition or clothing;
- blood, dirt, wetness, burns, frost and other transient states should correspond to gameplay/environmental causes.

Procedural variation must therefore be **causal and constrained**, not arbitrary noise.

## Character production architecture

The project should obtain broad character variation from tractable systems rather than bespoke manual drawing for every individual.

Useful controlled parameters may include:

- height;
- limb and torso proportions;
- mass/volume;
- posture;
- head and facial structure;
- hair families;
- age-related transforms;
- injury/state transforms;
- clothing layers;
- equipment states;
- species-specific anatomy where relevant.

The final visible output must still satisfy the locked gameplay raster language. Production efficiency does not excuse generic forms or incoherent pixels.

## Character animation direction

The previous Sprite Sheet Diffusion and Wan-Animate-2 routes were tested and rejected. They are no longer current production paths.

The active animation research path is documented in `docs/ANIMATION_PIPELINE.md` and currently tests:

`canonical high-detail design reference + explicit deterministic COCO-18 key poses + FLUX.2 Klein Base 4B FP8 + RefControl Pose`

This current spike is intentionally limited to **four static key poses**. Its first gate is identity/anatomy/pose adherence, not final gameplay pixel-art compliance.

If the pose renderer passes, the project must then solve the **production-raster translation** problem explicitly before choosing temporal completion/inbetweening.

## Environment direction

The environment should derive richness from composition, state and systemic consequence rather than an excessive number of one-off assets.

Preferred structure:

- modular architecture;
- procedural terrain and settlement composition;
- vegetation families with controlled variation;
- dynamic weather and lighting;
- persistent or semi-persistent evidence of events;
- simulation-driven settlement condition and resource use;
- pixel-art materials and shapes designed to remain readable under the actual gameplay camera.

## Camera

The baseline gameplay camera is **locked as a high oblique top-down camera**, chosen to balance tactical readability, character readability, free movement, verticality and production feasibility.

### Locked camera principles

- elevated and strongly top-down, but **not vertical**;
- viewing axis approximately **60–70° relative to the horizontal ground plane** (roughly 20–30° away from pure vertical top-down);
- enough of the character's full body must remain visible for posture, equipment, injuries and animation to read;
- movement is continuous and free in **360°**, not grid-stepped;
- presentation is **not constrained to rigid 2:1 isometric projection**;
- walls, doors, props, elevation changes and vertical structures must remain legible;
- character facing, locomotion direction, torso orientation, look direction and weapon aim may be partially independent;
- character/environment assets must be designed for this gameplay projection rather than unrelated front/profile/catalog views.

### Still to tune

- exact pitch within the 60–70° band;
- orthographic versus perspective implementation if needed;
- camera distance and zoom limits;
- azimuth and whether player-controlled rotation exists;
- occlusion handling for walls and tall objects;
- follow damping and combat framing.

Any tuning must preserve the locked high-oblique top-down gameplay language.

## Visual validation gate

Artwork is not approved because a concept or character sheet is attractive. Production art must be judged at actual game scale and in motion.

A representative validation sequence must eventually demonstrate:

1. one protagonist with a distinctive silhouette at gameplay scale;
2. a deliberate modern pixel-art production raster, not merely high-detail concept art;
3. continuous readable locomotion and rotation/facing changes;
4. at least one representative environment composition;
5. dynamic state such as light, injury, dirt, blood, weather or equipment without destroying readability;
6. reproducibility through project tooling without manual frame-by-frame repainting.

The current FLUX + RefControl key-pose spike does **not** need to prove item 2 by itself; it is an earlier structural gate focused on preserving the approved design while obeying explicit pose control.

## Current decision

**Locked:** modern pixel art remains the final gameplay visual language.

**Locked:** the current Exilada master is the canonical design/identity reference, but is too detailed to be treated as the final production pixel-art master.

**Locked:** do not blame a pose model for faithfully reproducing detail already present in the source; model fidelity and final raster stylization are separate gates.

**Locked:** stylized, mature, severe, atmospheric and systemic presentation.

**Locked:** gameplay camera is high oblique top-down, approximately 60–70° relative to the ground plane, with continuous 360° movement and no rigid isometric requirement.

**Locked:** visually relevant character/world state should be causal whenever feasible.

**Locked:** character production must remain scalable without manual art labor from the user or hired artists.

**Current character-animation path:** canonical Exilada design reference + four deterministic COCO-18 key poses + FLUX.2 Klein Base 4B FP8 + RefControl Pose, followed by a separate production-raster solution only if pose/identity control passes.
