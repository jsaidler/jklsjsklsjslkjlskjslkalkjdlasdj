# Roguelite — Current Project State

Status date: **2026-09-09**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER58_FLUX2_KLEIN_EDIT_STRENGTH_CALIBRATION_2026-09-09.md`
4. `docs/FLUX2_KLEIN_4B_ASSET_STUDIO_SPIKE_2026-09-08.md`
5. `docs/VISUAL_DIRECTION.md`
6. `docs/CHARACTERS.md`
7. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
8. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
9. `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`

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
- `tools/roguelite-asset-studio/flux2_klein_adapter.py`

The router and adapter boundary are UI-independent.

## Runner55 — FOUNDATION VALIDATION PASS

Runner55 proved the generic schema/router against both a referenced playable character and a reference-free architecture module.

Locked schema behavior:

- `references` must exist;
- `references: []` is valid for reference-free generation;
- `SPEC_ERROR` exit code 2 is fatal;
- route-not-found exit code 3 is the expected no-compatible-installed-route result.

## Runner56 — FLUX.2 KLEIN 4B DISTILLED T2I PASS

Runner:

`tools/structured-2d-character-pipeline/56_bootstrap_and_run_flux2_klein_4b_spike.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_t2i_probe.py`

Runtime:

- isolated workspace `Z:\AI\Flux2Klein`;
- ComfyUI commit `672ba9e5e388bd6bfac5ceef61f89ffdd9467200`;
- port default `8192`;
- RTX 3060 12 GB / 48 GB RAM;
- no H3/Kontext mutation.

Verified weights:

1. `flux-2-klein-4b-fp8.safetensors`
   - SHA256 `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6`
2. `qwen_3_4b.safetensors`
   - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
3. `flux2-vae.safetensors`
   - SHA256 `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`

Total weights: `12,451,817,860` bytes (~12.45 GB decimal / ~11.60 GiB).

Controlled T2I result:

- `architecture_module` / `static_master`;
- 768×768;
- 4 steps;
- CFG 1.0;
- Euler;
- seed 0;
- elapsed **12.054 s**;
- no OOM/runtime crash;
- output SHA256 `8ce5b54cf4f7ccabf3aee3583de9c76c8942115aed8592a9430b8ede68730a16`.

Visual continuation verdict: **PASS** as a useful static authoring master, not as final game art.

## Runner57 — REFERENCE EDIT TECHNICAL PASS / VISUAL-STRENGTH PARTIAL-FAIL

Runner:

`tools/structured-2d-character-pipeline/57_run_flux2_klein_reference_edit_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_edit_gate.py`

Final successful Runner57 result after harness/import-path fixes:

### Single-reference

- role `previous_approved_state`;
- 768×768;
- 4 steps;
- CFG 1.0;
- Euler;
- seed 0;
- elapsed **14.063 s**;
- output SHA256 `9545ea3dd06f3aaa5872fe7e433896f915e4eb4b45c249ce5c08fee0ed45c6b4`.

### Ordered multi-reference

- Image 1 `structure` = original Runner56 gate;
- Image 2 `material` = Runner57 single result;
- 768×768;
- 4 steps;
- CFG 1.0;
- Euler;
- seed 0;
- elapsed **16.025 s**;
- output SHA256 `437bdc4aebc290c8e688e6e93e5dfe0462aa70321b6cc0984313dc9033147962`.

Comparison SHA256:

`c65d43700cdc13feec4c96a5abbd738ffa25a291a61883ad557ea218f94e8ba8`

### Runner57 interpretation

Technical result: **PASS**.

The adapter/runtime proves that Klein distilled can execute both single- and multi-reference graphs without OOM, duplication, graph failure or catastrophic structure loss.

Visual production result: **not yet PASS**.

The generated edits preserved the gate strongly but remained too close to the original. Requested damage/material changes were not forceful enough for interactive art direction. Therefore the problem is currently edit strength/obedience, not runtime feasibility.

Do **not** activate production edit routing yet.

## FLUX.2 Klein router status — CURRENT

Machine-readable authority:

`tools/roguelite-asset-studio/model_registry.json`

Status:

`active_static_t2i_proven_edit_technical_pass_calibration_pending`

Active/routable now:

- `text_to_image`
- `interactive_concept`

Technically proven but still planned/non-routable until visual calibration passes:

- `single_reference_edit`
- `multi_reference_edit`
- `interactive_variant`

## CURRENT IMPLEMENTATION GATE — Runner58 / EDIT-STRENGTH + MULTI-REFERENCE OBEDIENCE CALIBRATION

Canonical record:

`docs/RUNNER58_FLUX2_KLEIN_EDIT_STRENGTH_CALIBRATION_2026-09-09.md`

Runner:

`tools/structured-2d-character-pipeline/58_run_flux2_klein_edit_strength_calibration.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_edit_strength_calibration.py`

Runner58 downloads **no new model** and reuses the exact Runner56/57 isolated runtime.

### Single-reference matrix

Same original gate, same seed/CFG/sampler, with deliberately binary edits, at:

- 4 steps;
- 8 steps;
- 12 steps.

Required visible changes include:

- remove one complete vertical plank from the left door leaf;
- remove one large top-left capstone/lintel block;
- break/partially remove the lower strap on the right door leaf;
- strong corrosion/grime;
- visibly warped/split timber.

### Separate material authority

Runner58 automatically generates a severe-decay material board through the already-proven Klein T2I route. It is deliberately not a gate/scene.

### Multi-reference matrix

- Image 1 `structure` = original gate;
- Image 2 `material` = generated severe-decay material board;
- 4/8/12-step variants.

This directly tests whether a distinct secondary reference exerts useful material influence while Image 1 retains structure/camera authority.

### Metrics

Manifest records image-difference magnitude against the original, including mean absolute luma/RGB delta and changed-pixel ratios. Metrics are diagnostic only; human visual review remains authoritative.

### Runner58 visual PASS

At least one single and one multi variant must make the requested large edits visibly while preserving recognizable gate identity/camera/construction.

If Runner58 passes visually:

1. activate Klein `single_reference_edit`, `multi_reference_edit`, `interactive_variant`;
2. expose the adapter through the first generic Asset Studio UI/state layer;
3. proceed to the reopened Exilada as the first high-difficulty Character Lab case;
4. validate another non-character class such as prop/equipment;
5. add candidate browser/history/approval/export;
6. wrap H3 behind the same orchestration boundary for temporal assets.

If Runner58 remains visually weak:

- keep Klein distilled active for T2I only;
- record the limitation;
- only then evaluate the next stronger editing branch rather than changing models prematurely.

## Model router — other families

### MiniMax H3 Base Ref2VA — ACTIVE / PROVEN MOTION SPECIALIST

Current proven Exilada motion baseline:

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

Do not download during Runner58. Retain for future Roguelite-specific LoRA/fine-tuning evaluation after enough approved licensable project data exists.

### Qwen-Image-Edit / 2509 — HEAVY QUALITY/CONTROL CANDIDATE

Apache-2.0 but heavier than the 12 GB baseline. Requires a dedicated low-VRAM spike before use.

### Step1X-Edit — DEFERRED

Published memory use remains a poor fit for the workstation.

## Local-first production — HARD LOCK

Routine asset production must work locally after installation. Hosted services may be optional accelerators but cannot be mandatory.

This keeps mature/adult fictional-state authoring independent from hosted-surface restrictions.

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

frames read left-to-right, frame count is variable, timing/events/pivots live in metadata.

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

- stronger Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell charge;
- severe asymmetrical cloth degradation;
- materially caused greater torso exposure/partial breast exposure where appropriate;
- near/full adult nudity as legitimate states;
- dirt/wear/captivity evidence;
- rejection of clean generic fantasy-bikini/MMO logic;
- preservation of mature adult anatomy and identity.

Runner53 remains paused until the static master is revised through the generic Studio path.

## Cleanup rule

Do not accumulate candidate checkpoints speculatively.

- keep proven H3 Base50 set;
- keep current Kontext R&D set while still needed;
- keep proven Klein distilled FP8 + full Qwen3-4B + VAE runtime;
- Runner58 downloads no model;
- do not download Klein Base, Qwen-Image-Edit or Step1X until their own hypothesis becomes active;
- remove rejected model payloads after evidence/manifests are preserved and the family is explicitly abandoned.
