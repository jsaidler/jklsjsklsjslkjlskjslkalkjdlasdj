# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
6. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
7. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

## Game / presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first canonical locomotion family is screen-left / mostly lateral-three-quarter;
- `72 deg` azimuth from travel heading is locked as the first locomotion-facing baseline (`90 deg` = pure side).

## Runtime animation architecture — CORRECTED / LOCKED 2026-09-07

The runtime plays **complete precomposed character frames**:

`complete frames -> complete-character spritesheet PNG(s) + metadata -> ordinary sprite playback`

The previous concept of constructing a visible character in runtime from body/hair/clothing/equipment layers is **ABOLISHED/CLOSED**.

Every exported animation frame must already contain the entire visible character state, including where present:

- body motion;
- soft-tissue/jiggle motion;
- hair motion;
- base clothing/bindings motion;
- shackles/chains/restraints/accessories motion;
- correct occlusion among all those elements.

Offline production may still use modular sources/rigs/layers to author variants efficiently, but composition is completed before export. Armor/equipment/accessory variation strategy will be designed later; it may not assume runtime character assembly.

## Canonical Exilada initial-state master

`assets/source/characters/exilada/reference/exilada_master.png`

The master is now explicitly the **complete initial-state appearance reference** for the first animation proof, not merely a body/identity anchor. Its visible hair, base clothing/bindings, restraints/shackles/chains and other initial details belong in the generated sequence.

## Motion state

C1A remains a mechanical gait/control proof using `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk` and eight contact/down/passing/up states.

Runner 31 locked `72 deg` facing.

Runner 32 V1 failed as final locomotion art direction because it remained generic.

Runner 33 V2 added restrained feminine pelvis/torso/shoulder treatment. It is not accepted as the final walk master, but the project will **not delay the first full spritesheet proof for further skeleton micro-adjustment**. V2 is the provisional motion driver for the complete-character proof.

## SSD / visible-authoring state

Exact upstream SSD remains **BLOCKED** because the public release omits the custom multi-scale `pose_guider.pth`.

The Moore-compatible fallback is technically runnable:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD denoising/reference UNets`

Runner 29: technical PASS / visual FAIL.

Runner 30: corrected the `1.7778×` pose-registration distortion and materially improved pose response/lower-limb reconstruction. It also proved that a complete-master temporal generation is technically possible, although visible quality and secondary-mass stability were not yet production-ready.

## CURRENT GATE — RUNNER 34 COMPLETE-CHARACTER WALK8 PLAYABLE PROOF

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

Purpose:

1. use `exilada_master.png` as the complete initial-state appearance reference;
2. use runner-33 V2 at locked `72 deg` as a provisional eight-frame motion driver;
3. generate the whole character through the proven Moore-compatible SSD route;
4. judge body motion, jiggle, hair, base clothing, bindings, shackles/chains/restraints and visible accessories **together**;
5. remove the neutral connected background from each generated frame;
6. pack eight complete RGBA frames into one spritesheet + metadata;
7. inspect the actual whole-character animation rather than continue skeleton-only refinement.

This is a **playable proof**, not final production approval.

### Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\34_run_exilada_complete_character_walk8_playable_proof.ps1"
```

Expected terminal marker:

`G3S-COMPLETE-WALK8: COMPLETE CHARACTER SPRITESHEET READY FOR QA`

Expected workspace:

`Z:\AI\SpriteSheetDiffusionSpike\exilada_initial_complete_walk8_playable_proof`

Primary outputs:

- generated complete-character contact sheet;
- generated complete-character GIF;
- transparent `frames_rgba`;
- `spritesheet\exilada_initial_walk8_complete_spritesheet.png`;
- `spritesheet\exilada_initial_walk8_complete_spritesheet_preview.gif`;
- `spritesheet\exilada_initial_walk8_complete_spritesheet.json`.

## Runner 34 QA rule

Judge the character as one baked temporal object. PASS for further development requires enough coherence to prove the route is worth continuing, especially:

- recognizable Exilada identity;
- readable locomotion;
- plausible whole-body secondary motion;
- hair not frozen or arbitrarily changing mass;
- base cloth/bindings moving coherently;
- shackles/chains/accessories remaining attached to the correct side and moving plausibly;
- no catastrophic anatomy or frame-to-frame identity break;
- spritesheet cells and pivot remaining stable enough for runtime playback.

The proof does **not** require final walk polish or final armor-variation architecture.

## Historical / closed assumptions

- runtime visible-character layer assembly — ABOLISHED/CLOSED;
- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- exact-upstream SSD runner 28 — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## No cleanup

Retain SSD environment/models and motion work. They are required for runner 34.
