# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / LOCKED — COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME; RUNNER 34 EXPORT PASS / POSE-ONLY COMPLETE-MOTION FAIL; WAN-ANIMATE-2 REJECTED/CLOSED; NEXT AUTHORING ROUTE UNSELECTED**

## Presentation lock

The game uses an elevated arcade beat'em-up / belt-scroller false-3D presentation:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall at gameplay scale;
- first canonical locomotion family is screen-left and mostly lateral/three-quarter;
- gameplay-depth movement and z-order are world/runtime concerns, not extra north/south sprite families.

Runner 31 compared `60`, `72` and `84 deg` azimuth from travel heading. `60` was too frontal, `84` too profile-thin, and **`72 deg` is locked as the first screen-left gameplay locomotion baseline**. `90 deg` is pure profile.

## Final runtime representation — LOCKED

The runtime consumes **complete, already-composed character frames**:

`complete authored frames -> complete-character spritesheet PNG(s) + metadata -> ordinary sprite playback`

Every runtime frame contains the whole visible character state for that animation/variant. The runtime does **not** assemble the visible character from body/hair/clothing/armor/accessory layers.

Runtime character-layer assembly is **ABOLISHED/CLOSED**.

Any rig, mocap, pose-control, image/video model, layer separation, simulation or compositing exists only in the **offline authoring pipeline**.

## Complete-frame motion requirement — LOCKED

A valid exported animation must bake the whole visible motion state, including where present:

- body locomotion;
- soft-tissue/jiggle motion;
- hair secondary motion;
- base-clothing/binding motion;
- shackles/chains/restraints motion;
- accessories visible in the chosen state;
- all occlusion changes produced by those motions.

A body-only animation may be used as an internal diagnostic, but it is never the final/runtime sprite artifact.

## Initial Exilada state — LOCKED

Canonical initial-state visual reference:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines the Exilada's **entire initial visible state** for the current production proof: body, hair, base clothing/bindings, shackles/chains/restraints and other visible initial details.

## Equipment / armor variation — OPEN LATER GATE

The project still requires armor/equipment/accessory/damage variation, but the implementation strategy is not runtime character assembly.

Offline source assets may remain modular so variants can be authored efficiently. Each runtime artifact must still export as a **complete precomposed character spritesheet family/state**.

## Offline authoring principle

Offline authoring may internally separate body, hair, cloth, restraints, armor and other systems to control motion and variation. Those separations are production controls only; they must resolve into one temporally coherent complete-character frame sequence before export.

- modular offline control = allowed;
- modular visible runtime construction = closed.

## Retained motion work

G2/C1A remains useful as mechanical motion infrastructure:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight support/phase states.

Runner 32 V1 remained too generic. Runner 33 V2 improved projected body language but is not final walk approval; it may serve as provisional body timing for route proofs.

## Runner 34 complete-character proof — RESULT

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 proved that the toolchain can:

- animate from the full `exilada_master.png` reference;
- output full-character frames;
- remove the neutral background;
- preserve RGBA transparency;
- pack a complete-character spritesheet and metadata;
- play it through ordinary frame animation.

Therefore the **runtime/export architecture is viable**.

However the current Moore-compatible SSD temporal authoring method failed the complete-motion quality requirement when driven by body OpenPose only:

- hair is mostly frozen/warped rather than physically trailing;
- base cloth morphs but lacks convincing controlled lag;
- jiggle is not intentionally controllable/readable;
- ankle restraint/chain detaches and mutates into stepped artifacts;
- lower limbs/feet degrade in extreme phases;
- loop coherence remains weak.

This is not grounds to return to runtime layers. It means the current offline authoring route is insufficient.

## Wan-Animate-2 — REJECTED/CLOSED

Wan-Animate-2 Base INT8 ConvRot was already tested locally on 2026-09-04.

It was rejected for two decisive reasons:

1. driving locomotion transfer was too weak;
2. output read as smooth painted/video-diffusion imagery rather than the required modern pixel-art/game-art language.

Identity retention was comparatively decent, but that did not compensate for motion/style failure.

Do not revisit the same Wan route with a richer synthetic driver, seed search, stronger reference strength, prompt cosmetics or post-generation pixel filtering. A future revisit requires a **materially different model/checkpoint/integration** with evidence that both failure classes are addressed.

The isolated Wan model/runtime workspace was deleted after rejection. Repository scripts remain research history only.

## Erroneous runner-35 proposal — WITHDRAWN

A 2026-09-07 proposal to reuse Wan as runner 35 ignored the prior rejection/cleanup record. That proposal was invalid and its newly-created runner/helper files were removed from `main`.

No runner 35 is active.

## Next complete-motion route requirement — LOCKED, IMPLEMENTATION OPEN

The next authoring route must satisfy all of the following before it can become production:

- complete-character output per frame;
- body locomotion plus hair, cloth, jiggle and restraints/chains baked together;
- explicit/inspectable motion control where possible;
- stable attachment ownership and topology;
- native/discrete pixel/game-art preservation rather than painted video output plus a pixel filter;
- local/free/self-hosted preference unless explicitly changed;
- no large installation until the candidate has a discriminating reason to succeed where earlier routes failed.

Prior post-Wan research identified pixel-native skeleton/keyframe animation classes as more relevant than another generic video diffusion model. Those remain candidates, not approvals.

## SSD route status

Exact upstream SSD remains blocked by the unreleased custom multi-scale `pose_guider.pth`.

The Moore-compatible route remains useful evidence because it preserves Exilada identity reasonably well and follows body pose to a degree, but it is **insufficient as the sole complete-motion author when driven only by OpenPose body maps**.

## Closed routes / assumptions

Closed unless explicitly reopened:

- runtime construction of the visible character from body/hair/clothing/equipment layers;
- Wan-Animate-2 Base INT8 production route;
- hidden 3D render as final visible pixel art;
- independent unconstrained full-body redraw for each frame;
- C0 nearest-segment hard partition as production route;
- single-still whole-body chain/cage warp as gait solution;
- MPFB skinned body as mandatory visible guide;
- implicit return to isometric/multi-directional character production.

## Current validation question

The active question is:

> Which **non-rejected** authoring route can produce a complete Exilada animation with explicit motion fidelity, coherent secondary motion/attachments and the required native/discrete game-art look?

Do not answer that by rerunning Wan-Animate-2.
