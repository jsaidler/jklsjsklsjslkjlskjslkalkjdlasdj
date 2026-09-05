# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth; detailed design stays in thematic docs rather than being duplicated here.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
7. `docs/ANIMATION_SOURCE_LIBRARY.md`
8. `docs/PHYSICAL_INTERACTION_VFX_GORE.md`
9. `docs/PIXEL_ART_PRODUCTION.md`
10. `docs/ANIMATION_PIPELINE.md`
11. `docs/G0_AUTOMATION_LOG.md`
12. `docs/G1_CAMERA_SCALE_LOG.md`
13. `docs/G2_MOTION_TOPOLOGY_LOG.md`
14. current tooling under `tools/deterministic-character-pipeline/`

After every material step: update the relevant thematic document(s) + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Immediate gameplay presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible character/environment language remains **true modern pixel art** at native gameplay raster. Hidden 3D may own motion/topology/physics but is not the final visible style.

## Exilada visual identity — LOCKED

Canonical high-detail identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master is not the final gameplay sprite. It defines identity, proportions, face, dominant long black hair mass, degraded beige clothing language, scars/restraints and overall physical character.

## Direct per-frame diffusion — CLOSED AS PRIMARY ARCHITECTURE

FLUX.2 Klein + RefControl V1/V2/V3 is frozen/rejected as production direct-frame animation because it failed topology/temporal/accessory consistency, culminating in a three-leg/three-foot frame in V3.

Qwen-Image-Edit-2509 tooling remains preserved but **PAUSED**. A perfect isolated generated pose would not prove natural motion, stable anatomy, equipment continuity or production scalability.

## Active character-production architecture — LOCKED FOR VALIDATION

Canonical roadmap:

`docs/CHARACTER_PRODUCTION_PIPELINE.md`

Pipeline:

`gameplay camera/scale -> real motion -> deterministic rig/topology -> persistent secondary systems -> native-raster semantic passes -> pixel-specific renderer -> modular equipment/state composition -> sprite/runtime export -> automated QA`

Hard user-operation constraint:

- no routine Blender GUI work;
- no manual rigging/animation/pixel-production operation by the user;
- no hired art/animation team assumed;
- recurring production must be driven by ChatGPT-authored command-line/headless tooling.

Canonical pattern:

`PowerShell -> blender.exe --background --python ... -> deterministic outputs/reports`

## Animation source strategy — LOCKED

Canonical catalog:

`docs/ANIMATION_SOURCE_LIBRARY.md`

Primary permissive sources already identified include:

- Quaternius Universal Animation Library / Library 2 — CC0 humanoid motion families;
- CMU Graphics Lab Motion Capture Database — real captured locomotion/recovery/combat-style trials under its stated reuse terms;
- Quaternius animal/monster/dinosaur packs — CC0 sources for quadruped/creature rig-family validation.

Blender is the deterministic import/retarget/bake backbone, not the sole animation source.

## Physical interaction / body / equipment architecture — LOCKED

Canonical docs:

- `docs/PHYSICAL_INTERACTION_VFX_GORE.md`
- `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`

Architectural requirements already include:

- persistent full body under clothing;
- modular removable/damageable clothing and armor;
- stable named equipment/restraint sockets;
- hair/cloth secondary motion and wind interaction;
- wetness/blood/dirt/material state via semantic masks;
- event-driven water/blood VFX;
- deterministic named gore/sever zones and detached-part behavior;
- discrete palette-band dynamic lighting using normal/material/depth metadata;
- support for unclothed body states without depending on generative image synthesis;
- damage persistence without body×item×damage×animation combinatorial sprite authoring.

## Risk-first gate order — LOCKED

- **G0 — automation:** headless Blender/toolchain proof.
- **G1 — camera/native scale:** belt-scroller framing and actual character pixel density.
- **G2 — motion/topology:** real captured walk on persistent generic rig with contacts/sockets.
- **G3 — pixel translation:** prove hidden 3D can become intentional native-grid pixel art before building Exilada geometry.
- **G4 — identity mapping:** low-detail Exilada production proxy / Production Pixel Master.
- **G5 — temporal stress:** locomotion + extreme action + impact/recovery.
- **G6 — equipment/attachments.**
- **G6A — wind/secondary motion.**
- **G6B — liquid/contact VFX.**
- **G6C — gore topology.**
- **G6D — clothing/armor damage.**
- **G7 — systemic state/dynamic lighting.**
- **G8 — production scaling.**

Cross-skeleton animation-library normalization is an explicit required validation before production scaling; it is not silently inferred from the first G2 same-skeleton bake.

# Current execution state

## G0 — HEADLESS AUTOMATION: PASS / CLOSED

Validated target environment:

- Windows 11 Home Single Language `10.0.26200`;
- Blender `5.1.1`;
- Blender executable: `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`;
- workspace: `Z:\AI\RogueliteCharacterPipeline`;
- diagnostic engine: `BLENDER_EEVEE`.

Validated G0 PNG SHA256:

`bb8c938d6fe64a84de264a7c01824b1dabad27f3abd307485f706553b0d19d53`

Detailed history: `docs/G0_AUTOMATION_LOG.md`.

## G1 — CAMERA / NATIVE SCALE: PASS / CLOSED

The corrected 3×3 camera/scale matrix was reviewed after fixing stale dependency-graph calibration.

Locked validation baseline:

- native raster: **640×360**;
- camera: **orthographic**;
- pitch: **26 deg**;
- protagonist reference visible height: **128 px**.

Machine-readable baseline:

`tools/deterministic-character-pipeline/g1_baseline.json`

Rationale/details: `docs/G1_CAMERA_SCALE_LOG.md`.

## G2 — REAL MOTION / TOPOLOGY: READY TO RUN

Tooling now exists in the repository:

- `tools/deterministic-character-pipeline/02_run_g2.ps1`
- `tools/deterministic-character-pipeline/g2_motion_topology.py`

First pinned real-motion source:

- CMU trial `105_34` — `NormalWalk`;
- BVH mirror commit `09a07f54f3bbb58797325f009282d0b2048a2871`;
- 2209 frames at 120 fps;
- runner downloads source automatically and records SHA256/provenance.

G2 automatically selects a straight ~1.5 s locomotion interval, verifies major named bones, bakes the motion to a persistent diagnostic clone, exposes stable left/right hand/foot sockets, estimates foot contacts and renders 12 sequence samples at the locked G1 presentation.

Review artifact:

`Z:\AI\RogueliteCharacterPipeline\g2\g2_contact_sheet.png`

G2 remains `REVIEW_REQUIRED` until that sequence is inspected. **Do not start G3 automatically.**

Detailed scope: `docs/G2_MOTION_TOPOLOGY_LOG.md`.

## Workspace state

- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
- active deterministic pipeline: `Z:\AI\RogueliteCharacterPipeline`
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`
