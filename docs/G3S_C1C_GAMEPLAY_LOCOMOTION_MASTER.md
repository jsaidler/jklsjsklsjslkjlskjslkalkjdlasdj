# G3S-C1C — Gameplay Locomotion Master

Status date: **2026-09-07**

Status: **ACTIVE — 72 DEG FACING LOCKED / RUNNER 32 V1 VISUAL FAIL / RUNNER 33 FEMININE WALK V2 READY**

## Why this gate exists

C1A proved that the retained CMU motion and hidden rig can produce a coherent eight-state human gait. That approval was a **mechanical motion/control proof**, not a final gameplay-animation art-direction approval.

Runner 29 failed visibly because its pose maps were distorted/misregistered. Runner 30 corrected that defect and clearly improved leg separation, phase response and lower-limb reconstruction, but the visible walk remained substantially below the target for the game. The project therefore stopped asking diffusion to invent animation art direction and moved locomotion back to skeleton-only authoring.

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
- compact, believable stride rather than marching motion;
- moderate vertical root motion rather than excessive bob;
- torso and head stable enough for combat readability;
- arms physically natural but not exaggerated pendulums;
- compatibility with later weapon/equipment states;
- silhouette readability at approximately `128 px` gameplay body height;
- mature, physical, severe body language rather than cartoon exaggeration.

For the Exilada specifically, the locomotion must also have an **adult feminine read**. This is an art-direction requirement for this character, not a claim that there is one universal female gait. The desired result is feminine, natural and physically grounded without becoming a catwalk caricature.

## Runner 31 facing audit — CLOSED / 72 DEG SELECTED

Runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Runner 31 used the same `G2_CANONICAL_RIG`, CMU `105_34 NormalWalk`, eight C1A phases, `640x360` orthographic projection, pitch `26 deg` and approximately `128 px` skeleton height while varying only horizontal camera azimuth.

Visual review result:

- `60 deg` rejected: still too frontal / depth-oriented;
- `84 deg` rejected as baseline: lateral readability is strong but projected body mass becomes too profile-thin;
- `72 deg` selected: best compromise between lateral locomotion readability, near/far leg separation, body mass, identity exposure and the elevated belt-scroller presentation.

### Facing lock

**Gameplay locomotion facing baseline = `72 deg` azimuth from travel heading.**

`90 deg` is pure side profile in the current convention. The selected family remains slightly three-quarter while being materially more lateral than the historical C1A `45 deg` sanity projection.

## Runner 32 gameplay walk overlay V1 — VISUAL FAIL / CLOSED

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_gameplay_walk_overlay.py`

V1 retained the real C1A timing/support structure while applying:

- projected stride compression;
- pelvis/root vertical-bob reduction;
- mild screen-left upper-body forward shear;
- reduced civilian arm pendulum;
- head-offset stabilization.

Visual review of the supplied baseline/V1 sheets and GIFs found that V1 was somewhat more controlled, but **did not solve the locomotion art direction**:

- the difference from the raw `72 deg` baseline remained too small;
- the walk still read as a generic human/mocap gait rather than the Exilada's authored locomotion;
- specifically, it did not achieve the expected feminine body-language read;
- V1 addressed bob/stride/arms but did not create convincing support-side weight transfer through pelvis, torso and shoulders.

Therefore runner 32 is **FAIL/CLOSED as locomotion master V1**. This is not grounds to reopen diffusion or broad parameter sweeps.

## CURRENT GATE — runner 33 gameplay walk overlay V2 / feminine

Runner:

`tools/structured-2d-character-pipeline/33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_feminine_walk_overlay_v2.py`

Machine-readable art-direction spec:

`tools/structured-2d-character-pipeline/g3s_c1c_gameplay_walk_overlay_v2_feminine_spec.json`

### Purpose

Create a clearly more feminine Exilada walk while remaining:

- grounded;
- action-ready;
- natural rather than runway-like;
- compatible with the `72 deg` belt-scroller family;
- faithful to the real eight-state gait timing/support order.

### V2 authored controls

V2 keeps the source gait timing but adds a bounded projected-body treatment:

- pelvis/root bob retained at `62%` of raw amplitude rather than V1's more aggressive `55%`;
- less aggressive stride compression than V1: hip `0.99`, knee `0.95`, ankle/toe `0.91`;
- phase-weighted pelvic obliquity with maximum total split `3.2 px` at the locked gameplay scale;
- subtle pelvic yaw split up to `2.2 px` so the swing side advances while the support side yields;
- torso/shoulder counterbalance against pelvis motion;
- shoulder counter-yaw split up to `1.4 px`;
- smaller forward upper-body shear than V1: `2.6 px` at the head;
- more compact arm pendulum: elbow X `0.70`, wrist X `0.56`, elbow Y `0.91`, wrist Y `0.86`;
- small phase-specific swing-leg clearance boost, strongest in passing/up, without marching knee lift;
- head stabilization blend `0.64`.

The phase weighting is deliberately strongest around passing/single-support and weaker at contact so the weight shift reads as locomotion rather than a continuous artificial sway.

### Guardrails

V2 explicitly rejects:

- exaggerated hip sway;
- catwalk leg crossing;
- cartoon bounce;
- loss of support-foot order;
- diffusion or visible-body generation before skeleton approval.

The helper hard-fails if projected left/right hip vertical separation exceeds `8 px`, which is a safety bound rather than an artistic target.

## Runner 33 decision rule

PASS requires all of the following:

1. the skeleton must read **clearly more feminine** than the raw `72 deg` baseline without costume/hair carrying that impression;
2. the result must still read as a grounded protagonist walk for an action belt-scroller, not runway locomotion;
3. contact/down/passing/up phases remain readable;
4. support-foot contacts remain grounded and left/right alternation intact;
5. pelvis/torso/shoulder counter-motion improves naturality rather than looking mechanically oscillated;
6. no anatomical break or cartoon exaggeration;
7. the improvement over runner 32 V1 must be material enough to justify returning to visible body authoring.

If runner 33 fails, diagnose the remaining motion-design defect before any visible generation. Do not compensate with SSD CFG/seed/resolution tuning.

## Expected runner 33 outputs

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine`

Baseline:

- `baseline_az72\g3s_c1_skeleton_walk_contact_sheet.png`;
- `baseline_az72\g3s_c1_skeleton_walk_zoom.gif`.

V2:

- `overlay_v2_feminine\g3s_c1_skeleton_walk_contact_sheet.png`;
- `overlay_v2_feminine\g3s_c1_skeleton_walk_zoom.gif`.

Marker:

`g3s_c1c_gameplay_walk_overlay_v2_feminine.json`

Summary:

`g3s_c1c_gameplay_walk_overlay_v2_feminine_review.json`

## Layering implication

Base locomotion concerns **body motion first**. Hair, clothing, bindings, shackles/chains and other secondary masses remain separate downstream animation/authoring problems.

## Visible-authoring rule

Do **not** run SSD again until the skeleton locomotion itself passes. Once the walk master is approved, the next visible proof must prioritize body-only transfer before secondary layers are reintroduced.
