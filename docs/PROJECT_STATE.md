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

Old provisional production values such as ~64 px visible height / `96×96` idle canvas / eight mandatory directions are superseded after the belt-scroller decision.

## Current animation checkpoint

### FLUX.2 Klein + RefControl Pose V1

This is the strongest route tested so far.

STEP 6 was actually executed successfully; any older statement that the project is still pre-inference is obsolete.

Run properties:

- four one-shot generations;
- fixed seed `20260904`;
- `768×1024`;
- no retry, fallback, inpainting, interpolation or seed fishing.

Runtime result: **PASS**.

Visual result: **CONDITIONAL PASS / not production-ready**.

Strengths:

- strongest Exilada identity retention obtained so far;
- four gait phases are clearly different;
- overall anatomy and clothing/hair coherence are substantially better than prior SSD/Wan attempts.

Blocking defects:

1. right-foot/toe orientation error in at least one frame;
2. left-arm inconsistency;
3. small inter-frame body-proportion drift;
4. chain/shackle side/topology drift.

Decision:

**Keep RefControl as the lead upstream re-posing route and run one controlled correction round.**

## Current exact gate — V2 correction run

Do not change models or search seeds.

### Unchanged variables

- Exilada reference;
- FLUX.2 Klein Base 4B FP8;
- RefControl Pose LoRA strength 1.0;
- seed `20260904`;
- `768×1024`;
- 20 steps;
- CFG 5.0;
- Euler;
- one prompt submission per pose.

### Changed variables only

1. cleaner COCO-18 skeleton geometry:
   - no arms crossing through torso centerline;
   - no crossed-leg X pose;
   - larger limb separation;
2. stricter prompt:
   - correct feet/toe direction toward screen-right;
   - coherent left/right arms;
   - fixed body dimensions;
   - exact chain/shackle topology from identity reference.

RefControl officially expects COCO-18, so toe/heel joints cannot simply be added to the control skeleton. Foot correction must be tested through less ambiguous ankle/knee geometry plus prompt constraints.

### Tooling

Prepare V2 inputs:

`tools/flux2-refcontrol-spike/06_prepare_v2_inputs.ps1`

Then run V2 once:

`tools/flux2-refcontrol-spike/07_run_v2.ps1`

Expected V2 output directory:

`D:\AI\Flux2RefControlSpike\ComfyUI_windows_portable\ComfyUI\output\flux2_refcontrol_v2`

Expected manifest:

`D:\AI\Flux2RefControlSpike\run_v2\step7_v2_run_manifest.json`

## V2 next decision

After four V2 images exist, compare against V1 on:

- foot correctness;
- left-arm correctness;
- body-proportion stability;
- chain/shackle continuity;
- Exilada identity retention;
- gait-phase readability.

Do not proceed to eight frames, inbetweening or final gameplay sprite authoring before this comparison.

## Gameplay-scale / Production Pixel Master gate — queued after V2

The belt-scroller gameplay-scale test remains necessary, but it is now **after** V2 structural correction.

After V2 determines whether the upstream re-poser is trustworthy, test the accepted motion/reference frames in a representative gameplay composition to establish:

- real Exilada on-screen height;
- native gameplay raster suitability (provisional `640×360`);
- safe action bounds;
- final Production Pixel Master dimensions;
- required facing families.

High-resolution RefControl outputs may serve as motion/identity references; they are not automatically final pixel sprites.

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
- workspace: `D:\AI\Flux2RefControlSpike`.

## Exact next action

Pull `main`, run `06_prepare_v2_inputs.ps1`, inspect the four V2 skeleton PNGs if desired, then run `07_run_v2.ps1` exactly once. Share the four generated V2 images plus `step7_v2_run_manifest.json` for comparative QA.
