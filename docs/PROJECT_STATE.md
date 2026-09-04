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

Immediate gameplay baseline: **elevated 2D belt-scroller / false 3D**.

Character-art/animation feasibility remains the current priority because it is the largest production risk; code capability is not the current unknown.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite. Final visible art remains true modern pixel art; simple high-resolution generation followed by resize/quantization is not accepted as the final-sprite route.

## Direct per-frame diffusion route — NO LONGER ACTIVE

### RefControl

Three controlled iterations were tested.

V1:

- strong identity retention;
- distinct gait phases;
- foot/arm/body/chain inconsistencies.

V2:

- feet/arms/body stability improved;
- opposite gait phases collapsed to near duplicates.

V3:

- four controls had unique screen-space silhouettes;
- generated `pose_01_passing_L_v3` contains **three visible legs / three feet**;
- chain/shackle drift remained.

Final decision:

**RefControl is rejected as the production direct-frame generator. No V4.**

### Broader conclusion

The failure is not only extra limbs.

Independent generated frames also fail to guarantee:

- stable body dimensions;
- natural locomotion timing/arcs;
- stable scars/clothing structure;
- stable hair structure;
- stable side assignment for shackles/chains/equipment;
- scalable consistency across many actions.

Therefore the project will no longer judge a production animation architecture from isolated generated poses.

## Important correction — tested walk-pose provenance

The `contact_L / passing_L / contact_R / passing_R` controls were **manually parameterized project test poses**, not real motion capture or a validated kinematic walk.

They were created to test pose controllability, not to define the final gait.

This means part of the artificial motion problem came from the motion source itself, not just the renderer.

Future locomotion must come from real captured motion, recorded human performance, or deterministic locomotion solving.

## Qwen-Image-Edit-2509 spike — PAUSED

Tooling is preserved under:

`tools/qwen-image-edit-2509-spike/`

Proposed workspace:

`Z:\AI\QwenImageEditSpike`

Do **not** run the preflight/download/inference as the active next step.

Reason:

Even if Qwen produced one perfect passing pose, that would not prove temporal consistency, natural gait, stable accessories, stable clothing/hair structure, or production scalability.

Qwen may later become a constrained editing/reference tool inside a deterministic pipeline, but it is no longer being treated as the system that must independently synthesize production animation frames.

## New active architecture — DETERMINISTIC MOTION FIRST

Production decomposition:

`real/procedural motion -> deterministic rig/topology -> deterministic attachments/secondary systems -> fixed camera/control passes -> final 2D/pixel representation -> QA`

### Motion source

Do not manually invent final walk key poses.

First validation preference:

- real walking BVH motion from the **CMU Graphics Lab Motion Capture Database**;
- imported into Blender as animated armature data.

The CMU database states that its motion data is free for all uses and may be included in commercially sold products under its stated terms.

### Rig/topology ownership

A deterministic rig must own:

- exactly one head/torso;
- exactly two arms/hands;
- exactly two legs/feet;
- pelvis/shoulder mechanics;
- fixed anatomical left/right identity;
- attachment sockets for equipment/restraints.

Diffusion must no longer own these facts.

### Persistent accessories

Shackles, chains, weapons, hair masses and cloth secondary structures must be attached/driven as persistent objects or rigged systems rather than redrawn independently every frame.

This directly addresses the observed side-swapping and topology drift.

## Recommended motion backbone

For the project constraints — no animator, no manual frame-by-frame work, many characters/actions/equipment states — the current recommendation is:

**hidden deterministic 3D rig as production/motion infrastructure**.

This does **not** mean the final game must look 3D.

The gameplay presentation remains 2D belt-scroller / false 3D. The rig can exist only to guarantee anatomy, motion, attachments and camera-consistent control passes.

A deterministic 2D skeletal/mesh route remains an alternative, but risks cut-out appearance and pixel-cluster deformation.

## Exact next gate — motion/topology spike

Do **not** use the Exilada art and do **not** run Qwen yet.

Create a minimal local/free test using:

- Blender;
- one generic human/armature proxy;
- one real walking BVH from CMU Mocap;
- orthographic/elevated belt-scroller camera;
- diagnostic silhouette/body-part output only.

The gate asks:

> Can we get a natural measured walk, fixed topology, stable attachments and the intended belt-scroller camera without manual animation?

### PASS requires the full sequence to have

- normal topology throughout;
- natural gait rather than guessed four-pose motion;
- acceptable ground contact/no obvious foot sliding after retargeting;
- stable left/right anatomy;
- stable attachment points;
- usable elevated belt-scroller camera;
- reproducible scripted/local workflow.

Only after that passes do we solve how the Exilada's approved 2D/pixel identity is mapped to the deterministic moving structure.

## Mandatory animation QA order — LOCKED

1. topology across the **full sequence**;
2. motion/grounding across the full sequence;
3. stable body proportions/anatomical sides;
4. stable attachments/equipment;
5. identity mapping;
6. final pixel-art quality/gameplay readability.

A single good generated frame is no longer sufficient evidence.

## Workspace state

Frozen RefControl evidence:

`Z:\AI\Flux2RefControlSpike`

Paused Qwen spike:

`Z:\AI\QwenImageEditSpike`

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Gameplay-scale / Production Pixel Master gate — queued

Gameplay-scale/native-raster validation remains queued until the deterministic motion/topology backbone passes.

The final visual layer must still satisfy the true modern pixel-art requirement; a naive 3D render followed by a pixel filter remains rejected.
