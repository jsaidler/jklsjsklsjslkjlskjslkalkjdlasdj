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
5. do not rely only on chat history or model memory.

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

**Visual-production feasibility for the Exilada under the new belt-scroller projection.**

The project is intentionally focused on the protagonist before large-scale gameplay implementation because character art/animation is the principal production-feasibility risk. Code implementation capability is not the current unknown.

The goal is to prove that the project can produce, reproducibly and without manual frame-by-frame work:

- a convincing protagonist at actual gameplay scale;
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

## Superseded pixel-scale assumptions

The following previous values were tied to the old high-oblique/360° presentation hypothesis and are now **unlocked/superseded**:

- Exilada visible height ~`64 px`;
- tuning band `56–72 px`;
- idle/locomotion canvas `96 × 96`;
- ordinary melee/action canvas `128 × 128`;
- mandatory eight-direction neutral reference family;
- `S`, `NE`, `N` as the first directional approval gate.

They must not be treated as current production requirements.

The provisional internal gameplay raster remains `640 × 360` only as a starting point for the next composition test; it may change based on evidence.

## Locked visual direction

- true modern pixel art, not pixel-textured illustration;
- mature, severe, physical, atmospheric sword-and-sorcery language;
- Exilada identity led by large black hair mass, adult lean anatomy, asymmetrical degraded clothing and captivity history;
- visually relevant state should be causal/systemic whenever feasible;
- no manual frame-by-frame production burden on the user;
- production route must scale to many characters, equipment states and world conditions.

## Exact next gate — do not skip

### Gameplay composition / camera-scale blockout

Before choosing a new sprite canvas or authoring another Exilada production sprite, create a representative belt-scroller gameplay composition at the provisional native raster (`640 × 360`).

The blockout must establish, by visual/gameplay evidence:

1. camera elevation/pitch language;
2. walkable depth-band size;
3. Exilada on-screen height and body readability;
4. enemy scale relative to the protagonist;
5. amount of visible world needed around combat;
6. foreground/background depth and occlusion behavior;
7. safe action/silhouette bounds for attacks and weapons;
8. whether `640 × 360` remains an appropriate native raster;
9. minimum facing-family requirement for locomotion/combat under the belt-scroller model.

**Do not lock another sprite size before this composition gate.**

Only after the blockout passes should `docs/PIXEL_ART_PRODUCTION.md` receive a new native character scale/canvas target and the first Production Pixel Master be authored.

## Animation pipeline — preserved but paused at visual dependency

The FLUX.2 Klein + RefControl local spike remains preserved and technically relevant, but it is not the immediate next action.

Validated state remains:

- STEP 1 preflight: PASS;
- STEP 2 ComfyUI portable runtime: PASS;
- STEP 3 required weights: PASS;
- STEP 4 canonical reference + four deterministic COCO-18 poses: PASS;
- STEP 5 runtime schema validation tooling: ready; local target-machine execution still pending.

Active tooling:

`tools/flux2-refcontrol-spike/`

Do not discard or silently restart that work. Resume it only when the new production projection/character requirements are defined enough to make the test relevant again, unless the user explicitly reprioritizes it.

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

Next: define and validate the representative elevated belt-scroller gameplay composition first. The resulting camera/scale evidence will determine the actual Production Pixel Master dimensions and character pixel density.
