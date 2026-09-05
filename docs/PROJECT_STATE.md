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
18. current tooling under `tools/deterministic-character-pipeline/`

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
- raw Blender `Action` copy between G2 and MPFB rigs: **REJECTED as retarget method**.
- raw per-frame `matrix_basis` copy between G2 and MPFB rigs: **REJECTED as retarget method** because later gait phases visibly collapse under rest-space mismatch.

## Active deterministic architecture

`gameplay camera/scale -> real motion -> deterministic rig/topology -> validated retarget -> representative visual asset -> native semantic passes -> pixel-specific visible representation -> modular equipment/state composition -> sprite/runtime export -> automated QA`

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
  - **G3V-R — retarget preflight** ← active sub-gate
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

Arbitrary cross-skeleton retargeting and production foot-lock cleanup were explicitly not solved by G2.

## G3 — NATIVE PIXEL TRANSLATION: TECHNICAL PASS / LOOK NOT APPROVED

Deterministic native-grid translation works, but primitive proxy output remained a technical mannequin / low-detail 3D. G2's 12-frame sequence remains the authoritative existing temporal evidence.

## G3R — RENDERER / STYLE REFINEMENT: FAIL / CLOSED

Renderer-only changes could not invent authored human form, silhouette or identity detail absent from the source representation.

Marker: `tools/deterministic-character-pipeline/g3r_failure.json`.

## G3V — REPRESENTATIVE VISUAL PROXY: PAUSED AT RETARGET SUB-GATE

Detailed log: `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`.

### Proven G3V infrastructure

- pinned MPFB 2.0.17 loads directly in one Blender background process;
- continuous female body and weighted `cmu_mb` rig are created;
- representative long hair / degraded cloth / wrist+ankle restraints render;
- accessory scale inheritance is controlled through rigid relative transforms and local-scale bake;
- binary semantic masks provide skin/hair/cloth/metal ownership diagnostics;
- contact-derived gait period is `80` frames at 120 fps;
- quarter-cycle frames are `1568,1588,1608,1628`;
- camera remains under the locked G1 presentation.

### Latest visual result — movement appears, deformation is wrong

The newest G3V sheet is no longer frozen: all four phases are visibly distinct. However later phases show severe target-body collapse, especially around pelvis/legs/trunk.

This changes the diagnosis:

- G2 source motion remains valid;
- frame selection is valid;
- MPFB body/weights render;
- direct target animation is invalid because source and target rest spaces are not interchangeable.

The old `matrix_basis` transfer is therefore rejected. Do not continue patching renderer, body, hair, cloth or pixel translation around a broken retarget.

## G3V-R — RETARGET PREFLIGHT: ACTIVE / READY TO RUN

Canonical log:

`docs/G3V_RETARGET_PREFLIGHT_LOG.md`

Tooling:

- `tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`
- `tools/deterministic-character-pipeline/g3v_retarget_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_retarget_preflight.py`

Purpose:

- compare source/target hierarchy, rest orientation and proportions;
- derive the same four real gait phases from G2 contacts;
- evaluate MPFB's documented pose API and an explicit rest-compensated FK method in one deterministic run;
- score joint-angle fidelity, endpoint-motion residual and pose diversity;
- choose the objectively better method;
- render source-vs-target skeleton contact sheet only after numeric PASS.

Numeric preflight thresholds:

- >= 3 distinct target poses;
- mean elbow/knee absolute error <= 15 deg;
- max elbow/knee error <= 35 deg;
- normalized endpoint-motion RMS <= 0.18 body heights.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v_retarget\g3v_retarget_contact_sheet.png`

### Exact next action — DO ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03d_run_g3v_retarget_preflight.ps1"
```

Then STOP. If it reaches `G3V RETARGET PREFLIGHT: REVIEW REQUIRED`, share `g3v_retarget_contact_sheet.png`. If it fails, share the full console output.

Do **not** rerun `03c_run_g3v.ps1` and do not start G4 until G3V-R passes.

## Workspace state

- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
- active deterministic character pipeline: `Z:\AI\RogueliteCharacterPipeline`
- retarget preflight workspace: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`
