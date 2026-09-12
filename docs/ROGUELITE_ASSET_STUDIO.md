# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-12**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / AUTOMATIC MASK STACK PROVEN / TASK-CONDITIONED OBJECT-REMOVAL GATE ACTIVE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

The Roguelite Asset Studio is the local authoring/control plane for the **entire game's visual asset base**. It is not an Exilada-specific editor and not a wrapper around one model.

It must cover playable characters, NPCs, humanoid/non-humanoid enemies, bosses, weapons, armor/equipment, props/interactables, architecture, terrain, vegetation, environment set pieces, materials/textures, VFX/environment animation and UI art where needed.

The Exilada remains the first high-difficulty Character Lab case. No Exilada-specific assumption defines the generic tool contract.

## Core production rule — HARD LOCK

Canonical architecture:

`Studio UI -> asset spec/state -> router -> specialized generation/edit/inpaint/perception/motion adapters -> deterministic processors -> candidate/version store -> explicit approval -> runtime export`

The tool owns:

- asset specification;
- semantic reference roles;
- model routing;
- automatic localization/segmentation/decomposition when needed;
- generation/edit/inpainting/removal execution;
- deterministic preprocessing/postprocessing;
- candidate comparison/provenance/history;
- explicit approval;
- runtime export.

Models are replaceable. Approved asset state and provenance are not.

## Local-first requirement — HARD LOCK

Routine production must work locally after installation because of repeatability, cost control, batch generation, arbitrary reference sets, mature/adult fictional states, long animation jobs, exact version preservation and future project-specific training.

Hardware baseline:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB RAM;
- AI root `Z:\AI`;
- repo `D:\GOOGLE DRIVE\DEV\Roguelite`.

Hosted APIs may be optional accelerators but never mandatory production dependencies.

## Semantic reference roles — HARD CONTRACT

References are typed as:

- `identity`
- `anatomy`
- `style`
- `material`
- `palette`
- `structure`
- `composition`
- `pose`
- `motion`
- `camera`
- `environment`
- `previous_approved_state`

Pipeline-control masks are not semantic references and must not be exposed as user-authored production inputs.

## Canonical production stages

1. brief/specification;
2. concept/static master;
3. controlled variants/states;
4. automatic parent/component localization when precision is required;
5. automatic segmentation and repeated-member decomposition when required;
6. operation-aware automatic mask generation;
7. route by operation type to semantic editor, task-conditioned object-removal backend, prompted fill backend, or another specialist;
8. deterministic regional/full-resolution composition;
9. temporal generation where required;
10. rendering-language reconstruction when needed;
11. deterministic alpha/alignment/pivots/timing/seams/metadata;
12. explicit candidate review/approval;
13. runtime export.

Routine manual per-frame repainting, hand compositing and user-drawn production masks are not dependencies.

## Current model routing

### MiniMax H3 Base Ref2VA — ACTIVE motion specialist

Proven character-motion baseline using appearance reference + real action video. Produces complete temporal character masters including body/hair/cloth behavior. Not a universal still generator.

### FLUX.2 Klein 4B distilled — ACTIVE fast T2I/concept

Runner56 proved fast local static generation. Runners57/58 rejected it for production precision editing.

Routable:

- `text_to_image`
- `interactive_concept`

### FLUX.2 Klein 4B Base — Base/training branch

Runner60 proved healthy Base parity; Runner61 proved exact structural edits remain too coarse. Retain for T2I/training/project-specialization research, not exact component routing.

### Qwen-Image-Edit-2511 — ACTIVE higher-level semantic editor

Keep for semantic/appearance/reference-driven revision and future Character Lab multi-reference role separation.

Do not route exact component removal/fill to Qwen2511. Runner68 proved native mask containment while requested physical operations remained near-no-ops.

### SDXL Inpainting 0.1 — RETIRED

Runner69 showed strong local response but wrong reconstruction below training resolution. Runner70 repeated the hard gate at `1024x1024` training-resolution parity and still failed both operations:

- plank remained rather than becoming an opening;
- strap remained structurally continuous;
- unrelated pixels remained perfectly protected.

Generated evidence is retained; the model payload was removed by Runner71 after exact-hash verification.

### Big-LaMa — RETIRED exact-removal candidate

Runner71 proved Big-LaMa technically healthy and exceptionally fast:

- four jobs in `7.478 s` total;
- exact deterministic outside-region preservation;
- no prompt or ComfyUI dependency.

However, both tight and expanded variants failed semantically:

- plank: reconstructed wooden/door continuity instead of a true opening;
- strap: reconstructed/smoothed local ferrage instead of exposing a real wood break.

Classification:

**TECHNICAL PASS / VERY FAST / MASK+COMPOSITOR PASS / VISUAL OBJECT-REMOVAL FAIL.**

The model is not production-routable and Runner72 removes its checkpoint after validating Runner71 evidence.

### PowerPaint v2.1 / BrushNet — CURRENT object-removal candidate

Runner72 tests a backend with an explicit learned `object removal` task rather than generic context completion.

Pinned PowerPaint behavior:

- learned positive task token family: `P_ctxt`;
- learned negative task token family: `P_obj`;
- standard text conditioning remains available to describe desired empty context and name the object that must not return.

This directly addresses the repeated failure mode of LaMa/SDXL/Qwen: reconstructing or preserving the target because that is easier than understanding the requested physical operation.

## Precision-control architecture — MASK STACK ACCEPTED

Canonical precision architecture:

`semantic request -> parent/component perception -> automatic segmentation/decomposition -> operation-specific mask -> specialist regional backend -> deterministic full-resolution composite`

The no-manual-mask rule is hard.

### Runner64 — flat localization

Flat Grounding DINO search selected side stone blocks instead of plank/strap. Deterministic compositor nevertheless proved exact outside-region preservation.

### Runner65 — hierarchical localization

`full asset -> parent door -> child search -> SAM2 rerank`.

Visual result:

- parent door PASS;
- lower-right strap PASS;
- plank request found the correct repeated left leaf but not one board.

### Runner66 — repeated-member decomposition / COMPLETE PASS

Project-owned deterministic processor:

`semantic repeated structure -> persistent vertical seam energy -> atomic intervals -> one member mask`.

First proof:

- seam peaks `358`, `388`;
- selected plank interval `[358,388]`;
- width `30 px`;
- bbox `[358,295,388,644]`;
- vertical aspect `11.633`;
- visual PASS for one actual plank;
- Runner65 strap mask retained and visually correct;
- elapsed `0.321 s`;
- no model inference or manual mask.

This demonstrates a core Studio pattern: semantic models may localize a repeated structure while cheap deterministic processors resolve atomic members before expensive generation.

### Runner67 — colored locator / rejected

Qwen copied the visual locator and shifted local geometry. Colored locator images are not a production control mechanism.

### Runner68 — native Qwen latent mask / containment pass, editor fail

Native masking removed guide leakage and preserved exact region containment, but Qwen did not execute the removal/break strongly enough.

### Runner69/70 — SDXL dedicated inpaint / exhausted

Resolution parity was tested. The semantic operation still failed, so further arbitrary steps/CFG tuning was rejected.

### Runner71 — Big-LaMa / exhausted

The lightweight backend was fast and resolution-robust but performed blind context continuation rather than task-aware removal.

## CURRENT PRECISION GATE — Runner72 / PowerPaint v2.1 task-conditioned object removal

Canonical record:

`docs/RUNNER72_POWERPAINT_OBJECT_REMOVAL_2026-09-12.md`

Implementation:

- `tools/roguelite-asset-studio/powerpaint_brushnet_adapter.py`
- `tools/roguelite-asset-studio/powerpaint_object_removal_gate.py`
- `tools/structured-2d-character-pipeline/72_bootstrap_and_run_powerpaint_object_removal.ps1`

### Native integration

Use `nullquant/ComfyUI-BrushNet` pinned at:

`505d8ef917ddf3896afd1926770ecc9b099704e2`

Reuse shared ComfyUI code pinned at:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

Python dependencies are isolated in `Z:\AI\PowerPaint\venv` so the Qwen environment is not downgraded:

- `diffusers==0.29.2`;
- `accelerate==0.31.0`;
- `peft==0.11.1`.

### Payload

- SD1.5 base checkpoint: `4265146304` bytes, SHA256 `6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa`;
- PowerPaint v2.1 BrushNet: `3544366408` bytes, SHA256 `530f2886ef5bcdf199269ec344155a517639ba64219b85eeb23fd86aab93147f`;
- learned PowerPaint text encoder: `492401329` bytes, SHA256 `73709b4360ca06ef990a67d090e8d81a4310943d67a88845653fc4e9f7f26b65`;
- SD1.5 FP16 CLIP: `246144864` bytes, SHA256 `77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e`.

Total new model payload: approximately `8.55 GB`.

### Matrix

Runner72 reuses Runner71's exact `512x512` source contexts and tight/expanded masks:

- plank/tight;
- plank/expanded;
- strap/tight;
- strap/expanded.

PowerPaint recipe:

- function `object removal`;
- fitting `1.0`;
- scale `1.0`;
- `save_memory=max`;
- 20 steps;
- CFG `7.5`;
- Euler / normal;
- denoise `1.0`;
- seed `0`.

Visual PASS requires at least one mask variant per task:

1. one atomic plank actually disappears and becomes a plausible narrow opening/background continuation;
2. the strap middle actually disappears and exposes plausible aged wood;
3. both external strap ends survive;
4. unrelated source geometry remains authoritative.

If PowerPaint passes, route task-conditioned object removal to it. If it fails, replace only this backend; do not reopen the accepted perception, masks or deterministic compositor.

## Current perception payload

### Grounding DINO Tiny

- Apache-2.0;
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`;
- SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`.

### SAM2.1 Hiera Small

- Apache-2.0;
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`;
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`.

Perception runs separately from generative editors so these models do not compete for VRAM.

## Character Lab

The reopened Exilada master is the first difficult Character Lab validation after the generic precision-control architecture proves a useful non-character case.

Character Lab must support identity, anatomy, style/material, approved-state and later motion references without routine manual masking or repainting.

`assets/source/characters/exilada/reference/exilada_master.png` remains identity/anatomy evidence but is not final visual-design authority.

Required redesign direction remains stronger Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell charge, adult anatomy, materially caused clothing degradation/exposure, captivity wear and rejection of generic fantasy-bikini/MMO logic.

## Environment/map production principle

The living belt-scroller world should prefer reusable independently composed terrain patches, architecture modules, vegetation, debris, props, foreground/background pieces, damage states and loops rather than one flattened AI-painted map.

## Animated-asset contract

Characters/creatures:

`approved static master + motion reference/context -> temporal master -> action distillation -> rendering-language reconstruction -> alpha/pivot/events -> sprite row/sequence -> runtime`.

Environment/VFX:

`approved static state + temporal instruction/reference -> temporal master -> loop/sequence extraction -> reconstruction if needed -> alpha/seam/timing metadata -> runtime`.

## Resolution contract — HARD LOCK

No universal 128/192/384 px sprite-cell size. Preserve useful source/final generation resolution. Runtime apparent/world scale is separate and must not create a second destructively reduced gameplay raster asset.

## Filesystem/provenance contract

Large model/generated data remains outside Git. Long-term umbrella state lives under:

`Z:\AI\RogueliteAssetStudio\`

with specs, references, candidate histories, approved state, jobs/cache and exports. Specialist workspaces may remain separate and be referenced by adapters.

## Immediate implementation order

1. run Runner72 and review task-conditioned object-removal results;
2. if both hard operations pass, promote `automatic_region_object_removal`;
3. validate semantic multi-reference role separation using Qwen2511;
4. validate reopened Exilada as first difficult Character Lab case;
5. validate another non-character asset class;
6. expose approved adapters through the generic Studio UI/state/candidate/history/approval layer;
7. wrap proven H3 Ref2VA behind the same orchestration boundary;
8. resume final rendering-language/pixel-art specialization from approved masters.

## Hard conclusion

The project is building a **local generative game-asset production system**. Specialized generation, semantic editing, task-conditioned object removal, inpainting, perception and motion models are interchangeable; approved asset identity/state and provenance remain stable; static and animated production must scale from one protagonist to the entire game asset catalog.
