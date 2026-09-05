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
18. tooling under `tools/deterministic-character-pipeline/`

After every material step: update relevant thematic docs + this file and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: elevated 2D belt-scroller / false 3D.

Final visible language remains **true modern pixel art at native gameplay raster**. Hidden 3D may own motion/topology/physics but is not automatically approved as final visible character art.

## Exilada identity — LOCKED

Canonical identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

This is a design master, not final gameplay pixels.

## Hard operator constraint

Normal production must remain:

`PowerShell -> Blender headless / deterministic tools -> outputs/reports`

No routine Blender GUI operation, manual rigging/animation burden, frame-by-frame repainting, or hired specialist is assumed.

## Rejected / paused routes

- FLUX.2 Klein + RefControl direct-frame animation: REJECTED/FROZEN after topology drift and a three-leg frame;
- Qwen-Image-Edit-2509: PAUSED as possible constrained future component only;
- high-resolution beauty render + generic shrink/pixel filter: REJECTED as final-art route;
- primitive mannequin renderer tuning: REJECTED after G3R;
- raw Blender `Action` copy G2 -> MPFB: REJECTED as retarget method;
- raw per-frame `matrix_basis` copy G2 -> MPFB: REJECTED as retarget method;
- local-axis `REST_COMPENSATED_FK`: REJECTED after G3V-R V1.

## Active deterministic architecture

`camera/scale -> real motion -> deterministic topology -> validated retarget -> representative visual asset -> semantic/native-grid representation -> modular equipment/state -> sprite/runtime export -> QA`

## Gate order

- G0 automation
- G1 camera/native scale
- G2 real motion/topology
- G3 first native translation
- G3R primitive-renderer refinement
- G3V representative continuous human visual proxy
  - **G3V-R retarget preflight** ← ACTIVE
- G4 Exilada identity mapping
- G5 temporal stress pack
- G6 equipment/attachments
- G6A wind/secondary motion
- G6B liquid/contact VFX
- G6C gore topology
- G6D clothing/armor damage
- G7 systemic state/dynamic lighting
- G8 production scaling

A later expensive stage never starts merely because an earlier technical demo looks attractive.

# Current execution state

## G0 — PASS / CLOSED

Windows 11 + Blender 5.1.1 headless automation validated.

## G1 — PASS / CLOSED

Locked:

- raster `640×360`;
- orthographic pitch `26 deg`;
- protagonist reference height `128 px`.

Marker: `tools/deterministic-character-pipeline/g1_baseline.json`.

## G2 — PASS / CLOSED

Source: CMU `105_34 NormalWalk`, 120 fps.

Validated: captured locomotion basis, stable major-limb topology, left/right alternation and persistent deterministic structure.

Marker: `tools/deterministic-character-pipeline/g2_approval.json`.

G2 did not claim arbitrary cross-skeleton retargeting.

## G3 — TECHNICAL PASS / LOOK NOT APPROVED

Native deterministic translation works, but primitive proxy output remained mannequin-like. G2 remains authoritative for motion continuity.

## G3R — FAIL / CLOSED

Renderer-only changes could not invent missing authored human form. No G3R2.

Marker: `tools/deterministic-character-pipeline/g3r_failure.json`.

## G3V — PAUSED AT RETARGET

Proven:

- pinned MPFB 2.0.17 loads directly in one Blender background process;
- continuous female body and weighted `cmu_mb` rig are created;
- representative long hair, degraded cloth, restraints and bare feet render;
- accessory scale inflation is fixed;
- semantic skin/hair/cloth/metal masks work;
- gait period is contact-derived: `80` frames;
- phases: `1568,1588,1608,1628`;
- G1 camera/scale are usable.

The latest body sheet produced real phase changes but severe later-phase deformation collapse. The blocker is retargeting, not renderer/camera/source mocap.

Detailed log: `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`.

## G3V-R — RETARGET PREFLIGHT: V3 ACTIVE / BOOTSTRAP IMPORT FIXED

Detailed log: `docs/G3V_RETARGET_PREFLIGHT_LOG.md`.

Canonical runner:

`tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`

### Locked rest-rig facts

- source/target identify as `cmu_mb`;
- required parent mismatches: `0`;
- mean rest-orientation delta: `83.1874 deg`;
- max rest-orientation delta: `180.0289 deg`.

Therefore naming/hierarchy match, but local/rest axes do not.

### V1 — FAIL / CLOSED

Local-axis fallback:

- 4 unique poses;
- mean elbow/knee angle error `25.0101 deg`;
- max error `43.6810 deg`;
- old endpoint RMS `0.27541`.

### V2 — solver result

`DIRECTION_SPACE_FK`:

- 4 unique poses;
- mean elbow/knee error `0.0000 deg`;
- max error `0.0001 deg`;
- old endpoint metric `0.24744`.

`MPFB_POSE_API`:

- 4 unique poses;
- mean elbow/knee error `25.4032 deg`;
- max error `44.3890 deg`;
- old endpoint metric `0.23865`.

Conclusion: direction-space transfer is decisively better for articulation. V2 failed only because the old endpoint metric subtracts each rig's incompatible rest pose, making it invalid under the measured ~83 deg rest mismatch.

### V3 — CURRENT

V3 retains V2's solvers and replaces only the invalid endpoint test with rest-independent:

`CHAIN_UNIT_DIRECTION_RMS`

The first V3 run did not execute the solver because Blender's `runpy.run_path()` did not expose the sibling script directory on `sys.path`, causing:

`ModuleNotFoundError: No module named 'g3v_retarget_preflight_v2'`

This was a bootstrap/package-path bug, not a retarget regression.

`g3v_retarget_bootstrap.py` now inserts `target_script.parent` into `sys.path` before executing V3. Expected marker:

`G3V_RETARGET_HELPER_PATH=BOUND`

Guard values remain unchanged:

- >= 3 unique poses;
- mean elbow/knee error <= 15 deg;
- max error <= 35 deg;
- chain-shape RMS <= 0.18.

### Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03d_run_g3v_retarget_preflight.ps1"
```

Then STOP.

If numeric PASS is reached, share:

`Z:\AI\RogueliteCharacterPipeline\g3v_retarget\g3v_retarget_contact_sheet.png`

If it fails, share the complete console output.

Do **not** rerun `03c_run_g3v.ps1` and do not start G4.

## Workspace

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- active deterministic pipeline: `Z:\AI\RogueliteCharacterPipeline`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
