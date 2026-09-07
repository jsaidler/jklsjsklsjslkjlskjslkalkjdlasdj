# G3S-C1C — Gameplay Locomotion Master

Status date: **2026-09-07**

Status: **ACTIVE — runner 30 improved transfer geometry but visible walk remains below production quality; locomotion art direction must be solved before more diffusion.**

## Why this gate exists

C1A proved that the retained CMU motion and hidden rig can produce a coherent eight-state human gait. That approval was a **mechanical motion/control proof**, not a final gameplay-animation art-direction approval.

Runner 29 then failed visibly because its pose maps were distorted/misregistered. Runner 30 corrected that defect and produced a clear A/B improvement: leg separation, phase response and lower-limb reconstruction improved. However the resulting visible walk remains substantially below the target for the game:

- locomotion reads too generic / insufficiently game-authored;
- body presentation remains too frontal for the intended arcade belt-scroller language;
- the walk lacks the grounded, readable lateral physicality required for combat spaces;
- pose transitions still do not read as a convincing production walk cycle;
- the complete-master generation continues to show accessory/restraint instability.

Therefore the next step is **not** CFG/seed/resolution tuning and not another image-model run.

## Correct separation of concerns

The project must first answer:

> What should the Exilada's base gameplay locomotion actually look like in the locked elevated belt-scroller camera?

Only after that hidden pose family is approved should an image-generation/authoring method be judged on whether it reproduces it.

This avoids asking diffusion to invent animation art direction.

## C1A status after runner 30

C1A remains valid for:

- real human phase timing;
- left/right gait alternation;
- support-foot sequencing;
- anatomical joint-chain sanity;
- source-rig/mocap infrastructure.

C1A is **no longer treated as the production gameplay locomotion master** merely because it passed the skeleton sanity gate.

The original `45 deg` camera azimuth from motion heading is specifically reopened for gameplay locomotion review. In this convention `90 deg` is a pure side view; therefore `45 deg` places the character halfway between frontal and lateral and can make a belt-scroller walk read too frontal.

## Target locomotion principles

The production walk should prioritize:

- strong screen-lateral travel readability;
- a mostly lateral body with enough three-quarter exposure to retain Exilada identity;
- clear near/far leg separation without crossed-leg ambiguity;
- grounded foot contacts;
- compact, believable stride rather than runway-like or marching motion;
- moderate vertical root motion rather than excessive bob;
- torso and head stable enough for combat readability;
- arms physically natural but not exaggerated pendulums;
- compatibility with later weapon/equipment states;
- silhouette readability at the locked approximately `128 px` gameplay body height;
- mature, physical, severe body language rather than cartoon exaggeration.

These are animation-design constraints, not diffusion parameters.

## First discriminant — runner 31 facing audit

Runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Purpose:

Before changing the gait itself, isolate how much of the wrong gameplay read comes from the original `45 deg` front-three-quarter projection.

The runner uses the same:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight C1A phases;
- `640x360` orthographic projection;
- pitch `26 deg`;
- approximately `128 px` skeleton height;
- skeleton-only review tooling.

It changes **only horizontal camera azimuth** and produces three review packages:

- `60 deg` — 30 deg off pure profile;
- `72 deg` — 18 deg off pure profile;
- `84 deg` — 6 deg off pure profile.

No diffusion/model execution occurs.

## Runner 31 decision rule

Review the three skeleton cycles for:

1. natural gait readability;
2. screen-left travel clarity;
3. near/far leg separation;
4. body/face readability;
5. fit with the elevated arcade belt-scroller presentation.

One of three outcomes is valid:

- choose one facing as the gameplay baseline;
- decide that an intermediate angle is needed;
- reject all three, proving that camera/facing is not enough and the gait itself must receive an authored additive gameplay pose treatment.

Do **not** rerun SSD before this is closed.

## Expected follow-up after facing selection

If a facing is approved but the gait remains too neutral, the next gate will author a deterministic gameplay locomotion overlay on top of the retained real gait timing. Likely controlled variables include:

- stride compression;
- pelvis/root vertical amplitude;
- torso forward inclination;
- shoulder orientation;
- elbow flexion / reduced arm swing;
- head/gaze stabilization;
- foot-lift amplitude.

Those adjustments must be reviewed first as skeleton motion, then fed to a visible body-only authoring test.

## Layering implication

The runner-30 complete-master output also reinforces the broader body-first production rule: dangling chains/restraints and complex secondary masses should not be expected to survive as one monolithic generative body image during locomotion.

The current locomotion-design gate therefore concerns **body motion first**. Hair, clothing and restraints remain separate downstream animation/authoring problems rather than criteria for defining the gait itself.
