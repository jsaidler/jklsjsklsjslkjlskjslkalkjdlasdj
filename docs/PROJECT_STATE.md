# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/PIXEL_ART_PRODUCTION.md`
6. `docs/ANIMATION_PIPELINE.md`
7. current tooling under `tools/`

After every material step: update thematic docs + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity

The game is a **systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a living world**.

Immediate gameplay baseline is an **elevated 2D belt-scroller / false 3D**. Character-art/animation feasibility remains the current priority because it is the largest production risk.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite. Final visible art remains true modern pixel art; simple high-resolution generation followed by resize/quantization is not accepted as the final-sprite route.

## RefControl walk checkpoint

### V1 — CONDITIONAL PASS upstream / FAIL final walk

V1 proved that FLUX.2 Klein + RefControl Pose can preserve the Exilada substantially better than prior routes.

Strengths:

- strong identity retention;
- four gait phases visibly distinct.

Defects:

- right-foot/toe error;
- left-arm inconsistency;
- small body drift;
- unstable chain/shackle topology.

### V2 — FAIL as walk

V2 improved feet, arms and body stability, but the left/right gait pairs collapsed:

- `contact_L` ≈ `contact_R`;
- `passing_L` ≈ `passing_R`.

Root cause: V2 left/right controls had nearly the same **screen-space geometry** and relied too heavily on COCO side colors/labels. RefControl followed visible geometry more strongly than the semantic reassignment.

Decision: do not expand V2. Build V3 with genuinely different screen-space skeletons.

## V3 — current gate

### STEP 8A — V3 controls: PASS

The user executed:

`tools/flux2-refcontrol-spike/08_prepare_v3_inputs.ps1`

against canonical workspace:

`Z:\AI\Flux2RefControlSpike`

Observed result:

- `generated_v3_poses=4`;
- `silhouette_uniqueness=PASS`;
- no model loaded;
- no inference performed.

Observed control hashes:

- `pose_00_contact_L_v3` — PNG `48f7988c8107c6ac741908d8604347423fe57b18df2c93ebf5f55900333193fa` — silhouette `f24c1ddcd7e396c47e946109465756ae86d57bbdb9d90b9d0caf16bccbf52ba0`;
- `pose_01_passing_L_v3` — PNG `5a06ba6cc32e76da4e1a8aad42e67a8c5a0258cbd9eb7464c54a4800dccfc465` — silhouette `a5e260fb5119d47ca58886d74f982cdcee01906563e7e37b536936b91510ee02`;
- `pose_02_contact_R_v3` — PNG `637ea37ebe25b43134d6374ec3e334646f9034b39c6e6b35be3c2ddb9cd08650` — silhouette `aa94a2f6a7d2908dfb20078aee8146b13b60d0b068342a0b2df89bb0096dfabd`;
- `pose_03_passing_R_v3` — PNG `ff98c35f70f49136c9cb55c0d6f93fdbf5b6d449d164402ee0348ba72dcdc58a` — silhouette `476ff26d61e80d05140eda6c75862280c1fc4adcd96d6159de334c11220d4098`.

Visual QA of the four controls: **PASS to inference**.

Important observation: unlike V2, all four phases are also visibly different without relying on COCO colors:

- `contact_L`: anatomical left leg is physically ahead in screen space;
- `passing_L`: right leg supports, left leg is visibly lifted/passing;
- `contact_R`: anatomical right leg is physically ahead;
- `passing_R`: left leg supports, right leg is visibly lifted/passing.

## STEP 8B — V3 inference tooling READY

Runner:

`tools/flux2-refcontrol-spike/09_run_v3.ps1`

V3 intentionally isolates one change from V2:

**changed:** screen-space COCO-18 gait geometry.

**unchanged:**

- canonical Exilada reference;
- FLUX.2 Klein Base 4B FP8;
- RefControl Pose LoRA strength `1.0`;
- V2 correction prompt contract;
- seed `20260904`;
- `768×1024`;
- `20` steps;
- CFG `5.0`;
- Euler;
- exactly one artistic submission per pose;
- no retry, seed fishing, inpainting or interpolation.

Runner safety:

- uses JSON serialization depth safely below the Windows PowerShell limit;
- validates V3 manifest + four unique silhouette hashes before inference;
- refuses to run if V3 sentinel, manifest or V3 PNG outputs already exist;
- writes request, accepted `prompt_id`, history and final run manifest evidence.

### Exact next action

Run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\flux2-refcontrol-spike\09_run_v3.ps1" -Workspace "Z:\AI\Flux2RefControlSpike"
```

Then **STOP** and share the four generated V3 images plus:

`Z:\AI\Flux2RefControlSpike\run_v3\step8b_v3_run_manifest.json`

Next decision is V2-vs-V3 QA on gait alternation, anatomy, body stability and chain continuity.

## Workspace relocation — LOCKED

Current canonical workspace:

`Z:\AI\Flux2RefControlSpike`

Old workspace:

`D:\AI\Flux2RefControlSpike` — superseded.

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Gameplay-scale / Production Pixel Master gate — queued

Only after the upstream walk route demonstrates four distinct acceptable phases do we return to gameplay-scale/native-raster validation under the elevated belt-scroller projection.

High-resolution RefControl outputs are motion/identity references; they are not automatically final pixel sprites.

## Rejected/stopped routes

- Sprite Sheet Diffusion — rejected;
- Wan-Animate-2 — rejected;
- paid hosted PixelLab/Pixel Engine/Retro Diffusion routes — stopped/disqualified;
- generic video diffusion as primary animation architecture — rejected;
- direct high-resolution generation as final pixel master — rejected;
- primitive Python/Pillow geometry as final artistic authoring — rejected.
