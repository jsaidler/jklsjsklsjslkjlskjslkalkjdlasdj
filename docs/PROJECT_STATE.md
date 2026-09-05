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
19. tooling under `tools/deterministic-character-pipeline/` and `tools/structured-2d-character-pipeline/`

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
- hidden 3D as owner of final visible character color pixels: REJECTED after G3V visual kill switch.

Qwen-Image-Edit-2509 remains forbidden as independent per-frame animation owner. It is active only as a bounded one-time static source-art candidate in G3S-A.

## Active architecture — LOCKED

`camera/scale -> real motion -> deterministic hidden topology -> validated DIRECTION_SPACE_FK -> projected joints/depth/sockets -> persistent structured 2D pixel assets -> deterministic 2D composition/deformation -> sprite/runtime export -> QA`

Hidden 3D owns control/infrastructure only: motion, topology/left-right identity, sockets, contacts/root data, physics, depth/occlusion, semantic guides and secondary-motion drivers.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3 first native translation — TECHNICAL PASS / LOOK NOT APPROVED
- G3R primitive-renderer refinement — FAIL/CLOSED
- G3V representative continuous human visual proxy — FAIL/CLOSED
  - G3V-R retarget preflight — PASS/CLOSED
- **G3S structured 2D visible representation** ← ACTIVE
  - **G3S-A static Exilada source sprite V2** ← READY TO RUN
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

Locked: `640×360`, orthographic pitch `26 deg`, protagonist visible height `128 px`.

## G2 — PASS / CLOSED

Source: CMU `105_34 NormalWalk`, 120 fps. Real locomotion, stable major-limb topology, left/right alternation and deterministic structure validated.

## G3 / G3R

G3 proved deterministic native-grid processing technically possible but not production-looking. G3R proved renderer-only refinement cannot invent authored 2D form from a primitive source.

## G3V-R — PASS / CLOSED

Accepted cross-rig method: **`DIRECTION_SPACE_FK`**.

Measured facts:

- source/target parent mismatches: `0`;
- mean rest-orientation difference: `83.1874 deg`;
- max: `180.0289 deg`;
- 4 unique target poses;
- mean elbow/knee error: `0.0000 deg`;
- max: `0.0001 deg`;
- rest-independent chain-shape metric passed;
- source/target skeleton sheet visually passed topology and gait-phase correspondence.

Marker: `tools/deterministic-character-pipeline/g3v_retarget_approval.json`.

## G3V — FAIL / CLOSED

Failure marker: `tools/deterministic-character-pipeline/g3v_failure.json`.

Final reviewed body/pixel sheet at frames `1568,1588,1608,1628` was technically coherent but visually still read as simplified conventional 3D translated into coarse native-raster/palette output. Hidden 3D therefore remains infrastructure only.

# G3S — STRUCTURED 2D VISIBLE REPRESENTATION

Canonical design: `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`.

Goal: final visible pixels come from persistent authored 2D pixel assets while validated hidden motion/topology provides control data.

## G3S-A dependency state

The isolated Qwen runtime is now provisioned under:

`Z:\AI\QwenImageEditSpike`

with pinned Qwen 2509 Q4_0 GGUF, Qwen VL encoder and Qwen image VAE.

One-command operator path:

`tools/structured-2d-character-pipeline/00_bootstrap_and_run_g3s_a.ps1`

## G3S-A V1 — INVALID INFERENCE / HARNESS FAIL

The first completed G3S-A inference produced an almost-black raw frame/contact sheet. This is **not** a Qwen visual/model verdict.

Inspection found the V1 API graph was wrong relative to the official ComfyUI Qwen 2509 workflow:

- `image1` conditioning was the Exilada master while the sampled latent came from the guide;
- `CFGNorm` was missing;
- negative conditioning lacked the same refs/VAE structure;
- `20 steps / CFG 4.0` mixed two different official setting families.

Therefore V1 is classified **INVALID INFERENCE / HARNESS FAIL**, not G3S-A visual FAIL.

## G3S-A V2 — READY

New helper:

`tools/structured-2d-character-pipeline/g3s_a_static_source_v2.py`

Runner `01_run_g3s_a.ps1` now points to V2.

Workflow revision:

`QWEN2509_OFFICIAL_ALIGNED_NATIVE_V2`

V2 locks:

- Picture 1 = generated 640×360 pose/scale guide;
- Picture 1 is also the VAE-encoded `latent_image`;
- Picture 2 = exact canonical Exilada master;
- positive and negative Qwen edit conditioning both receive both refs + VAE;
- model path `UnetLoaderGGUF -> ModelSamplingAuraFlow(3.0) -> CFGNorm(1.0)`;
- `20` steps / CFG `2.5` / Euler / simple / denoise `1.0`;
- fixed seed `20260905`;
- no post-inference resize.

The official blueprint's `FluxKontextImageScale` is intentionally omitted because G3S-A specifically tests true 640×360 output instead of a ~1MP primary raster followed by shrink.

V2 includes an automatic near-black/flat-output guard. Invalid output now fails before `REVIEW_REQUIRED` instead of wasting a visual review.

Expected valid-review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_a\g3s_a_contact_sheet.png`

Review order remains:

1. topology: one head/torso, two arms/hands, two legs/feet;
2. Exilada identity/design continuity;
3. ~128 px gameplay scale and lateral/slight-3/4 presentation;
4. intentional modern pixel cluster language at native 1×;
5. long hair / degraded cloth / restraints / bare feet readability.

## G3S-B / C — BLOCKED

Only after one G3S-A static source is visually approved: decompose into persistent side-aware parts, then drive those parts from the validated hidden rig across frames `1568,1588,1608,1628` without per-frame generation.

## G4 — RESCOPED / BLOCKED

After G3S passes, G4 becomes the Exilada production 2D identity system: canonical sprite parts, palette/material families, hair/cloth/restraint structure, sockets/occlusion metadata and damage-ready layers.

# Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\00_bootstrap_and_run_g3s_a.ps1"
```

Runtime/models should be reused; this should proceed directly to V2 inference.

Then STOP. If it reaches `G3S-A: REVIEW REQUIRED`, share `Z:\AI\RogueliteCharacterPipeline\g3s_a\g3s_a_contact_sheet.png`. If it fails, share the complete console output. Do not start G3S-B or G4.

## Workspace

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- hidden deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- Qwen static-source runtime: `Z:\AI\QwenImageEditSpike`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
