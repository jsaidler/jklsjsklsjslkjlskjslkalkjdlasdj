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

Canonical thematic docs require:

- complete persistent body under clothing;
- modular clothing/armor/accessories/weapons;
- structural + surface damage to clothing/armor;
- stable named sockets;
- hair/cloth secondary motion and wind interaction;
- wetness/blood/dirt/material state;
- dynamic lighting via discrete palette/material metadata;
- liquids and event-driven VFX;
- deterministic anatomical gore/sever zones;
- detached limb/equipment inheritance;
- optional unclothed body states without relying on generative image synthesis.

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

Validated on Windows 11 + Blender 5.1.1. Headless Python scene creation, `.blend` save, PNG rendering, manifests and hashes work.

## G1 — CAMERA / NATIVE SCALE: PASS / CLOSED

Locked baseline:

- native gameplay raster: **`640×360`**;
- orthographic pitch: **`26 deg`**;
- protagonist reference visible height: **`128 px`**.

Canonical baseline: `tools/deterministic-character-pipeline/g1_baseline.json`.

## G2 — REAL MOTION / TOPOLOGY: PASS / CLOSED

Source: CMU Graphics Lab Motion Capture Database, trial `105_34 NormalWalk`, pinned MotionBuilder-friendly BVH conversion.

Accepted for G2 scope: stable major-limb topology, real left/right gait alternation, natural captured motion basis and deterministic persistent structure under the locked G1 camera.

Canonical approval: `tools/deterministic-character-pipeline/g2_approval.json`.

Arbitrary cross-skeleton retargeting and production foot-lock cleanup are not generally solved yet.

## G3 — NATIVE PIXEL TRANSLATION: TECHNICAL PASS / LOOK NOT APPROVED

The primitive semantic proxy proved deterministic native-grid translation, but remained a technical mannequin / processed low-detail 3D.

**Correction:** G3's old four-frame subset could alias the gait cycle, so G2's full 12-frame review remains the authoritative temporal/topology evidence. G3's visual-style conclusion remains valid.

## G3R — RENDERER / STYLE REFINEMENT: FAIL / CLOSED

Renderer-only contour/value/cluster changes could not invent authored human form, silhouette, hair/cloth structure or identity detail absent from the source representation.

Marker: `tools/deterministic-character-pipeline/g3r_failure.json`.

## G3V — REPRESENTATIVE VISUAL PROXY: ACTIVE / LOCAL-SCALE-BAKE RERUN REQUIRED

Detailed log: `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`.

Tooling:

- `tools/deterministic-character-pipeline/03c_run_g3v.ps1`
- `tools/deterministic-character-pipeline/g3v_mpfb_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_bone_attachment_patch.py`
- `tools/deterministic-character-pipeline/g3v_geometry_phase_patch.py`
- `tools/deterministic-character-pipeline/g3v_semantic_masks.py`
- `tools/deterministic-character-pipeline/g3v_representative_visual_proxy.py`

### Proven G3V infrastructure

- pinned MPFB 2.0.17 loads directly in one background Blender process;
- MPFB `base.obj` imports;
- continuous female body and CMU-compatible rig are created;
- G2 real walk is reused;
- Eevee writes diagnostic passes;
- runtime patches bind to the actual `target_main.__globals__` namespace;
- binary masks distinguish real occlusion from classifier/material failures;
- gait sampling now derives a measured 80-frame cycle from G2 foot contacts and uses phases `1568,1588,1608,1628`;
- camera calibration uses skeleton head-to-foot projection, not accessory bbox.

### Latest run — exact blocker

The latest first frame reported:

- body geometry height: `1.713562`;
- skeleton height: `1.647693`;
- skeleton camera calibrated to locked 128 px target;
- skin: `visible=0`, `unoccluded=2314`;
- hair: `3426` visible pixels;
- cloth: `47692` visible pixels;
- metal: `visible=0`, `unoccluded=501`;
- composite semantic bbox: **285 px** high.

This is physically inconsistent with the sane body/skeleton dimensions. Therefore the current blocker is not MPFB or camera: representative attachment geometry is retaining inflated transform scale.

### Current fix — committed

`g3v_bone_attachment_patch.py` now:

1. bakes each proxy primitive's authored `obj.scale` directly into mesh vertices;
2. resets object scale to `(1,1,1)` before storing the bone-relative transform;
3. follows bones using explicit rigid translation+rotation matrices only;
4. disables inherited parent/bone scale entirely;
5. prints authored scale and resulting world dimensions for every attachment;
6. runs a hard dimension audit after all 10 representative attachments exist;
7. refuses rendering if any attachment's largest dimension exceeds 80% of skeleton height.

Expected markers:

- `G3V_ATTACHMENT_MODE=RIGID_RELATIVE_MATRIX`
- `G3V_ATTACHMENT_SCALE_INHERITANCE=DISABLED`
- `G3V_ATTACHMENT_LOCAL_SCALE=BAKED_TO_MESH`
- `G3V_ATTACHMENT_CREATED=...`
- `G3V_ATTACHMENT_AUDIT=...`
- `G3V_ATTACHMENT_DIMENSION_AUDIT=PASS`

If this passes, binary semantic totals must then show visible skin and metal before the result can proceed to visual review.

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
