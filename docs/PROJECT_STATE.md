# Roguelite — Current Project State

Status date: **2026-09-08**

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
- planned umbrella Studio root: `Z:\AI\RogueliteAssetStudio`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext R&D workspace: `Z:\AI\FluxKontext`
- Runner56 isolated Klein workspace: `Z:\AI\Flux2Klein`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## UMBRELLA DIRECTION — ROGUELITE ASSET STUDIO / HARD LOCK

The local production tool is not an Exilada editor and is not a wrapper around one model.

It must cover the complete visual asset base: playable characters, NPCs, enemies, creatures, bosses, equipment, props, architecture, terrain, vegetation, environment modules/set pieces, materials, VFX/environment animation and UI art where needed.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized model adapter -> local model runtime -> deterministic processing -> candidate/version store -> explicit approval -> runtime export`

The Exilada is the first high-difficulty Character Lab case, not the scope-defining application.

Canonical architecture document:

`docs/ROGUELITE_ASSET_STUDIO.md`

Generic implementation foundation:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`

The core router is UI-independent and model adapters are replaceable.

## Runner55 — FOUNDATION VALIDATION PASS

Runner55 passed on the actual local repository state.

Validated cases:

### Referenced playable character

- spec valid;
- requires `single_reference_edit + multi_reference_edit`;
- no currently installed generic static route;
- planning routes: FLUX.2 Klein 4B distilled, Klein Base and Qwen-Image-Edit.

### Reference-free architecture module

- spec valid with `references: []`;
- requires `text_to_image`;
- no currently installed generic static route;
- planning routes: FLUX.2 Klein 4B distilled and Klein Base.

Schema regression rule:

- `references` must exist as a field;
- an empty list is valid for reference-free generation;
- `SPEC_ERROR` code 2 is fatal;
- route-not-found code 3 is the only expected no-installed-model result.

Runner55 conclusion: **generic schema/router foundation PASS**.

## CURRENT IMPLEMENTATION GATE — Runner56 / FLUX.2 Klein 4B distilled

Runner56 is now the active gate.

Runner:

`tools/structured-2d-character-pipeline/56_bootstrap_and_run_flux2_klein_4b_spike.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_t2i_probe.py`

Record:

`docs/FLUX2_KLEIN_4B_ASSET_STUDIO_SPIKE_2026-09-08.md`

### Purpose

Prove the first real generic static-generation backend on the target machine before building the Studio UI around it.

The first generated asset is deliberately an `architecture_module`, not the Exilada.

### Runtime isolation

Runner56 creates/uses:

`Z:\AI\Flux2Klein\ComfyUI_windows_portable`

It copies the already-proven embedded Python as a starting runtime but does not modify the source Kontext installation. ComfyUI code is separately cloned and pinned to:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

Port default: `8192`.

### Exact model payload

Runner56 downloads only:

1. `flux-2-klein-4b-fp8.safetensors`
   - 4,070,624,520 bytes
   - SHA256 `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6`
2. `qwen_3_4b.safetensors`
   - 8,044,982,048 bytes
   - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
3. `flux2-vae.safetensors`
   - 336,211,292 bytes
   - SHA256 `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`

Total model payload: `12,451,817,860` bytes (~12.45 GB decimal / ~11.60 GiB).

The full Qwen3-4B encoder is intentional for the first quality-controlled spike. The smaller FP4 encoder is not used yet. Base 4B is not downloaded.

### Controlled first inference

- output contract: `static_master`;
- asset type: `architecture_module`;
- reference-free T2I;
- 768×768;
- 4 distilled steps;
- CFG 1.0;
- Euler;
- seed 0.

This does not set production resolution. It is a hardware/integration feasibility probe.

### PASS contract

Technical PASS requires:

- isolated pinned ComfyUI starts;
- all three exact hashes pass;
- native FLUX.2 nodes exist;
- no OOM/crash;
- one valid 768×768 image is produced;
- prompt/manifest/log provenance is written.

Visual review then decides whether quality is sufficient to proceed to single/multi-reference editing.

Do not promote Klein to `installed` in the registry merely because Runner56 is prepared or because files were downloaded. Promotion requires actual local inference plus review.

## Model router — CURRENT REGISTRY

Machine-readable authority:

`tools/roguelite-asset-studio/model_registry.json`

### MiniMax H3 Base Ref2VA — ACTIVE / PROVEN MOTION SPECIALIST

Current proven character-motion baseline:

- `448×800`;
- `124 frames @24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed 0;
- no Turbo/FL2VA/style embedding.

Evidence:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H3 remains a motion specialist, not the universal still generator.

### MiniMax H3 FL2VA — TEMPORAL CANDIDATE

Potential future route for first/last-frame animation, environmental loops, VFX and temporal assets without authoritative real-video motion. Validate per asset class.

### FLUX.1 Kontext [dev] FP8 — ACTIVE R&D ONLY

Existing `Z:\AI\FluxKontext` runtime remains useful for editing/reconstruction research. Its dev license prevents silently making it the commercial-production default without appropriate licensing.

### FLUX.2 Klein 4B distilled — Runner56 current candidate

Apache-2.0 4B model, planned capabilities: text-to-image, single-reference edit and multi-reference edit. Current registry status remains `priority_candidate_not_installed` until Runner56 and subsequent editing validation pass.

### FLUX.2 Klein 4B Base — TRAINING/SPECIALIZATION CANDIDATE

Do not download in Runner56. Retain as strategic candidate for future Roguelite-specific LoRAs/fine-tuning after enough approved, licensable project data exists.

### Qwen-Image-Edit / 2509 — HEAVY QUALITY/CONTROL CANDIDATE

Apache-2.0 but materially heavier; requires a dedicated low-VRAM spike before use on RTX 3060 12GB.

### Step1X-Edit — DEFERRED

Current published memory needs do not fit the workstation well enough to prioritize it.

## Local-first production — HARD LOCK

Routine asset production must work locally after installation. Hosted services may be optional accelerators but cannot be mandatory for normal production.

Hardware baseline:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB RAM.

This local requirement also permits project authoring of mature/adult fictional states without relying on hosted authoring surfaces.

## Resolution contract — HARD LOCK

The former 128px Exilada asset baseline is retired. There is no universal 160/180/200/192/384px production sprite size.

Preserve useful generation/render resolution. Runtime apparent scale is separate. The same rule applies to non-character assets: no universal cell/texture size is imposed by the Studio.

## Runtime visual contracts — LOCKED

For animated character/creature actions:

- one action = one horizontal spritesheet row;
- frames read left-to-right;
- frame count is variable;
- complete character is precomposed in every runtime frame;
- no visible runtime body/hair/clothing/equipment layer assembly;
- timing/events/pivots live in metadata.

For environment/map production, prefer modular independently useful pieces over a single flattened AI-painted gameplay map.

## Exilada design state — REOPENED / FIRST CHARACTER LAB CASE

`exilada_master.png` remains identity/anatomy evidence but is not final visual-design authority.

Required revision direction includes stronger Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell charge, severe asymmetrical cloth degradation, materially caused greater torso exposure/partial breast exposure where appropriate, near/full adult nudity as legitimate states, dirt/wear/captivity evidence, and rejection of clean generic fantasy-bikini/MMO logic.

Runner53 remains paused until the approved character master is revised through the generic Studio path.

## Immediate implementation order

1. run Runner56 on the target workstation;
2. inspect technical logs/manifest and the generated ruined-gate source candidate;
3. if T2I fails, classify the exact runtime/hardware integration failure before changing variables;
4. if T2I passes technically and source quality is useful, retain the isolated runtime;
5. implement the Klein generic adapter contract;
6. test `single_reference_edit` and `multi_reference_edit` with semantic reference roles;
7. only then promote Klein to installed/accepted generic static backend;
8. expose Character Lab, Prop/Equipment and Environment workflows through the same adapter;
9. revise/approve the Exilada master there;
10. route animated character/creature actions through H3 Ref2VA and other temporal classes through validated temporal adapters;
11. add generic candidate browser/comparison/approval/export;
12. resume final rendering-language/pixel-art specialization with approved masters.

## Cleanup rule

Do not accumulate candidate checkpoints speculatively.

- keep the proven H3 Base50 set;
- keep current Kontext R&D set while still needed;
- Runner56 downloads only the Klein distilled FP8 + full Qwen3-4B + VAE set;
- do not download Klein Base, Qwen-Image-Edit or Step1X until their hypothesis becomes active;
- remove rejected model payloads after evidence/manifests are preserved and the model family is explicitly abandoned.
