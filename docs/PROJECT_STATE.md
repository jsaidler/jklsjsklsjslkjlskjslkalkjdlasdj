# Roguelite — Current Project State

Status date: **2026-09-05**

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
16. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
17. current tooling under `tools/deterministic-character-pipeline/`

After every material step: update the relevant thematic document(s) + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Immediate gameplay presentation baseline:

**elevated 2D belt-scroller / false 3D**.

Final visible character/environment language remains **true modern pixel art** at native gameplay raster. Hidden 3D may own motion/topology/physics but is not automatically the final visible style.

## Exilada identity — LOCKED

Canonical high-detail identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines identity/design, not final gameplay pixels.

## Rejected / paused routes

- FLUX.2 Klein + RefControl direct-frame animation: **REJECTED / FROZEN** after V1/V2/V3; V3 produced a three-leg/three-foot frame and persistent accessory/topology drift.
- Qwen-Image-Edit-2509 spike: **PAUSED**, preserved only as a possible constrained future component.
- high-resolution beauty render followed by generic shrink/pixel filter: **REJECTED as final-art route**.
- routine manual frame-by-frame repainting: **REJECTED as production burden**.
- repeated outline/cluster/palette refinement on a primitive capsule/mannequin proxy: **REJECTED after G3R** because the source representation lacks the authored form needed to judge final art.

## Active deterministic character architecture — LOCKED FOR VALIDATION

`gameplay camera/scale -> real motion -> deterministic rig/topology -> representative visual asset -> pixel-specific visible representation -> modular equipment/state composition -> sprite/runtime export -> automated QA`

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

## Risk-first gate order — CURRENT

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

Validated environment:

- Windows 11 Home Single Language `10.0.26200`;
- Blender `5.1.1`;
- `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`;
- active workspace: `Z:\AI\RogueliteCharacterPipeline`.

Headless Python scene creation, `.blend` save, PNG rendering, manifests and hashes were validated.

Detailed log: `docs/G0_AUTOMATION_LOG.md`.

## G1 — CAMERA / NATIVE SCALE: PASS / CLOSED

Locked baseline:

- native gameplay raster: **`640×360`**;
- orthographic camera pitch: **`26 deg`**;
- protagonist reference visible height: **`128 px`**.

Canonical baseline: `tools/deterministic-character-pipeline/g1_baseline.json`.

Detailed log: `docs/G1_CAMERA_SCALE_LOG.md`.

## G2 — REAL MOTION / TOPOLOGY: PASS / CLOSED

Source: CMU Graphics Lab Motion Capture Database, trial `105_34 NormalWalk`, pinned MotionBuilder-friendly BVH conversion.

Accepted for G2 scope:

- stable major-limb topology;
- real left/right gait alternation;
- natural captured motion basis;
- persistent deterministic character structure;
- usable under the locked G1 camera/scale.

Canonical approval: `tools/deterministic-character-pipeline/g2_approval.json`.

Important boundary: arbitrary cross-skeleton retargeting and production foot-lock cleanup are not yet proven.

Detailed log: `docs/G2_MOTION_TOPOLOGY_LOG.md`.

## G3 — NATIVE PIXEL TRANSLATION: TECHNICAL PASS / LOOK NOT APPROVED

The primitive semantic proxy proved stable deterministic raster translation, but A/B/C still read as technical mannequin / processed low-detail 3D.

Useful result: deterministic motion/topology can drive stable native-grid material regions. Not enough to approve visible production art.

Detailed log: `docs/G3_PIXEL_TRANSLATION_LOG.md`.

## G3R — RENDERER / STYLE REFINEMENT: FAIL / CLOSED

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3r\g3r_contact_sheet.png`

D/E/F changed contour/value/cluster treatment but remained the same technical mannequin.

Root lesson:

**post-processing cannot invent authored human form, silhouette design, hair/cloth structure or identity-bearing detail that is absent from the source representation.**

Do not run more renderer-only variants on the capsule/mannequin proxy.

Detailed log: `docs/G3R_RENDERER_REFINEMENT_LOG.md`.

## G3V — REPRESENTATIVE VISUAL PROXY: ACTIVE NEXT GATE

Purpose: test the actual visible hypothesis with a materially richer continuous human asset before any finished Exilada model is built.

Preferred first candidate: **MakeHuman/MPFB 2.x** core human system, subject to local headless validation.

Minimal G3V asset must include:

- lean adult female continuous body mesh;
- real deformation rig/weights;
- large dark long-hair mass;
- one simple asymmetric degraded cloth mass;
- wrist/ankle restraint markers with stable side identity;
- bare feet;
- skin/hair/cloth/metal material IDs;
- one still + sampled approved real walk under `640×360 / 26 deg / ~128 px`.

G3V PASS requires the result to demonstrate a credible path to intentional modern pixel art **and** complete headless reproducibility.

If the representative continuous human asset still reads as filtered/low-resolution 3D, reject hidden 3D as the owner of the final visible character. Retain 3D only for motion/topology/sockets/physics guides and move the final image to a structured 2D representation.

G4 remains blocked until G3V passes.

Detailed gate plan: `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`.

## Workspace state

- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
- active deterministic character pipeline: `Z:\AI\RogueliteCharacterPipeline`
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`
