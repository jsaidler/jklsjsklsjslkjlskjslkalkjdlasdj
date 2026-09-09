# Roguelite — Current Project State

Status date: **2026-09-09**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER59_FLUX2_KLEIN_BASE_EDIT_GATE_2026-09-09.md`
4. `docs/RUNNER58_FLUX2_KLEIN_EDIT_STRENGTH_CALIBRATION_2026-09-09.md`
5. `docs/FLUX2_KLEIN_4B_ASSET_STUDIO_SPIKE_2026-09-08.md`
6. `docs/VISUAL_DIRECTION.md`
7. `docs/CHARACTERS.md`
8. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
9. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Historical preflight/model-screening documents remain evidence but do not override the current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs/registry and this file before completion is reported. Changed decisions replace stale locks rather than coexisting ambiguously.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- umbrella Studio root: `Z:\AI\RogueliteAssetStudio`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext R&D workspace: `Z:\AI\FluxKontext`
- active Klein workspace: `Z:\AI\Flux2Klein`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## UMBRELLA DIRECTION — ROGUELITE ASSET STUDIO / HARD LOCK

The local production tool is **not an Exilada editor** and is not a wrapper around one model.

It must cover the complete visual asset base: playable characters, NPCs, enemies, creatures, bosses, equipment, props, architecture, terrain, vegetation, environment modules/set pieces, materials, VFX/environment animation and UI art where needed.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized model adapter -> local model runtime -> deterministic processing -> candidate/version store -> explicit approval -> runtime export`

The Exilada is the first difficult Character Lab validation project, not the scope-defining application.

Generic foundation:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`
- `tools/roguelite-asset-studio/adapter_protocol.py`
- `tools/roguelite-asset-studio/flux2_klein_adapter.py`
- `tools/roguelite-asset-studio/flux2_klein_base_adapter.py`

The router and adapter boundary are UI-independent.

## Runner55 — FOUNDATION PASS

Runner55 proved the generic schema/router against both a referenced playable character and a reference-free architecture module.

Locked schema behavior:

- `references` must exist;
- `references: []` is valid;
- `SPEC_ERROR` exit code 2 is fatal;
- route-not-found exit code 3 is the expected no-compatible-installed-route result.

## Runner56 — FLUX.2 Klein 4B distilled T2I PASS

Runtime:

- isolated `Z:\AI\Flux2Klein`;
- ComfyUI commit `672ba9e5e388bd6bfac5ceef61f89ffdd9467200`;
- RTX 3060 12 GB / 48 GB RAM;
- no H3/Kontext mutation.

Verified payload:

- `flux-2-klein-4b-fp8.safetensors` — SHA256 `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6`
- `qwen_3_4b.safetensors` — SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
- `flux2-vae.safetensors` — SHA256 `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`

T2I result:

- `architecture_module` / `static_master`;
- 768×768;
- 4 steps, CFG 1.0, Euler, seed 0;
- elapsed **12.054 s**;
- no OOM/runtime crash;
- output SHA256 `8ce5b54cf4f7ccabf3aee3583de9c76c8942115aed8592a9430b8ede68730a16`.

Visual continuation verdict: **PASS** as useful static authoring master, not final game art.

## Runner57 — reference-edit technical PASS / visual-strength partial fail

Distilled 4B successfully executed:

- single reference: 768×768, 4 steps, CFG 1.0, Euler, seed 0, **14.063 s**;
- ordered two-reference: same settings, **16.025 s**;
- no OOM, graph failure, duplicated gate or catastrophic identity loss.

However edits remained too close to the source. Therefore single/multi editing was technically proven but not production-routable.

## Runner58 — distilled edit-strength calibration COMPLETE / VISUAL FAIL

Canonical record:

`docs/RUNNER58_FLUX2_KLEIN_EDIT_STRENGTH_CALIBRATION_2026-09-09.md`

Runner58 tested the same original gate with explicit binary edits at 4/8/12 steps and separately generated a severe-decay material board for the multi-reference test.

All seven jobs passed technically. Total elapsed: **156.620 s**.

Key single-reference metrics:

- 4 steps: mean abs luma 23.8699 / changed >24 = 0.386804
- 8 steps: 27.6526 / 0.794367
- 12 steps: 29.2693 / 0.808146

Key multi-reference metrics:

- 4 steps: mean abs luma 12.0681 / changed >24 = 0.042324
- 8 steps: 14.3251 / 0.161229
- 12 steps: 15.3945 / 0.203785

Visual conclusion:

- more distilled steps create much more broad re-rendering/material drift;
- they do **not** reliably execute the requested structural facts (full missing plank, large missing top-left block, broken requested strap);
- multi-reference preserves source structure strongly but imports the separate material authority too weakly.

Therefore:

**FLUX.2 Klein 4B distilled remains accepted for fast local T2I/concept generation, but its reference-edit paths are rejected for production routing in the current project.**

Do not keep increasing distilled steps without a new technical hypothesis.

## MODEL ROUTER STATUS — CURRENT

Machine authority:

`tools/roguelite-asset-studio/model_registry.json`

### FLUX.2 Klein 4B distilled

Status:

`active_static_t2i_proven_edit_visual_fail`

Routable:

- `text_to_image`
- `interactive_concept`

Technical-only / non-routable:

- `single_reference_edit`
- `multi_reference_edit`

### FLUX.2 Klein 4B Base

Status:

`runner59_prepared_pending_install_and_validation`

This is now the active stronger-edit hypothesis before changing model families.

## CURRENT IMPLEMENTATION GATE — Runner59 / FLUX.2 Klein 4B Base strong edit

Canonical record:

`docs/RUNNER59_FLUX2_KLEIN_BASE_EDIT_GATE_2026-09-09.md`

Runner:

`tools/structured-2d-character-pipeline/59_bootstrap_and_run_flux2_klein_base_edit_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_base_edit_gate.py`

Adapter:

`tools/roguelite-asset-studio/flux2_klein_base_adapter.py`

### Why Base now

The project is **not jumping model families yet**. Base is the non-distilled Apache-2.0 4B sibling and is the official higher-flexibility/full-step branch.

Current official ComfyUI Base edit recipe basis:

- Euler;
- CFG 5;
- 20 steps;
- Qwen3-4B;
- `full_encoder_small_decoder.safetensors`.

Runner59 also tests 50 steps because Base is the full-step/flexibility branch.

### Additional payload

Only two new files:

1. `flux-2-klein-base-4b-fp8.safetensors`
   - 4,089,498,488 bytes
   - SHA256 `44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840`
2. `full_encoder_small_decoder.safetensors`
   - 249,519,092 bytes
   - SHA256 `ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62`

Total additional payload: `4,339,017,580` bytes (~4.34 GB decimal).

Existing `qwen_3_4b.safetensors` is reused.

### Runner59 matrix

Same gate and same Runner58 material board:

- Base single-reference: 20 steps / 50 steps;
- Base multi-reference: 20 steps / 50 steps;
- 768×768;
- CFG 5;
- Euler;
- seed 0.

Visual PASS requires at least one single and one multi output to execute the explicit structural facts strongly while retaining gate identity/camera, with multi also importing the separate material authority visibly.

If Base passes:

1. activate Base single/multi edit routing;
2. build the first generic Studio UI/state layer;
3. use the reopened Exilada as the first high-difficulty Character Lab case;
4. validate a non-character prop/equipment case;
5. add candidate/history/approval/export;
6. wrap H3 behind the same orchestration boundary for temporal assets.

If Base fails:

- keep Klein distilled as T2I/concept backend;
- retain Base as a possible future training/specialization base;
- move strong reference editing to the next specialized editor branch;
- current next candidate is Qwen-Image-Edit-2509 under a controlled FP8/low-VRAM spike;
- do not continue increasing Klein steps blindly.

## OTHER MODEL FAMILIES

### MiniMax H3 Base Ref2VA — ACTIVE / PROVEN MOTION SPECIALIST

Current Exilada motion baseline:

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

Potential future route for environmental loops, VFX and first/last-frame tasks. Validate per asset class.

### FLUX.1 Kontext [dev] — ACTIVE R&D ONLY

Useful for editing/reconstruction research; non-commercial dev license means it cannot silently become the shipping default.

### Qwen-Image-Edit-2509 — NEXT STRONG EDIT CANDIDATE IF NEEDED

Apache-2.0, but heavier than the 12 GB baseline. Requires a dedicated low-VRAM feasibility spike before use.

### Step1X-Edit — DEFERRED

Current published memory use remains a poor fit for the workstation.

## LOCAL-FIRST PRODUCTION — HARD LOCK

Routine asset production must work locally after installation. Hosted services may be optional accelerators but cannot be mandatory.

This keeps mature/adult fictional-state authoring independent from hosted-surface restrictions.

## GAME/RUNTIME PRESENTATION — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- native raster 640×360;
- fixed orthographic-like camera;
- pitch 26°;
- facing baseline 72°;
- `relative_scale=1.0` means baseline adult-human world scale, not sprite pixel height;
- runtime consumes complete precomposed character sprites.

## RESOLUTION CONTRACT — HARD LOCK

The old 128px Exilada baseline is retired. There is no universal 160/180/200/192/384px production sprite resolution.

Preserve useful native source resolution. Runtime apparent/world scale is separate.

## RUNTIME CHARACTER REPRESENTATION — HARD LOCK

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

One animated action = one horizontal spritesheet row; frames read left-to-right; timing/events/pivots live in metadata.

## ENVIRONMENT/MAP PRODUCTION — LOCKED

Prefer modular independently useful pieces over one flattened AI-painted gameplay map: terrain patches, walls/cliffs, architecture modules, doors/gates, vegetation, rocks/debris, props, foreground/background set pieces, loops and damage-state variants.

## EXILADA DESIGN STATE — REOPENED / FIRST CHARACTER LAB CASE

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

## CLEANUP RULE

Do not accumulate candidate checkpoints speculatively.

- keep proven H3 Base50 set;
- keep current Kontext R&D set while still needed;
- keep proven Klein distilled runtime;
- Runner59 adds only Base FP8 + small-decoder VAE;
- do not download Qwen-Image-Edit or Step1X until their hypothesis becomes active;
- remove rejected payloads after evidence/manifests are preserved and a branch is explicitly abandoned.
