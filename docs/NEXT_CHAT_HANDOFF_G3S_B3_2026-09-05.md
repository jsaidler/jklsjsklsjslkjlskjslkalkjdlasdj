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

C1A remains mechanical gait infrastructure. Runner 31 locked `72 deg`. Runner 32 V1 remained generic. Runner 33 V2 was not approved as the final walk but is retained as a provisional body-motion driver so visible complete-character routing can be tested before further gait micro-polish.

## Runner 34 — COMPLETE-CHARACTER PLAYABLE PROOF RESULT

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 successfully produced:

- eight complete-character frames from the full master;
- RGBA transparency;
- `4×2` `2048×1024` spritesheet with `512×512` cells;
- playback GIF;
- metadata/pivot suitable for ordinary frame playback.

This is a **technical/export PASS**. The complete-character spritesheet architecture works.

### Visual result

The current pose-only Moore+SSD temporal route is **not production-viable** as complete-motion authoring:

- identity persists reasonably well;
- broad body pose response is present;
- hair is mostly frozen/warped instead of showing convincing inertia;
- cloth morphs but does not move like controlled cloth;
- intentional jiggle is not reliably readable;
- wrist chain persists but is mostly static;
- ankle chain/restraint detaches/mutates into dark stepped artifacts in middle frames;
- lower legs/feet still degrade under larger pose change;
- later phases become too similar and the loop is weak.

This is a **complete-motion authoring FAIL**, not a spritesheet-format failure.

## Primary diagnosis

The runner-34 control signal is body OpenPose geometry only. It does not explicitly carry hair, cloth, chain, jiggle or whole-silhouette motion.

Do not spend the next step on Moore+SSD CFG/seed/resolution sweeps or more skeleton-only micro-adjustments.

## CURRENT GATE — RUNNER 35 WAN-ANIMATE-2 COMPLETE-MOTION PROOF

Runner:

`tools/structured-2d-character-pipeline/35_run_exilada_wan_animate2_complete_motion_proof.ps1`

Driver builder:

`tools/structured-2d-character-pipeline/g3s_build_complete_motion_driver_v1.py`

Wan workflow builder:

`tools/wan-animate2-spike/build_workflow_complete_motion.py`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_wan_complete_character_spritesheet.py`

### Driver

Runner 35 creates a deterministic synthetic **complete-motion control video** only for offline motion transfer. It is not visible game art.

Contract:

- `17` frames;
- `384×576`;
- `16 fps`;
- first `16` frames = one in-place loop sampled from runner-33 V2 at locked `72 deg`;
- frame `17` duplicates frame 1 as explicit closure target;
- body motion;
- heavy rear/front hair lag;
- hip-wrap/base-cloth lag;
- subtle soft-body/chest lag signal;
- left-wrist shackle + broken-chain trajectory;
- left-ankle shackle + broken-chain trajectory.

This richer driver exists because Wan-Animate-2 directly conditions on a driving video instead of receiving only a stick-figure pose map.

### Wan route

Existing isolated workspace:

`D:\AI\WanAnimate2`

Required route:

- official Wan-Animate-2 Base INT8 ConvRot;
- `wan_animate_2_int8_convrot.safetensors`;
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`;
- `clip_vision_h.safetensors`;
- `Wan2_1_VAE_bf16.safetensors`;
- no distillation LoRA;
- `384×576`, `17` frames;
- seed `42`;
- Euler;
- shift `5`;
- `20` steps;
- CPU model cache for RTX 3060 12 GB.

Runner 35 does **not** automatically download missing model assets. Missing Wan infrastructure is fixed as infrastructure, not interpreted as visual failure.

### Output

Wan output frame 17 is used as closure conditioning evidence but dropped from runtime playback. Frames 1–16 are exported as:

- complete RGBA frames;
- `4×4` complete-character spritesheet;
- full-resolution 16 fps GIF;
- approximately `128 px` gameplay-scale GIF;
- metadata with runtime layer assembly explicitly disabled.

### Decision rule

Compare against runner 34 specifically on:

- hair inertia;
- base-cloth lag;
- subtle body soft response;
- wrist/ankle chain ownership and trajectories;
- lower-leg/foot topology;
- Exilada identity;
- loop coherence.

Continue only if the improvement is **material**. If not, do not rescue through seed fishing, CFG sweeps or cosmetic prompt tuning.

## EXACT NEXT OPERATOR ACTION

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\35_run_exilada_wan_animate2_complete_motion_proof.ps1"
```

Expected terminal marker:

`G3S-WAN-COMPLETE-MOTION: OUTPUT READY FOR VISUAL QA`

Expected workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_runner35_wan_complete_motion_proof`

Share these first:

1. `driver\complete_motion_driver_contact_sheet.png`
2. `driver\complete_motion_driver_preview.gif`
3. `spritesheet\exilada_initial_walk16_wan_complete_spritesheet.png`
4. `spritesheet\exilada_initial_walk16_wan_complete_preview.gif`
5. `spritesheet\exilada_initial_walk16_wan_gameplay_128px.gif`

## No cleanup

Retain runner-34 outputs, SSD assets, the existing Wan workspace/models and all runner-35 evidence until the route decision is closed.
