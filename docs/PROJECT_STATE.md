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

- FLUX.2 Klein + RefControl direct-frame animation: **REJECTED / FROZEN** after V1/V2/V3; V3 produced a three-leg/three-foot frame and accessory/topology drift.
- Qwen-Image-Edit-2509: **PAUSED** as a possible constrained future component only.
- high-resolution beauty render followed by generic shrink/pixel filter: **REJECTED as final-art route**.
- routine manual frame-by-frame repainting: **REJECTED as production burden**.
- repeated outline/cluster/palette refinement on a primitive mannequin: **REJECTED after G3R**.

## Active deterministic architecture

`gameplay camera/scale -> real motion -> deterministic rig/topology -> representative visual asset -> native semantic passes -> pixel-specific visible representation -> modular equipment/state composition -> sprite/runtime export -> automated QA`

Hard operator constraint:

- no routine Blender GUI work;
- no manual rigging/animation/pixel-production operation by the user;
- no hired art/animation team assumed;
- recurring production must be driven by ChatGPT-authored CLI/headless tooling.

Canonical operator pattern:

`PowerShell -> blender.exe --background --python ... -> deterministic outputs/reports`

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

- `640×360`;
- orthographic pitch `26 deg`;
- protagonist reference height `128 px`.

Canonical marker: `tools/deterministic-character-pipeline/g1_baseline.json`.

## G2 — REAL MOTION / TOPOLOGY: PASS / CLOSED

Source: CMU `105_34 NormalWalk` at 120 fps.

Accepted scope:

- stable major-limb topology;
- real left/right gait alternation;
- natural captured motion basis;
- deterministic persistent structure;
- usable under G1 camera/scale.

Canonical marker: `tools/deterministic-character-pipeline/g2_approval.json`.

Arbitrary cross-skeleton retargeting and production foot-lock cleanup are not generally solved yet.

## G3 — NATIVE PIXEL TRANSLATION: TECHNICAL PASS / LOOK NOT APPROVED

Deterministic native-grid translation works, but primitive proxy output remained a technical mannequin / low-detail 3D. The old four-frame G3 subset can alias gait phases; G2's 12-frame sequence remains the authoritative temporal evidence.

## G3R — RENDERER / STYLE REFINEMENT: FAIL / CLOSED

Renderer-only changes could not invent authored human form, silhouette or identity detail absent from the source representation.

Marker: `tools/deterministic-character-pipeline/g3r_failure.json`.

## G3V — REPRESENTATIVE VISUAL PROXY: ACTIVE / MOTION-BINDING RERUN REQUIRED

Detailed log: `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`.

Current tooling:

- `tools/deterministic-character-pipeline/03c_run_g3v.ps1`
- `tools/deterministic-character-pipeline/g3v_mpfb_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_bone_attachment_patch.py`
- `tools/deterministic-character-pipeline/g3v_geometry_phase_patch.py`
- `tools/deterministic-character-pipeline/g3v_semantic_masks.py`
- `tools/deterministic-character-pipeline/g3v_motion_binding_patch.py`
- `tools/deterministic-character-pipeline/g3v_representative_visual_proxy.py`

### Proven G3V infrastructure

- pinned MPFB 2.0.17 loads directly in one Blender background process;
- continuous female body and `cmu_mb` weighted rig are created;
- representative long hair / degraded cloth / wrist+ankle restraints render;
- accessory scale inheritance has been removed through rigid relative transforms and local-scale bake;
- binary semantic masks provide skin/hair/cloth/metal ownership diagnostics;
- gait phase selection derives from G2 contacts;
- current quarter-cycle frames: `1568,1588,1608,1628`;
- camera remains under the locked G1 presentation.

### First coherent contact sheet — important result but NOT VALID FOR PASS

The first visually coherent G3V contact sheet finally shows a human rather than blank/exploded proxy geometry. Skin, long dark hair, cloth and restraints are legible and the native 4-band row is visually inspectable.

However, quantitative review of the uploaded sheet found that the character area in all four columns is **byte-identical** for both rows. Frames `1568,1588,1608,1628` therefore display the same pose even though the frame selection itself is distinct.

Consequence:

**G3V remains technically invalid.** It cannot yet prove weighted deformation, gait, temporal continuity or attachment stability. Do not lock an aesthetic PASS/FAIL conclusion from this sheet and do not start G4.

### Current blocker — MPFB target rig is frozen

Boundary is now clear:

- G2 source motion remains valid;
- G3V phase selection is valid;
- visible representative asset is valid enough for testing;
- failure lies in motion transfer from `G2_CANONICAL_RIG` to `G3V_CMU_RIG`.

Copying the source Blender `Action` onto the MPFB rig is no longer trusted as motion authority.

### Current fix — explicit per-frame motion binding

`g3v_motion_binding_patch.py` now:

1. verifies required CMU bones on source and target rigs;
2. verifies `G3V_BODY` has an Armature modifier bound to `G3V_CMU_RIG`;
3. disables the MPFB target Action;
4. before bbox/render, copies matching source pose-bone `matrix_basis` values from `G2_CANONICAL_RIG` into `G3V_CMU_RIG` for the current frame;
5. updates Blender dependency graph;
6. records target pose signatures;
7. rejects review unless there are at least 3 unique target poses;
8. rejects review unless there are at least 3 unique rendered skin masks.

Expected markers:

- `G3V_MOTION_BINDING_MODE=EXPLICIT_PER_FRAME`
- `G3V_MOTION_BINDING=EXPLICIT_MATRIX_BASIS_FROM_G2`
- `G3V_TARGET_ACTION=DISABLED`
- `G3V_BODY_ARMATURE_MODIFIER=PASS`
- `G3V_MOTION_POSE_FRAME_...=BOUND`
- `G3V_MOTION_UNIQUE_POSES=...`
- `G3V_MOTION_UNIQUE_SKIN_MASKS=...`
- `G3V_MOTION_DIVERSITY_AUDIT=PASS`

A new contact sheet cannot reach `REVIEW REQUIRED` while still containing four identical body poses.

### G3V visual kill switch after motion is valid

Review order:

1. topology integrity;
2. actual motion/grounding;
3. body proportions and deformation;
4. attachment stability;
5. visible representation / pixel-art headroom.

If a technically valid representative human still reads only as conventional 3D made blocky, hidden 3D is rejected as owner of the final visible character while remaining the motion/topology/socket/physics backbone.

### Exact next action — DO ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03c_run_g3v.ps1"
```

Then STOP. If it reaches `G3V: REVIEW REQUIRED`, share the new `g3v_contact_sheet.png`. If it fails, share the full console output. Do not run G4.

## Workspace state

- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
- active deterministic character pipeline: `Z:\AI\RogueliteCharacterPipeline`
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`
