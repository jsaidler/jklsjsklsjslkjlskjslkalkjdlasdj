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
14. `docs/G3_PIXEL_TRANSLATION_LOG.md`
15. `docs/G3R_RENDERER_REFINEMENT_LOG.md`
16. current tooling under `tools/deterministic-character-pipeline/`

After every material step: update the relevant thematic document(s) + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Immediate gameplay presentation baseline:

**elevated 2D belt-scroller / false 3D**.

Final visible character/environment language remains **true modern pixel art** at native gameplay raster. Hidden 3D may own motion/topology/physics but is not the final visible style.

## Exilada identity — LOCKED

Canonical high-detail identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines identity/design, not final gameplay pixels.

## Rejected / paused routes

- FLUX.2 Klein + RefControl direct-frame animation: **REJECTED / FROZEN** after V1/V2/V3; V3 produced a three-leg/three-foot frame and persistent accessory/topology drift.
- Qwen-Image-Edit-2509 spike: **PAUSED**, preserved only as a possible constrained future component. It is not the active production architecture.
- high-resolution beauty render followed by generic shrink/pixel filter: **REJECTED as final-art route**.
- routine manual frame-by-frame repainting: **REJECTED as production burden**.

## Active deterministic character architecture — LOCKED FOR VALIDATION

`gameplay camera/scale -> real motion -> deterministic rig/topology -> persistent secondary systems -> native-raster semantic passes -> pixel-specific renderer -> modular equipment/state composition -> sprite/runtime export -> automated QA`

Hard operator constraint:

- no routine Blender GUI work;
- no manual rigging/animation/pixel-production operation by the user;
- no hired animation/art team assumed;
- recurring production must be driven by ChatGPT-authored CLI/headless tooling.

Canonical pattern:

`PowerShell -> blender.exe --background --python ... -> deterministic outputs/reports`

## Systemic character-state requirements — LOCKED

Already architected in canonical thematic docs:

- complete persistent body under clothing;
- modular clothing/armor/accessories/weapons;
- structural + surface damage to clothing/armor;
- stable named sockets;
- hair/cloth secondary motion and wind interaction;
- wetness/blood/dirt/material state;
- dynamic lighting via discrete palette bands / semantic metadata;
- liquids and event-driven VFX;
- deterministic anatomical gore/sever zones;
- detached limb/equipment inheritance;
- optional unclothed body states without relying on generative image synthesis.

## Risk-first gate order — LOCKED

- **G0 — automation**
- **G1 — camera/native scale**
- **G2 — real motion/topology**
- **G3 — first pixel translation feasibility**
- **G3R — renderer/style refinement**
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

Validated environment:

- Windows 11 Home Single Language `10.0.26200`;
- Blender `5.1.1`;
- `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`;
- active workspace: `Z:\AI\RogueliteCharacterPipeline`.

Headless Python scene creation, `.blend` save, PNG rendering, manifests and hashes were validated.

Detailed log:

`docs/G0_AUTOMATION_LOG.md`

## G1 — CAMERA / NATIVE SCALE: PASS / CLOSED

Locked baseline:

- native gameplay raster: **`640×360`**;
- orthographic camera pitch: **`26 deg`**;
- protagonist reference visible height: **`128 px`**.

Canonical baseline file:

`tools/deterministic-character-pipeline/g1_baseline.json`

Detailed log:

`docs/G1_CAMERA_SCALE_LOG.md`

## G2 — REAL MOTION / TOPOLOGY: PASS / CLOSED

Source:

- CMU Graphics Lab Motion Capture Database;
- trial `105_34 NormalWalk`;
- pinned MotionBuilder-friendly BVH conversion.

The 12-sample sequence was visually reviewed and accepted for G2 scope:

- stable major-limb topology;
- real left/right gait alternation;
- natural captured motion basis;
- persistent deterministic character structure;
- usable under the locked G1 camera/scale.

Canonical approval marker:

`tools/deterministic-character-pipeline/g2_approval.json`

Important boundary: G2 did not prove arbitrary cross-skeleton retargeting or final foot-lock cleanup for all clips; those remain explicit scaling validations.

Detailed log:

`docs/G2_MOTION_TOPOLOGY_LOG.md`

## G3 — NATIVE PIXEL TRANSLATION: PASS TECHNICAL / LOOK NOT APPROVED

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3\g3_contact_sheet.png`

Findings:

- deterministic hidden-3D motion/topology can become a stable native-grid sprite;
- semantic skin/cloth/hair/metal regions remain controllable;
- method B (`palette_banded`) is the strongest first technical baseline;
- method C proves a coarser cluster experiment but is not production-ready;
- none of A/B/C is approved as the final visible language because the proxy still reads as a technical mannequin / processed low-detail 3D.

Canonical decision marker:

`tools/deterministic-character-pipeline/g3_technical_approval.json`

G4 remains blocked.

Detailed log:

`docs/G3_PIXEL_TRANSLATION_LOG.md`

## G3R — RENDERER / STYLE REFINEMENT: ACTIVE / READY TO RUN

Tooling:

- `tools/deterministic-character-pipeline/03b_run_g3r.ps1`
- `tools/deterministic-character-pipeline/g3r_renderer_refinement.py`

Purpose: refine the visible deterministic pixel language before any Exilada production geometry is built.

The same four approved real-walk frames are compared through:

1. **D — outlined 4-band:** four discrete material bands + deterministic 1 px exterior outline;
2. **E — edge-preserving cluster:** D plus 2×2 majority clustering only inside the silhouette, preserving native edge pixels;
3. **F — selective contour cluster:** E plus directional lower/right silhouette darkening to test a less-uniform sprite contour.

Automated diagnostics include foreground pixel count, character bbox, tiny-island count and per-output hashes.

G3R PASS requires at least one method to be credible as the production rendering foundation at actual 1× gameplay scale. If all three still read as processed technical 3D, G4 must not start and the visible representation strategy changes while the proven motion/topology backbone may remain.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3r\g3r_contact_sheet.png`

Detailed log:

`docs/G3R_RENDERER_REFINEMENT_LOG.md`

## Workspace state

- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
- active deterministic character pipeline: `Z:\AI\RogueliteCharacterPipeline`
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`
