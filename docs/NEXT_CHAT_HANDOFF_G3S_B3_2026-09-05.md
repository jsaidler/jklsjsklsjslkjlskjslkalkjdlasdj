# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
6. `docs/CHARACTER_PRODUCTION_PIPELINE.md`

## Locked production direction

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed `640×360` orthographic camera, pitch `26 deg`;
- protagonist about `128 px` tall;
- first screen-left locomotion family mostly lateral/slight three-quarter;
- locomotion-facing baseline = **`72 deg` azimuth from travel heading** (`90 deg` pure side);
- final runtime = ordinary deterministic playback of **complete-character spritesheets**.

## Critical architecture lock

The visible character is **not assembled in runtime** from body/hair/clothing/equipment layers.

Each runtime frame is the already-composed full character. Offline tools may use modular sources internally, but before export the frame must contain the whole visible state and all baked secondary motion.

The exported animation therefore includes together:

- body locomotion;
- soft-tissue/jiggle;
- hair motion;
- base clothing/bindings motion;
- shackles/chains/restraints/accessories motion;
- final occlusion.

Armor/equipment/accessory variation will be solved later as an offline-production/state-variant problem.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

This is the **complete initial-state appearance reference**, including hair, base clothing/bindings, restraints and other visible initial details.

## Motion status

C1A remains mechanical gait infrastructure. Runner 31 locked `72 deg`. Runner 32 V1 remained generic. Runner 33 V2 was not approved as the final walk but was retained as a provisional body-motion driver so the first full spritesheet could be generated.

## Runner 34 — COMPLETE-CHARACTER PLAYABLE PROOF RESULT

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

Runner 34 successfully produced:

- eight complete-character frames from the full master;
- RGBA transparency;
- `4×2` `2048×1024` spritesheet with `512×512` cells;
- playback GIF;
- metadata/pivot suitable for ordinary frame playback.

This is a **technical/export PASS**. The complete-character spritesheet architecture works.

### Visual result

The current pose-only Moore+SSD temporal route is **not production-viable yet**:

- identity persists reasonably well;
- broad body pose response is present;
- hair is mostly frozen/warped rather than showing convincing inertial secondary motion;
- cloth morphs but does not move like controlled cloth;
- intentional jiggle is not reliably readable;
- wrist chain persists but is mostly static;
- ankle chain/restraint becomes detached/mutated into dark stepped artifacts in middle frames;
- lower legs/feet still degrade under large pose change;
- later phases become too similar and the loop is weak.

This is a **complete-motion authoring FAIL**, not a spritesheet-format failure.

## Primary diagnosis

The current driver supplies body OpenPose geometry only. It does not explicitly describe hair, cloth, chains, jiggle or the full moving silhouette.

The Moore/AnimateAnyone temporal prior is not reliable enough to invent those systems from one master reference while preserving attachment ownership and physical continuity.

Do not spend the next step on CFG/seed/resolution sweeps or more skeleton-only micro-adjustments.

## CURRENT NEXT GATE — RICH COMPLETE-MOTION DRIVER

Keep:

- complete `exilada_master.png` as appearance reference;
- complete precomposed runtime spritesheet architecture;
- `72 deg` facing;
- runner-33 V2 as provisional body timing/control unless a specific visible reason requires changing it.

Add a richer offline motion-control source that explicitly contains or constrains:

- body motion/weight transfer;
- hair mass inertia;
- cloth motion/lag;
- chain/restraint trajectories;
- soft-tissue/jiggle where required;
- full silhouette/occlusion motion.

Allowed offline controls include a hidden proxy rig, deterministic secondary systems, simulation or a driving video. This does **not** reopen runtime modular assembly or visible-3D-as-final-art.

## Immediate review artifact

Judge runner 34 at the locked approximate `128 px` gameplay body height. A gameplay-scale preview has been produced from the packed sheet; this determines which 512px defects remain visible at actual game scale.

## No cleanup

Retain runner-34 outputs, SSD environment/models and motion work. They are evidence and inputs for the next complete-motion-driver experiment.
