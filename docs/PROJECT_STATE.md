# Roguelite — Current Project State

Status date: **2026-09-10**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`
4. `docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`
5. `docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`
6. `docs/RUNNER60_FLUX2_KLEIN_BASE_OFFICIAL_PARITY_2026-09-09.md`
7. `docs/VISUAL_DIRECTION.md`
8. `docs/CHARACTERS.md`
9. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
10. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Historical screening/spike documents remain evidence but do not override the current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs/registry and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- umbrella Studio root: `Z:\AI\RogueliteAssetStudio`
- H3 workspace: `Z:\AI\MiniMaxH3`
- Kontext R&D: `Z:\AI\FluxKontext`
- Klein workspace: `Z:\AI\Flux2Klein`
- Qwen edit workspace: `Z:\AI\QwenImageEdit`
- Wan paused: `Z:\AI\WanAnimate2`
- SSD evidence retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## UMBRELLA DIRECTION — ROGUELITE ASSET STUDIO / HARD LOCK

The local production tool is for the **entire visual asset base**, not only Exilada and not one universal model.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized adapter -> local runtime -> deterministic processing -> candidate/version store -> explicit approval -> runtime export`

It must cover playable characters, NPCs, enemies, creatures, bosses, equipment, props, architecture, terrain, vegetation, set pieces, materials, VFX/environment animation and UI art.

Semantic reference roles remain a hard contract: `identity`, `anatomy`, `style`, `material`, `palette`, `structure`, `composition`, `pose`, `motion`, `camera`, `environment`, `previous_approved_state`.

Generic authority:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`
- `tools/roguelite-asset-studio/adapter_protocol.py`

## STATIC GENERATION — FLUX.2 KLEIN 4B DISTILLED / ACTIVE

Runner56 proved fast local T2I on RTX 3060 12 GB:

- 768×768;
- 4 steps / CFG 1 / Euler;
- 12.054 s;
- coherent architecture authoring master;
- no OOM/runtime failure.

Runners57/58 proved distilled reference editing technically but failed production structural obedience.

Routable:

- `text_to_image`
- `interactive_concept`

Not routable:

- production precision/reference editing.

## FLUX.2 KLEIN 4B BASE — STRUCTURAL PRECISION HYPOTHESIS EXHAUSTED

Runner59 visual result was invalid because the first Base graph diverged from official conditioning semantics.

Runner60 corrected the graph and proved sane VAE round-trip, T2I and naturally colored editing at 1024×1024 / 20 steps / CFG 5.

Runner61 then tested one-fact atomic edits and sequential composition.

Final verdict:

**TECHNICAL PASS / COARSE SEMANTIC EDIT USEFUL / EXACT STRUCTURAL PRECISION FAIL.**

Observed:

- one-plank request removed/reconstructed almost the entire left leaf/opening;
- one-capstone request altered a broader upper region than the named block;
- one-strap request reinterpreted a broad hardware configuration;
- sequential edits preserve coarse state but cannot repair inaccurate localization;
- final material pass can import stronger rust/material language.

Retain Base for valid Base/T2I research and future Roguelite-specific LoRA/fine-tuning. Do not route production precision structural edits through it.

## RUNNER62 — QWEN-IMAGE-EDIT-2509 / TECHNICAL PASS / PRECISION FAIL

Canonical record:

`docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`

Runtime:

- isolated `Z:\AI\QwenImageEdit`;
- ComfyUI commit `672ba9e5e388bd6bfac5ceef61f89ffdd9467200`;
- RTX 3060 12 GB / 48 GB RAM;
- ComfyUI `--lowvram`, 1 GB VRAM reserve;
- Qwen2.5-VL 7B FP8 encoder explicitly on CPU;
- no Lightning LoRA.

Payload used:

- `qwen_image_edit_2509_fp8_e4m3fn.safetensors`
  - 20,430,698,424 bytes
  - SHA256 `318568f61951ab9da21100c7b896e3c1da67f0d2efad6421545e022cfaa2b2b4`
- `qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - 9,384,670,680 bytes
  - SHA256 `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`
- `qwen_image_vae.safetensors`
  - 253,806,246 bytes
  - SHA256 `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

Recipe:

- 1024×1024;
- 20 steps;
- CFG 4;
- Euler/simple;
- denoise 1;
- AuraFlow shift 3;
- CFGNorm 1.

Actual results:

### Plank

- elapsed **498.011 s**;
- mean abs luma 5.8785;
- changed ratio >24 = 0.054299.

Visual: extremely good source preservation compared with Klein, but the requested narrow full-height one-plank opening is not unambiguously executed.

### Strap

- elapsed **455.408 s**;
- mean abs luma 6.3035;
- changed ratio >24 = 0.057031.

Visual: more localized than Klein, but the lower hardware/door-bottom region is reinterpreted instead of simply breaking only the named strap with a missing middle section.

Runner62 classification:

**TECHNICAL PASS / LOCALIZATION-PRESERVATION IMPROVED / EXACT STRUCTURAL FACT FAIL.**

Do not route 2509 as production precision editor and do not blindly add steps.

Generated evidence/manifests are preserved. Its diffusion checkpoint is eligible for cleanup when Runner63 activates 2511. Shared Qwen2.5-VL + VAE must be retained.

## CURRENT IMPLEMENTATION GATE — RUNNER63 / QWEN-IMAGE-EDIT-2511

Canonical record:

`docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`

Runner:

`tools/structured-2d-character-pipeline/63_bootstrap_and_run_qwen_image_edit_2511_precision.ps1`

Executor:

`tools/roguelite-asset-studio/qwen_image_edit_2511_precision_gate.py`

Adapter:

`tools/roguelite-asset-studio/qwen_image_edit_2511_adapter.py`

### Why 2511

Qwen-Image-Edit-2511 is the immediate same-family successor because the official revision targets lower image drift, better consistency and stronger geometric reasoning — exactly the unresolved Runner62 problem.

Shared Runner62 encoder/VAE are reused. New model only:

`qwen_image_edit_2511_fp8mixed.safetensors`

- bytes `20,533,762,817`;
- SHA256 `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`.

Runner63 first verifies preserved Runner62 evidence, then removes the rejected 2509 diffusion checkpoint if and only if its hash matches. This prevents model accumulation while retaining provenance.

### Updated native ComfyUI parity

Runner63 pins:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

2511 adapter uses:

- `TextEncodeQwenImageEditPlus`;
- `FluxKontextImageScale`;
- `FluxKontextMultiReferenceLatentMethod(index_timestep_zero)` on positive and negative;
- `ModelSamplingAuraFlow` shift 3.1;
- `CFGNorm` strength 1;
- Euler/simple/denoise 1;
- CFG 4;
- no Lightning.

### Runner63 matrix

Same two atomic tasks:

- exact one-plank-width full-height removal;
- exact lower-right strap break.

Each runs at:

- 20 steps;
- 40 steps.

Comparison sheet:

`original -> Klein Runner61 -> Qwen2509 Runner62 -> Qwen2511/20 -> Qwen2511/40`.

Visual PASS requires exact structural-fact improvement, not just low pixel drift.

If 2511 passes, proceed to multi-reference semantic role separation, then Exilada Character Lab and another non-character class before generic UI promotion.

If 2511 fails both 20/40 precision tests, stop blind step tuning and move to **automatic localization/region-control architecture or another editor family**. Routine manual masks remain outside the production contract.

## MODEL ROUTER AUTHORITY

`tools/roguelite-asset-studio/model_registry.json`

Current statuses:

- H3 Ref2VA: active motion specialist;
- Klein distilled: active fast T2I/concept;
- Klein Base: training/T2I candidate, precision edit rejected;
- Qwen 2509: technical evidence retained, precision route rejected;
- Qwen 2511: **current precision editor gate**;
- Step1X: deferred hardware mismatch.

## MOTION BRANCH — MINIMAX H3 BASE REF2VA / ACTIVE PROVEN

Exilada motion baseline:

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

## LOCAL-FIRST PRODUCTION — HARD LOCK

Routine production must work locally after installation. Hosted services can be optional accelerators, never mandatory normal-production dependencies. This includes mature/adult fictional character states.

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

Preserve useful native/final generation resolution. Apparent runtime/world scale is separate and must not create a second destructively reduced gameplay raster asset. Same rule applies to non-character assets.

## RUNTIME CHARACTER REPRESENTATION — HARD LOCK

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

One animated action = one horizontal spritesheet row; frames left-to-right; timing/events/pivots in metadata.

## EXILADA DESIGN STATE — REOPENED / FIRST CHARACTER LAB CASE

`assets/source/characters/exilada/reference/exilada_master.png` remains identity/anatomy evidence but is not final visual-design authority.

Required revision direction:

- stronger Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell charge;
- severe asymmetric cloth degradation;
- materially caused greater torso exposure/partial breast exposure where appropriate;
- near/full adult nudity as legitimate states;
- dirt/wear/captivity evidence;
- reject clean generic fantasy-bikini/MMO logic;
- preserve mature adult anatomy and identity.

Runner53 remains paused until the static master is revised through the generic Studio path.

## CLEANUP RULE

Do not accumulate checkpoints speculatively.

- keep proven H3 Base50;
- keep Kontext R&D while still needed;
- keep Klein distilled as fast T2I;
- keep Klein Base while it remains a training/specialization candidate;
- preserve Runner62 generated evidence;
- Runner63 may remove the rejected Qwen2509 diffusion checkpoint after exact-hash/evidence verification;
- retain shared Qwen2.5-VL encoder + Qwen VAE for 2511;
- do not download Step1X while Runner63 is active.
