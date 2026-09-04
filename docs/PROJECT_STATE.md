# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** This file records the current active work, latest validated checkpoints, rejected routes and exact next gate. Detailed design lives in the linked living documents.

## Canonical living documents

Read in this order before acting:

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/PIXEL_ART_PRODUCTION.md`
6. `docs/ANIMATION_PIPELINE.md`
7. current tooling under the relevant `tools/` spike directory

GitHub living documents are the source of truth across chats.

## Mandatory checkpoint protocol

After every material project step:

1. update the relevant thematic living document;
2. update this file;
3. commit tooling/documentation changes with a focused commit;
4. record PASS/FAIL, observed result and next gate;
5. do not rely only on chat history or memory.

## What the game is — canonical summary

The project is a **systemic action RPG with roguelite structure, persistent fortress growth and a living sword-and-sorcery world**.

Five coupled layers define the game:

1. **Living world:** cultures, creatures, settlements, resources, territories and factions behave from causal rules rather than arbitrary procedural randomness.
2. **Fortress:** a persistent foothold that grows, produces, defends, attracts population and affects/is affected by the same world simulation.
3. **Exilada meta-progression:** the protagonist persists and changes through capabilities, equipment, knowledge, relationships and history/state.
4. **Expeditions/runs:** dangerous excursions feed consequences back into protagonist, fortress and world state rather than existing as isolated arcade stages.
5. **Immediate gameplay:** physical, readable action inspired by arcade belt-scrolling beat'em ups but updated with systemic AI, state, equipment, environment and contemporary combat expectations.

Detailed canonical formulation lives in `docs/GAME_VISION.md`.

## Locked gameplay projection change — PASS

The previous high-oblique top-down / continuous-360° presentation baseline is superseded.

The current locked baseline is:

**elevated 2D belt-scroller / false 3D**

This means:

- strong lateral travel axis;
- continuous depth movement within walkable bands;
- elevated camera showing enough ground to read spatial depth;
- mostly lateral / three-quarter full-body action presentation;
- foreground/background overlap and false-3D environmental depth;
- not a pure side-scrolling platformer;
- not rigid technical isometry;
- combat readability and production scalability take priority over geometric purity.

Observed design consequence:

This should substantially reduce the directional-art multiplication of an eight-direction isometric/top-down system while preserving the spatial language desired for the game's beat'em-up-like maps.

## Current active focus

**Resolve the Exilada base-walk production scale under the belt-scroller projection.**

The project is intentionally focused on the protagonist before large-scale gameplay implementation because character art/animation is the principal production-feasibility risk. Code implementation capability is not the current unknown.

The goal is to prove that the project can produce, reproducibly and without manual frame-by-frame work:

- a convincing protagonist at actual gameplay scale;
- a readable and physically grounded base walk;
- animation suitable for the selected projection;
- equipment/state variation;
- scalable character production for NPCs, enemies and creatures.

This focus is a feasibility gate for the full game, not a redefinition of the project as a sprite experiment.

## Current visual-production findings

### Identity/design master: PASS

Canonical Exilada reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It remains canonical for identity and defines:

- adult female identity;
- lean functional anatomy;
- long black hair as dominant mass;
- olive/brown skin;
- minimal degraded clothing;
- captivity/restraint markers;
- barefoot, weaponless initial state.

It is **not** the final gameplay sprite master.

### Direct high-resolution generation as Production Pixel Master: FAIL

Observed:

- high-resolution illustration rather than actual production-grid pixel art;
- excessive generative texture/detail;
- no trustworthy native-grid cluster/palette control.

Decision:

Do not prompt-iterate this route as final sprite authoring.

### Native Python/Pillow primitive sprite spike: FAIL visually

Technical native-raster properties passed, but visual quality failed through generic procedural/mannequin anatomy and weak authored silhouette.

Decision:

Python/Pillow remains useful for deterministic QA/export/masks/palette checks, but not as the artistic authoring engine.

## Recovered base-walk checkpoint — PASS as historical evidence

The work had already reached an eight-frame Exilada walk-cycle test before the production-raster concern interrupted it.

Recovered artifacts:

- **smoke:** `8` frames, `8 fps`, `384 × 576` pixels per frame;
- **quality:** `8` frames, `8 fps`, `512 × 768` pixels per frame.

These artifacts prove that the active question was already the **base walk**, not a new static-sprite exercise.

They are now classified as:

**high-resolution motion/reference proxies — not approved production sprites.**

The unresolved question is:

> How much does evaluating/generating the walk at these high resolutions change what remains readable or usable at the real gameplay scale?

Locked interpretation:

- high-resolution output can still be useful for pose sequence, stride mechanics, foot contacts, identity continuity and secondary-motion reference;
- it cannot establish final pixel clusters, palette, gameplay-scale detail or native-grid animation quality;
- simple downscale/quantization of these frames is not an accepted final-art pipeline.

## Superseded pixel-scale assumptions

The following previous values were tied to the old high-oblique/360° presentation hypothesis and are **unlocked/superseded**:

- Exilada visible height ~`64 px`;
- tuning band `56–72 px`;
- idle/locomotion canvas `96 × 96`;
- ordinary melee/action canvas `128 × 128`;
- mandatory eight-direction neutral reference family;
- `S`, `NE`, `N` as the first directional approval gate.

They must not be treated as current production requirements.

The provisional internal gameplay raster remains `640 × 360` only as a starting point for evidence gathering; it may change.

## Locked visual direction

- true modern pixel art, not pixel-textured illustration;
- mature, severe, physical, atmospheric sword-and-sorcery language;
- Exilada identity led by large black hair mass, adult lean anatomy, asymmetrical degraded clothing and captivity history;
- visually relevant state should be causal/systemic whenever feasible;
- no manual frame-by-frame production burden on the user;
- production route must scale to many characters, equipment states and world conditions.

## Exact next gate — do not skip

### Motion-aware gameplay scale validation

Do **not** author another final sprite first and do **not** resume full FLUX generation yet.

Use the existing eight-frame high-resolution walk cycle only as a **motion proxy** inside a representative elevated belt-scroller composition at the provisional `640 × 360` native raster.

Test several provisional visible Exilada heights, initially around:

- `112 px`;
- `128 px`;
- `144 px`.

These are comparison samples, not production locks.

The test must establish, at native `1×`:

1. stride readability;
2. distinct foot-contact / passing phases;
3. whether the feet feel grounded or appear to slide;
4. hair-mass readability during motion;
5. arm/leg separation across the cycle;
6. protagonist screen occupancy;
7. ability to read approximately 3–5 simultaneous nearby enemies;
8. available space for ordinary weapon/attack arcs;
9. usable walkable depth band for foreground/background combat positioning;
10. whether `640 × 360` remains viable.

This is explicitly a **motion + gameplay-scale gate**, not an approval of the resized high-resolution art.

### Gate output

Only after this comparison should the project lock:

- protagonist visible pixel height;
- idle/locomotion canvas bounds;
- ordinary action canvas bounds;
- ground/pivot convention;
- facing-family requirement under the belt-scroller model.

Then:

1. author the first real native-grid Production Pixel Master at that scale;
2. build the definitive native-grid eight-frame base walk from the validated motion language;
3. evaluate it in the same gameplay composition at `1×`.

## Animation pipeline — preserved but paused at visual dependency

The FLUX.2 Klein + RefControl local spike remains preserved and technically relevant as an upstream character re-posing/reference route, but it is not the immediate next action.

Validated state remains:

- STEP 1 preflight: PASS;
- STEP 2 ComfyUI portable runtime: PASS;
- STEP 3 required weights: PASS;
- STEP 4 canonical reference + four deterministic COCO-18 poses: PASS;
- STEP 5 runtime schema validation tooling: ready; local target-machine execution still pending.

Active tooling:

`tools/flux2-refcontrol-spike/`

Do not discard or silently restart that work. Resume it only after the gameplay-scale walk gate establishes what representation the renderer must ultimately serve, unless the user explicitly reprioritizes it.

## Rejected / stopped routes

Do not revive casually:

- Sprite Sheet Diffusion — tested and rejected;
- Wan-Animate-2 Base INT8 — tested and rejected;
- PixelLab hosted/tiered route — stopped;
- Pixel Engine — disqualified as hosted/paid dependency;
- Retro Diffusion hosted route — disqualified under same rule;
- direct generic image generation as final pixel master — rejected;
- primitive Python/Pillow geometry as final artistic authoring — rejected;
- generic video diffusion as primary animation architecture — rejected.

## Target machine / relevant paths

- Windows 11 Home Single Language;
- 47.7 GB usable RAM detected;
- NVIDIA GeForce RTX 3060 12 GB;
- project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`;
- FLUX spike workspace: `D:\AI\Flux2RefControlSpike`.

## Current next action

**Do not generate another character sprite yet.**

Next: use the already-existing eight-frame walk as a temporary motion proxy and perform the belt-scroller gameplay-scale comparison. The result will determine the real character pixel density; only then do we author the Production Pixel Master and definitive native-grid base walk.
