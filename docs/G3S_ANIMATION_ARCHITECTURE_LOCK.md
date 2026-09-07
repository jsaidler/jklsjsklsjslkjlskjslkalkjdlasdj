# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / LOCKED — COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME; MODEL EXHAUSTION REQUIRED BEFORE ROUTE SWITCH; MOORE+SSD AUDIT ACTIVE**

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

The master defines the Exilada's **entire initial visible state** for the current production proof.

## Equipment / armor variation — OPEN LATER GATE

The project still requires armor/equipment/accessory/damage variation, but the implementation strategy is not runtime character assembly.

Offline source assets may remain modular so variants can be authored efficiently. Each runtime artifact must still export as a **complete precomposed character spritesheet family/state**.

## Offline authoring principle

Offline authoring may internally separate body, hair, cloth, restraints, armor and other systems to control motion and variation. Those separations are production controls only; they must resolve into one temporally coherent complete-character frame sequence before export.

- modular offline control = allowed;
- modular visible runtime construction = closed.

## Model-exhaustion rule — LOCKED 2026-09-07

Do not switch animation/generation models simply because one tested configuration produces a bad result.

A route can be closed at model/task level only after:

1. its official/reference behavior is reproduced locally where practical;
2. loader/checkpoint/integration semantics are verified;
3. preprocessing/input-domain correctness is verified;
4. project task is tested first in a controlled/easier matched form;
5. meaningful parameters are tested systematically with fixed seed/input and one variable at a time;
6. the same decisive failure persists across multiple valid configurations.

Until then classify problems as infrastructure, integration, configuration or BLOCKED rather than “model cannot do it.”

Cleanup of large model assets occurs only after genuine abandonment/model-task failure or an explicit decision that a blocked route is no longer worth retaining.

## Retained motion work

G2/C1A remains useful as mechanical motion infrastructure:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight support/phase states.

Runner 32 V1 remained too generic. Runner 33 V2 improved projected body language but is not final walk approval; it may serve as provisional body timing for route proofs.

## Runner 34 complete-character proof — RESULT

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 proved the runtime/export architecture:

- full-character frames from the complete master;
- RGBA transparency;
- complete-character spritesheet + metadata;
- ordinary sprite playback.

Its visible temporal result was poor for production, but the correct classification is:

> **current Moore-compatible SSD configuration FAIL; model capability unresolved.**

The distinction matters because runner 30 already demonstrated that a preprocessing/pose-registration mistake in our own integration materially degraded the result before being fixed.

## SSD route status

Exact upstream SSD remains **BLOCKED** because the public release does not include the custom SSD pose-guider checkpoint required by the exact published graph.

The current runnable route is a compatibility reconstruction:

`Moore AnimateAnyone graph + Moore baseline pose guider/motion module + released SSD reference/denoising UNets`

Therefore runner 34 is not a valid experiment for concluding that the exact published SSD method cannot perform the task.

The active gate is to exhaust meaningful integration questions in the retained Moore/SSD environment before changing models.

## Moore/SSD exhaustion audit — CURRENT

The audit must isolate components instead of changing several variables at once:

1. establish pure Moore baseline behavior with Moore weights + our validated preprocessing;
2. A/B substitute only the released SSD reference/denoising UNets;
3. validate actual pose-guider input domain/registration;
4. identify whether the Moore pose guider is the dominant compatibility bottleneck;
5. use staged diagnostics for body motion, identity/topology, hair/cloth, restraints/chains, jiggle and loop;
6. only after a repeatable ceiling decide whether recovering/retraining a compatible SSD pose guider is justified.

Controlled parameter sweeps are allowed as diagnostics if seed/input are fixed and one meaningful variable changes at a time. Random reroll/seed hunting is not an acceptable production method.

## Wan-Animate-2 historical status — CONFIGURATION FAIL / NOT ACTIVE

Wan-Animate-2 Base INT8 ConvRot was tested locally on 2026-09-04 and the tested configuration had two major failures:

- weak locomotion transfer;
- smooth painted/video-diffusion appearance instead of the required game-art language.

Those observations remain valid. However the earlier project classification of the **entire model family** as conclusively rejected was stronger than the evidence justified.

The earlier test did not first establish a documented official/reference baseline in the exact local integration and then systematically isolate the conditioning/input variables before closure.

The Wan workspace was already deleted under the earlier cleanup decision. It is **not active** and should not be rebuilt while Moore/SSD still has unresolved integration questions. A later Wan revisit, if chosen after SSD exhaustion, must begin from an official/reference baseline rather than directly from another Exilada artistic test.

## Erroneous runner-35 proposal — WITHDRAWN

The 2026-09-07 Wan runner-35 proposal remains withdrawn/deleted. The corrected lesson is not “never use Wan again”; it is “do not jump to Wan before the current model branch is exhausted, and do not rerun it without a proper baseline protocol.”

No runner 35 is active.

## Closed routes / assumptions

Closed unless explicitly reopened:

- runtime construction of the visible character from body/hair/clothing/equipment layers;
- hidden 3D render as final visible pixel art;
- independent unconstrained full-body redraw for each frame;
- C0 nearest-segment hard partition as production route;
- single-still whole-body chain/cage warp as gait solution;
- MPFB skinned body as mandatory visible guide;
- implicit return to isometric/multi-directional character production.

Exact public SSD remains BLOCKED; Wan remains inactive with a failed historical configuration. Neither is currently entitled to the stronger claim “model family proven incapable.”

## Current validation question

> Is the current Moore/SSD result limited by the model family, or by our compatibility reconstruction/input/integration — and can we prove which one before switching models?
