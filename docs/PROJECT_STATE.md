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
19. current tooling under `tools/deterministic-character-pipeline/` and `tools/structured-2d-character-pipeline/`

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

Qwen-Image-Edit-2509 remains forbidden as an independent per-frame animation owner. It is reactivated only as a bounded **one-time static source-art candidate** in G3S-A.

## Active architecture — LOCKED

`camera/scale -> real motion -> deterministic hidden topology -> validated DIRECTION_SPACE_FK -> projected joints/depth/sockets -> persistent structured 2D pixel assets -> deterministic 2D composition/deformation -> sprite/runtime export -> QA`

Hidden 3D now owns only control/infrastructure:

- real motion;
- topology/left-right identity;
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
- G3V representative continuous human visual proxy — FAIL/CLOSED
  - G3V-R retarget preflight — PASS/CLOSED
- **G3S structured 2D visible representation** ← ACTIVE
  - **G3S-A static Exilada source sprite** ← READY TO RUN
  - G3S-B persistent part decomposition — BLOCKED
  - G3S-C four-phase walk proof — BLOCKED
- G4 Exilada production 2D identity system — BLOCKED UNTIL G3S PASS
- G5 temporal stress pack
- G6 equipment/attachments
- G6A wind/secondary motion
- G6B liquid/contact VFX
- G6C gore topology
- G6D clothing/armor damage
- G7 systemic state/dynamic lighting
- G8 production scaling

# Validated history

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

Measured facts:

- source/target parent mismatches: `0`;
- mean rest-orientation difference: `83.1874 deg`;
- max: `180.0289 deg`;
- 4 unique target poses;
- mean elbow/knee error: `0.0000 deg`;
- max: `0.0001 deg`;
- rest-independent chain-shape metric passed;
- source/target skeleton sheet visually passed topology and gait-phase correspondence.

Marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

This retarget remains hidden production infrastructure.

## G3V — FAIL / CLOSED

Failure marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

The final reviewed body/pixel sheet at frames `1568,1588,1608,1628` was technically coherent: distinct motion phases, stable major topology, no retarget collapse, reproducible representative hair/cloth/restraints.

Visual result: **FAIL.** The character still read as simplified conventional 3D translated into coarse native-raster/palette output rather than intentional modern pixel art. The defined kill switch was triggered. No G3V2 renderer refinement will be attempted.

# G3S — STRUCTURED 2D VISIBLE REPRESENTATION

Canonical design:

`docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`

Goal:

Use validated hidden motion/topology only as control data while final visible pixels come from persistent authored 2D pixel assets.

## G3S-A — READY TO RUN

Tooling now exists and has been verified in the repository:

- `tools/structured-2d-character-pipeline/01_run_g3s_a.ps1`
- `tools/structured-2d-character-pipeline/g3s_a_static_source.py`

Runtime reused from the preserved local Qwen spike:

`Z:\AI\QwenImageEditSpike`

Expected existing models:

- `Qwen-Image-Edit-2509-Q4_0.gguf`;
- `qwen_2.5_vl_7b_fp8_scaled.safetensors`;
- `qwen_image_vae.safetensors`.

The G3S-A runner itself downloads nothing. Missing large dependencies are a hard fail rather than an implicit download.

Test contract:

- exact canonical `exilada_master.png` as identity/design input;
- generated abstract pose/scale guide as second reference;
- direct native `640×360` output canvas;
- target figure ≈`128 px` high;
- fixed seed `20260905`;
- one static candidate only;
- no post-inference resize;
- a 32-color same-raster version is generated only for inspection;
- topology/identity/pixel-art quality remain a visual review gate.

Expected output:

`Z:\AI\RogueliteCharacterPipeline\g3s_a\g3s_a_contact_sheet.png`

Review order:

1. topology: exactly one head/torso, two arms/hands, two legs/feet;
2. Exilada identity/design continuity;
3. approximately 128 px gameplay scale and correct lateral/slight-3/4 presentation;
4. intentional modern pixel cluster language at native 1×;
5. long hair / degraded cloth / restraints / bare feet readability.

Do not approve merely because the enlarged zoom looks attractive.

## G3S-B / C — BLOCKED

Only after one G3S-A static source is visually approved:

- decompose it into persistent side-aware parts;
- drive those parts from the validated hidden rig;
- test four gait phases `1568,1588,1608,1628` without per-frame generation.

No per-frame diffusion and no routine frame-by-frame repainting.

## G4 — RESCOPED / BLOCKED

After G3S passes, G4 becomes the **Exilada production 2D identity system**: canonical sprite parts, palette/material families, hair/cloth/restraint structure, sockets/occlusion metadata and damage-ready layers.

# Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\01_run_g3s_a.ps1"
```

Then STOP.

If it reaches `G3S-A: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a\g3s_a_contact_sheet.png`

If it fails, share the complete console output. Do not start G3S-B or G4.

## Workspace

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- hidden deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- Qwen static-source runtime: `Z:\AI\QwenImageEditSpike`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
