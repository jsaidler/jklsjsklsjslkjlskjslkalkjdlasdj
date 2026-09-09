# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
6. `docs/EXILADA_MASTER_REVISION_LOCAL_EDITOR_2026-09-08.md`
7. `docs/GAMEPLAY_CHARACTER_SCALE_RECALIBRATION_2026-09-08.md`
8. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
9. `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`
10. `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`
11. `docs/ANIMATION_PIPELINE.md`
12. `docs/CHARACTER_PRODUCTION_PIPELINE.md`

Historical preflight/model-screening documents remain evidence but do not override the current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file before completion is reported. Changed decisions replace stale locks rather than coexisting ambiguously.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- planned umbrella Studio root: `Z:\AI\RogueliteAssetStudio`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext workspace: `Z:\AI\FluxKontext`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## CURRENT UMBRELLA DIRECTION — ROGUELITE ASSET STUDIO

The local production tool is **not an Exilada editor** and is not a wrapper around one model.

The project is building a local generative game-asset production system covering the complete visual asset base:

- playable characters;
- NPCs;
- enemies;
- creatures;
- bosses;
- equipment/weapons/armor;
- props/interactables;
- architecture;
- terrain/vegetation;
- environment/map modules and set pieces;
- tileable materials where useful;
- VFX/environment animation;
- UI art where needed.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized model adapter -> local model runtime -> deterministic processing -> candidate/version store -> explicit approval -> runtime export`

The Exilada is the first difficult **Character Lab validation project**, not the scope-defining application.

Canonical specification:

`docs/ROGUELITE_ASSET_STUDIO.md`

Initial generic implementation files:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`

The core router is deliberately UI-independent.

## Local-first production — HARD LOCK

Routine asset production must be possible locally after model installation.

Hosted services may later be optional accelerators/quality branches, but may not be mandatory for ordinary production.

This is important for cost, reproducibility, batch generation, large reference sets, long animation jobs, project-specific fine-tuning and mature/adult fictional character states that may not be workable through hosted authoring surfaces.

Current hardware baseline:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB system RAM.

Model routing must account for this machine explicitly.

## Game/runtime presentation — LOCKED EXCEPT FINAL APPARENT CHARACTER SCALE

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- `relative_scale=1.0` means baseline adult-human/Exilada world scale, not a sprite pixel height;
- first locomotion family screen-left / mostly lateral-three-quarter;
- facing baseline `72°`;
- runtime consumes complete precomposed character sprites only;
- no visible runtime body/hair/clothing/equipment layer assembly.

## Resolution contract — HARD LOCK

The former `128px` Exilada asset baseline is retired.

There is no mandatory `160/180/200px`, `192px` or `384px` production sprite resolution. Those values are historical diagnostics or optional composition comparisons only.

Production assets preserve the useful resolution of the approved generation/render chain. Gameplay apparent size is controlled separately by runtime/world/camera scaling.

The same principle applies outside characters: the Studio does not impose one universal texture/cell size on all asset classes.

## Final visible-art target — LOCKED

Runtime character graphics remain deliberate high-quality pixel art, but asset design must be correct before final rendering-language reconstruction is optimized.

For characters/creatures, H3 painterly/raster video is an intermediate **motion master**, not final runtime art.

Canonical character temporal chain after master approval:

`approved static master -> motion reference/context -> temporal motion master -> action-frame distillation -> rendering-language reconstruction at useful source resolution -> alpha/pivot/events -> one action row/sequence -> runtime`

Environment/VFX temporal assets may use a different temporal adapter but follow the same candidate/approval/provenance rules.

## Environment/map production principle — LOCKED DIRECTION

The living belt-scroller world should not default to one flattened AI-painted gameplay map.

Prefer modular assets where simulation/gameplay needs independent pieces:

- terrain strips/patches;
- walls/cliffs;
- architecture modules/facades;
- doors/gates;
- vegetation groups;
- rocks/debris;
- furniture/props;
- foreground/background set pieces;
- environmental loops;
- decals and damage-state variants.

The engine/level system composes these modules. Large background plates remain valid only where they do not destroy gameplay modularity.

## Spritesheet layout contract — HARD LOCK

For animated character/creature actions:

**One action = one spritesheet row.**

- frames read left-to-right in time;
- action frame count is variable;
- internal renderer tiles/chunks never become semantic final rows;
- durations/events live in metadata;
- complete character remains visible per exported frame;
- final asset resolution follows the approved production chain rather than legacy cell sizes.

## Exilada core identity — LOCKED

The protagonist is an unambiguously adult woman, approximately 162 cm tall, from the Ilhas do Sul.

Identity anchors:

- mature severe adult face/presence;
- lean, functional, resilient natural adult feminine anatomy;
- olive-to-brown skin;
- very long, heavy, voluminous, messy black hair as a primary silhouette anchor;
- alert, contained violence and survival rather than clean heroic presentation;
- weapon is not part of permanent identity.

The approved nude anatomy source remains legitimate offline authoring evidence. Adult partial or complete nudity is a normal supported character/world state.

## Exilada initial-state design — REOPENED / CHARACTER LAB FIRST CASE

The existing `assets/source/characters/exilada/reference/exilada_master.png` remains useful identity/anatomy evidence but is **not final visual-design authority**.

Problems still to solve:

- clothing reads too intact/generic;
- approved severe tearing/greater exposure are not visually resolved;
- sword-and-sorcery lineage is insufficiently visible;
- master needs stronger material, danger, grime, sensuality and pulp physicality.

The initial state may explore:

- severely torn asymmetrical cloth;
- irregular holes, missing edges, displaced remnants and incomplete coverage;
- substantially more torso exposure;
- partial breast exposure where caused by torn-cloth logic;
- near-nudity or full nudity where deliberately appropriate;
- equally degraded hip cloth;
- dirt, sweat, abrasions, scars/wounds and captivity evidence;
- no mandatory censor garment;
- no neat fantasy bikini/bandeau/corset/MMO costume logic.

Exact tear geometry/exposure remains open until explicit visual approval.

## 1980s sword-and-sorcery direction — HARD LOCK

Active inspiration lineage:

- Heavy Metal;
- Conan;
- Red Sonja;
- Frank Frazetta;
- Julie Bell.

The revised Exilada and the broader game's visual system must visibly carry adult physical weight, danger, grime, sensuality where appropriate, tactile materials and pulp-fantasy excess. Merely naming references in prompts is not sufficient.

## Model router — CURRENT REGISTRY

Machine-readable registry:

`tools/roguelite-asset-studio/model_registry.json`

### MiniMax H3 Base Ref2VA — ACTIVE / PROVEN MOTION SPECIALIST

Current proven Exilada quality baseline:

- `448×800`;
- `124 frames @24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed `0`;
- no Turbo LoRA;
- no FL2VA for this proven job.

Evidence:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H3 remains the active motion-master specialist for character work. It is not the universal still-asset generator.

### MiniMax H3 FL2VA — TEMPORAL CANDIDATE

Potential future use for first/last-frame animation, environmental loops, VFX and temporal assets without an authoritative real-video motion driver. Validate per asset class before production.

### FLUX.1 Kontext [dev] FP8 — ACTIVE R&D ONLY

Workspace: `Z:\AI\FluxKontext`

Installed/proven set:

- ComfyUI v0.34.0;
- `flux1-dev-kontext_fp8_scaled.safetensors`;
- `clip_l.safetensors`;
- `t5xxl_fp16.safetensors`;
- `ae.safetensors`.

Useful for R&D editing/reconstruction, but FLUX dev model licensing prevents it from becoming the default commercial-production dependency without appropriate licensing.

### FLUX.2 Klein 4B — PRIORITY GENERIC STATIC/EDIT CANDIDATE / NOT YET INSTALLED

Priority because the official 4B family supports text-to-image, single-reference editing and multi-reference editing on consumer GPUs, and the 4B variants are Apache-2.0.

The distilled 4B is the leading interactive-generation/edit candidate.

The 4B Base is strategically interesting for future project-specific LoRA/fine-tuning.

**Do not download/install silently. Run a controlled feasibility/install spike first.**

### Qwen-Image-Edit / 2509 — QUALITY/STRUCTURAL-CONTROL CANDIDATE / NOT YET INSTALLED

Apache-2.0 and attractive for semantic/appearance editing plus structural controls. It is materially heavier than the 12 GB baseline, therefore needs a dedicated FP8/low-VRAM feasibility spike before acceptance.

### Step1X-Edit — DEFERRED

Apache-2.0 but published memory use remains above the current GPU even with FP8/offload. Do not prioritize it ahead of candidates that fit the workstation better.

## Project-specific specialization — LOCKED DIRECTION

The long-term Studio should not depend forever on generic public style LoRAs.

After enough approved project art exists, train/evaluate Roguelite-specific adapters using only training material whose provenance/license permits it.

Candidate specialization targets:

- final rendering-language/pixel-art adapter;
- character-family consistency;
- environment/material language;
- creature families;
- controlled variants/damage states.

FLUX.2 Klein 4B Base is a priority technical candidate for this because the 4B family supports customization under Apache-2.0.

## Character Lab prototype history

Runner54 / `exilada_master_editor.py` remains useful prototype evidence for:

- semantic reference roles;
- iterative candidate editing;
- native useful resolution;
- versioning;
- explicit approval.

It must **not** be expanded as the umbrella application. Those concepts are to be refactored behind the generic Asset Studio contracts.

Runner53 remains paused while the Exilada master is visually reopened.

## Runtime character representation — LOCKED

The game does not visibly assemble body/hair/clothing/equipment layers at runtime.

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

Variation is solved offline.

## CURRENT IMPLEMENTATION GATE — ASSET STUDIO FOUNDATION

Do not spend the next development cycle polishing the Exilada-only Gradio editor.

Runner55 foundation validation now has explicit regression semantics:

- schema v2 separates **field presence** from **field non-emptiness**;
- `references` is required as a field but `references: []` is valid for reference-free/text-to-image asset creation;
- `SPEC_ERROR` exit code `2` is fatal;
- only route-not-found exit code `3` may be treated as an expected "no installed model yet" result;
- the validation pair intentionally covers a referenced playable-character spec and a reference-free architecture-module spec.

Immediate order:

1. pull the current repository state;
2. run corrected Runner55 and require both specs to validate;
3. refactor model execution into adapter interfaces independent of the UI;
4. wrap the already-proven H3 Ref2VA and Kontext runtimes as first adapters;
5. enumerate the exact FLUX.2 Klein 4B local spike payload, disk use and pass/fail criteria before downloading it;
6. run the Klein 4B feasibility spike on RTX 3060 12GB / 48GB RAM;
7. if it passes, make it the first generic static generation/edit adapter;
8. expose Character Lab through the generic Studio and revise the Exilada there;
9. add static `prop/environment` workflows so the architecture is proven outside characters;
10. route animated actions/loops through H3 adapters;
11. add generic browser/comparison/approval/export;
12. resume final pixel-art reconstruction validation with the approved project-specific masters rather than a stale Exilada-only path.

## License caveats

- FLUX.1/FLUX.2 dev-family licenses must not silently become commercial-production dependencies.
- The model registry records licenses per adapter.
- Commercial/release decisions must be checked against the exact model/adapters used for approved assets.

## Cleanup

- keep Base H3 Ref2VA minimal proven set;
- keep current Kontext model set while R&D remains active;
- keep the Modern Pixel Art LoRA only while its downstream hypothesis remains open;
- do not download FLUX.2/Qwen/other candidate checkpoints until their controlled spike is specified;
- Wan large checkpoints may remain removed/paused while evidence is retained;
- SSD comparison evidence remains until explicit abandonment/final verdict.