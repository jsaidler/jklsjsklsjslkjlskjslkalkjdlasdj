# Character Animation Production — Living Decision Record

Status: **Direct per-frame diffusion is no longer the active production architecture. RefControl is rejected after repeated topology/continuity failures, and the planned Qwen-Image-Edit-2509 single-pose test is PAUSED because a successful isolated pose would not answer the larger production problems: natural motion, temporal body consistency, stable accessories, stable clothing/hair structure, and scalable animation across many actions. The project now moves to a deterministic motion/topology architecture first, with generative models allowed only where they do not own body topology or temporal continuity.**

This document is canonical across chats. Update it after every material animation test, PASS/FAIL decision or pipeline change.

## Hard production constraints

The animation pipeline must:

- start from the approved Exilada identity reference;
- preserve adult anatomy, face, long black hair mass, clothing state, scars/restraints and equipment state;
- provide explicit inspectable motion control;
- guarantee normal body topology across every frame;
- maintain stable anatomical side assignment for accessories/equipment;
- produce natural locomotion rather than hand-authored approximate stick-figure motion;
- run reproducibly on Windows 11 / RTX 3060 12 GB / ~48 GB RAM;
- avoid routine manual frame-by-frame repainting or hand animation;
- use free/local/self-hosted tools and assets unless explicitly approved otherwise;
- scale to many actions, characters, equipment states and world conditions.

Canonical Exilada identity reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design master, not the final gameplay sprite.

## Critical correction — provenance of the tested walk poses

The four tested pose families:

- `contact_L`
- `passing_L`
- `contact_R`
- `passing_R`

were **not** extracted from motion capture, a filmed walk, a kinematic solver, or a validated animation source.

They were manually parameterized in project scripts as a simplified gait-blocking experiment to test pose controllability.

That means they were valid only for answering:

> Can the renderer distinguish explicit pose controls while preserving the Exilada?

They were **not** a valid foundation for judging a natural final walk.

A convincing full walk normally requires more than four crude phase drawings. At minimum, a real motion source must preserve:

- contact;
- loading/down phase;
- passing;
- high/up phase;
- opposite-side equivalents;
- pelvis translation and rotation;
- shoulder counter-rotation;
- vertical center-of-mass motion;
- knee/ankle arcs;
- heel-to-toe foot roll;
- cadence and asymmetry appropriate to the character.

Therefore the artificial feel observed in the tests is not solely a renderer problem; part of it came from using synthetic blocking poses rather than real motion.

## What the diffusion experiments actually proved

### RefControl V1

Strengths:

- strongest Exilada identity retention obtained so far;
- four requested controls rendered as visibly different poses.

Failures:

- foot/toe anatomy;
- arm inconsistency;
- body drift;
- chain/shackle topology drift.

Verdict: **useful research reference; not production animation.**

### RefControl V2

Improvements:

- feet;
- arms;
- body stability.

Failure:

- opposite gait phases collapsed into near duplicates because screen-space geometry was too similar.

Verdict: **FAIL.**

### RefControl V3

Improvement:

- four controls had genuinely different color-independent silhouettes;
- left/right phase differentiation returned.

Catastrophic failure:

- `pose_01_passing_L_v3` contains three visible legs / three feet.

Secondary failures:

- chain/shackle topology still drifts;
- clothing/body details vary between frames.

Verdict: **FAIL as direct-frame generation. RefControl direct-frame route frozen.**

## Broader production conclusion — LOCKED

The problem is not merely extra limbs.

Independent generative frames also create unresolved production risks:

- body dimensions change subtly frame to frame;
- scars/clothing folds move or mutate;
- shackles/chains can swap anatomical sides;
- hair mass changes internally;
- equipment topology may drift;
- gait timing is not mechanically guaranteed;
- motion arcs and center of mass are not shared across frames;
- every new action can reopen the same failures.

Therefore **a model that passes one anatomically valid pose is not enough to qualify as the production animation system**.

The project was incorrectly trying to solve an animation-system problem as an image-generation problem.

## Qwen-Image-Edit-2509 status — PAUSED, NOT REJECTED

Tooling under:

`tools/qwen-image-edit-2509-spike/`

is preserved as research infrastructure.

Do **not** run the preflight/download/inference as the active next gate.

Reason:

Even if Qwen produced one perfect difficult passing pose, that would still not prove:

- temporally coherent body proportions;
- stable chains/accessories across a cycle;
- natural gait;
- stable clothing/hair topology;
- production scalability across dozens of actions.

Qwen may later be useful as a constrained editing/reference component inside a deterministic pipeline, but it is no longer being treated as the candidate that must solve animation by independently synthesizing frames.

## New production architecture — DETERMINISTIC MOTION FIRST

The animation system is now decomposed as:

`real/procedural motion source -> deterministic rig/topology -> deterministic secondary attachments -> fixed camera/control passes -> final 2D/pixel representation -> QA`

### Layer 1 — motion source

Do not invent walk key poses manually.

Use either:

- real motion-capture data;
- motion extracted from recorded human performance;
- or a deterministic locomotion solver.

First preference for the validation spike: **real BVH locomotion data**.

The CMU Graphics Lab Motion Capture Database is free for use, including in commercially sold products, subject to its stated terms. It contains locomotion/walking trials. Blender imports BVH directly as animated armature data.

This gives us an actual measured walk instead of guessed contact/passing stick figures.

### Layer 2 — topology-owning rig

A persistent rig must own:

- one torso/head;
- exactly two arms/hands;
- exactly two legs/feet;
- pelvis/shoulder relation;
- attachment sockets for shackles/equipment;
- stable left/right anatomical identity.

The rig, not diffusion, is responsible for body topology.

### Layer 3 — deterministic secondary systems

Persistent objects are separated from character-image synthesis:

- wrist shackles attached to fixed wrist sockets;
- ankle shackles attached to fixed ankle sockets;
- chains attached to known endpoints;
- weapons attached to sockets;
- hair and cloth secondary motion driven by bones/curves/physics or other persistent deterministic structures.

This prevents accessories from changing sides simply because a model redraws the whole frame.

### Layer 4 — fixed camera / control representation

The gameplay baseline remains:

**elevated 2D belt-scroller / false 3D**.

The deterministic rig can render or export, per frame:

- silhouette;
- body-part ID mask;
- depth;
- normals;
- keypoints;
- attachment positions;
- optional flat-shaded reference render.

These are stable across a motion sequence and may feed downstream 2D/pixel authoring.

### Layer 5 — final visual representation

Still open. Two candidate families remain:

#### A. Deterministic 2D skeletal/mesh character

Advantages:

- final representation is genuinely 2D;
- identity/art assets stay fixed;
- equipment can be layered deterministically.

Risks:

- can look like a cut-out puppet;
- mesh deformation can damage pixel clusters;
- complex hair/cloth requires careful rig design.

#### B. Hidden 3D rig rendered as 2D/native-raster art

Advantages:

- anatomy/topology guaranteed;
- real mocap/IK directly usable;
- arbitrary actions and camera-relative movement scale well;
- equipment, chains, hair and collisions can attach mechanically;
- much more scalable for many NPCs/actions.

Important clarification:

**the game does not need to become visually 3D.**

The 3D rig may exist only as hidden production infrastructure. Gameplay can remain orthographic/oblique 2D belt-scroller, and the final representation can still target authored native-raster/pixel language.

Risk:

- a naive low-resolution render or pixel filter would look like filtered 3D and is rejected;
- the final raster/look still needs a deliberate production solution.

## Current recommendation

For the project's constraints — no animation team, no manual frame-by-frame work, many characters/equipment states, systemic world — **hidden deterministic 3D rigging is currently the more scalable motion/topology backbone**.

This is a production recommendation, not a decision that final graphics must look 3D.

## Next validation spike — motion/topology only

Do not use the Exilada art yet.

Build a minimal neutral human rig test that answers only:

> Can we obtain a natural real walk, preserve exact topology, and view it through the intended elevated belt-scroller camera without manual animation?

Suggested minimal stack:

- Blender, local/free;
- one generic human/armature proxy;
- one real walking BVH from CMU Mocap;
- orthographic/elevated belt-scroller camera;
- render/export only simple silhouette/body-part diagnostic frames first.

No pixel-art styling, no diffusion, no Exilada identity generation in this gate.

### PASS criteria

- exactly normal topology for the whole sequence;
- natural measured gait rather than hand-authored contact/passing guesses;
- stable ground contact/no obvious foot sliding after retargeting;
- usable belt-scroller camera angle;
- repeatable scripted/local workflow;
- attachment sockets remain stable through the full walk.

Only after this passes do we solve:

> How is the approved Exilada visual design mapped onto this deterministic moving structure while retaining true modern pixel-art quality?

## Mandatory QA order — UPDATED

1. topology integrity for the full sequence;
2. motion quality/grounding for the full sequence;
3. stable body proportions and anatomical sides;
4. stable attachments/equipment;
5. identity mapping;
6. final pixel-art quality/gameplay readability.

A single good frame can never again qualify an animation architecture.
