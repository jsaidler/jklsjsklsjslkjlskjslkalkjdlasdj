# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`

## Locked production direction

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed `640×360` orthographic camera, pitch `26 deg`;
- protagonist about `128 px` tall;
- first screen-left locomotion family mostly lateral/slight three-quarter;
- locomotion-facing baseline = **`72 deg` azimuth from travel heading** (`90 deg` pure side);
- final runtime = ordinary deterministic playback of **complete-character spritesheets**.

## Critical architecture lock

The visible character is **not assembled in runtime** from body/hair/clothing/equipment layers.

Each runtime frame is the already-composed full character. Offline tools may use modular controls internally, but before export the frame must contain the whole visible state and all baked secondary motion:

- body locomotion;
- soft-tissue/jiggle;
- hair motion;
- base clothing/bindings motion;
- shackles/chains/restraints/accessories motion;
- final occlusion.

Armor/equipment/accessory variation will be solved later as an offline-production/state-variant problem.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

This is the **complete initial-state appearance reference**.

## Motion status

C1A remains mechanical gait infrastructure. Runner 31 locked `72 deg`. Runner 32 V1 remained generic. Runner 33 V2 is not final locomotion approval but may be used as a provisional body-motion driver for route proofs.

## Runner 34 — complete-character playable proof

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Result:

- technical/export **PASS**;
- complete-character spritesheet architecture **PASS**;
- current Moore+SSD pose-only complete-motion authoring **FAIL**.

Observed failures:

- hair mostly frozen/warped;
- cloth morphing without convincing controlled lag;
- jiggle not deliberately readable;
- wrist chain mostly static;
- ankle chain/restraint detaches/mutates;
- lower legs/feet degrade in displaced phases;
- loop/phase differentiation remains weak.

Do not spend the next step on Moore+SSD seed/CFG/resolution sweeps.

## Wan-Animate-2 — HISTORICAL FAIL / CLOSED

This route was already tested on **2026-09-04** using official Wan-Animate-2 Base INT8 ConvRot on the RTX 3060 12 GB machine.

The generation completed and was visually evaluated. It was rejected because:

1. driving-motion transfer was too weak — the driver walked while generated Exilada stayed largely planted;
2. output lost the required modern-pixel-art language and read as smooth painted/video-diffusion imagery.

Identity/anatomy retention was better than some earlier diffusion attempts, but those two failures were decisive.

Result: **Wan-Animate-2 Base INT8 REJECTED/CLOSED.**

Do not rescue/retry this exact route with a richer synthetic driver, seed search, prompt cosmetics, stronger reference strength or post-generation pixel filtering.

The isolated Wan workspace/model files were deleted after rejection. **Do not assume `D:\AI\WanAnimate2` exists.**

`tools/wan-animate2-spike/` remains research history only.

## 2026-09-07 correction

A proposed runner 35 that attempted to reuse Wan-Animate-2 was invalid because it ignored the already-recorded rejection/cleanup history. The newly-created retry runner/helpers were removed from `main`.

There is currently **no active runner 35**.

## Current next gate

The next route is not yet selected. It must:

- generate the Exilada as a complete character per frame;
- preserve the full initial master state;
- include body motion, hair, cloth, jiggle and restraints/chains in the baked animation;
- provide explicit/inspectable motion control where possible;
- preserve native/discrete pixel/game-art structure;
- avoid generic video-diffusion reruns that already failed the style/motion requirements;
- be checked against the rejection history before any large install/download.

Prior post-Wan research found pixel-native / explicit-control classes more promising than another generic video model, but none is production-approved yet.

## Operator action

Do **not** run the previously proposed runner 35.

First pull the corrected canonical state:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only
```

Then select the next candidate from the corrected route history before installing or downloading anything new.

## Cleanup rule

When a model/route is declared FAIL/CLOSED and no longer required, include exact cleanup commands at the time of rejection. Rejected isolated workspaces must not later be assumed to exist.
