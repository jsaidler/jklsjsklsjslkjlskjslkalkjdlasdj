# Roguelite — Current Project State

Status date: **2026-09-09**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`
4. `docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`
5. `docs/RUNNER60_FLUX2_KLEIN_BASE_OFFICIAL_PARITY_2026-09-09.md`
6. `docs/RUNNER58_FLUX2_KLEIN_EDIT_STRENGTH_CALIBRATION_2026-09-09.md`
7. `docs/VISUAL_DIRECTION.md`
8. `docs/CHARACTERS.md`
9. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
10. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Historical screening/spike docs remain evidence but do not override the current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs/registry and this file before completion is reported. Changed decisions replace stale locks rather than coexisting ambiguously.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- umbrella Studio root: `Z:\AI\RogueliteAssetStudio`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext R&D workspace: `Z:\AI\FluxKontext`
- Klein workspace: `Z:\AI\Flux2Klein`
- active Qwen edit workspace: `Z:\AI\QwenImageEdit`
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

The router/adapter boundary is UI-independent.

## Static-generation baseline — FLUX.2 Klein 4B distilled / ACTIVE

Runner56 proved fast local T2I on RTX 3060 12 GB:

- 768×768;
- 4 steps;
- CFG 1.0;
- Euler;
- seed 0;
- elapsed 12.054 s;
- coherent architecture-module authoring master;
- no OOM/runtime failure.

Runners57/58 proved distilled reference editing technically but failed production edit-strength/obedience.

Current role:

- **ROUTABLE**: `text_to_image`, `interactive_concept`;
- **NOT ROUTABLE**: production structural/reference editing.

## FLUX.2 Klein 4B Base — PARITY VALID / STRUCTURAL PRECISION FAIL

Installed:

- `flux-2-klein-base-4b-fp8.safetensors`
  - SHA256 `44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840`
- `qwen_3_4b.safetensors`
  - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
- `full_encoder_small_decoder.safetensors`
  - SHA256 `ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62`

### Runner59

Hardware PASS, visual verdict invalid because the custom graph did not match the official CFG-5 conditioning recipe and produced cyan/posterized output.

### Runner60 — official parity

Corrected graph:

- separate positive prompt encoding;
- separate empty negative encoding;
- ~1 MP reference scaling;
- geometry derived from first reference;
- Euler / CFG 5 / 20 steps.

Result:

- Base small-decoder VAE round-trip sane;
- full-VAE control sane;
- Base T2I sane/naturally colored;
- single edit meaningful but compound structural request incomplete;
- multi edit preserved identity but remained conservative.

Conclusion: Runner59 cyan was a recipe error, not a model defect.

### Runner61 — atomic + sequential structural gate / FINAL KLEIN EDIT VERDICT

Canonical record:

`docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`

Independent atomic outputs showed:

- **plank request**: model removed/reconstructed almost the entire left door leaf/opening instead of exactly one plank-width;
- **capstone request**: removed meaningful upper masonry but over-edited a broader top region than the named block;
- **strap request**: broadly reinterpreted door hardware rather than isolating only the requested lower-right strap.

Sequential chain:

- broad earlier states generally survived later stages;
- final material pass imported stronger rust/material language;
- but chaining coarse states did not solve localization precision.

### Klein Base conclusion

**TECHNICAL PASS / COARSE SEMANTIC EDITING USEFUL / PRECISION STRUCTURAL EDIT FAIL.**

Do not keep tuning Klein steps/prompts without a new technical mechanism.

Retain Klein Base for:

- Base/T2I research;
- future Roguelite-specific LoRA/fine-tuning;
- coarse concept-revision R&D if useful.

Do not route precision structural edits through it.

## CURRENT IMPLEMENTATION GATE — Runner62 / Qwen-Image-Edit-2509 native FP8

Canonical record:

`docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`

Runner:

`tools/structured-2d-character-pipeline/62_bootstrap_and_run_qwen_image_edit_2509_feasibility.ps1`

Executor:

`tools/roguelite-asset-studio/qwen_image_edit_2509_feasibility_gate.py`

Adapter:

`tools/roguelite-asset-studio/qwen_image_edit_2509_adapter.py`

### Why Qwen now

The Klein family has been genuinely exhausted for precision structural edits on the current validated recipes.

Qwen-Image-Edit-2509 is tested as a **specialized semantic/structural editor**, not as a replacement for every asset-generation model.

Native support already exists in the same pinned ComfyUI commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

Native graph semantics:

- `TextEncodeQwenImageEditPlus`;
- up to three image references;
- Qwen2.5-VL visual/text conditioning;
- Qwen image VAE;
- `FluxKontextImageScale` for the primary edit image;
- primary source VAE latent as KSampler latent;
- `ModelSamplingAuraFlow` shift 3;
- `CFGNorm` strength 1;
- Euler / simple / denoise 1;
- 20 steps;
- CFG 4;
- no Lightning LoRA for the first verdict.

### Runner62 payload

Isolated workspace:

`Z:\AI\QwenImageEdit`

Files:

1. `qwen_image_edit_2509_fp8_e4m3fn.safetensors`
   - 20,430,698,424 bytes
   - SHA256 `318568f61951ab9da21100c7b896e3c1da67f0d2efad6421545e022cfaa2b2b4`
2. `qwen_2.5_vl_7b_fp8_scaled.safetensors`
   - 9,384,670,680 bytes
   - SHA256 `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`
3. `qwen_image_vae.safetensors`
   - 253,806,246 bytes
   - SHA256 `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

Total weights: `30,069,175,350` bytes (~30.07 GB decimal / ~28.00 GiB).

### 12 GB strategy

Target remains RTX 3060 12 GB / 48 GB RAM.

Runner62:

- launches ComfyUI with `--lowvram`;
- reserves 1 GB VRAM;
- uses expandable CUDA allocation segments;
- explicitly loads the 9.38 GB Qwen2.5-VL encoder on CPU;
- uses the full native FP8 diffusion model, not Nunchaku/int4 or Lightning.

### Precision comparison

Runner62 runs two atomic edits from the same original gate and builds a direct comparison against Runner61 Klein outputs:

1. remove **one plank-width only** from the left leaf;
2. break **only** the lower-right horizontal strap.

Visual PASS requires materially better localization than Klein without losing gate identity/camera/unrelated geometry.

### Runner62 decision

- **technical + visual PASS** -> advance Qwen to multi-reference role separation and Exilada Character Lab validation;
- **OOM/runtime fail** -> preserve evidence and evaluate a lower-memory Qwen implementation such as Nunchaku/int4 before rejecting model capability;
- **technical PASS / precision FAIL** -> do not blindly increase steps; reconsider editor/control architecture.

## Model router authority

Machine-readable authority:

`tools/roguelite-asset-studio/model_registry.json`

Current Qwen status:

`runner62_active_pending_install_and_validation`

## Motion branch — MiniMax H3 Base Ref2VA / ACTIVE PROVEN

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

## Local-first production — HARD LOCK

Routine asset production must work locally after installation. Hosted services may be optional accelerators but cannot be mandatory.

This keeps mature/adult fictional-state authoring independent from hosted-surface restrictions.

## Game/runtime presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- native raster 640×360;
- fixed orthographic-like camera;
- pitch 26°;
- facing baseline 72°;
- `relative_scale=1.0` means baseline adult-human world scale, not sprite pixel height;
- runtime consumes complete precomposed character sprites.

## Resolution contract — HARD LOCK

The old 128px Exilada baseline is retired. There is no universal 160/180/200/192/384px production sprite resolution.

Preserve useful native/final generation resolution. Apparent runtime/world scale is separate and must not create a second destructively reduced gameplay raster asset.

The same principle applies to non-character assets.

## Runtime character representation — HARD LOCK

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

One animated action = one horizontal spritesheet row; frames read left-to-right; timing/events/pivots live in metadata.

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
- keep Klein distilled runtime as fast T2I;
- keep Klein Base while it remains a training/specialization candidate;
- Runner62 is the active new-model payload;
- do not download Step1X;
- do not delete rejected/retired payloads until evidence/manifests are preserved and cleanup is explicitly safe.
