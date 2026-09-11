# Roguelite — Current Project State

Status date: **2026-09-11**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER68_QWEN2511_LATENT_MASK_REGION_EDIT_2026-09-11.md`
4. `docs/RUNNER67_QWEN2511_ATOMIC_REGION_EDIT_2026-09-11.md`
5. `docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`
6. `docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`
7. `docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`
8. `docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`
9. `docs/VISUAL_DIRECTION.md`
10. `docs/CHARACTERS.md`
11. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
12. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Historical runner docs remain evidence but do not override the current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs/registry and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- umbrella Studio root: `Z:\AI\RogueliteAssetStudio`
- H3: `Z:\AI\MiniMaxH3`
- Kontext R&D: `Z:\AI\FluxKontext`
- Klein: `Z:\AI\Flux2Klein`
- Qwen edit: `Z:\AI\QwenImageEdit`
- automatic localization: `Z:\AI\RogueliteAssetStudio\localization`
- Wan paused: `Z:\AI\WanAnimate2`
- SSD evidence retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## Umbrella direction — ROGUELITE ASSET STUDIO / HARD LOCK

The local production tool is for the **entire visual asset base**, not only Exilada and not one universal model.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized generation/edit/perception/motion adapters -> deterministic processors -> candidate/version store -> explicit approval -> runtime export`

It must cover playable characters, NPCs, enemies, creatures, bosses, equipment, props, architecture, terrain, vegetation, set pieces, materials, VFX/environment animation and UI art.

Semantic reference roles remain a hard contract:

`identity`, `anatomy`, `style`, `material`, `palette`, `structure`, `composition`, `pose`, `motion`, `camera`, `environment`, `previous_approved_state`.

Generic authority:

- `tools/roguelite-asset-studio/asset_schema.json`
- `tools/roguelite-asset-studio/model_registry.json`
- `tools/roguelite-asset-studio/asset_studio_core.py`
- `tools/roguelite-asset-studio/adapter_protocol.py`

## Static generation — FLUX.2 Klein 4B distilled / ACTIVE

Runner56 proved fast local T2I on RTX 3060 12 GB:

- 768×768;
- 4 steps / CFG 1 / Euler;
- 12.054 s;
- no OOM;
- useful general static concept/master backend.

Runners57/58 proved reference editing technically but rejected it visually for production precision.

Routable:

- `text_to_image`
- `interactive_concept`

Not routable:

- production precision editing.

## FLUX.2 Klein 4B Base — edit precision hypothesis exhausted

Runner60 fixed the original Base graph and proved healthy parity. Runner61 proved atomic/sequential edits remain too coarse.

Final role:

- T2I/Base research;
- future project LoRA/fine-tuning;
- coarse concept revision.

Not routable for exact component edits.

## Qwen-Image-Edit-2509 — retired

Runner62:

**TECHNICAL PASS / BETTER PRESERVATION THAN KLEIN / EXACT STRUCTURAL FACT FAIL.**

Its diffusion checkpoint was removed after preserving evidence. Shared Qwen2.5-VL encoder and Qwen VAE remain for 2511.

## Qwen-Image-Edit-2511 — strongest installed semantic editor

Runtime:

- `qwen_image_edit_2511_fp8mixed.safetensors`
- bytes `20,533,762,817`
- SHA256 `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`
- Qwen2.5-VL 7B FP8 on CPU
- `--lowvram`, reserve 1 GB
- AuraFlow shift 3.1
- CFGNorm 1
- Euler/simple, CFG 4

Runner63 closed unrestricted global precision prompting:

- plank improved materially;
- strap failed with a large replacement bar;
- 40 steps roughly doubled runtime without solving the hard case.

Qwen2511 remains installed, but exact structural edits require automatic control architecture.

## Precision-control architecture — CURRENT

Canonical production idea:

`semantic request -> parent/component perception -> automatic mask/decomposition -> operation-specific control -> semantic editor -> deterministic full-resolution composite`

No user-drawn production mask/box is allowed.

### Runner64 — COMPLETE

Flat full-image localization selected stone blocks instead of plank/strap.

Useful proof:

- SAM2 segmented selected boxes cleanly;
- deterministic regional compositor preserved source pixels outside the allowed region with changed ratio >Δ12 of `0.0`.

Classification:

**FLAT LOCALIZATION FAIL / COMPOSITOR PASS.**

### Runner65 — COMPLETE

Hierarchical localization:

`full image -> parent door -> child search -> SAM2 rerank`.

Visual result:

- parent door: PASS;
- lower-right strap: PASS;
- plank request: correct left repeated-structure leaf found, but entire leaf selected.

Classification:

**PARENT PASS / STRAP PASS / REPEATED STRUCTURE FOUND / ONE-PLANK GRANULARITY FAIL.**

### Runner66 — COMPLETE / STRUCTURAL PERCEPTION PASS

Deterministic repeated-member decomposition split the Runner65 left leaf by persistent vertical seam energy.

Actual plank evidence:

- seam peaks: `x=358`, `x=388`;
- selected interval: `[358,388]`;
- width: `30 px`;
- bbox: `[358,295,388,644]`;
- area relative to parent: `0.08923`;
- vertical aspect: `11.633`;
- width relative to parent: `0.10909`;
- elapsed: `0.321 s`;
- visual: **PASS — exactly one vertical plank**.

Runner65 strap mask remained visually correct and was retained unchanged.

Classification:

**TECHNICAL PASS / ONE-PLANK MASK PASS / LOWER-RIGHT STRAP MASK PASS / NO MANUAL INPUT.**

### Runner67 — COMPLETE / EDIT CONTROL FAIL

Architecture:

`approved automatic mask -> source crop + red target-guide image -> Qwen2511 -> deterministic regional composite`.

Technical jobs completed and the deterministic compositor again preserved outside-region pixels exactly enough that changed ratio >Δ12 remained `0.0`.

Plank:

- Qwen raw crop produced a narrow opening;
- local geometry shifted relative to the separately applied automatic mask;
- final composite produced elongated/reconstructed strips instead of a clean removed plank.

Strap:

- Qwen copied the red locator rectangle into generated content;
- the final result contained a red patch rather than a physical break.

Runner67 metrics:

- plank Qwen elapsed `639.175 s`, inside-allowed changed ratio >Δ12 `0.272004`;
- strap Qwen elapsed `601.176 s`, inside-allowed changed ratio >Δ12 `0.124109`;
- both outside-allowed changed ratio >Δ12 `0.0`.

Classification:

**TECHNICAL PASS / MASKS PASS / COMPOSITOR PASS / RED GUIDE LEAK FAIL / CROP-MASK ALIGNMENT FAIL / PRECISION EDIT FAIL.**

Colored target guides are rejected as a control mechanism.

## CURRENT IMPLEMENTATION GATE — RUNNER68 / native automatic latent mask

Canonical record:

`docs/RUNNER68_QWEN2511_LATENT_MASK_REGION_EDIT_2026-09-11.md`

Runner:

`tools/structured-2d-character-pipeline/68_run_qwen2511_latent_mask_region_edit.ps1`

Masked adapter:

`tools/roguelite-asset-studio/qwen_image_edit_2511_masked_adapter.py`

Executor:

`tools/roguelite-asset-studio/qwen2511_latent_mask_region_gate.py`

Architecture:

`Runner66 automatic mask -> source crop -> same-scale automatic mask -> ImageToMask -> SetLatentNoiseMask(source latent) -> Qwen2511 -> deterministic full-resolution composite`

Key changes from Runner67:

- no red/colored locator image is passed to Qwen;
- source crop is the only semantic image reference;
- automatic mask controls where sampling noise is injected;
- mask and source pass through the same `FluxKontextImageScale` path to preserve alignment;
- plank uses its full atomic operation mask;
- strap-break derives the central 40% of the approved strap mask so both ends are outside the editable region;
- deterministic final composite remains as a second containment layer;
- no download and no manual mask/box.

Runner68 PASS requires:

1. plank becomes one clean aligned same-width opening;
2. neighboring planks/door geometry remain stable;
3. strap middle is clearly absent while both strap ends remain;
4. no replacement bar appears;
5. no locator-color artifact exists;
6. outside allowed regions remain source pixels by construction.

If Runner68 passes, promote `automatic_region_edit` and move to semantic multi-reference role separation before Character Lab.

If Runner68 fails with correct masks, keep perception/decomposition/compositor accepted and replace only the regional editor with a dedicated mask-native/inpainting backend.

## Current perception payload

Grounding DINO Tiny:

- `IDEA-Research/grounding-dino-tiny`
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`
- SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`
- Apache-2.0.

SAM2.1 Hiera Small:

- `facebook/sam2.1-hiera-small`
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`
- Apache-2.0.

Repeated-element decomposition is project-owned deterministic code and adds no model payload.

## Motion branch — MiniMax H3 Base Ref2VA / ACTIVE PROVEN

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

H3 remains a motion specialist, not a universal still generator.

## Local-first production — HARD LOCK

Routine production must work locally after installation. Hosted services may be optional accelerators, never mandatory normal-production dependencies. This includes mature/adult fictional character states.

## Game/runtime presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- native raster 640×360;
- fixed orthographic-like camera;
- pitch 26°;
- facing baseline 72°;
- `relative_scale=1.0` means baseline adult-human world scale, not sprite pixel height;
- runtime consumes complete precomposed character sprites.

## Resolution contract — HARD LOCK

The old 128px baseline is retired. There is no universal 160/180/200/192/384px production sprite resolution.

Preserve useful native/final generation resolution. Apparent runtime/world scale is separate and must not create a second destructively reduced gameplay raster asset. Same rule applies to non-character assets.

## Runtime character representation — HARD LOCK

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

One animated action = one horizontal spritesheet row; frames left-to-right; timing/events/pivots in metadata.

## Exilada design state — REOPENED / first Character Lab case

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

## Cleanup rule

Do not accumulate checkpoints speculatively.

- keep proven H3 Base50;
- keep Kontext R&D while still needed;
- keep Klein distilled as fast T2I;
- keep Klein Base while useful as training/specialization base;
- Qwen2509 diffusion remains retired/deleted; preserve evidence;
- keep Qwen2511 + shared Qwen2.5-VL + Qwen VAE;
- keep Grounding DINO Tiny + SAM2.1 while precision architecture remains active;
- Runner66/68 add no model checkpoint;
- do not download another regional editor until Runner68 evidence exists.
