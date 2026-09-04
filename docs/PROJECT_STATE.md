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

Immediate gameplay baseline is an **elevated 2D belt-scroller / false 3D** rather than rigid isometric/top-down 360° presentation.

Character-art/animation feasibility is the current priority because it is the largest production risk; code capability is not the current unknown.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite.

Final visible art remains true modern pixel art. Simple high-resolution generation followed by resize/quantization is not an accepted final-sprite route.

## RefControl animation checkpoint

### V1 — strong identity, structural defects

V1 produced four one-shot key poses at `768×1024`, fixed seed `20260904`, with no artistic retry.

Result:

- identity retention: strong;
- four gait phases: visibly distinct;
- right-foot/toe anatomy: faulty in at least one frame;
- left arm: inconsistent;
- body proportions: small drift;
- chain/shackle continuity: unstable.

Verdict:

**CONDITIONAL PASS as upstream re-posing route; FAIL as production-ready walk.**

### V2 — anatomy improved, gait alternation collapsed

V2 deliberately changed only pose geometry + stricter anatomy/continuity prompt while preserving model, seed and inference settings.

The four V2 outputs were generated and visually reviewed.

What improved:

- feet/toe anatomy improved materially;
- arms improved materially;
- Exilada identity remained strong;
- general body stability improved.

Critical failure:

- `pose_00_contact_L_v2` and `pose_02_contact_R_v2` rendered as nearly the same pose;
- `pose_01_passing_L_v2` and `pose_03_passing_R_v2` rendered as nearly the same pose;
- the set therefore collapsed from four useful gait phases to effectively two repeated phase geometries.

Root cause:

V2 used nearly the same **screen-space skeleton silhouettes** for left/right phase pairs and relied too heavily on COCO left/right color/semantic labels. RefControl followed the visible geometry more strongly than the semantic side assignment.

Secondary failure remains:

- chain/shackle topology is still not rigidly stable between frames.

V2 verdict:

**FAIL as a usable walk cycle.**

Important positive finding:

**RefControl remains the strongest upstream character re-poser tested, because identity/anatomy quality is materially better than prior routes. The next correction must change actual screen-space geometry, not just COCO left/right semantics.**

## Current gate — V3 structural pose controls

Do not run another character inference yet.

V3 fixes the specific V2 failure before spending GPU time.

New tooling:

`tools/flux2-refcontrol-spike/08_prepare_v3_inputs.ps1`

V3 names:

- `pose_00_contact_L_v3`
- `pose_01_passing_L_v3`
- `pose_02_contact_R_v3`
- `pose_03_passing_R_v3`

V3 rules:

- four genuinely different screen-space skeleton geometries;
- no crossed-leg X geometry;
- support and swing legs visibly distinct;
- opposite arm geometry changes with gait phase;
- slight 3/4 side-facing-right asymmetry;
- all four controls must remain distinct even when COCO colors are removed.

The script enforces the last rule automatically by rendering a color-independent binary silhouette for each control and requiring **four unique silhouette hashes**.

### Exact next action

Run only STEP 8A:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\flux2-refcontrol-spike\08_prepare_v3_inputs.ps1" -Workspace "Z:\AI\Flux2RefControlSpike"
```

Expected outputs:

`Z:\AI\Flux2RefControlSpike\ComfyUI_windows_portable\ComfyUI\input\refcontrol_poses_v3\`

Expected manifest:

`Z:\AI\Flux2RefControlSpike\input_manifest_v3.json`

**STOP after STEP 8A. Do not run inference.** Share the four V3 skeleton PNGs for visual QA first.

## Workspace relocation — LOCKED

Current canonical workspace:

`Z:\AI\Flux2RefControlSpike`

Old workspace:

`D:\AI\Flux2RefControlSpike` — superseded.

Repository remains:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Gameplay-scale / Production Pixel Master gate — queued

Only after the upstream walk-pose route has four actually distinct, acceptable gait phases should the project return to gameplay-scale/native-raster validation.

High-resolution RefControl outputs remain motion/identity references; they are not automatically final pixel sprites.

## Rejected/stopped routes

- Sprite Sheet Diffusion — rejected;
- Wan-Animate-2 — rejected;
- paid hosted PixelLab/Pixel Engine/Retro Diffusion routes — stopped/disqualified;
- generic video diffusion as primary animation architecture — rejected;
- direct high-resolution generation as final pixel master — rejected;
- primitive Python/Pillow geometry as final artistic authoring — rejected.

## Target machine

- Windows 11;
- RTX 3060 12 GB;
- ~48 GB RAM;
- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`;
- workspace: `Z:\AI\Flux2RefControlSpike`.
