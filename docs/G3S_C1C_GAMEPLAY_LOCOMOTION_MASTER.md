# G3S-C1C — Gameplay Locomotion Master

Status date: **2026-09-07**

Status: **ACTIVE — 72 DEG FACING LOCKED / RUNNER 32 V1 VISUAL FAIL / RUNNER 33 FEMININE WALK V2 TECHNICAL GUARD FIXED, RERUN READY**

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

V1 retained the real C1A timing/support structure while applying projected stride compression, pelvis/root vertical-bob reduction, mild forward upper-body intent, reduced civilian arm pendulum and head stabilization.

Visual review found V1 somewhat more controlled, but still too close to generic mocap/human locomotion and specifically lacking the expected feminine Exilada body-language read. It did not create convincing support-side weight transfer through pelvis, torso and shoulders. Runner 32 is therefore **FAIL/CLOSED as locomotion master V1**.

## CURRENT GATE — runner 33 gameplay walk overlay V2 / feminine

Runner:

`tools/structured-2d-character-pipeline/33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_feminine_walk_overlay_v2.py`

Machine-readable art-direction spec:

`tools/structured-2d-character-pipeline/g3s_c1c_gameplay_walk_overlay_v2_feminine_spec.json`

### Purpose

Create a clearly more feminine Exilada walk while remaining grounded, action-ready, natural rather than runway-like, compatible with the locked `72 deg` family and faithful to the real eight-state gait timing/support order.

### V2 authored controls

- pelvis/root bob at `62%` of raw amplitude;
- moderate stride compression: hip `0.99`, knee `0.95`, ankle/toe `0.91`;
- phase-weighted pelvic obliquity with maximum authored total split `3.2 px`;
- subtle pelvic yaw split up to `2.2 px`;
- torso/shoulder counterbalance and shoulder counter-yaw up to `1.4 px`;
- mild forward upper-body shear `2.6 px` at the head;
- compact arm pendulum;
- small swing-leg clearance boost in passing/up;
- head stabilization blend `0.64`.

### Runner 33 first execution — TECHNICAL GUARD FAIL / RESOLVED

The first real V2 run built the fresh `72 deg` baseline successfully, then stopped in the overlay helper with:

`V2 pelvic obliquity exceeded safety limit: 10.12px`

This was a **guard implementation error, not evidence that the authored V2 pelvis motion itself was 10.12 px**. The old guard compared the final absolute projected left/right hip Y separation against a flat `8 px` limit. At `72 deg`, the source gait already contains a substantial projected hip-Y separation from real pose/depth geometry before the V2 authored obliquity is added.

The guard is corrected to measure the **additional projected hip-Y separation introduced by V2 relative to the same source frame**, not the absolute final separation. The additive allowance is tied to the authored `pelvic_obliquity_total_px` (`3.2 px`) plus a small numerical tolerance (`0.25 px`). The marker now records source maximum, authored maximum, added maximum and allowed added maximum separately. Runner 33 validates the same additive metric.

No V2 art-direction parameter was changed in this correction. This preserves the experiment rather than weakening pelvic motion just to satisfy a bad absolute bound.

### Guardrails

V2 rejects exaggerated hip sway, catwalk leg crossing, cartoon bounce, loss of support-foot order and any diffusion/visible-body generation before skeleton approval.

## Runner 33 decision rule

PASS requires all of the following:

1. clearly more feminine skeleton read than raw `72 deg` baseline without costume/hair carrying that impression;
2. grounded protagonist locomotion rather than runway locomotion;
3. readable contact/down/passing/up phases;
4. stable support-foot contacts and left/right alternation;
5. natural pelvis/torso/shoulder counter-motion rather than mechanical oscillation;
6. no anatomical break or cartoon exaggeration;
7. material improvement over runner 32 V1 sufficient to justify returning to visible body authoring.

If runner 33 fails visually, diagnose the remaining motion-design defect before any SSD rerun.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\33_run_g3s_c1c_gameplay_walk_overlay_v2_feminine.ps1"
```

Expected terminal marker:

`G3S-C1C-FEMININE-V2: A/B SKELETON REVIEW PACKAGE READY`

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
