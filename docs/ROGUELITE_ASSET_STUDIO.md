# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-11**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / STATIC T2I PROVEN / AUTOMATIC LATENT-MASK PRECISION GATE ACTIVE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

The project requires a production tool for the **entire game's visual asset base**, not an Exilada-specific editor and not a single-model prompt UI.

The Roguelite Asset Studio is the local authoring/control plane used to create, revise, animate, approve, version and export game assets with specialized generative models and deterministic processing.

It must cover playable characters, NPCs, humanoid/non-humanoid enemies, bosses, weapons, armor/equipment, props/interactables, architecture, terrain, vegetation, environment set pieces, materials/textures, VFX/environment animation and UI art where needed.

The Exilada remains the first high-difficulty Character Lab case. No Exilada-specific assumption defines the generic tool contract.

## Core production rule — HARD LOCK

The Asset Studio is a **model router + asset-state system**, not a wrapper around one checkpoint.

Canonical architecture:

`Studio UI -> asset spec/state -> router -> specialized generation/edit/perception/motion adapters -> deterministic processors -> candidate/version store -> explicit approval -> runtime export`

The tool owns:

- asset specification;
- semantic reference roles;
- model routing;
- automatic localization/segmentation/decomposition when needed;
- generation/edit execution;
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

## Asset taxonomy

Initial types include:

- `character_playable`, `character_npc`, `enemy_humanoid`, `enemy_creature`, `boss`;
- `weapon`, `armor_equipment`, `prop`;
- `architecture_module`, `terrain_module`, `vegetation`, `environment_setpiece`, `tileable_material`;
- `vfx`, `ui_art`.

Output contracts include static masters/RGBA, variant sets, turnaround references, animated actions/loops, sprite rows/atlases, layered environment modules, tileable textures and RGBA sequences.

Asset type never implies one fixed model.

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

Adapters translate ordered semantic roles into model-specific conditioning. Pipeline-control masks are not semantic references and must not be exposed as user-authored production inputs.

## Generic foundation — PASS

Authority:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`
- `tools/roguelite-asset-studio/adapter_protocol.py`

Runner55 proved referenced-character and reference-free-environment routing. `references` must exist structurally while `references: []` remains valid for reference-free generation.

## Canonical production stages

1. brief/specification;
2. concept/static master;
3. controlled variants/states;
4. automatic parent/component localization when precision is required;
5. automatic segmentation and repeated-member decomposition when required;
6. operation-aware region control;
7. local/global semantic editing as appropriate;
8. temporal generation where required;
9. rendering-language reconstruction when needed;
10. deterministic alpha/alignment/pivots/timing/seams/metadata;
11. explicit candidate review/approval;
12. runtime export.

Routine manual per-frame repainting, hand compositing and user-drawn production masks are not dependencies.

## Current model routing

### MiniMax H3 Base Ref2VA — ACTIVE motion specialist

Proven character-motion baseline using appearance reference + real action video. Produces complete temporal character masters including body/hair/cloth behavior. Not a universal still generator.

### MiniMax H3 FL2VA — future temporal candidate

Potential environment/VFX/first-last-frame specialist. Validate per asset class.

### FLUX.1 Kontext [dev] — R&D only

Useful for edit/reconstruction research. Dev licensing prevents making it the commercial-production default.

### FLUX.2 Klein 4B distilled — ACTIVE fast T2I/concept

Runner56 proved 768×768 / 4 steps / CFG 1 / Euler in `12.054 s` on RTX 3060 12 GB.

Routable:

- `text_to_image`
- `interactive_concept`

Runners57/58 rejected it for production precision editing.

### FLUX.2 Klein 4B Base — Base/training branch

Runner60 fixed the graph and proved sane runtime behavior; Runner61 proved exact structural edits remain too coarse.

Retain for T2I/training/project-specialization research, not exact component routing.

### Qwen-Image-Edit-2509 — retired

Runner62 proved feasibility/preservation improvement but exact plank/strap facts still failed. Diffusion checkpoint deleted after evidence preservation; shared encoder/VAE retained.

### Qwen-Image-Edit-2511 — strongest installed semantic editor

Installed:

- `qwen_image_edit_2511_fp8mixed.safetensors`;
- bytes `20,533,762,817`;
- SHA256 `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`;
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`;
- Qwen2.5-VL 7B FP8 on CPU;
- Qwen image VAE;
- low-VRAM / reserve 1 GB;
- AuraFlow shift 3.1;
- CFGNorm 1;
- Euler/simple / CFG 4.

Runner63 closed unrestricted global precision prompting: plank improved but strap produced a large replacement bar, and 40 steps did not solve the hard case.

Qwen2511 remains the current semantic editor, but precision must come from external automatic control.

## Precision-control architecture

Canonical precision architecture:

`semantic request -> parent/component perception -> automatic segmentation/decomposition -> operation-specific mask -> semantic editor -> deterministic full-resolution composite`

The no-manual-mask rule is hard.

### Runner64 — flat localization / COMPLETE

Flat Grounding DINO search selected side stone blocks instead of the requested plank/strap.

Useful proof:

- SAM2 segmented the selected boxes cleanly;
- deterministic regional composite preserved source pixels outside allowed masks with changed ratio >Δ12 of `0.0`.

### Runner65 — hierarchy / COMPLETE

`full asset -> parent door -> child search -> SAM2 rerank`.

Visual result:

- parent door PASS;
- lower-right strap PASS;
- plank request found the correct repeated left leaf but not one board.

### Runner66 — repeated-member decomposition / COMPLETE PASS

Project-owned deterministic processor:

`semantic repeated structure -> persistent vertical seam energy -> atomic intervals -> one member mask`.

First proof:

- internal seam peaks `358`, `388`;
- selected plank interval `[358,388]`;
- width `30 px`;
- bbox `[358,295,388,644]`;
- vertical aspect `11.633`;
- visual PASS for one actual plank;
- Runner65 strap mask retained and still visually correct;
- elapsed `0.321 s`;
- no model inference or manual mask.

This demonstrates an important Studio pattern: semantic models may localize a repeated structure while cheap deterministic processors resolve atomic members before any expensive generation.

### Runner67 — approved masks + visual locator guide / COMPLETE FAIL

Architecture:

`approved automatic mask -> source crop + red overlay reference -> Qwen2511 -> deterministic composite`.

Technical execution passed but edit control failed:

- plank raw generation created a narrow opening that shifted relative to the separately applied mask, producing distorted strips after final composition;
- strap raw generation copied the red locator rectangle into content instead of making a physical break;
- outside-region changed ratio >Δ12 remained `0.0` for both tasks.

Final classification:

**AUTOMATIC MASKS PASS / COMPOSITOR PASS / RED GUIDE LEAK FAIL / CROP-MASK ALIGNMENT FAIL.**

Colored locator references are rejected as production control.

## CURRENT PRECISION GATE — Runner68 / native automatic latent mask

Canonical record:

`docs/RUNNER68_QWEN2511_LATENT_MASK_REGION_EDIT_2026-09-11.md`

Implementation:

- `tools/roguelite-asset-studio/qwen_image_edit_2511_masked_adapter.py`
- `tools/roguelite-asset-studio/qwen2511_latent_mask_region_gate.py`
- `tools/structured-2d-character-pipeline/68_run_qwen2511_latent_mask_region_edit.ps1`

Architecture:

`Runner66 approved automatic mask -> contextual source crop -> same-scale mask -> ImageToMask -> SetLatentNoiseMask on VAE source latent -> Qwen2511 -> deterministic final composite`.

Key properties:

- Qwen receives only the source crop as semantic image conditioning;
- no colored guide image exists in the model inputs;
- mask and source pass through the same Qwen/FluxKontext scaling path;
- sampling noise is restricted natively to the automatic operation region;
- final composition applies a second deterministic containment layer;
- no new model download;
- no user box or mask.

Operation semantics:

- plank removal: use the complete Runner66 atomic plank mask;
- strap break: automatically derive and edit only the central `40%` of the approved strap mask so both ends remain source-authoritative.

Runner68 PASS requires:

1. plank becomes a clean aligned same-width opening;
2. neighboring planks/door remain stable;
3. strap middle is absent while both ends survive;
4. no replacement bar;
5. no locator-color leak;
6. outside-region pixels remain source pixels by construction.

If Runner68 passes, promote `automatic_region_edit` and test semantic multi-reference role separation before Exilada Character Lab.

If Runner68 fails with correct masks, keep perception/decomposition/compositor accepted and replace only the regional editor with a dedicated mask-native/inpainting backend.

## Current perception payload

### Grounding DINO Tiny

- Apache-2.0;
- `IDEA-Research/grounding-dino-tiny`;
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`;
- SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`.

### SAM2.1 Hiera Small

- Apache-2.0;
- `facebook/sam2.1-hiera-small`;
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`;
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`.

Perception runs separately from Qwen so these models do not compete for VRAM.

## Character Lab

The reopened Exilada master is the first difficult Character Lab validation after the generic precision-control architecture proves a real non-character case.

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

1. run Runner68 and review latent-mask plank/strap edits;
2. if both pass, promote automatic regional precision editing;
3. validate semantic multi-reference role separation;
4. validate reopened Exilada as first difficult Character Lab case;
5. validate another non-character asset class;
6. expose approved adapters through the generic Studio UI/state/candidate/history/approval layer;
7. wrap proven H3 Ref2VA behind the same orchestration boundary;
8. resume final rendering-language/pixel-art specialization from approved masters.

If Runner68 fails, replace only the regional editor behind the already-proven automatic target/mask/compositor contract before proceeding.

## Hard conclusion

The project is building a **local generative game-asset production system**. Specialized generation, editing, perception and motion models are interchangeable; approved asset identity/state and provenance remain stable; static and animated production must scale from one protagonist to the entire game asset catalog.
