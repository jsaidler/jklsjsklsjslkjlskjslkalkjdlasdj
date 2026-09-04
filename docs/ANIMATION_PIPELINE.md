# Character Animation Production — Living Decision Record

Status: **direct per-frame diffusion is no longer the active production architecture. RefControl is rejected as a direct frame generator; Qwen-Image-Edit-2509 is paused. The active route is a risk-first deterministic pipeline in which real motion and a persistent rig own topology/attachments, while the final pixel-art translation is validated early—before a detailed Exilada model or animation library is built.**

Canonical end-to-end production roadmap:

`docs/CHARACTER_PRODUCTION_PIPELINE.md`

This document records animation-specific research/decisions. The end-to-end dependencies, visual translation, equipment/state plan and kill switches live in the roadmap above.

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
- scale to many actions, characters, equipment states and world conditions;
- require no recurring Blender GUI or specialist animation-tool operation from the user.

Canonical Exilada identity reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design master, not the final gameplay sprite.

## Headless-operation requirement — LOCKED

Recurring production must be callable through scripts, e.g.:

`PowerShell -> blender.exe --background --python <script.py> -> deterministic outputs/reports`

Blender GUI use may be tolerated for one-off debugging by the assistant/developer when unavoidable, but no accepted production workflow may depend on the user learning or manually operating Blender/rigging/animation software.

## Correct architecture principle

The animation problem is decomposed as:

`real/procedural motion -> deterministic rig/topology -> deterministic secondary attachments -> fixed camera/semantic passes -> pixel-specific visual translation -> export/QA`

The character renderer/editor no longer owns anatomy through independent image synthesis.

## Critical correction — provenance of old walk poses

The four tested pose families:

- `contact_L`
- `passing_L`
- `contact_R`
- `passing_R`

were **not** extracted from motion capture, a filmed walk, a kinematic solver or a validated animation source.

They were manually parameterized in project scripts as a simplified gait-blocking experiment to test pose controllability.

They were valid only for asking whether an image model could distinguish pose controls while retaining identity. They are not the canonical final gait.

A convincing walk source must preserve measured/solved relationships including contact/loading/passing/up phases, pelvis motion, shoulder counter-rotation, center-of-mass motion, knee/ankle trajectories, foot roll and timing.

## Diffusion research history — FROZEN

### RefControl V1

Strengths:

- strongest Exilada identity retention obtained in direct-frame testing;
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

- opposite gait phases collapsed into near duplicates because the controls relied too much on COCO semantic left/right labels rather than visibly different geometry.

Verdict: **FAIL.**

### RefControl V3

Improvement:

- controls had genuinely different color-independent silhouettes;
- left/right phase differentiation returned.

Catastrophic failure:

- `pose_01_passing_L_v3` contains three visible legs / three feet.

Secondary failures:

- chain/shackle topology drift;
- clothing/body detail drift.

Verdict: **FAIL as direct-frame generation. No V4.**

## Qwen-Image-Edit-2509 — PAUSED

Tooling under:

`tools/qwen-image-edit-2509-spike/`

is preserved as research infrastructure.

Do not run it as the active next gate.

Reason: even one perfect pose would not prove temporal body consistency, natural gait, stable accessories, stable clothing/hair structure or scalable animation across many actions.

Qwen may later assist constrained non-topological editing/reference work inside a deterministic pipeline.

## Active motion backbone candidate — hidden deterministic 3D rig

Current recommendation for the project's constraints:

**hidden deterministic 3D rig as production/motion infrastructure**.

This does not lock conventional visible 3D graphics.

Why it is favored as the motion backbone:

- body topology mechanically persists;
- left/right anatomical identity persists;
- real mocap/IK can drive many actions;
- equipment/restraints can use named sockets;
- root motion/contact data can be measured;
- animation can be reused across related models;
- command-line Blender/Python automation is practical.

A deterministic 2D mesh/skeletal route remains fallback if the 3D-to-pixel visual translation cannot satisfy the final art requirement.

## Motion-source rule — LOCKED

Do not invent final locomotion key poses manually.

Use:

- real motion-capture data;
- motion extracted from recorded human performance;
- or a deterministic locomotion solver.

First validation preference: a real walking BVH from a permissively usable source such as the CMU Graphics Lab Motion Capture Database.

## Scripted motion-processing contract

For each source clip, tooling should eventually automate:

1. import source motion;
2. retarget/map to canonical rig;
3. normalize scale/orientation;
4. detect/record foot contacts;
5. extract/normalize root motion when required;
6. calculate stride/natural travel speed;
7. bake canonical animation;
8. drive deterministic secondary systems;
9. sample/bake frames for the sprite cadence;
10. output semantic passes, sprites, events, attachment metadata and QA.

Game locomotion speed must be compatible with the animation stride/root metadata to avoid systematic foot sliding.

## Secondary-motion/attachment plan

These are persistent structures, not image details regenerated per frame.

- hair: large rigged masses + deterministic secondary bones/spring solver;
- cloth: persistent meshes/secondary bones first; free simulation only if reproducibility/need are proven;
- shackles: rigid objects on named wrist/ankle sockets;
- chains: persistent endpoint-connected geometry/curve/segments;
- weapons/equipment: canonical named sockets.

## Risk-first validation gates

The active implementation sequence intentionally proves downstream visual risk early:

### G0 — headless automation

Blender/toolchain creates a known scene/render/manifest with one command and no GUI interaction.

### G1 — gameplay camera/native scale

Use primitive composition to lock pixel density/camera before final art.

### G2 — motion/topology

Generic rig + real walk. The full cycle must preserve natural gait, topology, contacts and sockets.

### G3 — pixel translation feasibility

Before building the Exilada model, run the same simple rig through the planned exact-density semantic-pass -> pixel-renderer route. If the result looks like filtered/low-resolution 3D, reject that visible route immediately.

Only if G0–G3 all PASS do we build the Exilada production proxy.

## Animation stress pack before library expansion

A walk alone can never approve the animation architecture.

Before mass production, the accepted Exilada representation must survive at least:

- locomotion/repeated foot contacts;
- one high-energy/extreme-silhouette action;
- one compressed impact/recovery action.

The stress pack evaluates full-sequence topology, grounding, silhouette separation, secondary motion, pixel temporal stability, bounds and attachment behavior.

## Frame-cadence principle

Mocap source FPS does not automatically become sprite FPS.

The sprite pipeline may sample/bake a lower cadence appropriate to pixel animation, but selection should preserve contacts, motion extrema and error bounds rather than blindly taking every Nth frame.

The target must avoid both choppy accidental motion and an overly smooth rendered-3D appearance.

## Mandatory animation QA order — LOCKED

1. topology across the **full sequence**;
2. motion/grounding across the full sequence;
3. stable body proportions/anatomical sides;
4. stable attachments/equipment;
5. identity mapping;
6. final pixel-art quality/gameplay readability.

A single good frame can never qualify an animation architecture.

## Immediate next implementation sequence — LOCKED

Do not build a detailed Exilada rig yet.

Do not run the paused Qwen spike.

Implement in order:

`G0 headless probe -> G1 camera/scale blockout -> G2 real-mocap generic walk -> G3 generic native-pixel renderer proof`

Only after all four PASS do we commit to Exilada geometry and the first Production Pixel Master.
