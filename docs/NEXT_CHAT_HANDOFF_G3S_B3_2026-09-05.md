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
- facing baseline = `72 deg` azimuth from travel heading;
- final runtime = ordinary deterministic playback of **complete-character spritesheets**;
- no runtime visible-character assembly from layers.

Every exported frame must already contain the complete visible state, including body locomotion, soft-tissue/jiggle, hair, clothing/bindings, shackles/chains/restraints/accessories and final occlusion.

Canonical initial-state appearance reference:

`assets/source/characters/exilada/reference/exilada_master.png`

## Process correction — MODEL EXHAUSTION BEFORE SWITCHING

A bad result from one configuration is not enough to conclude that a model family cannot perform the task.

Before changing models, classify failures as infrastructure, integration, configuration, BLOCKED or genuine MODEL/TASK FAIL.

A model/task rejection requires, where practical:

- official/reference baseline reproduced in the same runtime;
- loader/checkpoint semantics validated;
- preprocessing/input domain validated;
- easy matched project case tested before maximum complexity;
- controlled fixed-seed, one-variable-at-a-time sweeps of meaningful parameters;
- repeated decisive failure across multiple valid configurations.

Do not delete a workspace merely because one visual configuration failed.

## Motion status

C1A remains mechanical gait infrastructure. Runner 31 locked `72 deg`. Runner 32 V1 remained generic. Runner 33 V2 is not final locomotion approval but remains usable for route diagnostics.

## Runner 34

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Result:

- technical/export PASS;
- complete-character spritesheet architecture PASS;
- tested Moore-compatible SSD configuration quality FAIL;
- **no model-level SSD rejection.**

Runner 30 is critical evidence: fixing our `1.7778×` pose-registration distortion materially improved pose adherence/lower limbs. Integration correctness is therefore a first-order variable and must be exhausted before blaming the model.

## Exact SSD status

Exact published Sprite Sheet Diffusion has **not** been reproduced locally because its custom SSD pose-guider checkpoint is not in the public release available to us.

Current route:

`Moore AnimateAnyone graph + Moore baseline pose guider/motion module + released SSD reference/denoising UNets`

This is a compatibility reconstruction, not exact SSD.

Correct classification:

- exact public SSD: **BLOCKED**;
- current Moore/SSD hybrid: runnable, current configuration insufficient, integration/model boundary still unresolved.

## Wan historical status

Wan-Animate-2 Base INT8 was genuinely run on 2026-09-04 and that tested configuration failed on weak locomotion transfer and smooth painted/video-diffusion appearance.

The evidence remains valid for that configuration, but the whole Wan model family was not exhaustively disproven. The earlier workspace cleanup was premature under the newly locked exhaustion protocol.

`D:\AI\WanAnimate2` should still be assumed deleted. **Do not rebuild it now.** The retained Moore/SSD branch must be exhausted first.

The erroneous 2026-09-07 Wan runner 35 remains withdrawn/deleted. There is currently no active runner 35.

## CURRENT NEXT GATE — MOORE BASELINE VS SSD SUBSTITUTION AUDIT

Stay in:

`Z:\AI\SpriteSheetDiffusionSpike`

Do not install another large model.

Next implementation must create one controlled diagnostic runner that:

1. runs pure Moore baseline weights with the same validated Exilada reference/pose package;
2. runs the Moore-compatible SSD substitution with **identical** reference, pose maps, seed, scheduler, frame count and sampling settings;
3. outputs side-by-side contact sheets/GIFs and a manifest of every differing weight/component;
4. audits pose-map representation/registration expected by the actual Moore pose guider;
5. reports whether pose adherence breaks before or after SSD weight substitution;
6. does not change gait art direction, hair simulation, chains or jiggle yet — this gate isolates the body-control/integration layer first.

After that A/B result, decide the next diagnostic inside the same model branch rather than switching models automatically.

## Operator action

No new command has been authored yet for this audit. First pull the corrected canonical state:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only
```

Then implement the Moore-baseline-vs-SSD A/B runner as the next gate.

## Cleanup

Retain the SSD workspace/models and runner-34 evidence until the exhaustion audit explicitly closes the branch.
