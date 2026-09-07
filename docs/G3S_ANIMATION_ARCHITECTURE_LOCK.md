# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / LOCKED — COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME; RUNNER 34 EXPORT PASS / POSE-ONLY COMPLETE-MOTION FAIL; RICH COMPLETE-MOTION DRIVER REQUIRED NEXT**

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

This distinction is critical:

- modular offline control = allowed;
- modular visible runtime construction = closed.

## Retained motion work

G2/C1A remains useful as mechanical motion infrastructure:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight support/phase states.

Runner 32 V1 remained too generic. Runner 33 V2 improved the projected body language but was not approved as the final walk. It was intentionally used as a provisional motion driver so the project could test a real full-character spritesheet.

## Runner 34 complete-character proof — RESULT

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 proved that the toolchain can:

- animate from the full `exilada_master.png` reference;
- output eight full-character frames;
- remove the neutral background;
- preserve RGBA transparency;
- pack a complete-character `4×2` spritesheet and metadata;
- play it through ordinary frame animation.

Therefore the **runtime/export architecture is viable**.

However the current temporal authoring method failed the complete-motion quality requirement. With only body OpenPose control, the Moore-compatible SSD route does not reliably produce the required secondary systems:

- hair is mostly frozen/warped rather than physically trailing;
- base cloth morphs but lacks convincing inertial cloth response;
- jiggle is not intentionally controllable/readable;
- the ankle restraint/chain becomes detached and mutates into dark stepped artifacts in middle frames;
- lower limbs/feet still degrade in extreme phases;
- the cycle does not yet read as a coherent production walk.

This is **not** grounds to return to runtime layers. It means the offline motion-control signal is too weak.

## Complete-motion driver requirement — LOCKED NEXT DIRECTION

The next complete-character authoring route must supply richer motion information than a body stick-figure pose map.

The offline motion driver must explicitly contain or constrain:

- skeletal/body motion;
- hair mass inertia;
- base-cloth deformation/lag;
- restraint/chain trajectories;
- soft-tissue/jiggle where required;
- moving silhouette and occlusion relationships.

Acceptable offline sources may include a hidden proxy rig, deterministic secondary solvers, simulation, or a full driving video. The visible appearance reference remains `exilada_master.png`.

A hidden 3D/proxy motion source is allowed **only as motion/control infrastructure**. It does not reopen hidden-3D-render-as-final-art.

## SSD route status

Exact upstream SSD remains blocked by the unreleased custom multi-scale `pose_guider.pth`.

The Moore-compatible route remains useful evidence because it preserves Exilada identity reasonably well and follows body pose to a degree, but it is now classified as **insufficient as a complete-motion author when driven only by OpenPose body maps**.

Do not burn time on broad CFG/seed/resolution sweeps before adding richer whole-character control.

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

The active question is now:

> Can a richer complete-motion driver move body, hair, cloth, jiggle and restraints coherently while `exilada_master.png` continues to control the final complete-character appearance, producing a baked spritesheet fit for ordinary runtime playback?

That is the next route-level proof.
