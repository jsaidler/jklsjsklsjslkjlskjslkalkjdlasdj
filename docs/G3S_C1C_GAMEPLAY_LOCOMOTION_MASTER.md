# G3S-C1C — Gameplay Locomotion Master

Status date: **2026-09-07**

Status: **ACTIVE — 72 DEG FACING BASELINE SELECTED / RUNNER 32 GAMEPLAY WALK OVERLAY V1 READY**

## Why this gate exists

C1A proved that the retained CMU motion and hidden rig can produce a coherent eight-state human gait. That approval was a **mechanical motion/control proof**, not a final gameplay-animation art-direction approval.

Runner 29 failed visibly because its pose maps were distorted/misregistered. Runner 30 corrected that defect and clearly improved leg separation, phase response and lower-limb reconstruction, but the visible walk remained substantially below the target for the game:

- locomotion read too generic / insufficiently game-authored;
- body presentation remained too frontal for the intended arcade belt-scroller language;
- the walk lacked grounded, readable lateral physicality;
- pose transitions still did not read as a convincing production walk cycle;
- complete-master generation continued to show accessory/restraint instability.

The project therefore stopped asking diffusion to invent animation art direction and moved locomotion back to skeleton-only authoring.

## C1A status

C1A remains valid for:

- real human phase timing;
- left/right gait alternation;
- support-foot sequencing;
- anatomical joint-chain sanity;
- source-rig/mocap infrastructure.

C1A is **not** the production gameplay locomotion master merely because it passed the skeleton sanity gate.

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
- silhouette readability at approximately `128 px` gameplay body height;
- mature, physical, severe body language rather than cartoon exaggeration.

These are animation-design constraints, not diffusion parameters.

## Runner 31 facing audit — CLOSED / 72 DEG SELECTED

Runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Runner 31 used the same `G2_CANONICAL_RIG`, CMU `105_34 NormalWalk`, eight C1A phases, `640x360` orthographic projection, pitch `26 deg` and approximately `128 px` skeleton height while varying only horizontal camera azimuth:

- `60 deg`;
- `72 deg`;
- `84 deg`.

Visual review result:

- `60 deg` rejected: still too frontal / depth-oriented for the intended belt-scroller locomotion read;
- `84 deg` rejected as baseline: lateral readability is strong but projected body mass becomes too profile-thin and sacrifices too much useful torso/face/asymmetry exposure;
- `72 deg` selected: best current compromise between lateral locomotion readability, near/far leg separation, body mass, identity exposure and compatibility with the elevated belt-scroller presentation.

### Facing lock

**Gameplay locomotion facing baseline = `72 deg` azimuth from travel heading.**

In the current convention `90 deg` is pure side profile. The selected baseline therefore remains slightly three-quarter while being materially more lateral than the old `45 deg` C1A sanity projection.

This lock applies to the first canonical screen-left locomotion family. It does not imply that every combat action must use an identical torso yaw if later gameplay readability requires action-specific pose staging.

## Current gate — runner 32 gameplay walk overlay V1

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_gameplay_walk_overlay.py`

Purpose:

> Keep the real C1A timing/support structure, but author the projected walk into a grounded gameplay locomotion cycle before any more visible generation.

Runner 32 is a **skeleton-only A/B test**. It rebuilds a fresh `72 deg` baseline and then applies one bounded deterministic overlay.

### Overlay V1 controls

- projected stride compression, progressively stronger from hip to foot;
- pelvis/root vertical-bob reduction to `55%` of the raw projected amplitude;
- mild screen-left upper-body forward shear, reaching about `4.5 px` at the head;
- reduced civilian arm pendulum amplitude;
- head-offset stabilization relative to the neck;
- retained real gait phase timing and support-foot sequencing.

Current fixed parameter set:

- hip X scale `0.97`;
- knee X scale `0.90`;
- ankle/toe X scale `0.84`;
- elbow swing X scale `0.74`;
- wrist swing X scale `0.62`;
- elbow swing Y scale `0.92`;
- wrist swing Y scale `0.88`;
- head-offset stabilization blend `0.50`.

### What runner 32 does not change

- CMU source timing;
- eight canonical gait events;
- left/right support order;
- camera pitch;
- native raster;
- character scale target;
- diffusion/model parameters — because no diffusion runs at this gate;
- hair, clothing, bindings or restraints.

## Runner 32 decision rule

PASS requires the overlay to be clearly better than the fresh `72 deg` raw baseline in the following combined sense:

1. more natural and intentional locomotion;
2. more appropriate to a contemporary belt-scroller combat space;
3. compact but still human stride;
4. grounded support contacts and clear phase progression;
5. reduced casual-walk bob/arm pendulum;
6. no obvious anatomical break or cartoon exaggeration;
7. preserved left/right gait readability.

If V1 is directionally right but visibly over/under-corrected in one specific control, only that identified control may be revised in the next bounded skeleton-only pass. Do not reopen broad parameter sweeps.

## Expected runner 32 outputs

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v1`

Baseline:

- `baseline_az72\g3s_c1_skeleton_walk_contact_sheet.png`;
- `baseline_az72\g3s_c1_skeleton_walk_zoom.gif`.

Overlay:

- `overlay_v1\g3s_c1_skeleton_walk_contact_sheet.png`;
- `overlay_v1\g3s_c1_skeleton_walk_zoom.gif`.

Summary:

`g3s_c1c_gameplay_walk_overlay_v1_review.json`

## Layering implication

Runner-30 complete-master output reinforced the body-first production rule: dangling chains/restraints and complex secondary masses should not define or validate the base gait.

The locomotion master therefore concerns **body motion first**. Hair, clothing, bindings, shackles/chains and other secondary masses remain separate downstream animation/authoring problems.

## Visible-authoring rule

Do **not** run SSD again until the skeleton locomotion itself passes this gate. Once the walk master is approved, the next visible proof must prioritize body-only transfer before secondary layers are reintroduced.
