# Visual Direction — Living Document

Status: **modern pixel art and baseline gameplay camera locked; production execution still under validation**

## Core production constraint

The project is developed end-to-end by ChatGPT, with the user directing and approving decisions.

The user will **not produce game art manually and will not hire external artists**. Therefore the complete production visual pipeline — characters, creatures, environments, animation, effects, variation, maintenance, and future expansion — must be executable by ChatGPT and project tooling without depending on a conventional art team or bespoke manual artwork supplied by the user.

This is a hard design constraint.

A visual direction is invalid if it can produce an attractive isolated concept but cannot be reproduced, animated, varied, maintained, and expanded by the same production pipeline used to build the game.

## Locked final visual language: modern pixel art

The game uses **modern pixel art as an actual image-making language**, not a simulated pixel texture applied to another rendering style.

### This means

- Characters and environments must be designed for pixel-art readability from the beginning.
- Pixel clusters, silhouette, value grouping, palette, edge treatment and animation readability are primary design concerns.
- The final image must not read as painted or generated artwork that was subsequently downscaled, quantized, sharpened or covered with a pixel filter.
- The final image must not read as conventional 3D rendered at low resolution and disguised as pixel art.
- Pixel density and detail must be intentional and coherent at gameplay scale.
- The style may be detailed and contemporary, but detail must remain organized into readable pixel structures rather than noisy microtexture.
- Controlled palettes, clean clusters and strong silhouettes are preferred over decorative dithering or texture for its own sake.
- The target is mature, severe, atmospheric and systemic rather than nostalgic, cute or cartoonish.

### Explicitly rejected as final visible art

- simple procedural primitives or generic low-poly geometry presented directly;
- the same geometry hidden behind outlines, hatching, fog or more sophisticated shaders;
- conventional rendered imagery with a pixelation/post-process filter;
- AI-looking painterly imagery merely reduced to a coarse raster;
- fake pixel-art texture that does not survive inspection as coherent pixel construction;
- large libraries of hand-painted frame-by-frame sprites that require manual art labor from the user;
- production approaches that require manual frame repair as their normal mode of operation.

The previously documented **pixel-rendered systemic 3D** hypothesis is therefore superseded as the target aesthetic. 3D or procedural geometry may still be useful internally for blockout, collision, navigation, pose generation, lighting reference or hidden production tooling, but it is not the visible art direction.

## Character pixel-art principles

Characters must be identifiable first through **silhouette, large masses, posture and controlled contrast**, then through secondary detail.

At gameplay scale:

- hair masses, body proportions, clothing asymmetry and large equipment shapes must remain readable;
- facial microdetail cannot carry identity by itself;
- weapons are gameplay-variable equipment and must not be treated as permanent identity anchors unless a specific character design explicitly requires it;
- clothing and equipment may evolve without erasing the character's underlying body, hair and posture identity;
- anatomy remains adult and materially grounded;
- exposed skin or nudity may be used when narratively and materially appropriate, without forcing erotic framing;
- dirt, wounds, blood, scars and wear should preferably express actual simulated history or state rather than arbitrary decoration.

The protagonist-specific rules are maintained in `docs/CHARACTERS.md`.

## Systemic visual rule

Whenever feasible, visually relevant state must be represented as a consequence of simulation rather than random decoration.

Examples:

- scars should preferably reflect survived injuries or history;
- equipment wear should reflect use and material condition;
- population clothing and equipment should reflect available resources, culture, climate, trade and conflict;
- looted equipment may visually propagate between factions after warfare;
- hunger, disease, age, fatigue, status, occupation and injuries may affect silhouette, posture, animation, material condition or clothing;
- blood, dirt, wetness, burns, frost and other transient states should correspond to gameplay or environmental causes.

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

The final visible output must still satisfy the locked pixel-art language. Production efficiency does not excuse generic forms or incoherent pixels.

## Character animation direction

The current production path uses **Sprite Sheet Diffusion (SSD)** driven by deterministic pose sequences and a canonical character reference.

The objective is not to ask an image generator to invent independent frames. The canonical reference anchors identity while deterministic skeletal poses define motion. Generated sequences are accepted only when temporal consistency and pixel-art readability survive actual gameplay-scale inspection.

Full technical details live in `docs/ANIMATION_PIPELINE.md`.

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

- The camera is elevated and strongly top-down, but **not vertical**.
- The viewing axis should descend at approximately **60–70° relative to the horizontal ground plane** (roughly 20–30° away from a purely vertical top-down view).
- The camera must show enough of the character's full body for posture, equipment, injuries and animation to remain readable.
- Movement is continuous and free in **360°**, not grid-stepped.
- The presentation is **not constrained to a rigid 2:1 isometric projection**.
- Walls, doors, props, elevation changes and vertical structures must remain legible.
- Character facing, locomotion direction, torso orientation, look direction and weapon aim may be partially independent.
- Character and environment assets must be designed for this actual gameplay projection rather than unrelated front/profile/catalog views.

### Still to tune

- exact pitch within the 60–70° target band;
- orthographic versus perspective implementation if needed;
- camera distance and zoom limits;
- azimuth and whether player-controlled rotation exists;
- occlusion handling for walls and tall objects;
- follow damping and combat framing.

Any tuning must preserve the locked high-oblique top-down gameplay language.

## Visual validation gate

Artwork is not approved because a character sheet or concept is attractive. Production art must be judged at actual game scale and in motion.

A representative validation sequence must demonstrate:

1. one protagonist with a distinctive silhouette at gameplay scale;
2. coherent modern pixel-art construction rather than post-processed illustration;
3. continuous readable locomotion and rotation/facing changes;
4. at least one small representative environment composition;
5. dynamic state such as light, injury, dirt, blood, weather or equipment without destroying pixel clarity;
6. reproducibility through the project pipeline without manual frame-by-frame repainting.

## Current decision

**Locked:** modern pixel art is the final visual language.

**Locked:** pixel art must be native to the design and final image, not a texture/filter applied to AI illustration, 3D rendering or generic low-poly art.

**Locked:** stylized, mature, severe, atmospheric and systemic presentation.

**Locked:** gameplay camera is high oblique top-down, approximately 60–70° relative to the ground plane, with continuous 360° movement and no rigid isometric requirement.

**Locked:** visually relevant character/world state should be causal whenever feasible.

**Locked:** character production must remain scalable without manual art labor from the user or hired artists.

**Current character-animation path:** canonical pixel-art reference + deterministic pose driving + Sprite Sheet Diffusion + automated post-processing + gameplay-scale validation.

**Still under validation:** whether the complete SSD-based production chain can preserve the approved modern pixel-art character identity across all required animations, directions, equipment states and character families.