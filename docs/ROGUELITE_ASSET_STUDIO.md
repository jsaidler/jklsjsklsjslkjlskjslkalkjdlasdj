# Roguelite Asset Studio — Local Generative Asset Production System

Status date: **2026-09-08**

Status: **CANONICAL UMBRELLA TOOL ARCHITECTURE / LOCAL-FIRST / MODEL-ROUTED / EXILADA IS FIRST CHARACTER-LAB CASE, NOT THE TOOL SCOPE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

The project requires a production tool for the **entire game's visual asset base**, not an Exilada-specific editor and not a single-model prompt UI.

The Roguelite Asset Studio is the local authoring/control plane used to create, revise, animate, approve, version and export game assets with specialized generative models and deterministic post-processing.

The tool must cover at minimum:

- playable characters;
- NPCs;
- ordinary enemies;
- elite enemies;
- bosses;
- humanoid and non-humanoid creatures;
- weapons, armor and equipment;
- props and interactables;
- architecture modules;
- terrain/ground/cliff/vegetation modules;
- map/background set pieces;
- tileable materials/textures where useful;
- environmental animation;
- combat/VFX animation;
- portraits/icons/UI art where the game needs authored imagery.

The Exilada is the first high-difficulty validation project because she stresses identity preservation, mature anatomy, hair, cloth, restraints, nudity/state variation and animation. **No Exilada-specific assumption may define the generic tool contract.**

## Core production rule — HARD LOCK

The Asset Studio is a **model router + asset-state system**, not a wrapper around one checkpoint.

Different tasks may use different specialized models. The tool owns:

1. asset specification;
2. reference-role assignment;
3. model/pipeline selection;
4. generation/edit execution;
5. deterministic preprocessing/postprocessing;
6. candidate comparison;
7. provenance/version history;
8. explicit approval;
9. runtime export.

A model is replaceable. Approved asset state and provenance are not.

## Local-first requirement — HARD LOCK

Routine production must be possible locally after model installation.

Reasons include:

- repeatability and cost control;
- large batch production;
- access to arbitrary project reference material;
- mature/adult character states that may be unsuitable for hosted authoring surfaces;
- long-running animation jobs;
- preservation of project-specific workflows and model versions;
- eventual fine-tuning/LoRA training on approved project art.

Hosted APIs may later exist as optional accelerators or quality branches, but must not be required for normal asset production.

## Hardware baseline

Current target workstation:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB system RAM;
- model/workspace root under `Z:\AI`;
- project repo under `D:\GOOGLE DRIVE\DEV\Roguelite`.

Model routing must account for this hardware explicitly. A model that requires substantially more VRAM may still be tested through quantization/offload if useful, but cannot silently become the default interactive path.

## Asset taxonomy

Every asset project has an `asset_type` and an `output_contract`.

Initial canonical asset types:

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

Initial output contracts:

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

Asset type does not imply one fixed model.

## Reference roles — HARD CONTRACT

References are assigned semantic roles instead of being dumped into an undifferentiated image list.

Supported roles must include:

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

The execution adapter translates those roles into the input semantics of each model.

Example:

- character image = identity;
- nude turnaround = anatomy;
- pulp-fantasy references = style/material;
- real action video = motion;
- existing approved master = previous_approved_state.

## Canonical production stages

### 1. Brief / asset specification

Create an asset project with:

- id and display name;
- asset type;
- narrative/gameplay role;
- world scale;
- art-profile id;
- required output contract;
- design constraints;
- references and their semantic roles.

### 2. Concept / master generation

Generate or edit the approved static design master.

This stage is used for characters, creatures, architecture modules, props, equipment, vegetation, set pieces and other static source assets.

No animation pipeline begins from a design that has not passed master approval.

### 3. Variant/state generation

Derive controlled variants while preserving the approved identity/design where required.

Examples:

- clothing/armor states;
- damage/wear states;
- restraint states;
- enemy rank variants;
- color/material variants;
- architecture damage states;
- seasonal/environmental states;
- prop open/closed/broken states.

### 4. Motion/temporal generation

Animated assets route to an animation model appropriate to the task.

Character/creature actions may use reference-video motion transfer. Environmental loops and VFX may use image-to-video/first-last-frame generation or a specialized temporal model.

### 5. Rendering-language reconstruction

If the motion master is not already in the final runtime visual language, reconstruct selected frames into the approved project rendering language.

For the current character direction this remains high-quality pixel art, but the pipeline must preserve useful source resolution rather than forcing old 128/192/384 px packaging assumptions.

### 6. Deterministic extraction and cleanup

Where applicable:

- alpha/background removal;
- frame selection/distillation;
- alignment;
- pivot/root derivation;
- loop boundary optimization;
- tile/seam validation;
- palette/material validation;
- transparent-edge cleanup;
- collision/anchor metadata generation.

Routine per-frame repainting remains disallowed.

### 7. Candidate review and approval

Every generation is a candidate. Candidates may be compared side-by-side and iterated from.

Approval is explicit. Generation must never silently overwrite the approved master.

### 8. Runtime export

Export only approved state:

- images/sequences/sheets/atlases;
- JSON metadata;
- pivots/events/rectangles;
- hashes and provenance;
- project/engine import metadata where needed.

## Model-routing architecture

The Studio maintains a machine-readable model registry. Each entry records:

- adapter id;
- model family;
- task capabilities;
- license;
- local workspace;
- VRAM/RAM expectation;
- installation state;
- quality tier;
- allowed asset/output contracts;
- known weaknesses;
- canonical tested settings.

The router selects only among installed/approved adapters unless the user explicitly starts a model-evaluation/install task.

## Current model families

### MiniMax H3 Base Ref2VA — ACTIVE motion specialist

Current proven use:

- character identity + real action video -> complete motion master;
- multimodal reference routing;
- body/hair/cloth motion.

Existing Exilada Base50 result remains the current motion-quality evidence.

H3 is not the universal still-image asset generator.

### MiniMax H3 FL2VA — AVAILABLE LATER FOR TEMPORAL TASKS

Potential use:

- first-frame animation;
- first/last-frame interpolation;
- environmental loops;
- VFX and set-piece motion where a real performer is not the authoritative driver.

It must be validated per task before production use.

### FLUX.1 Kontext [dev] — EXISTING R&D EDITOR / NON-COMMERCIAL MODEL LICENSE

Already installed and useful for structure-preserving editing/reconstruction experiments.

It remains a technical R&D adapter, but its model license makes it unsuitable as the long-term default production dependency for a commercial game without separate licensing.

### FLUX.2 Klein 4B — PRIORITY STATIC/EDIT CANDIDATE

Priority candidate for the general Studio because the official family supports:

- text-to-image;
- single-reference editing;
- multi-reference editing;
- consumer-GPU execution;
- 4B Apache-2.0 licensing.

The distilled 4B path is a strong candidate for interactive ideation/editing. The 4B Base path is strategically important because it is trainable/fine-tunable and may become the basis for a project-specific rendering/style adapter.

**Not installed/accepted until a controlled local spike passes.**

### Qwen-Image-Edit / 2509 family — QUALITY/CONTROL CANDIDATE

Apache-2.0 editing family with strong semantic/appearance editing and structural-control capabilities. It is substantially heavier than the interactive 4B route, so on the RTX 3060 it should be treated as a quality/control branch requiring a dedicated quantized/offload feasibility spike.

**Not a default until local feasibility is proven.**

### Step1X-Edit — DEFERRED

Apache-2.0 and technically interesting, but published memory requirements remain above the current 12 GB GPU even with FP8/offload. Do not prioritize it ahead of candidates that fit the target machine better.

## Project-specific specialization strategy

The long-term goal is not to depend forever on public generic style LoRAs.

Once the project has enough approved visual examples, the Studio should support training/evaluating **Roguelite-specific adapters** using only assets whose provenance permits that use.

Likely targets:

- project rendering-language LoRA;
- character-family consistency adapter;
- environment/material adapter;
- pixel-art reconstruction adapter;
- optional creature/anatomy families.

FLUX.2 Klein 4B Base is a priority candidate for this strategy because the 4B family is Apache-2.0 and the official project explicitly supports fine-tuning/customization.

## Character Lab

The existing Exilada master editor becomes the first **Character Lab prototype** inside the Studio.

Its useful concepts are retained:

- identity/anatomy/style reference roles;
- iterative edit from candidate;
- full useful output resolution;
- candidate history;
- explicit approval only.

Its Exilada-specific prompt fields are not the generic application architecture.

## Environment / map production principle

The game is a living belt-scroller world. The Studio should not default to generating one flattened painting for an entire gameplay map.

Prefer reusable modular sources where gameplay/simulation needs them independently:

- terrain strips/patches;
- cliffs/walls;
- architecture façades/modules;
- doors/gates;
- vegetation groups;
- rocks/debris;
- furniture/props;
- foreground/background set pieces;
- environmental animated loops;
- decals/damage states.

The game/level system composes those modules. Large background plates are allowed when they do not destroy gameplay modularity.

## Animated-asset contract

For characters/creatures:

`approved static master + motion reference/context -> temporal motion master -> action distillation -> final rendering-language reconstruction -> alpha/pivot/events -> one action row/sequence -> runtime`

For environment/VFX:

`approved static state + temporal instruction/reference -> temporal master -> loop/sequence extraction -> final rendering-language reconstruction if needed -> alpha/seam/timing metadata -> runtime`

The temporal master may differ by asset class.

## Resolution contract — HARD LOCK

The Studio does **not** impose 128 px, 192 px, 384 px or another universal sprite cell size.

Asset resolution is driven by:

- model output quality;
- asset type;
- action envelope;
- required gameplay/world scale;
- runtime memory/atlas constraints assessed later.

Useful production source resolution is preserved. Runtime display scale is separate.

## Application architecture

The UI and generation backends are decoupled.

Recommended structure:

`Studio UI -> Asset API/orchestrator -> model adapters -> model runtimes (ComfyUI/native) -> deterministic processors -> asset store/provenance -> runtime exporter`

This allows us to replace Gradio later without rewriting generation logic.

### V0/V1 UI

Gradio may remain temporarily useful for rapid local validation, but the umbrella Studio must not make Gradio components part of pipeline semantics.

Once the model router and asset schema stabilize, a dedicated local UI can replace the prototype surface while keeping the same backend contracts.

## Filesystem contract

Large generated/model data stays outside Git.

Recommended local root:

`Z:\AI\RogueliteAssetStudio\`

Suggested structure:

- `models/` or pointers to isolated model workspaces;
- `projects/<asset_id>/spec.json`;
- `projects/<asset_id>/references/`;
- `projects/<asset_id>/candidates/<candidate_id>/`;
- `projects/<asset_id>/approved/`;
- `jobs/`;
- `cache/`;
- `exports/`.

The Git repository stores schemas, adapters, launchers, tested recipes and canonical project decisions; large generated candidates remain local unless deliberately promoted as source assets.

## Immediate implementation order

1. establish the generic asset schema and model registry;
2. refactor Runner54 concepts into a generic Studio/Character Lab rather than expanding Exilada-specific code;
3. add a model-adapter interface around the already installed Kontext and H3 runtimes;
4. run a controlled FLUX.2 Klein 4B local feasibility/install spike before downloading it as a production dependency;
5. if it passes, make Klein 4B the first generic static generation/edit adapter;
6. test the Exilada master revision through the generic Character Lab;
7. add `prop/environment` static workflows;
8. add H3 temporal routing for `animated_action` and `animated_loop`;
9. add generic approval/export/version browser;
10. only then scale production across the full game asset catalog.

## Hard conclusion

The project is building a **local generative game-asset production system**, not a character-specific image editor.

The tool must make specialized models interchangeable, preserve approved asset identity/state, support both static and animated assets, and scale from one protagonist to the complete visual content of the game.