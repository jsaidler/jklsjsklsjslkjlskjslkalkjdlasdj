# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-11**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / STATIC T2I PROVEN / REPEATED-ELEMENT PERCEPTION GATE ACTIVE**

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
4. automatic parent/component localization/segmentation when an edit needs subcomponent precision;
5. deterministic structural decomposition when the localized target is a repeated/coarse structure rather than one atomic member;
6. local or global semantic editing as appropriate;
7. temporal generation where required;
8. reconstruction into the approved game rendering language when needed;
9. deterministic extraction/alpha/alignment/pivots/timing/seams/metadata;
10. explicit candidate review/approval;
11. runtime export.

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

## Precision-control architecture

Precision editing is treated as a composition of independent capabilities:

`semantic request -> parent/component perception -> optional repeated-element decomposition -> automatic mask/crop -> semantic editor -> deterministic regional composite`

The no-manual-mask rule remains hard: detection, instance choice, segmentation, repeated-element splitting and crop construction are pipeline responsibilities.

### Runner64 — flat localization experiment / COMPLETE

Canonical evidence:

`docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`

Runner64 tested:

`semantic target -> Grounding DINO Tiny on full asset -> selector -> SAM2.1 -> Qwen2511 crop edit -> deterministic composite`

Actual result:

- technical pipeline completed;
- plank selector chose the lower-left stone pedestal;
- strap selector chose the lower-right stone block;
- SAM2 segmented those wrong boxes cleanly;
- Qwen regional outputs are invalid semantic evidence because the target masks were wrong;
- deterministic compositing itself passed: pixels outside the allowed region had changed ratio above Δ12 of `0.0` in both tasks.

Final Runner64 classification:

**FLAT FULL-IMAGE SUBCOMPONENT LOCALIZATION FAIL / REGIONAL COMPOSITOR PASS.**

This proves that regional containment is useful while flat perception is not.

### Grounding DINO Tiny

Current compact open-vocabulary detector:

- repo `IDEA-Research/grounding-dino-tiny`;
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`;
- safetensors SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`;
- Apache-2.0.

### SAM2.1 Hiera Small

Current automatic box-to-mask segmenter:

- repo `facebook/sam2.1-hiera-small`;
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`;
- safetensors SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`;
- Apache-2.0.

Perception runs separately from Qwen so the models do not compete for VRAM.

## Runner65 — hierarchical perception / COMPLETE PARTIAL PASS

Canonical record:

`docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`

Architecture:

`full asset -> parent object grounding -> parent crop/upscale -> component grounding -> SAM2 multi-candidate rerank -> human visual gate`

Actual result:

- parent door: **PASS**;
- lower-right strap: **PASS**;
- plank request: Grounding DINO + SAM2 found the correct **left door leaf**, but not one individual board;
- Runner65 plank mask bbox `[325,285,422,651]`, area relative to parent `0.27724`, visually the complete left leaf;
- Runner65's `auto_valid=true` for the plank was too permissive for the semantic requirement.

Final classification:

**SEMANTIC HIERARCHY PASS / STRAP ATOMIC PASS / REPEATED-STRUCTURE LEAF PASS / ONE-PLANK ATOMIC GRANULARITY FAIL.**

This evidence changes the next step: the perception stack already found the correct repeated structure. Replacing the detector immediately would conflate semantic localization with atomic repeated-member decomposition.

## CURRENT PRECISION GATE — RUNNER66 / repeated-element atomic decomposition

Canonical record:

`docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`

Processor:

`tools/roguelite-asset-studio/repeated_element_decomposer.py`

Runner:

`tools/structured-2d-character-pipeline/66_run_repeated_element_decomposition_gate.ps1`

Architecture:

`Runner65 localized repeated structure -> persistent oriented seam profile -> atomic intervals -> target-relative member -> deterministic mask -> visual gate`

Current first proof:

`door -> left leaf -> persistent vertical board joints -> one plank`

Runner66 intentionally runs **no model inference** and no Qwen generation. It consumes the Runner65 source/mask/manifest and uses image structure only.

For the vertical plank proof:

- horizontal pixel differences are measured inside the localized leaf;
- differences are aggregated robustly across height so persistent vertical joints survive while local texture/horizontal hardware are attenuated;
- seam peaks are non-maximum-suppressed;
- seams plus leaf edges define board intervals;
- intervals are ranked by target-relative position, seam strength, leaf occupancy and width plausibility;
- the selected interval is intersected with the existing leaf mask;
- the atomic geometry gate now requires small parent-relative area, high vertical aspect, narrow width and near-full leaf-height span.

Runner65's visually correct strap mask is retained unchanged rather than rerun.

Runner66 PASS requires:

1. the plank mask corresponds to exactly one actual vertical board;
2. the mask spans that board rather than a small patch;
3. unrelated stone/frame regions are excluded;
4. the retained lower-right strap mask remains correct.

Only after Runner66 passes visually should Qwen2511 be reconnected behind the deterministic regional compositor.

### Why repeated-element decomposition belongs in the generic Studio

Many assets contain repeated members that open-vocabulary detectors reasonably collapse into a larger structure:

- door/fence planks;
- prison/cage bars;
- railings;
- roof slats;
- repeated armor plates;
- wall panels;
- ribs/spines;
- mechanical fins.

The Studio therefore treats `repeated_element_decomposition` as a deterministic processing capability rather than a door-specific production hack.

### Future perception upgrade — deferred

A stronger local concept/visual grounding or dense-correspondence backend may replace/augment the compact perception stack if semantic hierarchy plus repeated-element decomposition still cannot isolate difficult targets. Do not add larger perception checkpoints before Runner66 evidence exists.

### Step1X-Edit — deferred

Current memory profile remains poorly matched to the workstation. Do not prioritize while the automatic precision-control architecture is still being validated.

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

1. run Runner66 and review the atomic plank mask plus retained Runner65 strap mask;
2. if Runner66 perception/structure passes, reconnect Qwen2511 to the validated atomic regions and deterministic compositor;
3. if repeated-element decomposition fails, improve/replace only the atomic-decomposition/perception backend behind the same no-manual-mask contract;
4. if perception is correct but the local semantic edit still fails, test a region-aware/inpainting editor behind the same automatic-mask contract;
5. after regional precision passes, validate semantic multi-reference role separation;
6. validate the reopened Exilada as the first difficult Character Lab case;
7. validate another non-character class;
8. expose approved adapters through the generic Studio UI/state/candidate/history/approval layer;
9. wrap proven H3 Ref2VA behind the same orchestration boundary for animated actions;
10. resume final rendering-language/pixel-art specialization from approved masters.

## Hard conclusion

The project is building a **local generative game-asset production system**, not a character-specific image editor. Specialized generation, editing, perception, deterministic structure processors and motion models remain interchangeable; approved asset identity/state and provenance remain stable; static and animated production must scale from one protagonist to the entire game asset catalog.
