# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-10**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / STATIC T2I PROVEN / AUTOMATIC REGION-CONTROL GATE ACTIVE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

The project requires a production tool for the **entire game's visual asset base**, not an Exilada-specific editor and not a single-model prompt UI.

The Roguelite Asset Studio is the local authoring/control plane used to create, revise, animate, approve, version and export game assets with specialized generative models and deterministic processing.

It must cover playable characters, NPCs, humanoid/non-humanoid enemies, bosses, weapons, armor/equipment, props/interactables, architecture, terrain, vegetation, environment set pieces, materials/textures, VFX/environment animation and UI art where needed.

The Exilada is the first high-difficulty Character Lab case. **No Exilada-specific assumption defines the generic tool contract.**

## Core production rule — HARD LOCK

The Asset Studio is a **model router + asset-state system**, not a wrapper around one checkpoint.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized model/perception adapters -> local runtimes -> deterministic processors -> candidate/version store -> explicit approval -> runtime export`

The tool owns asset specification, semantic reference-role assignment, model routing, automatic localization when required, generation/edit execution, deterministic preprocessing/postprocessing, candidate comparison, provenance/history, explicit approval and export.

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
4. automatic component localization/segmentation when an edit needs subcomponent precision;
5. local or global semantic editing as appropriate;
6. temporal generation where required;
7. reconstruction into the approved game rendering language when needed;
8. deterministic extraction/alpha/alignment/pivots/timing/seams/metadata;
9. explicit candidate review/approval;
10. runtime export.

Routine manual per-frame repainting, hand compositing and user-drawn production masks are not dependencies.

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

- production precision/reference editing.

### FLUX.2 Klein 4B Base — valid Base/training branch, not precision editor

Runner60 fixed the Runner59 graph error and proved sane VAE/T2I/edit behavior. Runner61 then tested atomic and sequential editing.

Final edit verdict:

**coarse semantic edit useful / exact structural localization FAIL.**

Retain for T2I/training/project-specialization research, not precision structural routing.

### Qwen-Image-Edit-2509 — retired precision candidate

Runner62 proved native FP8 feasibility on RTX 3060 12 GB with low-VRAM execution and Qwen2.5-VL on CPU. It preserved/localized edits better than Klein but still failed exact one-plank and one-strap structural facts.

The 2509 diffusion checkpoint has been removed after preserving generated evidence. Shared Qwen2.5-VL + Qwen image VAE remain installed for 2511.

### Qwen-Image-Edit-2511 — strongest installed semantic editor / GLOBAL PRECISION PARTIAL

Canonical evidence:

`docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`

Installed checkpoint:

`qwen_image_edit_2511_fp8mixed.safetensors`

- bytes `20,533,762,817`;
- SHA256 `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`.

Runtime uses ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`, Qwen2.5-VL on CPU, `--lowvram`, `FluxKontextMultiReferenceLatentMethod(index_timestep_zero)`, AuraFlow shift 3.1, CFGNorm 1, Euler/simple and CFG 4.

Runner63 final result:

- one-plank / 20 and 40 steps: meaningful improvement over 2509/Klein; narrow opening created with strong source preservation;
- one-strap / 20 and 40 steps: FAIL; both produce a large replacement/transverse bar rather than breaking only the named lower-right strap;
- 40 steps roughly doubles cost without solving the hard failure.

Final classification:

**TECHNICAL PASS / PLANK IMPROVED / STRAP PRECISION FAIL / GLOBAL-PROMPT-ONLY PRECISION HYPOTHESIS CLOSED.**

Qwen2511 remains installed as the strongest semantic editor, but unrestricted global prompts are not routable as `precision_structural_edit`.

## CURRENT PRECISION ARCHITECTURE — RUNNER64 / automatic localization + region control

Canonical record:

`docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`

Architecture:

`semantic target -> Grounding DINO Tiny -> deterministic instance selector -> SAM2.1 Hiera Small -> contextual Qwen2511 crop edit -> deterministic automatic regional composite`

This is a control-architecture change, not another prompt-tuning pass.

### Grounding DINO Tiny

Role: public Apache-2.0 open-vocabulary text-grounded detection.

Pinned model:

- repo `IDEA-Research/grounding-dino-tiny`;
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`;
- safetensors SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`;
- ~689 MB.

### SAM2.1 Hiera Small

Role: convert the selected text-grounded box into an automatic component mask.

Pinned model:

- repo `facebook/sam2.1-hiera-small`;
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`;
- 184,305,280-byte safetensors;
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`;
- Apache-2.0.

Perception runs and exits before the Qwen runtime starts so the models do not compete for VRAM.

### No-manual-mask rule — HARD LOCK

The user does **not** draw masks or boxes. Detection, instance choice, segmentation, crop construction and final regional composite are pipeline responsibilities.

Runner64 persists candidate boxes, scores, masks, overlays, crops and provenance so perception errors can be distinguished from editor errors.

### Regional Qwen edit

Qwen2511 receives:

1. Image 1 = contextual crop from the source;
2. Image 2 = the same crop with an automatically generated target overlay.

The final crop result is composited into the original using an automatically dilated/feathered SAM2 mask. Pixels outside the generated allowed neighborhood remain sourced from the original image by construction.

Runner64 tests the same one-plank and lower-right-strap tasks that exposed the global-edit limitation.

### Future perception upgrade — SAM3.1

SAM3.1 is a stronger future concept-segmentation candidate with text/exemplar/visual prompting, but its official checkpoint is gated and materially larger. Do not make it a mandatory dependency until Runner64 proves whether the control architecture itself is useful with the public compact stack.

### Step1X-Edit — deferred

Current memory profile remains poorly matched to the workstation. Do not prioritize while the automatic region-control architecture is untested.

## Character Lab

The older Exilada-specific editor is prototype evidence only. Its useful concepts—identity/anatomy/style roles, iterative candidates, native resolution, history and explicit approval—belong behind the generic Studio contracts.

The reopened Exilada master becomes the first high-difficulty Character Lab validation after the generic control architecture proves it can make precise non-character edits without manual masks.

Character Lab must support identity, anatomy, style/material, approved-state and later motion references without routine manual masking or repainting.

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

1. run Runner64 and validate automatic GroundingDINO + SAM2.1 localization and regional Qwen2511 control;
2. if perception is wrong, improve/replace only the perception layer rather than blaming the editor;
3. if perception is correct but the local semantic edit fails, test a region-aware/inpainting editor behind the same automatic-mask contract;
4. after regional precision passes, validate semantic multi-reference role separation;
5. validate the reopened Exilada as the first difficult Character Lab case;
6. validate another non-character class;
7. expose approved adapters through the generic Studio UI/state/candidate/history/approval layer;
8. wrap proven H3 Ref2VA behind the same orchestration boundary for animated actions;
9. resume final rendering-language/pixel-art specialization from approved masters.

## Hard conclusion

The project is building a **local generative game-asset production system**, not a character-specific image editor. Specialized generation, editing, perception and motion models remain interchangeable; approved asset identity/state and provenance remain stable; static and animated production must scale from one protagonist to the entire game asset catalog.
