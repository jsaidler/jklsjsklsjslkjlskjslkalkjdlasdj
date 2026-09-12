# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-11**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / AUTOMATIC MASK STACK PROVEN / SPECIALIST OBJECT-REMOVAL GATE ACTIVE**

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
- generation/edit/inpainting execution;
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
7. route by operation type to semantic editor, object-removal backend, prompted fill/inpainting backend, or other specialist;
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

Runner56 proved 768×768 / 4 steps / CFG 1 / Euler in `12.054 s` on RTX 3060 12 GB.

Routable:

- `text_to_image`
- `interactive_concept`

Runners57/58 rejected it for production precision editing.

### FLUX.2 Klein 4B Base — Base/training branch

Runner60 fixed the graph and proved sane runtime behavior; Runner61 proved exact structural edits remain too coarse.

Retain for T2I/training/project-specialization research, not exact component routing.

### Qwen-Image-Edit-2511 — ACTIVE higher-level semantic editor

Keep for semantic/appearance/reference-driven revision and future Character Lab role separation.

Do not route exact component removal/fill to Qwen2511. Runner68 proved native latent-mask containment but the requested operations remained semantic near-no-ops.

### SDXL Inpainting 0.1 — RETIRED exact-removal candidate

Runner69 proved strong local mask response but wrong reconstruction on subtraining-resolution crops. Runner70 removed the resolution confound by running exact `1024x1024` parity and still failed both hard operations.

Runner70 final evidence:

- plank inside-allowed >Delta12 `0.316580`, outside `0.0`, board remained present;
- strap inside-allowed >Delta12 `0.165934`, outside `0.0`, strap remained structurally continuous.

Classification:

**TECHNICAL PASS / MASK+COMPOSITOR PASS / VISUAL OPERATION FAIL / SDXL EXACT-REMOVAL ROLE CLOSED.**

Runner69/70 generated evidence is retained. Runner71 removes the retired SDXL model payload after exact-hash verification.

### Big-LaMa — CURRENT lightweight object-removal candidate

Runner71 tests a deliberately narrower specialist:

- no text prompt;
- input = source context + accepted automatic binary operation mask;
- direct TorchScript inference;
- no ComfyUI server;
- Apache-2.0 LaMa lineage;
- ~196 MiB model rather than another multi-GB diffusion stack.

Pinned artifact:

- `big-lama.pt`;
- bytes `205803670`;
- SHA256 `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`;
- upstream `enesmsahin/simple-lama-inpainting` v0.1.0 release.

TorchScript is executable; only the pinned size/hash may be loaded.

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

### Runner68 — native latent mask / containment pass, editor fail

Native masking removed guide leakage and preserved exact region containment, but Qwen did not execute the removal/break strongly enough.

### Runner69/70 — SDXL dedicated inpaint / exhausted

SDXL was given a fair second gate at 1024 training-resolution parity. It remained semantically wrong for the hard operations, so the backend is retired rather than tuned indefinitely.

## CURRENT PRECISION GATE — Runner71 / Big-LaMa automatic object removal

Canonical record:

`docs/RUNNER71_BIG_LAMA_OBJECT_REMOVAL_2026-09-11.md`

Implementation:

- `tools/roguelite-asset-studio/lama_inpaint_adapter.py`
- `tools/roguelite-asset-studio/lama_object_removal_gate.py`
- `tools/structured-2d-character-pipeline/71_bootstrap_and_run_big_lama_object_removal.ps1`

Runner71 keeps all accepted geometry/mask/compositor authority and changes only the removal engine.

To avoid rejecting a very cheap backend because of one arbitrary edge treatment, it tests two automatic mask-boundary variants per task:

- tight;
- expanded.

Four jobs total:

- plank/tight;
- plank/expanded;
- strap/tight;
- strap/expanded.

Visual PASS requires at least one variant per task:

1. one atomic plank actually disappears and becomes a plausible narrow opening/background continuation;
2. the strap middle actually disappears and exposes plausible underlying aged door/wood;
3. both external strap ends survive;
4. unrelated source geometry remains authoritative.

If Big-LaMa passes, route **object removal/background continuation** to it and keep prompt-driven semantic fill as a distinct capability. The Studio should not force one model to perform both jobs.

If it fails, replace only the removal backend; do not reopen perception, accepted masks or deterministic composition.

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

1. run Runner71 and review Big-LaMa tight/expanded object-removal results;
2. if both operations pass, promote `automatic_region_object_removal`;
3. separately validate prompted semantic fill/multi-reference role separation;
4. validate reopened Exilada as first difficult Character Lab case;
5. validate another non-character asset class;
6. expose approved adapters through the generic Studio UI/state/candidate/history/approval layer;
7. wrap proven H3 Ref2VA behind the same orchestration boundary;
8. resume final rendering-language/pixel-art specialization from approved masters.

## Hard conclusion

The project is building a **local generative game-asset production system**. Specialized generation, semantic editing, object removal, prompted inpainting, perception and motion models are interchangeable; approved asset identity/state and provenance remain stable; static and animated production must scale from one protagonist to the entire game asset catalog.
