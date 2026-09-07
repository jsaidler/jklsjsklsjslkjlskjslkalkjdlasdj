# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / LOCKED — COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME; 72 DEG LOCOMOTION FACING LOCKED; INITIAL MASTER-DRIVEN PLAYABLE PROOF ACTIVE**

## Presentation lock

The game uses an elevated arcade beat'em-up / belt-scroller false-3D presentation:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall at gameplay scale;
- first canonical locomotion family is screen-left and mostly lateral/three-quarter;
- gameplay-depth movement and z-order are world/runtime concerns, not extra north/south sprite families.

Runner 31 compared `60`, `72` and `84 deg` azimuth from travel heading. `60` was too frontal, `84` too profile-thin, and **`72 deg` is locked as the first screen-left gameplay locomotion baseline**. `90 deg` is pure profile. The historical C1A `45 deg` view remains only a mechanical sanity projection.

## Final runtime representation — LOCKED

The runtime consumes **complete, already-composed character frames**:

`complete authored frames -> complete-character spritesheet PNG(s) + metadata -> ordinary sprite playback`

Every visible sprite frame contains the whole character state for that animation/variant. The runtime does **not** assemble the character from body/hair/clothing/armor/accessory layers.

Runtime character-layer assembly is therefore **ABOLISHED/CLOSED**.

The runtime does not require:

- a 3D skeleton;
- MPFB;
- segmented-body puppets;
- diffusion;
- per-frame generation;
- body/hair/clothing/equipment compositing.

Any rig, mocap, pose-control, image/video model, layer separation, simulation or compositing exists only in the **offline authoring pipeline**.

## Complete-frame motion requirement — LOCKED

The animation is not only skeletal locomotion. The exported frame sequence must bake the whole visible motion state, including where present:

- body locomotion;
- soft-tissue/jiggle motion;
- hair secondary motion;
- base-clothing/binding motion;
- shackles/chains/restraints motion;
- accessories visible in the chosen character state;
- all occlusion changes produced by those motions.

A body-only animation may be used as an internal diagnostic, but it is **never** the production/runtime sprite artifact.

## Initial Exilada state — LOCKED

Canonical initial-state visual reference:

`assets/source/characters/exilada/reference/exilada_master.png`

For the first complete-character animation proof, this master is the reference for the Exilada's **entire initial visible state**. It includes the appearance that must be preserved and animated as one character: body, hair, base clothing/bindings, shackles/chains/restraints and other visible initial-state details.

The master defines the initial character state, not merely a body reference.

## Equipment / armor variation — OPEN LATER GATE

The project still needs character-state variation across armor, equipment, accessories, damage and exposure, but the implementation strategy is **not** runtime body-layer assembly.

The production source may remain modular offline so variants can be authored efficiently, but each runtime artifact must be exported as a **complete precomposed character spritesheet family/state**.

Possible later strategies include offline regeneration/composition of complete variants, bounded state families, masks or other production optimizations. No specific variant system is locked yet beyond this invariant:

> the runtime plays complete-character frames and does not construct the visible character from interchangeable body/equipment layers.

## Offline authoring principle

The authoring pipeline may internally separate body, hair, cloth, restraints, armor and other systems to control motion and variation. Those separations are production tools only. Before export they must resolve into one temporally coherent complete-character frame sequence.

This means secondary-motion quality is part of the animation test itself. Frozen hair, detached chains, migrating clothing or missing jiggle are not deferred runtime-layer problems; they are visible authoring failures in the baked sequence.

## Retained motion work

G2/C1A remains useful as mechanical motion infrastructure:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight support/phase states.

Runner 32 V1 and runner 33 V2 explored projected gameplay-walk art direction. Neither is treated as final animation mastery. The user has explicitly prioritized generating a full spritesheet now to determine whether the complete-character authoring route works in practice.

The current provisional motion driver for that proof is runner-33 V2 at the locked `72 deg` facing. It is **provisional input**, not final walk approval.

## Current complete-character proof

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Purpose:

- use `exilada_master.png` as the complete initial-state appearance reference;
- use the current 8-frame `72 deg` V2 walk guide as provisional motion control;
- run the proven Moore-compatible SSD fallback;
- require hair/clothing/jiggle/restraints/accessories to move as part of the same temporal generation;
- export eight complete RGBA frames;
- pack them into a complete-character spritesheet + metadata;
- visually judge whether this route can produce a usable whole-character animation.

This proof intentionally stops delaying visible generation for further skeleton micro-adjustment.

## SSD route status

Exact upstream SSD remains blocked because the public release omits the custom multi-scale `pose_guider.pth`. The Moore-compatible fallback remains technically runnable and runner 30 proved that corrected pose registration improves visible pose response.

Runner 34 reuses that working route with the complete master and the current gameplay motion guide. The test is now explicitly about **whole-character temporal authoring**, including secondary motion.

## Closed routes / assumptions

Closed unless explicitly reopened:

- runtime construction of the visible character from body/hair/clothing/equipment layers;
- hidden 3D render as final visible pixel art;
- independent unconstrained full-body redraw for each frame;
- C0 nearest-segment hard partition as production route;
- single-still whole-body chain/cage warp as gait solution;
- MPFB skinned body as mandatory visible guide;
- implicit return to isometric/multi-directional character production.

## Current validation question

The immediate question is now:

> Can the complete initial-state Exilada master be animated into a coherent eight-frame walk spritesheet in which body motion, jiggle, hair, base clothing and restraints/accessories all read as one believable baked character sequence?

That answer must come from the actual complete-character spritesheet, not from more skeleton-only refinement.
