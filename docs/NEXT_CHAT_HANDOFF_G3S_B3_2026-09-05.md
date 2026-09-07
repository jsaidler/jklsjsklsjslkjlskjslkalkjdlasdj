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

## Critical architecture correction — LOCKED

The visible character is **not assembled in runtime** from body/hair/clothing/equipment layers. That approach is abolished.

Each runtime frame is the already-composed full character. Offline tools may use modular sources internally, but before export the frame must contain the whole visible state and all baked secondary motion.

The exported walk must therefore include, together:

- body locomotion;
- soft-tissue/jiggle motion;
- hair motion;
- base clothing/bindings motion;
- shackles/chains/restraints/accessories motion;
- final occlusion among those elements.

Armor/equipment/accessory variation will be solved later as an offline-production/state-variant problem. Do not reintroduce runtime character construction.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

This is the **complete initial-state appearance reference** for the immediate walk proof, including hair, base clothing/bindings, restraints and other visible initial details.

## Motion status

C1A remains a mechanical eight-phase human-gait sanity source. Runner 31 locked `72 deg` facing. Runner 32 V1 remained too generic. Runner 33 V2 adds restrained feminine body-language treatment but is not treated as final animation approval.

The user explicitly chose to stop delaying the first spritesheet for further gait micro-adjustment. Runner-33 V2 is therefore used as a **provisional motion driver** for the whole-character proof.

## SSD status

Exact upstream SSD remains blocked by the missing custom multi-scale `pose_guider.pth`.

Moore-compatible fallback is technically runnable. Runner 30 fixed the target-pose registration distortion and materially improved visible pose response. It remains the best working temporal reference-to-pose route currently available locally.

## CURRENT GATE — runner 34 complete-character playable proof

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

Runner 34:

1. takes the complete `exilada_master.png`;
2. takes the current `72 deg` V2 eight-frame guide;
3. aligns those poses uniformly to the master DWPose footprint;
4. runs the proven Moore-compatible SSD inference at `512×512`, 8 frames, 25 steps, CFG 3.5, seed 42, fp16;
5. treats hair/cloth/jiggle/restraints as part of the same temporal-generation test;
6. removes connected neutral background from each generated frame;
7. exports eight RGBA complete-character frames;
8. packs a 4×2 complete-character spritesheet and metadata;
9. creates a playback GIF.

## EXACT NEXT OPERATOR ACTION

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\34_run_exilada_complete_character_walk8_playable_proof.ps1"
```

Expected final marker:

`G3S-COMPLETE-WALK8: COMPLETE CHARACTER SPRITESHEET READY FOR QA`

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike\exilada_initial_complete_walk8_playable_proof`

Share at minimum:

1. `generated_complete_character\exilada_walk8_moore_compat_contact_sheet.png`
2. `generated_complete_character\exilada_walk8_moore_compat.gif`
3. `spritesheet\exilada_initial_walk8_complete_spritesheet.png`
4. `spritesheet\exilada_initial_walk8_complete_spritesheet_preview.gif`

## Decision rule

This is not a final-art gate. It answers whether the full-master temporal route is viable enough to continue.

Judge the complete baked character, especially identity, locomotion, jiggle, hair, cloth/bindings and restraint/accessory attachment/motion. Detached, frozen, migrating or identity-changing secondary masses count as failures of the full-character authoring route; they are not deferred runtime-layer problems.

No cleanup applies.
