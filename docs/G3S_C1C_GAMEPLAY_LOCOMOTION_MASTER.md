# G3S-C1C — Gameplay Locomotion Master

Status date: **2026-09-07**

Status: **72 DEG FACING LOCKED / V1 FAIL / V2 NOT FINAL, RETAINED AS PROVISIONAL BODY DRIVER / COMPLETE-MOTION DRIVER NOW PRIMARY BOTTLENECK**

## Purpose

C1A proved coherent eight-state human gait mechanics on the retained `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk`. C1C exists to convert that mechanical source into gameplay-appropriate Exilada locomotion.

Important distinction:

- C1A = gait/control sanity;
- C1C = animation art direction.

## Facing lock

Runner 31 compared `60`, `72` and `84 deg` azimuth from travel heading.

Decision:

- `60 deg` rejected as too frontal;
- `84 deg` rejected as too profile-thin;
- **`72 deg` selected and locked** as the first screen-left locomotion-facing baseline.

`90 deg` is pure profile in this convention.

## Runner 32 V1 — FAIL/CLOSED

V1 reduced bob/stride/arm pendulum and stabilized the head, but remained too close to generic mocap/human locomotion and did not achieve the desired Exilada-specific feminine body language.

## Runner 33 V2 — NOT FINAL / PROVISIONAL BODY DRIVER

V2 added restrained phase-weighted pelvic obliquity, mild pelvic yaw, torso/shoulder counterbalance, moderate stride compression, compact arm pendulum, swing-leg clearance and head stabilization.

Visual review still did not approve V2 as the final Exilada walk. The project deliberately stopped micro-adjusting the skeleton and used V2 as provisional body control for runner 34 so the real complete-character spritesheet could be tested.

That decision was correct: runner 34 exposed a larger bottleneck than the remaining body-walk polish.

## Runner 34 feedback to C1C

Runner 34 generated the full Exilada state and demonstrated that the body driver alone is not sufficient to define the complete animation.

The visible failure class is now dominated by **secondary whole-character motion control**:

- hair inertia/lag is not explicitly controlled;
- cloth motion is not explicitly controlled;
- chain/restraint trajectories are not explicitly controlled;
- jiggle/soft-tissue motion is not explicitly controlled;
- OpenPose body geometry leaves those systems to temporal prior/hallucination.

Therefore C1C body-motion refinement is no longer the immediate blocker for proving the production route.

## Current rule

Keep V2 and `72 deg` as the provisional body component of the next experiments unless a visible full-character test proves a specific body-motion change necessary.

Do **not** resume blind skeleton-only micro-adjustment before richer complete-motion control exists.

The final walk still requires later polish, but that polish should be reviewed in the context of the full moving character rather than a stick-figure alone.

## Complete-character requirement

The final locomotion clip must read as one baked character sequence containing:

- body movement;
- soft-tissue/jiggle motion;
- hair secondary motion;
- base clothing/binding motion;
- shackles/chains/restraints/accessories motion;
- resulting occlusions.

Skeleton-only work is diagnostic and does not constitute the runtime artifact.

## Long-term target locomotion principles

The eventual production walk should still prioritize:

- clear lateral travel;
- adult feminine Exilada body language without catwalk caricature;
- grounded contacts;
- readable phase progression;
- stable head/torso for action readability;
- natural weight transfer;
- compact but believable stride;
- whole-character secondary motion that supports rather than obscures locomotion.

## Next dependency

Before revisiting fine body-walk art direction, establish a **complete-motion driver** that can explicitly control or constrain the major secondary masses while retaining V2/72-degree body timing as a provisional base.

See:

- `docs/PROJECT_STATE.md`;
- `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`;
- `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`.
