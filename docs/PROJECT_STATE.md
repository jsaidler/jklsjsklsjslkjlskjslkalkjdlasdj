# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/PIXEL_ART_PRODUCTION.md`
6. `docs/ANIMATION_PIPELINE.md`
7. current tooling under `tools/`

After every material step: update thematic docs + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity

The game is a **systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a living world**.

Immediate gameplay baseline is an **elevated 2D belt-scroller / false 3D**. Character-art/animation feasibility remains the current priority because it is the largest production risk.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite. Final visible art remains true modern pixel art; simple high-resolution generation followed by resize/quantization is not accepted as the final-sprite route.

## RefControl walk checkpoint

### V1 — CONDITIONAL PASS upstream / FAIL final walk

V1 proved that FLUX.2 Klein + RefControl Pose can preserve the Exilada substantially better than prior routes.

Strengths:

- strong identity retention;
- four gait phases visibly distinct.

Defects:

- right-foot/toe error;
- left-arm inconsistency;
- small body drift;
- unstable chain/shackle topology.

### V2 — FAIL as walk

V2 improved feet, arms and body stability, but the left/right gait pairs collapsed:

- `contact_L` ≈ `contact_R`;
- `passing_L` ≈ `passing_R`.

Root cause: V2 left/right controls had nearly the same **screen-space geometry** and relied too heavily on COCO side colors/labels. RefControl followed visible geometry more strongly than the semantic reassignment.

### V3 — distinct gait restored, but catastrophic anatomy FAIL

STEP 8A V3 controls passed:

- four deterministic COCO-18 controls generated;
- `silhouette_uniqueness=PASS`;
- all four gait controls remain visibly distinct even without COCO colors.

STEP 8B inference then produced four V3 character outputs.

Positive finding:

- V3 restored real left/right phase differentiation; the V2 two-pose collapse did not recur.

Catastrophic failure:

- `pose_01_passing_L_v3` contains **three legs / three visible feet**.

This is an immediate gross-anatomy failure and invalidates the V3 set as a usable walk cycle.

Secondary unresolved issues:

- chain/shackle topology still varies between frames;
- passing-pose anatomy remains unstable;
- fine body/prop continuity is not production-stable.

V3 verdict:

**FAIL as a usable walk set.**

Research conclusion:

**FLUX.2 Klein + RefControl Pose can preserve identity and respond to explicit phase geometry, but it does not yet guarantee one-to-one major-limb topology. Extra-limb hallucination is now a production-blocking risk.**

## Mandatory QA order — LOCKED

All future generated frames must be judged in this order:

1. **gross anatomy / limb count** — exactly two arms, two hands, two legs, two feet; no duplicated/fused major limbs;
2. **requested pose/gait semantics** — correct support/swing/contact leg and distinct phase;
3. **identity/continuity** — same body, face, hair, clothes, scars, restraints;
4. **visual quality/gameplay usefulness**.

A frame failing step 1 is not to be discussed as a usable gait frame.

## Workspace relocation — LOCKED

Current canonical workspace:

`Z:\AI\Flux2RefControlSpike`

Old workspace:

`D:\AI\Flux2RefControlSpike` — superseded.

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Exact next gate

Do **not** expand to eight frames and do **not** rerun V3 with another seed.

Next decision: determine how to constrain or reject major-limb topology errors before another generation round. Any next experiment must explicitly target extra-limb hallucination and retain the mandatory limb-count QA gate.

## Gameplay-scale / Production Pixel Master gate — queued

Only after the upstream walk route demonstrates four distinct anatomically valid phases do we return to gameplay-scale/native-raster validation under the elevated belt-scroller projection.

High-resolution RefControl outputs are motion/identity references; they are not automatically final pixel sprites.

## Rejected/stopped routes

- Sprite Sheet Diffusion — rejected;
- Wan-Animate-2 — rejected;
- paid hosted PixelLab/Pixel Engine/Retro Diffusion routes — stopped/disqualified;
- generic video diffusion as primary animation architecture — rejected;
- direct high-resolution generation as final pixel master — rejected;
- primitive Python/Pillow geometry as final artistic authoring — rejected.
