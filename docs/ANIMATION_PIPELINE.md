# Character Animation Production — Living Decision Record

Status: **Sprite Sheet Diffusion pipeline selected for validation; canonical reference format clarified; not yet production-proven**

## Production constraint

The user will not manually animate production characters and will not hire an animation/art team. A valid character-animation pipeline must therefore be reproducible by project tooling and scale beyond a single hand-corrected demo.

The visible game style is **modern pixel art**. Animation output must preserve that language rather than looking like painted AI frames that were subsequently pixelated.

## Rejected approaches

The following approaches are rejected as production foundations:

- generating independent animation frames with a general-purpose image generator and hoping identity remains stable;
- asking a general image generator for a complete sprite sheet in one generation;
- cutting an already-flattened character PNG into rigid body parts and rotating those parts as a 2D puppet;
- accepting conventional rendered or painted animation and adding a pixel filter afterward;
- relying on frame-by-frame manual repainting to repair identity or anatomy.

Observed failures included character drift, biomechanically incoherent cycles, inconsistent clothing/equipment, changing proportions and obvious paper-doll articulation.

## Current production candidate: Sprite Sheet Diffusion hybrid

Sprite Sheet Diffusion (SSD) is aimed specifically at game-character animation from a reference character plus driving poses and is therefore materially more relevant than general image generation.

The public SSD release is incomplete: its trained custom multi-scale pose guider was not released. The runnable local reconstruction documented by the project uses:

- SSD finetuned `denoising_unet.pth`;
- SSD finetuned `reference_unet.pth`;
- baseline AnimateAnyone `pose_guider.pth`;
- baseline AnimateAnyone `motion_module.pth`;
- CLIP vision image encoder;
- SD VAE.

This is a **hybrid public-weight reconstruction**, not the exact unreleased paper checkpoint set.

## Hardware target

Initial target machine:

- Windows 11;
- RTX 3060 12 GB;
- 48 GB RAM.

The chosen C++ port documents an RTX 3060 configuration using FP16 model loading, CPU parameter offload, flash attention and VAE tiling.

The quality profile currently targets a tall reference format because the approved protagonist source is full-body and detail retention matters.

## Canonical character reference

Each production character has **one approved master reference** that anchors identity.

The master reference is not a decorative character sheet. It is a production conditioning image.

### Required reference format

For the Exilada and equivalent humanoid characters:

- one character only;
- full body completely visible, including feet;
- neutral or mildly alert standing pose;
- arms separated enough from the torso to keep limb anatomy legible;
- legs separated enough to make lower-body structure clear;
- no title, UI, inset, environment composition or extra view;
- flat or very simple neutral background;
- no weapon in the identity master unless the weapon itself is canonically inseparable from that character;
- stable adult anatomy and proportions;
- approved hair, body, clothing and persistent character markers clearly visible;
- native modern pixel-art construction and controlled palette;
- sufficient margin around the figure for downstream processing.

The currently approved Exilada production reference follows this format: full-body, weaponless, minimal initial clothing, long heavy black hair and visible captivity markers.

Recommended repository-side source layout:

`assets/source/characters/exilada/reference/exilada_master.png`

The image should be promoted to this path when binary asset ingestion is incorporated into the repository workflow.

## Identity versus equipment

Weapons are **gameplay-variable equipment**, not part of the Exilada's permanent character identity.

The canonical master reference therefore excludes a weapon.

Animation generation must distinguish:

1. **body identity** — anatomy, face, hair, permanent marks, base silhouette;
2. **current clothing/equipment state** — variable through progression;
3. **weapon state** — supplied as an animation/equipment condition when needed.

Pass criteria must therefore check stability of whatever equipment state was explicitly requested for that animation, without treating one particular weapon as permanently canonical.

## Deterministic pose driving

The project does not ask the model to invent motion.

A deterministic BODY_18/OpenPose-style skeleton sequence is generated locally.

The base walk cycle uses eight conventional phases:

1. contact A;
2. down A;
3. passing A;
4. up A;
5. contact B;
6. down B;
7. passing B;
8. up B.

This cycle can be repeated to create a longer motion context, with the stable center window extracted for the final candidate cycle.

## Recurring production routine

### 1. Ground the character state

Select the canonical character master plus any explicitly requested current clothing/equipment/weapon state.

### 2. Define the animation spec

Each action is described by a machine-readable specification containing, as needed:

- action name;
- final frame count;
- loop/non-loop behavior;
- intended facing/direction;
- timing;
- contact frames;
- locomotion speed;
- current equipment state;
- current weapon state;
- deterministic pose sequence.

Examples include `walk`, `run`, `idle`, `light_attack`, `heavy_attack`, `hit_react`, `dodge` and `death`.

### 3. Generate candidates

The canonical reference plus deterministic pose sequence are passed through the SSD hybrid.

Generation uses a small controlled seed set when needed. Record:

- seed;
- resolution;
- steps;
- model identifiers;
- conditioning/reference asset version;
- pose-spec version.

A successful animation must be reproducible.

### 4. Automated post-processing

The toolchain should automatically:

- extract stable center frames;
- align a common ground/contact line;
- normalize canvas dimensions;
- remove/key the background if necessary;
- preserve alpha;
- crop consistently without changing character scale;
- assemble sprite sheets;
- write frame metadata;
- write pivots and hitbox/hurtbox references where applicable.

Manual frame-by-frame repainting is outside the accepted production workflow.

### 5. Visual validation

Every candidate is reviewed as motion, not as isolated attractive frames.

Review checks:

- identity preservation;
- stable adult anatomy and proportions;
- stable hair and persistent character markers;
- stability of explicitly requested clothing/equipment/weapon state;
- coherent gait/action mechanics;
- foot sliding and ground contact;
- temporal jitter;
- unwanted morphing;
- preservation of authentic modern pixel-art readability.

If a candidate fails, adjust pose driving, inference parameters, seed or reference conditioning and regenerate.

### 6. Runtime validation

Approved sheets are immediately tested at actual game camera scale and movement speed.

Validate:

- cadence;
- continuous translation;
- loop seam;
- silhouette readability;
- ground contact;
- combat timing;
- facing/directional readability;
- whether the result still reads as intentional pixel art in motion.

### 7. Canonical promotion

Only approved outputs become production assets.

Promote together:

- sprite sheet;
- animation metadata;
- generation manifest;
- source/master reference version;
- pose specification version.

Temporary generations remain outside the canonical asset set.

## Initial validation order for the Exilada

The first sequence should prove the core body before weapon complexity:

1. `walk` — identity and temporal consistency;
2. `idle` — subtle motion without drift;
3. `run` — faster locomotion stress;
4. `hit_react` / `dodge` — rapid silhouette change without external equipment;
5. one **equipped-weapon test** using a chosen temporary validation weapon — proves equipment conditioning, not character identity;
6. light and heavy attacks for that weapon class;
7. additional weapon classes only after the base pipeline passes.

No large animation library should be generated before `walk` passes.

## Additional human-body-family test

A masculine counterpart reference has been generated in the same production-reference format as an exploratory second human-body-family sample.

It is **not automatically canonical as a playable character** merely because the reference exists. If approved, it can become a controlled validation case demonstrating that the SSD pipeline generalizes beyond the Exilada while preserving the same modern pixel-art language.

## Decision gate

The pipeline passes only if it can produce animation that preserves:

- character identity;
- adult anatomy;
- stable proportions;
- hair and clothing consistency;
- explicitly requested equipment/weapon state;
- coherent motion;
- clean temporal consistency;
- authentic modern pixel-art readability at gameplay scale;
- reproducibility without manual frame-by-frame repainting.

If acceptable quality requires ongoing manual repainting, the pipeline is rejected.

## Repository tooling

Implementation lives under:

`tools/sprite-animation/`

The repository currently versions scripts, configuration and documentation. Model checkpoints, dependency checkouts, build products and temporary generated files remain excluded from git.