# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / LOCKED — COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME; RUNNER 34 EXPORT PASS / POSE-ONLY COMPLETE-MOTION FAIL; RUNNER 35 WAN COMPLETE-MOTION PROOF ACTIVE**

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

Runner 32 V1 remained too generic. Runner 33 V2 improved the projected body language but was not approved as the final walk. It is currently retained as a provisional body-motion/timing source for complete-character route tests.

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

## Complete-motion driver requirement — LOCKED

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

## Runner 35 Wan-Animate-2 complete-motion proof — CURRENT

Runner:

`tools/structured-2d-character-pipeline/35_run_exilada_wan_animate2_complete_motion_proof.ps1`

Runner 35 implements the next discriminant without changing runtime architecture.

### Offline driver

A deterministic control proxy is rendered as a `17`-frame `384×576` / `16 fps` video:

- `16` playable samples from the provisional V2 loop at locked `72 deg`;
- one repeated first frame at the end as explicit closure target;
- body motion;
- delayed heavy rear/front hair masses;
- base hip-wrap/cloth lag;
- subtle soft-body lag signal;
- persistent left-wrist shackle/chain motion;
- persistent left-ankle shackle/chain motion.

The proxy is not final art. It exists only to place whole-character temporal information into the driving video.

### Appearance vs motion ownership

- `exilada_master.png` owns final character appearance/state;
- the complete-motion driver owns desired motion relationships;
- Wan-Animate-2 is tested as the transfer mechanism;
- output is still baked into complete spritesheet cells before runtime.

### Wan route

Runner 35 reuses the existing `D:\AI\WanAnimate2` Base environment with official `wan_animate_2_int8_convrot.safetensors`, UMT5 FP8, CLIP Vision H and Wan VAE. No distillation LoRA is allowed in this proof. Generation remains `384×576`, `17` frames, seed `42`, Euler, shift `5`, `20` steps, CPU cache for the RTX 3060 12 GB target.

Runner 35 does not silently download missing models.

### Export

Wan frame 17 is closure evidence only. Frames 1–16 become:

- complete RGBA frames;
- one `4×4` complete-character spritesheet;
- full-resolution preview GIF;
- approximate `128 px` gameplay preview GIF;
- metadata declaring `runtime_character_layer_assembly=false`.

### Kill rule

Continue only if the richer driver produces a **material** improvement over runner 34 in hair inertia, cloth lag, jiggle/soft motion, chain ownership/trajectory, feet/lower-leg stability, identity and loop coherence.

If not, close the Wan complete-video branch in its current form. Do not use seed fishing, CFG sweeps or cosmetic prompt tuning to manufacture a marginal pass.

## SSD route status

Exact upstream SSD remains blocked by the unreleased custom multi-scale `pose_guider.pth`.

The Moore-compatible route remains useful evidence because it preserves Exilada identity reasonably well and follows body pose to a degree, but it is now classified as **insufficient as a complete-motion author when driven only by OpenPose body maps**.

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

> Does direct full driving-video conditioning with explicit whole-character secondary motion produce a materially better complete Exilada spritesheet than the pose-only runner-34 route?

Runner 35 answers that question.
