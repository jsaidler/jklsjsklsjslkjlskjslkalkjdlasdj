# G3S-C1C — Gameplay Locomotion Master

Status date: **2026-09-07**

Status: **72 DEG FACING LOCKED / V1 FAIL / V2 PROVISIONAL MOTION DRIVER FOR COMPLETE-CHARACTER SPRITESHEET PROOF**

## Purpose

C1A proved coherent eight-state human gait mechanics on the retained `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk`. C1C exists to convert that mechanical source into gameplay-appropriate Exilada locomotion.

The important distinction remains:

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

## Runner 33 V2 — NOT FINAL / RETAINED AS PROVISIONAL DRIVER

V2 added:

- restrained phase-weighted pelvic obliquity;
- mild pelvic yaw;
- torso/shoulder counterbalance;
- moderate stride compression;
- compact arm pendulum;
- swing-leg clearance;
- head stabilization.

The generated skeleton was still not approved as the final walk master. However the user explicitly chose to stop delaying the first spritesheet for further skeleton micro-adjustment.

Therefore V2 is now **retained as a provisional motion driver** for the complete-character playable proof. This does not mean the final Exilada walk is approved; it means the project will first determine whether the complete visible authoring route can work at all.

Current V2 guide expected by runner 34:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\overlay_v2_feminine\g3s_c1c_gameplay_walk_overlay_v2_feminine_guide.json`

## Complete-character architecture consequence

Locomotion approval can no longer be treated as body skeleton alone when deciding whether the production route works.

The final visible animation must be judged as one baked character sequence containing:

- body movement;
- body soft-tissue/jiggle motion;
- hair secondary motion;
- base clothing/binding motion;
- shackles/chains/restraints/accessories motion;
- resulting occlusions.

Skeleton-only work remains useful for diagnosing body motion, but it is not the runtime artifact and will not block the immediate whole-character proof.

## Current downstream gate

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 uses V2 at the locked `72 deg` facing as provisional control and animates the complete `exilada_master.png` state through the current Moore-compatible SSD route.

The project will review the actual full spritesheet first. If the complete-character route is viable but the gait still needs refinement, C1C can resume with the visible result as context rather than continuing blind skeleton-only tuning.

## Long-term target locomotion principles

The eventual production walk should still prioritize:

- clear lateral travel;
- adult feminine Exilada body language without catwalk caricature;
- grounded contacts;
- readable contact/down/passing/up phases;
- stable head/torso for action readability;
- natural weight transfer;
- compact but believable stride;
- whole-character secondary motion that supports rather than obscures locomotion.

## No SSD-parameter compensation rule

The visible proof may reveal failures in the temporal authoring route. Do not treat CFG/seed/resolution sweeps as substitutes for solving a clearly identified motion or secondary-motion problem.

But further skeleton micro-adjustment is no longer a prerequisite to **seeing the complete spritesheet work or fail**.
