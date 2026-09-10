# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-10**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / STATIC T2I PROVEN / PRECISION EDITOR GATE ACTIVE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

The project requires a production tool for the **entire game's visual asset base**, not an Exilada-specific editor and not a single-model prompt UI.

The Roguelite Asset Studio is the local authoring/control plane used to create, revise, animate, approve, version and export game assets with specialized generative models and deterministic processing.

It must cover playable characters, NPCs, humanoid/non-humanoid enemies, bosses, weapons, armor/equipment, props/interactables, architecture, terrain, vegetation, environment set pieces, materials/textures, VFX/environment animation and UI art where needed.

The Exilada is the first high-difficulty Character Lab case. **No Exilada-specific assumption defines the generic tool contract.**

## Core production rule — HARD LOCK

The Asset Studio is a **model router + asset-state system**, not a wrapper around one checkpoint.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized model adapter -> local model runtime -> deterministic processors -> candidate/version store -> explicit approval -> runtime export`

The tool owns asset specification, semantic reference-role assignment, model routing, execution, deterministic preprocessing/postprocessing, candidate comparison, provenance/history, explicit approval and export.

Models are replaceable. Approved asset state and provenance are not.

## Local-first requirement — HARD LOCK

Routine production must work locally after installation because of repeatability, cost control, batch generation, arbitrary reference sets, mature/adult fictional states, long animation jobs, exact version preservation and future project-specific training.

Hosted APIs may be optional accelerators/quality branches, never a mandatory normal-production dependency.

Hardware baseline:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB RAM;
- AI root `Z:\AI`;
- repo `D:\GOOGLE DRIVE\DEV\Roguelite`.

## Asset taxonomy

Initial types:

- `character_playable`, `character_npc`, `enemy_humanoid`, `enemy_creature`, `boss`;
- `weapon`, `armor_equipment`, `prop`;
- `architecture_module`, `terrain_module`, `vegetation`, `environment_setpiece`, `tileable_material`;
- `vfx`, `ui_art`.

Initial output contracts include `static_master`, `static_rgba`, `variant_set`, `turnaround_reference`, `animated_action`, `animated_loop`, `sprite_row`, `sprite_atlas`, `layered_environment_module`, `tileable_texture`, `sequence_rgba`.

Asset type never implies one fixed model.

## Reference roles — HARD CONTRACT

References are semantically typed:

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

Adapters translate ordered semantic roles into model-specific conditioning. The UI/state layer must not hard-code ComfyUI graph semantics.

## Generic foundation — PASS

Machine-readable foundation:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`
- `tools/roguelite-asset-studio/adapter_protocol.py`

Runner55 proved referenced-character and reference-free-environment routing. `references` must exist structurally, while `references: []` is valid for reference-free generation.

## Canonical production stages

1. brief/specification;
2. concept/static master;
3. controlled variants/states;
4. temporal generation where required;
5. reconstruction into the approved game rendering language when needed;
6. deterministic extraction/alpha/alignment/pivots/timing/seams/metadata;
7. explicit candidate review/approval;
8. runtime export.

Routine manual per-frame repainting, hand compositing and manual masks are not a production dependency.

## Current model routing

### MiniMax H3 Base Ref2VA — ACTIVE / motion specialist

Current proven character-motion baseline. Uses target appearance reference + real motion video and produces complete temporal character masters including body/hair/cloth behavior. It is not the universal still generator.

### MiniMax H3 FL2VA — temporal candidate

Future candidate for environmental loops, VFX and first/last-frame tasks. Validate per asset class.

### FLUX.1 Kontext [dev] — R&D only

Useful for editing/reconstruction research. Dev licensing prevents silently making it the commercial-production default.

### FLUX.2 Klein 4B distilled — ACTIVE fast T2I/concept

Runner56 proved fast local T2I on RTX 3060 12 GB at 768×768 / 4 steps / CFG 1 / Euler in **12.054 s**.

Runners57/58 proved reference editing technically but rejected it visually for production: more steps produced broad rerender/material drift without reliable structural-fact obedience.

Routable:

- `text_to_image`
- `interactive_concept`

Not routable:

- production structural/reference editing.

### FLUX.2 Klein 4B Base — valid Base/training branch, not precision editor

Runner60 fixed the Runner59 graph error and proved sane VAE/T2I/edit color behavior. Runner61 then tested atomic and sequential editing.

Final edit verdict:

**coarse semantic edit useful / exact structural localization FAIL.**

It can remove/reinterpret broad semantic regions and preserve coarse sequential states, but cannot reliably isolate one named plank/strap/block without over-editing. Retain for T2I/training/project-specialization research, not precision structural routing.

### Qwen-Image-Edit-2509 — technical PASS / precision FAIL / retired editor evidence

Runner62 proved native FP8 feasibility on RTX 3060 12 GB with:

- diffusion FP8;
- Qwen2.5-VL 7B FP8 encoder on CPU;
- Qwen image VAE;
- ComfyUI low-VRAM/offload;
- 1024×1024;
- 20 steps / CFG 4 / Euler/simple;
- no OOM.

It preserved/localized edits substantially better than Klein, but still failed exact structural facts:

- one-plank request did not create an unambiguous one-plank full-height opening;
- one-strap request reinterpreted local hardware/door-bottom geometry instead of simply breaking the named strap.

Therefore 2509 is not production-routable. Its generated evidence is preserved; its diffusion checkpoint may be removed when 2511 activates. Shared Qwen2.5-VL + VAE remain useful.

### Qwen-Image-Edit-2511 — CURRENT precision-editor gate

Canonical record:

`docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`

Why it is the current hypothesis:

- same Apache-2.0 Qwen edit family;
- official revision targets lower image drift, better consistency and stronger geometric reasoning;
- reuses already-installed Qwen2.5-VL encoder and Qwen image VAE;
- only the new 2511 diffusion payload is required.

Runner63 checkpoint:

`qwen_image_edit_2511_fp8mixed.safetensors`

- bytes `20,533,762,817`;
- SHA256 `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`.

Runner63 uses current native ComfyUI 2511 semantics at commit:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

including:

- `TextEncodeQwenImageEditPlus`;
- `FluxKontextMultiReferenceLatentMethod(index_timestep_zero)`;
- `ModelSamplingAuraFlow` shift 3.1;
- `CFGNorm` 1;
- Euler/simple/denoise 1;
- CFG 4;
- 20 and 40 step precision tests.

The gate compares, for both one-plank and one-strap tasks:

`original -> Klein Runner61 -> Qwen2509 Runner62 -> Qwen2511/20 -> Qwen2511/40`.

2511 only passes if it executes the named structural fact more precisely, not merely if it changes fewer pixels.

### Step1X-Edit — deferred

Current memory profile remains poorly matched to the workstation. Do not prioritize while stronger same-family/local control hypotheses remain.

## Character Lab

The older Exilada-specific editor is prototype evidence only. Its useful concepts—identity/anatomy/style roles, iterative candidates, native resolution, history and explicit approval—belong behind the generic Studio contracts.

The reopened Exilada master becomes the first high-difficulty Character Lab validation **after a precision editor passes its non-character structural gate**.

Character Lab must support identity, anatomy, style/material, approved-state and later motion references without requiring routine manual masking or repainting.

## Environment/map production principle

The living belt-scroller world should not default to one flattened AI-painted gameplay map. Prefer reusable independently composed terrain patches, cliffs/walls, architecture modules, doors/gates, vegetation, rocks/debris, props, foreground/background pieces, loops and damage-state variants.

## Animated-asset contract

Characters/creatures:

`approved static master + motion reference/context -> temporal motion master -> action distillation -> rendering-language reconstruction -> alpha/pivot/events -> one action row/sequence -> runtime`

Environment/VFX:

`approved static state + temporal instruction/reference -> temporal master -> loop/sequence extraction -> rendering-language reconstruction if needed -> alpha/seam/timing metadata -> runtime`

## Resolution contract — HARD LOCK

The Studio imposes no universal 128/192/384 px sprite-cell size. Preserve useful source/final generation resolution. Runtime apparent/world scale is separate and must not create a second destructively reduced gameplay raster asset.

## Filesystem/provenance contract

Large model/generated data remains outside Git. Long-term umbrella state:

`Z:\AI\RogueliteAssetStudio\`

with project specs, references, candidate histories, approved state, jobs/cache and exports. Existing specialist workspaces may remain outside this root and be referenced by adapters.

## Project-specific specialization strategy

Once enough approved, licensable project art exists, train/evaluate Roguelite-specific adapters for rendering language/pixel art, character-family consistency, environment/material language, creature/anatomy families and damage/state variants.

## Immediate implementation order

1. run Runner63 and issue the Qwen-Image-Edit-2511 exact-precision verdict;
2. if precision PASS, validate multi-reference semantic role separation;
3. then validate the reopened Exilada as the first difficult Character Lab case;
4. validate another non-character class;
5. expose approved adapters through the generic Studio UI/state/candidate/history/approval layer;
6. wrap proven H3 Ref2VA behind the same orchestration boundary for animated actions;
7. resume final rendering-language/pixel-art specialization from approved masters.

If Qwen 2511 fails exact precision at both 20 and 40 steps, do not continue blind step tuning. Move to automatic localization/region-control architecture or another editor family while keeping routine manual masking outside the production contract.

## Hard conclusion

The project is building a **local generative game-asset production system**, not a character-specific image editor. Specialized models remain interchangeable; approved asset identity/state and provenance remain stable; static and animated production must scale from one protagonist to the entire game asset catalog.
