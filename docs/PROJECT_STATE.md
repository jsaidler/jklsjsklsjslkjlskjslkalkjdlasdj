# Roguelite — Current Project State

Status date: **2026-09-05**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

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
14. `docs/G3_PIXEL_TRANSLATION_LOG.md`
15. `docs/G3R_RENDERER_REFINEMENT_LOG.md`
16. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
17. `docs/G3V_RETARGET_PREFLIGHT_LOG.md`
18. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
19. tooling under `tools/deterministic-character-pipeline/`

After every material step: update relevant thematic docs + this file and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: elevated 2D belt-scroller / false 3D.

Final visible language remains **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines identity/design, not final gameplay pixels.

## Hard operator constraint

Normal production must remain scriptable/headless. The user must not need routine Blender/Aseprite/rigging operation, frame-by-frame repainting or a hired specialist.

## Rejected / paused routes

- FLUX.2 Klein + RefControl direct-frame animation: REJECTED/FROZEN after topology drift and a three-leg frame;
- direct per-frame diffusion as animation owner: REJECTED;
- high-resolution beauty render + generic shrink/pixel filter: REJECTED as final-art route;
- primitive mannequin renderer tuning: REJECTED after G3R;
- raw Blender `Action` copy G2 -> MPFB: REJECTED as retarget method;
- raw per-frame `matrix_basis` copy G2 -> MPFB: REJECTED as retarget method;
- local-axis `REST_COMPENSATED_FK`: REJECTED after G3V-R V1;
- MPFB pose API for this G2/MPFB pair: REJECTED after measured articulation error;
- **hidden 3D as owner of the final visible character color image: REJECTED after G3V visual kill switch.**

Qwen-Image-Edit-2509 remains unavailable as a per-frame animation owner. It may return only as a constrained **one-time static source-art candidate** under G3S-A, subject to topology/identity/pixel-art QA.

## Active architecture — UPDATED

`camera/scale -> real motion -> deterministic hidden topology -> validated DIRECTION_SPACE_FK -> projected joints/depth/sockets -> persistent structured 2D pixel assets -> deterministic 2D composition/deformation -> sprite/runtime export -> QA`

Hidden 3D remains useful, but only as infrastructure for:

- real motion;
- topology/side identity;
- sockets;
- contacts/root data;
- physics;
- depth/occlusion;
- semantic/body-part guides;
- secondary-motion drivers.

It no longer owns final visible color pixels.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3 first native translation — TECHNICAL PASS / LOOK NOT APPROVED
- G3R primitive-renderer refinement — FAIL/CLOSED
- G3V representative continuous human visual proxy — **FAIL/CLOSED**
  - G3V-R retarget preflight — PASS/CLOSED
- **G3S structured 2D visible representation** ← ACTIVE NEXT
  - G3S-A static Exilada source sprite
  - G3S-B persistent part decomposition
  - G3S-C four-phase walk proof
- G4 Exilada production 2D identity system — BLOCKED UNTIL G3S PASS
- G5 temporal stress pack
- G6 equipment/attachments
- G6A wind/secondary motion
- G6B liquid/contact VFX
- G6C gore topology
- G6D clothing/armor damage
- G7 systemic state/dynamic lighting
- G8 production scaling

# Current execution state

## G0 — PASS / CLOSED

Windows 11 + Blender 5.1.1 headless automation validated.

## G1 — PASS / CLOSED

Locked:

- raster `640×360`;
- orthographic pitch `26 deg`;
- protagonist visible reference height `128 px`.

## G2 — PASS / CLOSED

Source: CMU `105_34 NormalWalk`, 120 fps.

Validated: real locomotion basis, stable major-limb topology, left/right alternation and deterministic structure.

## G3 / G3R

G3 proved deterministic native-grid processing technically possible but not production-looking. G3R proved renderer-only refinement cannot invent authored 2D form from a primitive source.

## G3V-R — PASS / CLOSED

Accepted cross-rig method:

**`DIRECTION_SPACE_FK`**

Source/target rest-rig facts:

- parent mismatches: `0`;
- mean rest-orientation difference: `83.1874 deg`;
- max: `180.0289 deg`.

Measured accepted solver articulation:

- 4 unique poses;
- mean elbow/knee error: `0.0000 deg`;
- max: `0.0001 deg`;
- V3 rest-independent chain-shape metric passed;
- source/target skeleton sheet visually passed topology and gait-phase correspondence.

Marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

Retarget is retained as hidden production infrastructure.

## G3V — FAIL / CLOSED

Canonical log:

`docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`

Failure marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

Final reviewed body/pixel sheet used frames:

`1568,1588,1608,1628`

Technical result:

- motion phases distinct;
- major topology coherent;
- no duplicated/missing major limbs;
- no retarget collapse;
- representative human/hair/cloth/restraints render reproducibly.

Visual result:

**FAIL.** The native semantic/palette row still reads as conventional simplified 3D made coarse/blocky. It does not exhibit enough intentional native pixel-art shape/value-cluster language to justify hidden 3D as final visible-image owner.

This triggers the previously defined kill switch. No G3V2 renderer refinement will be attempted.

## G3S — STRUCTURED 2D VISIBLE REPRESENTATION: ACTIVE NEXT

Canonical design:

`docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`

Goal:

Use validated hidden motion/topology only as control data while final visible pixels come from persistent 2D pixel assets.

### G3S-A — immediate risk

Create one approved static gameplay-scale Exilada sprite before attempting any animation.

Requirements include:

- ~128 px visible height at native raster;
- lateral/slight-3/4 gameplay presentation;
- true native pixel clusters, no antialiased pseudo-pixel look;
- identity-bearing long black hair, degraded beige cloth, restraints, bare feet and lean adult anatomy;
- topology and recognizability against the canonical master.

The existing Qwen-Image-Edit-2509 local tooling may be reactivated **only for this one-time static source-art spike**. It is not permitted to generate independent animation frames.

### G3S-B / C — after one static source is approved

Decompose the sprite into persistent side-aware parts and drive those parts from the validated hidden rig through deterministic 2D transforms/deformation/depth composition across the four known gait phases.

No per-frame diffusion and no routine frame-by-frame repainting.

## G4 — RESCOPED / BLOCKED

The old assumption of building a detailed Exilada 3D proxy for direct final pixel rendering is closed.

After G3S passes, G4 becomes the **Exilada production 2D identity system**: canonical sprite parts, palette/material families, hair/cloth/restraint structure, sockets/occlusion metadata and damage-ready layers.

## Workspace

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- hidden deterministic backbone: `Z:\AI\RogueliteCharacterPipeline`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- paused/static-source candidate workspace: `Z:\AI\QwenImageEditSpike`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
