# Pixel Art Production — Living Document

Status: **production pixel-art language is specified at a first actionable level; first direct image-generation attempt for the Exilada production pixel master was tested and rejected as a production asset.**

This document defines the production-raster rules that separate true modern pixel art from the project's higher-detail identity/concept references. It is canonical across chats and must be updated whenever pixel-art production rules change.

## Core distinction

The project uses two different character-reference layers:

1. **Identity master** — defines who the character is.
2. **Production pixel master** — defines how that character exists on the actual gameplay pixel grid.

For the Exilada, the current identity master remains:

`assets/source/characters/exilada/reference/exilada_master.png`

It is intentionally richer and more detailed than the final gameplay sprite. It must not be downscaled mechanically and called production pixel art.

The production route must instead reinterpret the locked identity on the target raster while preserving the character's essential form.

## Quality target

The target is **best-in-class modern pixel art**, not retro imitation for its own sake and not a high-resolution illustration with square pixels.

Quality is judged by:

- deliberate clusters rather than noisy per-pixel texture;
- strong silhouette at native size;
- controlled value grouping;
- economy of detail;
- readable anatomy and action;
- coherent material separation;
- intentional edge treatment;
- animation readability;
- consistency across characters, equipment, states and environments.

Modern pixel-art games such as *Children of Morta*, *Blasphemous*, *Eastward* and *Sea of Stars* are useful quality references for discipline, clarity and authored raster structure, but the project is not to copy any one game's style.

## Native gameplay raster — first locked target

### Internal rendering grid

Initial target:

**640 × 360 native gameplay pixels**

Rationale:

- exact 3× integer scale to 1920 × 1080;
- exact 4× integer scale to 2560 × 1440;
- enough tactical field of view for a high-oblique roguelite;
- still coarse enough that individual pixel decisions remain visible and meaningful.

This resolution may only change after an actual gameplay-camera composition test. It must not drift casually because the chosen grid controls sprite scale, environment density and camera readability.

### Exilada gameplay body height

Initial target:

**64 native pixels from highest visible hair mass to lowest grounded foot pixel in a neutral standing pose at gameplay projection.**

Acceptable tuning band during the first composition spike:

**56–72 px**, but 64 px is the canonical starting point.

The target is not a 64×64 boxed character. The *body/silhouette* is approximately 64 px high; action canvases may be larger.

Reasoning:

- 32 px is too restrictive for the Exilada's mature anatomy, hair mass, minimal clothing and restraint markers at the requested quality level;
- 96–128+ px invites portrait/illustration-level microdetail and substantially increases animation instability and production cost;
- ~64 px forces readable pixel-art decisions while retaining enough information for a distinctive adult protagonist.

## Sprite canvas conventions

Canonical starting canvases:

- idle / locomotion: **96 × 96 px**;
- ordinary melee/action frames: **128 × 128 px**;
- exceptional VFX-heavy or wide-action frames may use larger logical bounds, but the character itself must retain the same pixel density and world scale.

Rules:

- do not rescale a character inside its canvas from frame to frame;
- preserve one common ground-contact convention;
- preserve stable pivot/origin metadata;
- empty transparent margin is allowed and preferable to changing character scale;
- no fractional runtime scaling for the production sprite layer.

## Gameplay projection

The production pixel master must be designed for the actual locked camera family:

- high-oblique top-down;
- approximately 60–70° viewing axis relative to the horizontal ground plane;
- not vertical top-down;
- not rigid 2:1 isometric projection.

The production master is therefore **not** primarily a frontal catalogue portrait.

The existing high-detail identity master remains useful for face/body identity, while the production reference pack must explicitly show how the character reads from gameplay-facing directions.

## Exilada production reference pack — required deliverables

The production pixel master is a **reference pack**, not one oversized illustration.

Required canonical set before animation approval:

### A. Eight-direction neutral turntable

Eight gameplay-facing neutral poses:

- S
- SW
- W
- NW
- N
- NE
- E
- SE

Requirements:

- same world scale;
- same body proportions;
- same hair volume logic;
- same clothing/restraint state;
- no weapon;
- identical lighting assumption;
- fixed ground contact;
- no pose theatrics.

Purpose: prove that identity survives rotation and establish the correct source family for future directional animation.

### B. Silhouette sheet

The same eight views as flat one-color silhouettes.

Pass condition: the character should remain identifiable through the large black hair mass, compact adult body, asymmetric cloth masses and overall posture without interior detail.

### C. Material/value sheet

One representative gameplay view reduced to the major value/material groups only:

- hair;
- skin;
- cloth;
- restraint metal;
- deepest occlusion/shadow;
- selected highlights.

Purpose: prevent later generations from replacing structure with microtexture.

### D. Native-scale inspection strip

Every approved reference must be shown at:

- **1× native size**;
- 2× nearest-neighbor;
- 4× nearest-neighbor.

Approval is made first at **1×**. Enlarged versions are inspection aids only.

## Exilada — locked pixel-art identity anchors

At 64 px body height, the priority order is:

1. **hair mass** — primary silhouette anchor;
2. **adult compact body proportion**;
3. **severe / forward-alert posture**;
4. **skin-versus-hair value separation**;
5. **asymmetric minimal clothing masses**;
6. **bare feet / grounded stance**;
7. **broken-restraint markers**, when readable from the current direction;
8. facial detail.

Facial microdetail is explicitly last in gameplay priority. The Exilada must remain recognizable when the face is only a few pixels.

## Proportion rules

The sprite must remain recognizably adult and must not drift toward chibi proportions.

Starting rule:

- overall anatomical impression approximately **6.5–7 heads tall** before perspective compression;
- head may be enlarged only slightly for readability, approximately **5–8% over strict realistic projection**;
- hands and feet may receive modest pixel-scale exaggeration where needed for action readability;
- shoulders, pelvis and knees must remain clearly locatable during motion;
- limbs must retain enough separation to avoid merging into the torso at 1×.

Foreshortening from the high-oblique camera takes precedence over literal front-view ratios.

## Cluster rules

### Required

- connected pixel clusters should describe planes and forms;
- single-pixel decisions must have a visual function;
- large forms first, small accents last;
- internal detail must reinforce anatomy/material rather than create noise;
- clusters should remain stable enough that adjacent animation frames do not shimmer arbitrarily.

### Avoid

- random single-pixel speckling;
- high-frequency dirt/noise across every surface;
- pseudo-photographic skin texture;
- hair rendered as hundreds of isolated strands;
- dithering used as default shading;
- one-pixel decorative detail that disappears at 1×.

Dithering may be used selectively when it produces a deliberate material or atmospheric effect, not merely because an AI model generated texture.

## Palette and value rules

The project does not use a single tiny retro console palette, but character palettes must remain controlled.

Starting Exilada base target:

**approximately 24–32 visible sprite colors**, excluding transparency and temporary state overlays.

Suggested distribution, not a rigid per-frame quota:

- skin: 5–7 useful values/hues;
- hair: 4–5;
- cloth: 4–5;
- restraints/metal: 3–4;
- shared deepest shadows / accents / highlight bridges: remaining colors.

Rules:

- value structure matters more than exact color count;
- adjacent shades must be perceptually distinct at native scale;
- do not add near-duplicate colors merely to simulate smooth gradients;
- hair must remain the darkest dominant mass;
- skin, cloth and metal must separate immediately without outlines doing all the work;
- transient blood/dirt/wetness/frost should be implemented as controlled state palettes/overlays and not baked indiscriminately into the canonical clean master.

## Edge treatment

Use **selective contouring**, not a uniform black outline around every form.

Preferred:

- darkest contour around parts of the hair silhouette and high-contrast occlusions;
- local-color dark edges around skin and cloth where appropriate;
- broken/omitted contour where light or adjacency already separates forms;
- contour thickness generally one native pixel at this scale.

Avoid:

- continuous thick black sticker-outline;
- anti-aliased smooth edges;
- inconsistent pseudo-vector curves.

## Hair treatment

The Exilada's hair is the principal identity anchor and must be handled as **large designed masses**.

Rules:

- 3–6 principal locks/masses should control the outer silhouette in a given view;
- internal strand suggestion is secondary;
- use highlight clusters to imply volume, not strand-by-strand rendering;
- hair motion may simplify or merge internal shapes but should preserve the dominant outer mass;
- do not fill the hair with random checkerboard texture.

## Skin/anatomy treatment

At gameplay size:

- anatomy is communicated through value planes and contour changes;
- no pore/freckle-level texture;
- scars only survive if they are large enough to read or narratively important;
- breasts, abdomen, limbs and joints are treated materially rather than erotically;
- nudity/minimal clothing does not justify additional micro-detail;
- body readability and motion mechanics take priority over anatomical decoration.

## Cloth treatment

The initial cloth is intentionally minimal and degraded, but degradation must be graphically economical.

Rules:

- one major chest-wrap mass;
- one asymmetric hip/loincloth mass;
- a few deliberate torn contour breaks;
- one or two internal folds/value groups only where they improve volume;
- no dense fabric texture;
- fraying represented by controlled silhouette interruptions rather than pixel noise.

## Restraint treatment

Broken restraints are secondary but meaningful identity/history markers.

At native gameplay scale:

- cuff must read as a compact metal band with strong value separation;
- chain should use only as many links/pixels as remain legible;
- if a chain becomes unreadable in a particular facing direction, do not enlarge it unnaturally merely to preserve detail;
- the history of captivity is canonical, but readability has priority over literal hardware visibility in every frame.

## Lighting assumption for the canonical master

The production master should use **neutral readable baked form-light**, not a dramatic scene-specific light.

Starting assumption:

- soft key from upper-left / camera-left;
- restrained highlight range;
- readable shadow planes;
- no strong colored environmental light baked into the canonical character.

Runtime lighting/state systems may tint or modify this base later, but the source master must remain structurally readable without a specific environment.

## Background and transparency

Production reference sprites:

- transparent background for canonical assets;
- inspection sheets may use one neutral flat background plus checkerboard alpha view;
- no atmospheric background contamination;
- no cast-shadow shape baked into the sprite unless the runtime system explicitly adopts sprite-attached shadows.

## Pixel integrity

Production assets must satisfy:

- nearest-neighbor scaling only;
- integer-position placement for the sprite layer;
- no bilinear filtering;
- no anti-aliased transform bake;
- no arbitrary rotation of completed sprites at runtime;
- no fractional scale differences between characters of the same body-size state unless the change is a deliberate world-scale mechanic.

## Equipment compatibility

Because weapons and later clothing are gameplay-variable, the production master must leave the character suitable for modular variation.

Rules:

- weaponless base reference;
- hands readable and spatially separable;
- arms should not be permanently hidden by hair/cloth in every direction;
- equipment must obey the same pixel density and lighting logic;
- equipment variation must not redefine the protagonist's body scale or hair identity;
- future armor/clothing may change silhouette, but the underlying identity anchors must remain recoverable.

## First production-master generation spike

Do **not** attempt an entire walk cycle first.

Generate/construct only the following initial three views:

1. `S` — toward camera/down-screen;
2. `NE` — representative diagonal/back-side view;
3. `N` — away from camera/up-screen.

Each must use:

- 64 px target body height;
- actual gameplay high-oblique projection;
- transparent background;
- weaponless initial state;
- same neutral pose;
- same palette/value logic.

### Pass gate

All three must pass before generating the remaining five directions.

Pass requires:

- unmistakably the same Exilada;
- convincing modern pixel art at 1×;
- clean cluster construction;
- no high-resolution-image-downsample look;
- hair silhouette remains dominant and coherent;
- anatomy remains adult and readable;
- minimal clothing remains asymmetric and legible;
- no dependence on facial microdetail;
- no obvious AI texture/noise;
- direction changes do not redesign the character.

If the three-view test fails, fix the **production-raster method**, not the identity master.

## First direct image-generation attempt — rejected (2026-09-04)

A direct image-generation attempt was made for a nominal `S` production sprite.

Observed output properties:

- file dimensions: **1024 × 1536 px RGBA**, not the required 96 × 96 native production canvas;
- the visible character occupied almost the full high-resolution image rather than approximately 64 native pixels;
- transparency existed, but the output still carried a high-resolution generative treatment rather than a native-grid sprite construction;
- the result was visually close to the Exilada identity but technically incompatible with the Production Pixel Master specification.

### What the attempt preserved successfully

- adult female identity;
- long dark hair as the dominant silhouette mass;
- olive/brown skin;
- minimal degraded chest and hip cloth;
- broken restraints / chains;
- barefoot initial state;
- weaponless base state;
- severe survival-oriented presence.

### Why it failed the production gate

- not generated on the 96 × 96 native canvas;
- not approximately 64 pixels tall at native scale;
- detail density remained closer to high-resolution illustration than authored native pixel art;
- excessive surface texture remained on skin, cloth and hair;
- hair was described through many fine internal strands rather than a small number of stable designed masses;
- palette/value economy was not demonstrably controlled;
- the output could not be inspected as a true 1× production sprite;
- therefore it cannot be used as a canonical conditioning source for production animation.

**Decision:** reject this output as a Production Pixel Master candidate. Keep only as evidence that the generator can preserve the broad Exilada identity. The next experiment must produce an actual native-grid asset rather than a large image that merely looks pixel-art-like.

## Relationship to the FLUX + RefControl pose spike

The current FLUX.2 Klein + RefControl test remains useful as an isolated test of pose adherence and character preservation against the high-detail identity reference.

It does **not** validate this production pixel-art specification.

The intended production architecture, if the pose-control technology itself passes, becomes:

`identity master -> approved production pixel reference pack -> pose-controlled generation -> native-grid pixel QA -> animation/inbetweening -> runtime validation`

The project should not advance to mass animation generation until the production pixel reference pack exists and passes this document's gate.

## QA checklist — production pixel master

A candidate master fails if any of the following is true:

- only looks good enlarged, not at 1×;
- reads as a shrunk illustration;
- relies on antialiasing or smooth gradients;
- contains uncontrolled high-frequency pixel noise;
- hair becomes strand soup rather than designed masses;
- body age/proportions become ambiguous or juvenile;
- clothing becomes generic fantasy decoration;
- important silhouette masses change between views without perspective justification;
- different directions appear to depict different people;
- palette expands without structural reason;
- equipment or a specific weapon becomes necessary to identify the Exilada;
- manual pixel-by-pixel repair would be required as a routine production step.

## Current decision

**Locked starting native gameplay raster:** 640 × 360.

**Locked starting Exilada body height:** 64 px, tunable only within 56–72 px during actual gameplay-composition validation.

**Locked:** production pixel master is a directional reference pack, not a single oversized portrait.

**Locked:** first validation uses S, NE and N neutral weaponless views before expanding to all eight directions.

**Locked:** identity master and production pixel master are separate canonical assets with different purposes.

**Locked:** all art is approved first at 1× native scale.

**Rejected:** first direct image-generation attempt as a production master because it produced a 1024 × 1536 high-detail image instead of a native 96 × 96 sprite.

**Not yet approved:** any generated production pixel master image or the method that will create it reproducibly.