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
17. current tooling under `tools/deterministic-character-pipeline/`

After every material step: update thematic docs + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Immediate presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible character/environment language remains **true modern pixel art at native gameplay raster**. Hidden 3D may own motion/topology/physics but is not automatically the final visible style.

## Exilada identity — LOCKED

Canonical high-detail identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines identity/design, not final gameplay pixels.

## Rejected / paused routes

- FLUX.2 Klein + RefControl direct-frame animation: **REJECTED / FROZEN** after V1/V2/V3; V3 produced a three-leg/three-foot frame and persistent accessory/topology drift.
- Qwen-Image-Edit-2509: **PAUSED** as a possible constrained future component only.
- high-resolution beauty render followed by generic shrink/pixel filter: **REJECTED as final-art route**.
- routine manual frame-by-frame repainting: **REJECTED as production burden**.
- repeated outline/cluster/palette refinement on a primitive capsule/mannequin proxy: **REJECTED after G3R**.

## Active deterministic architecture

`gameplay camera/scale -> real motion -> deterministic rig/topology -> representative visual asset -> native semantic passes -> pixel-specific visible representation -> modular equipment/state composition -> sprite/runtime export -> automated QA`

Hard operator constraint:

- no routine Blender GUI work;
- no manual rigging/animation/pixel-production operation by the user;
- no hired art/animation team assumed;
- recurring production must be driven by ChatGPT-authored CLI/headless tooling.

Canonical operator pattern:

`PowerShell -> blender.exe --background --python ... -> deterministic outputs/reports`

## Systemic visual architecture already locked

Canonical thematic docs already require complete persistent body under clothing, modular equipment/layers, structural and surface damage, stable sockets, wind/secondary motion, material state, dynamic palette lighting, liquids/VFX, deterministic sever zones and detached-limb/equipment inheritance.

## Gate order — CURRENT

- **G0 — automation**
- **G1 — camera/native scale**
- **G2 — real motion/topology**
- **G3 — first pixel translation feasibility**
- **G3R — renderer-only refinement on primitive proxy**
- **G3V — representative continuous human visual proxy**
- **G4 — Exilada identity mapping**
- **G5 — temporal stress pack**
- **G6 — equipment/attachments**
- **G6A — wind/secondary motion**
- **G6B — liquid/contact VFX**
- **G6C — gore topology**
- **G6D — clothing/armor damage**
- **G7 — systemic state/dynamic lighting**
- **G8 — production scaling**

A later expensive stage does not start merely because an earlier technical demo looked attractive.

# Current execution state

## G0 — HEADLESS AUTOMATION: PASS / CLOSED

Validated on Windows 11 + Blender 5.1.1.

## G1 — CAMERA / NATIVE SCALE: PASS / CLOSED

Locked baseline:

- native gameplay raster: **`640×360`**;
- orthographic camera pitch: **`26 deg`**;
- protagonist reference visible height: **`128 px`**.

## G2 — REAL MOTION / TOPOLOGY: PASS / CLOSED

CMU `105_34 NormalWalk`; full 12-sample sequence reviewed. Stable major-limb topology, real left/right gait alternation, natural captured motion basis and deterministic persistent structure are approved for G2 scope.

Arbitrary cross-skeleton retargeting and production foot-lock cleanup remain future validations.

## G3 — NATIVE PIXEL TRANSLATION: TECHNICAL PASS / LOOK NOT APPROVED

Deterministic native-grid translation works, but the primitive proxy remained a technical mannequin. Correction recorded on 2026-09-05: G3's four selected frames could alias the gait cycle, so G2's full 12-sample review remains the authoritative temporal evidence.

## G3R — RENDERER / STYLE REFINEMENT: FAIL / CLOSED

Renderer-only contour/value/cluster changes could not invent authored human form or identity-bearing structure absent from the source representation.

## G3V — REPRESENTATIVE VISUAL PROXY: ACTIVE / RIGID-ATTACHMENT RERUN REQUIRED

Detailed log: `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`.

Tooling:

- `tools/deterministic-character-pipeline/03c_run_g3v.ps1`
- `tools/deterministic-character-pipeline/g3v_mpfb_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_bone_attachment_patch.py`
- `tools/deterministic-character-pipeline/g3v_geometry_phase_patch.py`
- `tools/deterministic-character-pipeline/g3v_semantic_masks.py`
- `tools/deterministic-character-pipeline/g3v_representative_visual_proxy.py`

### Proven execution facts

- pinned MPFB 2.0.17 loads directly in one background Blender process;
- MPFB body and CMU-compatible rig are created;
- G2 walk is reused;
- representative hair/cloth/shackles are generated;
- contact-derived gait period is now used instead of the aliased fixed subset;
- current derived period: **80 frames**;
- current phases: **1568, 1588, 1608, 1628**;
- body geometry height: **1.713562**;
- skeleton head-to-foot height: **1.647693**;
- camera calibration is owned by skeleton head-to-foot projection.

### Latest diagnosis — bone-parent scale inflation

At frame 1568, despite a sane ~1.65 m skeleton and 128 px skeleton calibration, the representative composite produced a **285 px** visible bbox and:

- skin: `visible=0`, `unoccluded=2314`;
- hair: `visible=3426`;
- cloth: `visible=47692`;
- metal: `visible=0`, `unoccluded=501`.

This is incompatible with the authored physical cloth dimensions. The blocker is therefore no longer camera, MPFB, materials or semantic classification: Blender BONE-parent evaluation was inflating the attached proxy transforms.

### Current fix now committed

`g3v_bone_attachment_patch.py` replaces BONE parenting for representative hair/cloth/cuffs with explicit rigid bone-relative matrices. Each attachment follows owning-bone translation+rotation but deliberately does **not** inherit parent/bone scale.

Bootstrap install order is now:

1. rigid attachment owner;
2. geometry/phase corrections;
3. binary semantic diagnostics;
4. G3V main.

Expected new console markers:

- `G3V_ATTACHMENT_MODE=RIGID_RELATIVE_MATRIX`
- `G3V_ATTACHMENT_SCALE_INHERITANCE=DISABLED`
- `G3V_GEOMETRY_SCALE=SKELETON_DERIVED`
- `G3V_PHASE_SELECTION=CONTACT_DERIVED_QUARTER_CYCLE`
- `G3V_CAMERA_CALIBRATION=SKELETON_HEAD_FOOT`
- `G3V_MASK_SEQUENCE_TOTALS=...`

Expected valid review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_contact_sheet.png`

### G3V kill switch

If a validated representative human still reads only as conventional 3D made blocky, hidden 3D is rejected as owner of the final visible character. It remains the motion/topology/socket/physics backbone and final character art moves to structured 2D.

G4 remains blocked until G3V review.

### Exact next action — DO ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03c_run_g3v.ps1"
```

Then STOP. If G3V reaches `REVIEW REQUIRED`, share `g3v_contact_sheet.png`. If it fails, share the full console output.

## Workspace state

- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
- active deterministic character pipeline: `Z:\AI\RogueliteCharacterPipeline`
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`
