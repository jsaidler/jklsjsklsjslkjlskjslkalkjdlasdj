# G3S — Animation Architecture Lock

Status date: **2026-09-06**

Status: **CANONICAL / LOCKED — CONVENTIONAL 2D SPRITESHEET RUNTIME; SSD SOURCE-AUTHORING SPIKE ACTIVE**

## Presentation constraint that makes animation feasible

The project is **not** targeting true isometric multi-directional character animation.

That option was deliberately abandoned in favor of an elevated arcade beat'em-up / belt-scroller presentation because it radically reduces character-production complexity while preserving a walkable gameplay-depth band.

Locked presentation consequences:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist standing body height about `128 px`;
- first canonical visible family: screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime world-depth movement and z-order are separate from visible facing;
- do not multiply view families unless an explicit later gate proves one necessary.

This simplification is a production contract, not a temporary test convenience.

## Final runtime representation — LOCKED

The game uses conventional 2D frame animation:

`approved 2D animation frames -> spritesheet PNG(s) + metadata -> ordinary sprite playback`

Each action is a deterministic frame sequence arranged in a row/block or an equivalent atlas region. A single giant PNG is not mandatory; grouped sheets such as locomotion/combat/damage/contextual are acceptable.

Runtime does **not** require:

- a 3D skeleton;
- MPFB;
- a segmented-body puppet;
- diffusion;
- per-frame generation.

Any hidden rig, mocap, pose-control or image model belongs only to the **offline authoring pipeline**.

## Offline source-authoring principle

The source-authoring method is allowed to change as long as the resulting approved frames are persistent 2D assets and the method does not silently recreate the complexity that the belt-scroller decision removed.

Current authoring spike:

**Sprite Sheet Diffusion (SSD)** using the Exilada master as appearance reference plus pose/motion control.

Canonical spike document:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

## Retained motion work

G2/C1A motion infrastructure remains useful as an **offline motion/pose source**:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- approved C1A eight-state walk cycle.

It is not a runtime dependency and is not mandatory if a future spritesheet authoring tool provides a better direct action-generation workflow.

## Historical segmented-puppet route

The minimal segmented 2D puppet remains documented as a historical/experimental route, but it is **not the current production route** after the explicit decision to return to conventional spritesheet production.

Do not continue runner 23 unless that route is explicitly reopened.

## Closed routes

The following remain closed unless explicitly reopened:

- hidden 3D render -> final visible pixel art;
- independent unconstrained full-body generative redraw for each frame (the failed Flux2 walk proof);
- C0 V1 nearest-segment hard partition with exposed rigid joints;
- single-still whole-body chain/cage warp -> gait;
- MPFB skinned body as mandatory hidden guide;
- implicit return to isometric/multi-directional character production.

## Current validation question

The active question is now simple:

> Can a local sprite-animation model generate a coherent action sequence of the Exilada from the approved master strongly enough that the resulting frames can be frozen into a conventional spritesheet?

Current candidate under test: **Sprite Sheet Diffusion**.

## Hair / clothing / equipment

The user-supplied Exilada master may be used as the complete identity/design reference for spritesheet generation. Earlier body-only/hair-deferred staging remains historical context, but the SSD spike is allowed to test the complete master because its purpose is direct spritesheet source generation rather than layered puppet construction.

If the SSD route passes, modular runtime layering for hair/equipment is a later production optimization, not a prerequisite for proving the base spritesheet pipeline.
