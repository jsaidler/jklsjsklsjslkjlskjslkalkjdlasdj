# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / LOCKED — CONVENTIONAL 2D SPRITESHEET RUNTIME; 72 DEG LOCOMOTION FACING LOCKED; GAMEPLAY WALK AUTHORING ACTIVE; SSD VISIBLE AUTHORING PAUSED**

## Presentation constraint that makes animation feasible

The project is **not** targeting true isometric multi-directional character animation.

That option was deliberately abandoned in favor of an elevated arcade beat'em-up / belt-scroller presentation because it radically reduces character-production complexity while preserving a walkable gameplay-depth band.

Locked presentation consequences:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist standing body height about `128 px`;
- first canonical visible family is screen-left and mostly lateral/three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime world-depth movement and z-order are separate from visible facing;
- do not multiply view families unless an explicit later gate proves one necessary.

### Gameplay locomotion facing — LOCKED 2026-09-07

Runner 31 compared `60`, `72` and `84 deg` azimuth from travel heading using the same retained real gait and camera baseline.

Decision:

- `60 deg` rejected as too frontal;
- `84 deg` rejected as too profile-thin for the first canonical baseline;
- **`72 deg` selected and locked as the first screen-left gameplay locomotion facing baseline**.

In this convention `90 deg` is pure side profile. The selected `72 deg` family remains slightly three-quarter while prioritizing lateral gait readability.

The old `45 deg` C1A projection remains historical/mechanical only and is not the production locomotion baseline.

This facing lock does not require every combat action to preserve exactly the same torso yaw if an action-specific pose later needs more exposure for gameplay readability.

## Final runtime representation — LOCKED

The game uses conventional 2D frame animation:

`approved 2D animation frames -> spritesheet PNG(s) + metadata -> ordinary sprite playback`

Each action is a deterministic frame sequence arranged in a row/block or equivalent atlas region.

Runtime does **not** require:

- a 3D skeleton;
- MPFB;
- a segmented-body puppet;
- diffusion;
- per-frame generation.

Any hidden rig, mocap, pose-control or image model belongs only to the offline authoring pipeline.

## Offline source-authoring principle

The source-authoring method may change as long as approved persistent 2D assets result and the method does not silently recreate the directional complexity the belt-scroller decision removed.

The authoring pipeline separates two questions:

1. **motion design** — the exact gameplay pose sequence and facing must be approved first;
2. **visible rendering/authoring** — a model/tool must then reproduce that approved motion without destroying anatomy/identity.

Do not use image-model parameter tuning to compensate for an unapproved locomotion design.

## Retained motion work

G2/C1A remains useful as a mechanical human-gait source:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight support/phase states.

C1A proves gait timing and skeletal consistency. It is **not** automatically the final gameplay locomotion master.

Current locomotion document:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Current skeleton-only runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

Runner 32 keeps the real gait timing/support sequence but applies a bounded deterministic gameplay locomotion overlay at the locked `72 deg` facing. No visible diffusion inference should run until this walk master passes skeleton-only review.

## SSD spike status

Canonical spike document:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Facts retained:

- exact upstream SSD is blocked by the unreleased custom multi-scale pose-guider checkpoint;
- the Moore-compatible fallback is technically runnable;
- runner 29 visually failed;
- runner 30 corrected a real pose-registration defect and clearly improved pose response/lower-limb reconstruction;
- runner 30 still remained far below production quality and exposed the need for gameplay-specific locomotion art direction.

Therefore SSD visible authoring is **paused**, not production-approved and not currently closed. It may be revisited after C1C provides a correct locomotion master.

## Hair / clothing / equipment

The direct complete-master SSD test was useful diagnostically, but runner 30 still produced unstable restraint/accessory fragments.

For locomotion definition, body motion comes first. Hair, clothing, bindings, shackles/chains and other secondary masses are downstream authoring/layer problems and must not dictate the base gait.

This is consistent with the broader body-first production principle.

## Historical segmented-puppet route

The minimal segmented 2D puppet remains historical/experimental and is not the current runtime route. Do not continue runner 23 unless explicitly reopened.

## Closed routes

The following remain closed unless explicitly reopened:

- hidden 3D render -> final visible pixel art;
- independent unconstrained full-body generative redraw for each frame;
- C0 V1 nearest-segment hard partition with exposed rigid joints;
- single-still whole-body chain/cage warp -> gait;
- MPFB skinned body as mandatory hidden guide;
- implicit return to isometric/multi-directional character production.

## Current validation question

The active question is:

> Can the retained real gait be authored into a natural, grounded and combat-readable Exilada walk at the locked `72 deg` belt-scroller facing without losing human phase/support integrity?

Solve that skeleton-only first; then judge visible authoring against it.
