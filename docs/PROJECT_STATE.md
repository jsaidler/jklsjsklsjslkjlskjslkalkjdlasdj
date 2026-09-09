# Roguelite — Current Project State

Status date: **2026-09-09**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/FLUX2_KLEIN_4B_ASSET_STUDIO_SPIKE_2026-09-08.md`
4. `docs/VISUAL_DIRECTION.md`
5. `docs/CHARACTERS.md`
6. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
7. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
8. `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`
9. `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`

Historical preflight/model-screening documents remain evidence but do not override the current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs/registry and this file before completion is reported. Changed decisions replace stale locks rather than coexisting ambiguously.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- umbrella Studio root: `Z:\AI\RogueliteAssetStudio`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext R&D workspace: `Z:\AI\FluxKontext`
- active Klein static workspace: `Z:\AI\Flux2Klein`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## UMBRELLA DIRECTION — ROGUELITE ASSET STUDIO / HARD LOCK

The local production tool is **not an Exilada editor** and is not a wrapper around one model.

It must cover the complete visual asset base: playable characters, NPCs, enemies, creatures, bosses, equipment, props, architecture, terrain, vegetation, environment modules/set pieces, materials, VFX/environment animation and UI art where needed.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized model adapter -> local model runtime -> deterministic processing -> candidate/version store -> explicit approval -> runtime export`

The Exilada is the first difficult Character Lab validation project, not the scope-defining application.

Canonical umbrella document:

`docs/ROGUELITE_ASSET_STUDIO.md`

Generic foundation:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`
- `tools/roguelite-asset-studio/adapter_protocol.py`

The router and adapter boundary are UI-independent.

## Runner55 — FOUNDATION VALIDATION PASS

Runner55 passed on the actual local repository state.

Validated cases:

### Referenced playable character

- spec valid;
- requires `single_reference_edit + multi_reference_edit`;
- planning routes correctly identified Klein distilled/Base and Qwen editing candidates.

### Reference-free architecture module

- spec valid with `references: []`;
- requires `text_to_image`;
- planning routes correctly identified Klein distilled/Base.

Schema regression contract:

- `references` must exist as a field;
- `references: []` is valid;
- `SPEC_ERROR` exit code 2 is fatal;
- route-not-found exit code 3 is the only expected no-route condition.

Runner55 conclusion: **generic schema/router foundation PASS**.

## Runner56 — FLUX.2 KLEIN 4B DISTILLED T2I PASS

Runner:

`tools/structured-2d-character-pipeline/56_bootstrap_and_run_flux2_klein_4b_spike.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_t2i_probe.py`

Detailed record:

`docs/FLUX2_KLEIN_4B_ASSET_STUDIO_SPIKE_2026-09-08.md`

### Actual local result

Runner56 completed successfully on the target RTX 3060 12 GB / 48 GB RAM workstation.

Exact runtime:

- isolated workspace `Z:\AI\Flux2Klein`;
- isolated ComfyUI commit `672ba9e5e388bd6bfac5ceef61f89ffdd9467200`;
- default port `8192`;
- existing H3/Kontext runtimes were not modified.

Exact model payload verified:

1. `flux-2-klein-4b-fp8.safetensors`
   - SHA256 `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6`
2. `qwen_3_4b.safetensors`
   - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
3. `flux2-vae.safetensors`
   - SHA256 `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`

Total weights: `12,451,817,860` bytes (~12.45 GB decimal / ~11.60 GiB).

Controlled T2I inference:

- asset type `architecture_module`;
- output `static_master`;
- no references;
- 768×768;
- 4 distilled steps;
- CFG 1.0;
- Euler;
- seed 0.

Actual result:

- **no OOM**;
- **no runtime/CUDA crash**;
- valid `768×768 RGB` output;
- inference elapsed **12.054 s**;
- prompt id `e65a7d0c-f8a5-479b-9995-78cf8978d79f`;
- output SHA256 `8ce5b54cf4f7ccabf3aee3583de9c76c8942115aed8592a9430b8ede68730a16`.

Output:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_probe.png`

Manifest:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_manifest.json`

### Runner56 visual continuation verdict — PASS

The generated ruined gate is coherent enough to establish Klein as a useful static-authoring backend:

- strong readable silhouette;
- plausible load-bearing construction;
- useful stone/wood/iron/root material separation;
- complete neutral-background authoring composition;
- enough specificity/detail for iterative revision.

The specific image is **not an approved game asset**. Remaining weaknesses include excess symmetry, decorative crack distribution and a door/iron treatment still somewhat clean/polished/generic-fantasy. Those weaknesses are deliberately useful for the reference-edit gate because the next test asks the model to alter them without replacing the gate identity wholesale.

Runner56 conclusion: **technical PASS + visual continuation PASS**.

## FLUX.2 Klein router status after Runner56

Machine-readable authority:

`tools/roguelite-asset-studio/model_registry.json`

Current status:

`active_static_t2i_proven_edit_pending`

Active/routable capabilities:

- `text_to_image`
- `interactive_concept`

Planned but **not routable** until Runner57 passes:

- `single_reference_edit`
- `multi_reference_edit`
- `interactive_variant`

The core router now distinguishes active capabilities from planned ones so upstream documentation cannot accidentally promote an untested local capability.

## Generic static adapter — IMPLEMENTED

Files:

- `tools/roguelite-asset-studio/adapter_protocol.py`
- `tools/roguelite-asset-studio/flux2_klein_adapter.py`

The Studio request contract supplies asset type, output contract, prompt, dimensions/settings and ordered semantic references. The Klein adapter owns the ComfyUI translation.

For reference editing, the adapter follows the current native FLUX.2 distilled semantics:

- CLIP text conditioning;
- zeroed negative conditioning for reference edit;
- each reference is encoded through FLUX.2 VAE;
- ordered reference latents are appended to both positive and zeroed-negative conditioning through `ReferenceLatent`;
- UI/orchestrator remains unaware of graph-node details.

References are conditioning copies only. Original authored files are never destructively resized or overwritten.

## CURRENT IMPLEMENTATION GATE — Runner57 / GENERIC SINGLE + MULTI REFERENCE EDIT

Runner:

`tools/structured-2d-character-pipeline/57_run_flux2_klein_reference_edit_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_edit_gate.py`

Runner57 downloads **no new checkpoints**. It reuses the Runner56 isolated runtime and exact verified model hashes.

### Test A — single reference

Source:

Runner56 ruined gate.

Semantic role:

`previous_approved_state`

Requested change:

- preserve the same recognizable gate;
- preserve camera/framing and underlying construction;
- make broken lintel/damage less symmetric and more causal;
- make doors/planks/iron straps more broken/warped;
- deepen corrosion, dirt and physical aging;
- remove some polished generic fantasy/asset-store neatness.

PASS requires meaningful requested edits **without wholesale replacement of the asset identity**.

### Test B — ordered two references

- Image 1 role: `structure` — original Runner56 gate; authority for identity, silhouette, camera and construction.
- Image 2 role: `material` — Test A result; authority only for harsher damage/material aging.

PASS requires one coherent recognizable gate preserving Image 1 structure while carrying useful damage/material information from Image 2. Duplicated gates, incoherent averaging or camera identity loss fail.

### Controlled settings

Both jobs:

- 768×768;
- 4 steps;
- CFG 1.0;
- Euler;
- seed 0.

Only the reference-edit contract changes relative to the proven T2I path.

### Expected outputs

Under:

`Z:\AI\Flux2Klein\edit_gate`

- `flux2_klein_single_reference_edit.png`
- `flux2_klein_multi_reference_edit.png`
- `flux2_klein_edit_gate_comparison_original_single_multi.png`
- `flux2_klein_edit_gate_manifest.json`
- `flux2_klein_edit_gate_executor.log`
- isolated Comfy stdout/stderr logs.

Expected technical completion line:

`RUNNER57-FLUX2-KLEIN-EDIT: PASS - TECHNICAL SINGLE+MULTI REFERENCE COMPLETE / VISUAL VERDICT PENDING`

Technical PASS alone does not activate edit capabilities. Human visual review is mandatory.

## Next gate after Runner57 PASS

Only if both edit tests pass visually:

1. move `single_reference_edit`, `multi_reference_edit` and `interactive_variant` from planned to active Klein capabilities;
2. make the generic Studio router select Klein for referenced static assets;
3. expose the adapter through the first generic Studio UI/state layer;
4. use the reopened Exilada as the first high-difficulty Character Lab validation with semantic identity/anatomy/style references;
5. validate a second non-character asset class such as prop/equipment;
6. add candidate browser/comparison/history/approval/export;
7. wrap H3 Ref2VA behind the same orchestration boundary for animated character/creature actions.

## Model router — other families

### MiniMax H3 Base Ref2VA — ACTIVE / PROVEN MOTION SPECIALIST

Current proven character-motion baseline:

- 448×800;
- 124 frames @24fps;
- `ref_image_size=match`;
- 50 steps;
- `res_multistep/beta`;
- seed 0;
- no Turbo/FL2VA/style embedding.

Evidence:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H3 remains a motion specialist, not the universal still generator.

### MiniMax H3 FL2VA — TEMPORAL CANDIDATE

Potential route for first/last-frame animation, environmental loops, VFX and temporal assets without authoritative performer video. Validate per asset class.

### FLUX.1 Kontext [dev] FP8 — ACTIVE R&D ONLY

Useful for editing/reconstruction R&D. Its dev license prevents silently making it the commercial-production default without appropriate licensing.

### FLUX.2 Klein 4B Base — TRAINING/SPECIALIZATION CANDIDATE

Do not download now. Retain for future Roguelite-specific LoRA/fine-tuning evaluation after enough approved licensable project data exists.

### Qwen-Image-Edit / 2509 — HEAVY QUALITY/CONTROL CANDIDATE

Apache-2.0 but heavier than the 12 GB baseline. Requires a dedicated low-VRAM spike before use.

### Step1X-Edit — DEFERRED

Published memory use remains a poor fit for the current workstation.

## Local-first production — HARD LOCK

Routine asset production must work locally after installation. Hosted services may be optional accelerators but cannot be mandatory.

This also keeps mature/adult fictional state authoring independent from hosted-surface restrictions.

## Game/runtime presentation — LOCKED EXCEPT FINAL APPARENT CHARACTER SCALE

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- native raster 640×360;
- fixed orthographic-like camera;
- pitch 26°;
- facing baseline 72°;
- `relative_scale=1.0` means baseline adult-human world scale, not sprite pixel height;
- runtime consumes complete precomposed character sprites.

## Resolution contract — HARD LOCK

The old 128px Exilada asset baseline is retired. There is no universal 160/180/200/192/384px production sprite resolution.

Preserve useful source resolution from approved generation/render chains. Runtime apparent/world scale is separate. The same principle applies to non-character assets.

## Runtime character representation — HARD LOCK

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

For animated character/creature actions:

**one action = one horizontal spritesheet row**;

frames read left-to-right, frame count is variable, and timing/events/pivots live in metadata.

## Environment/map production principle — LOCKED

Prefer modular independently useful pieces over a single flattened AI-painted gameplay map:

- terrain strips/patches;
- walls/cliffs;
- architecture modules/facades;
- doors/gates;
- vegetation groups;
- rocks/debris;
- furniture/props;
- foreground/background set pieces;
- environmental loops;
- decals/damage-state variants.

The engine/level system composes these modules.

## Exilada design state — REOPENED / FIRST CHARACTER LAB CASE

`assets/source/characters/exilada/reference/exilada_master.png` remains identity/anatomy evidence but is not final visual-design authority.

Required revision direction includes:

- stronger Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell charge;
- severe asymmetrical cloth degradation;
- materially caused greater torso exposure/partial breast exposure where appropriate;
- near/full adult nudity as legitimate states;
- dirt/wear/captivity evidence;
- rejection of clean generic fantasy-bikini/MMO logic;
- preservation of mature adult anatomy and identity.

Runner53 remains paused until the static master is revised through the generic Studio path.

## Cleanup rule

Do not accumulate candidate checkpoints speculatively.

- keep the proven H3 Base50 set;
- keep current Kontext R&D set while still needed;
- keep the now-proven Klein distilled FP8 + full Qwen3-4B + VAE runtime;
- Runner57 downloads no model;
- do not download Klein Base, Qwen-Image-Edit or Step1X until their own hypothesis becomes active;
- remove rejected model payloads after evidence/manifests are preserved and the family is explicitly abandoned.
