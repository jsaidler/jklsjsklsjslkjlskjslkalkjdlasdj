# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-09**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / FIRST GENERIC STATIC BACKEND T2I PROVEN / REFERENCE EDIT GATE ACTIVE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

The project requires a production tool for the **entire game's visual asset base**, not an Exilada-specific editor and not a single-model prompt UI.

The Roguelite Asset Studio is the local authoring/control plane used to create, revise, animate, approve, version and export game assets with specialized generative models and deterministic post-processing.

The tool must cover at minimum:

- playable characters and NPCs;
- humanoid/non-humanoid enemies and bosses;
- weapons, armor and equipment;
- props and interactables;
- architecture modules;
- terrain, ground, cliffs and vegetation modules;
- environment/map set pieces;
- tileable materials/textures where useful;
- environmental/combat/VFX animation;
- portraits/icons/UI art where needed.

The Exilada is the first high-difficulty Character Lab case because she stresses identity preservation, mature anatomy, hair, cloth, restraints, adult nudity/state variation and animation. **No Exilada-specific assumption may define the generic tool contract.**

## Core production rule — HARD LOCK

The Asset Studio is a **model router + asset-state system**, not a wrapper around one checkpoint.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized model adapter -> local model runtime -> deterministic processors -> candidate/version store -> explicit approval -> runtime export`

The tool owns:

1. asset specification;
2. semantic reference-role assignment;
3. model/pipeline routing;
4. generation/edit execution;
5. deterministic preprocessing/postprocessing;
6. candidate comparison;
7. provenance/version history;
8. explicit approval;
9. runtime export.

Models are replaceable. Approved asset state and provenance are not.

## Local-first requirement — HARD LOCK

Routine production must work locally after model installation because of:

- repeatability and cost control;
- large batch generation;
- arbitrary project reference sets;
- mature/adult fictional character states that may be unsuitable for hosted authoring surfaces;
- long-running animation jobs;
- preservation of exact model/workflow versions;
- future project-specific LoRA/fine-tuning.

Hosted APIs may later be optional accelerators/quality branches, never a mandatory normal-production dependency.

Current hardware baseline:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB system RAM;
- AI/model root `Z:\AI`;
- project repo `D:\GOOGLE DRIVE\DEV\Roguelite`.

## Asset taxonomy

Canonical initial asset types:

- `character_playable`
- `character_npc`
- `enemy_humanoid`
- `enemy_creature`
- `boss`
- `weapon`
- `armor_equipment`
- `prop`
- `architecture_module`
- `terrain_module`
- `vegetation`
- `environment_setpiece`
- `tileable_material`
- `vfx`
- `ui_art`

Canonical initial output contracts:

- `static_master`
- `static_rgba`
- `variant_set`
- `turnaround_reference`
- `animated_action`
- `animated_loop`
- `sprite_row`
- `sprite_atlas`
- `layered_environment_module`
- `tileable_texture`
- `sequence_rgba`

Asset type never implies one fixed model.

## Reference roles — HARD CONTRACT

References are semantically typed rather than passed as an undifferentiated image list:

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

Examples:

- character image -> `identity`;
- nude turnaround -> `anatomy`;
- visual-art references -> `style` / `material`;
- real action video -> `motion`;
- existing master -> `previous_approved_state`;
- existing architectural module -> `structure`.

The adapter translates ordered semantic references into model-specific conditioning. UI and asset-state logic must never hard-code ComfyUI graph semantics.

## Generic schema/router foundation — PASS

Machine-readable foundation:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`

Runner55 proved the router with two distinct cases:

- referenced playable character requiring edit capabilities;
- reference-free architecture module requiring T2I.

Schema rule: `references` is structurally required, but `references: []` is valid for reference-free generation.

## Generic adapter boundary — ACTIVE

The first UI-independent adapter contract now exists:

- `tools/roguelite-asset-studio/adapter_protocol.py`
- `tools/roguelite-asset-studio/flux2_klein_adapter.py`

`StaticGenerationRequest` carries:

- job id;
- asset type;
- output contract;
- prompt/negative instruction;
- ordered semantic references;
- width/height;
- steps/CFG/sampler/seed.

`GenerationResult` records:

- adapter id;
- backend prompt id;
- output path;
- elapsed time;
- reference hashes;
- output hash;
- original request.

This boundary is intentional: a future dedicated Studio UI may replace Gradio without rewriting model graphs.

## Canonical production stages

### 1. Brief / specification

Create an asset project with identity, gameplay/narrative role, world scale, art profile, output contract, constraints and semantic references.

### 2. Concept / static master

Generate or edit a source design master. No animation begins from an unapproved design.

### 3. Variant/state generation

Create controlled states such as clothing/armor, damage/wear, restraint, enemy rank, material/color, open/closed/broken, seasonal/environmental variants while preserving approved identity/design where required.

### 4. Motion/temporal generation

Route animated assets to the appropriate temporal specialist. Character/creature actions may use real-video motion reference; environment/VFX may use first/last-frame or image-to-video paths.

### 5. Rendering-language reconstruction

If the motion/static master is not already in final runtime visual language, reconstruct it into the approved project rendering language. Current character direction remains deliberate modern pixel art.

### 6. Deterministic extraction/cleanup

Where applicable: alpha extraction, frame distillation, alignment, pivots, loop optimization, tile/seam checks, palette/material checks, edge cleanup, collision/anchor metadata. Routine per-frame repainting remains disallowed.

### 7. Review/approval

Every generation is a candidate. Approval is explicit and must never be implied by successful generation.

### 8. Runtime export

Export only approved state: images/sequences/sheets/atlases + JSON metadata, pivots/events/rectangles, hashes and provenance.

## Current model families

### MiniMax H3 Base Ref2VA — ACTIVE proven motion specialist

Current use: character identity + real action video -> complete motion master including body/hair/cloth behavior. Existing Exilada Base50 remains the motion-quality baseline. H3 is not the universal still generator.

### MiniMax H3 FL2VA — TEMPORAL candidate

Potential path for first/last-frame animation, environmental loops, VFX and set-piece motion without authoritative performer video. Validate by asset class before production use.

### FLUX.1 Kontext [dev] FP8 — ACTIVE R&D only

Useful for editing/reconstruction R&D. Its dev license means it must not silently become the commercial-production default without appropriate licensing.

### FLUX.2 Klein 4B distilled — ACTIVE static T2I / EDIT VALIDATION IN PROGRESS

Workspace:

`Z:\AI\Flux2Klein`

License: Apache-2.0.

Runner56 actual local proof on RTX 3060 12 GB:

- 768×768;
- 4 distilled steps;
- CFG 1.0;
- Euler;
- seed 0;
- **12.054 s** inference;
- no OOM/crash;
- coherent useful architecture master generated.

Registry status:

`active_static_t2i_proven_edit_pending`

Currently active/routable capabilities:

- `text_to_image`
- `interactive_concept`

Planned but **not routable** until Runner57 passes:

- `single_reference_edit`
- `multi_reference_edit`
- `interactive_variant`

The Runner56 gate image is useful but not approved game art: it still has excess symmetry and some polished/generic fantasy asset language. This makes it a deliberate edit-control source.

Detailed evidence:

`docs/FLUX2_KLEIN_4B_ASSET_STUDIO_SPIKE_2026-09-08.md`

### FLUX.2 Klein 4B Base — TRAINING/SPECIALIZATION candidate

Do not download yet. It remains strategically important for future Roguelite-specific fine-tuning/LoRAs once enough approved, licensable training data exists.

### Qwen-Image-Edit / 2509 — HEAVY quality/control candidate

Apache-2.0 and promising for stronger structural controls, but materially heavier. Requires a dedicated 12-GB/low-VRAM feasibility spike before normal use.

### Step1X-Edit — DEFERRED

Published memory requirements remain poorly matched to the workstation; do not prioritize ahead of proven candidates.

## Runner57 — ACTIVE reference-edit gate

Runner:

`tools/structured-2d-character-pipeline/57_run_flux2_klein_reference_edit_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_edit_gate.py`

Runner57 downloads **no new model** and reuses the proven isolated Runner56 stack.

It validates the same generic adapter with two jobs:

1. single-reference editing — original gate as `previous_approved_state`; preserve identity/camera/construction while making requested damage/material changes;
2. ordered multi-reference editing — original gate as `structure`, single-edit result as `material`; preserve Image 1 identity/structure while carrying useful damage/material information from Image 2.

Both remain 768×768, 4 steps, CFG 1.0, Euler, seed 0 so only the reference-conditioning contract changes.

Pass requires both technical execution and human review. Only after visual PASS may edit capabilities move from `planned_capabilities` to active `capabilities` in the registry.

## Character Lab

The older Exilada-specific editor is prototype evidence only. Its useful concepts—identity/anatomy/style roles, iterative candidates, useful native resolution, history and explicit approval—are being refactored behind the generic Studio adapter/state contracts.

After Runner57 passes, the next high-difficulty static test should use the generic adapter on Exilada with identity/anatomy/art-direction references rather than expanding Exilada-only code.

## Environment / map production principle

The living belt-scroller world should not default to one flattened AI-painted gameplay map.

Prefer reusable independently simulated/composed modules:

- terrain patches/strips;
- cliffs/walls;
- façades/modules;
- doors/gates;
- vegetation groups;
- rocks/debris;
- furniture/props;
- foreground/background set pieces;
- environmental loops;
- decals/damage states.

The game/level system composes them. Large background plates are allowed where they do not destroy gameplay modularity.

## Animated-asset contract

Characters/creatures:

`approved static master + motion reference/context -> temporal motion master -> action distillation -> rendering-language reconstruction -> alpha/pivot/events -> one action row/sequence -> runtime`

Environment/VFX:

`approved static state + temporal instruction/reference -> temporal master -> loop/sequence extraction -> rendering-language reconstruction if needed -> alpha/seam/timing metadata -> runtime`

The temporal adapter may differ by asset class.

## Resolution contract — HARD LOCK

The Studio imposes **no universal 128/192/384 px or other sprite cell size**.

Useful source resolution is preserved. Runtime display/world scale is separate. Resolution depends on model quality, asset class, action envelope and later atlas/runtime constraints rather than a destructive one-size-fits-all downscale.

## Filesystem contract

Large model/generated data remains outside Git.

Umbrella local root:

`Z:\AI\RogueliteAssetStudio\`

Long-term project-state layout:

- `projects/<asset_id>/spec.json`
- `projects/<asset_id>/references/`
- `projects/<asset_id>/candidates/<candidate_id>/`
- `projects/<asset_id>/approved/`
- `jobs/`
- `cache/`
- `exports/`

Existing isolated model workspaces may remain outside this root and be referenced by adapters.

## Project-specific specialization strategy

The long-term goal is not permanent dependence on generic public style LoRAs. Once enough approved project art exists, train/evaluate Roguelite-specific adapters only from material whose provenance/license permits training.

Likely targets:

- final rendering-language / pixel-art adapter;
- character-family consistency;
- environment/material language;
- creature/anatomy families;
- damage/state variants.

## Immediate implementation order

1. run Runner57 and validate single + multi-reference editing;
2. if visual PASS, activate Klein edit capabilities in the registry;
3. expose the adapter through a generic Studio UI/state layer;
4. validate Character Lab on the reopened Exilada master using semantic identity/anatomy/style references;
5. validate another non-character class such as prop/equipment;
6. add generic candidate comparison/history/approval/export;
7. wrap proven H3 Ref2VA behind the same orchestration boundary for animated actions;
8. add environmental/VFX temporal routes only after their own task-specific gates;
9. resume final pixel-art/rendering-language specialization from approved masters.

## Hard conclusion

The project is building a **local generative game-asset production system**, not a character-specific image editor.

Specialized models must remain interchangeable; approved asset identity/state and provenance must remain stable; static and animated production must scale from one protagonist to the entire game asset catalog.
