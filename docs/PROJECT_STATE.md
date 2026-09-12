# Roguelite — Current Project State

Status date: **2026-09-11**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER70_SDXL_INPAINT_1024_PARITY_2026-09-11.md`
4. `docs/RUNNER69_SDXL_INPAINT_PRECISION_2026-09-11.md`
5. `docs/RUNNER68_QWEN2511_LATENT_MASK_REGION_EDIT_2026-09-11.md`
6. `docs/RUNNER67_QWEN2511_ATOMIC_REGION_EDIT_2026-09-11.md`
7. `docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`
8. `docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`
9. `docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`
10. `docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`
11. `docs/VISUAL_DIRECTION.md`
12. `docs/CHARACTERS.md`
13. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
14. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

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
- dedicated SDXL inpaint: `Z:\AI\SDXLInpaint`
- automatic localization: `Z:\AI\RogueliteAssetStudio\localization`
- Wan paused: `Z:\AI\WanAnimate2`
- SSD evidence retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## Umbrella direction — ROGUELITE ASSET STUDIO / HARD LOCK

The local production tool is for the **entire visual asset base**, not only Exilada and not one universal model.

Canonical architecture:

`Studio UI -> asset spec/state -> model router -> specialized generation/edit/inpaint/perception/motion adapters -> deterministic processors -> candidate/version store -> explicit approval -> runtime export`

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

Runners57/58 rejected it for production precision editing.

Routable:

- `text_to_image`
- `interactive_concept`

Not routable:

- production precision editing.

## FLUX.2 Klein 4B Base — edit precision exhausted

Runner60 fixed the graph and proved healthy parity. Runner61 proved atomic/sequential edits remain too coarse.

Final role:

- T2I/Base research;
- future project LoRA/fine-tuning;
- coarse concept revision.

Not routable for exact component edits.

## Qwen-Image-Edit-2509 — retired

Runner62:

**TECHNICAL PASS / BETTER PRESERVATION THAN KLEIN / EXACT STRUCTURAL FACT FAIL.**

Its diffusion checkpoint was removed after preserving evidence. Shared Qwen2.5-VL encoder and Qwen VAE remain for 2511.

## Qwen-Image-Edit-2511 — installed semantic editor / exact masked role closed

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

Runner63 closed unrestricted global precision prompting. Runner67 closed colored locator conditioning. Runner68 proved native latent mask containment but Qwen remained semantically near-no-op inside the mask.

Runner68:

- plank inside-allowed changed ratio >Δ12 `0.059154`;
- strap inside-allowed changed ratio >Δ12 `0.052066`;
- both outside-allowed changed ratio >Δ12 `0.0`;
- plank remained present;
- strap remained effectively continuous.

Classification:

**TECHNICAL PASS / AUTOMATIC MASK CONTROL PASS / OUTSIDE-REGION CONTAINMENT PASS / SEMANTIC OPERATION FAIL / QWEN MASKED-PRECISION ROLE CLOSED.**

Qwen2511 remains installed for higher-level semantic/appearance/reference editing. Do not route exact component removal/fill to it.

## Precision-control architecture — ACCEPTED THROUGH MASK/COMPOSITOR

Canonical precision architecture:

`semantic request -> parent/component perception -> automatic segmentation/decomposition -> operation-specific mask -> specialized regional editor -> deterministic full-resolution composite`.

No user-drawn production mask/box is allowed.

### Runner64 — COMPLETE

Flat full-image localization failed; deterministic regional compositor passed with outside-region changed ratio >Δ12 `0.0`.

### Runner65 — COMPLETE

Hierarchical localization passed for parent door and lower-right strap. Plank request found the correct repeated left leaf but not one board.

### Runner66 — COMPLETE / STRUCTURAL PERCEPTION PASS

Deterministic repeated-member decomposition:

- seam peaks `x=358`, `x=388`;
- selected interval `[358,388]`;
- width `30 px`;
- bbox `[358,295,388,644]`;
- area relative to parent `0.08923`;
- vertical aspect `11.633`;
- elapsed `0.321 s`;
- visual: **PASS — exactly one plank**.

Runner65 strap mask remained visually correct.

Accepted precision components:

1. semantic hierarchy;
2. Grounding DINO parent/component localization where appropriate;
3. SAM2.1 box-prompt segmentation;
4. project-owned repeated-element decomposition;
5. operation-aware submask derivation;
6. deterministic full-resolution composite.

The active uncertainty is only the dedicated regional inpainting backend and its correct operating regime.

## Runner69 — COMPLETE / SDXL dedicated inpaint at subtraining resolution

Canonical record:

`docs/RUNNER69_SDXL_INPAINT_PRECISION_2026-09-11.md`

Payload:

- SDXL Inpainting 0.1 FP16 UNet, SHA256 `6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f`;
- SDXL Base 1.0 checkpoint, SHA256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`, used only for CLIP/VAE;
- license: CreativeML Open RAIL++-M.

Technical execution passed on RTX 3060 12 GB with no OOM.

Plank:

- crop `256x512`;
- elapsed `18.075 s`;
- inside-allowed changed ratio >Δ12 `0.539487`;
- outside >Δ12 `0.0`;
- visually reacted strongly but produced bright/shiny vertical reconstruction artifacts instead of a clean opening.

Strap:

- crop `384x256`;
- elapsed `10.047 s`;
- inside-allowed changed ratio >Δ12 `0.336265`;
- outside >Δ12 `0.0`;
- visually failed to create a clean central break with matching wood underneath.

Important qualification:

SDXL Inpainting 0.1 was trained at `1024x1024`, so Runner69 used inputs far below the model's intended spatial regime. Runner69 is therefore **not** the final verdict on the backend.

Classification:

**TECHNICAL PASS / MASK-NATIVE RESPONSE PASS / OUTSIDE-REGION CONTAINMENT PASS / VISUAL OPERATION FAIL AT SUBTRAINING RESOLUTION / SDXL HYPOTHESIS STILL OPEN.**

## CURRENT IMPLEMENTATION GATE — RUNNER70 / SDXL 1024 training-resolution parity

Canonical record:

`docs/RUNNER70_SDXL_INPAINT_1024_PARITY_2026-09-11.md`

Runner:

`tools/structured-2d-character-pipeline/70_run_sdxl_inpaint_1024_parity_gate.ps1`

Executor:

`tools/roguelite-asset-studio/sdxl_inpaint_1024_parity_gate.py`

Existing adapter reused:

`tools/roguelite-asset-studio/sdxl_inpaint_adapter.py`

Hypothesis:

Runner69's artifacts may be caused by running a 1024-trained model on tiny rectangular crops. Test the exact same backend and operation semantics at native training-scale geometry before switching models.

One-variable architecture:

`Runner66 target -> exact 512x512 source context -> jointly upscale source+mask to 1024x1024 -> same SDXL InpaintModelConditioning recipe -> downsample generated crop back to 512 source coordinates -> deterministic full-resolution composite`.

Unchanged recipe:

- 30 steps;
- CFG 6;
- DPM++ 2M / Karras;
- denoise 1.0;
- seed 0;
- low-VRAM / reserve 1 GB.

No download is allowed. Runner70 reuses the verified Runner69 payload.

Runner70 PASS requires:

1. one plank becomes a true narrow opening/background continuation;
2. no bright/shiny replacement strip appears;
3. neighboring boards/hardware remain coherent;
4. strap center disappears and matching aged wood is visible;
5. both external strap ends survive;
6. no replacement/continuous bar appears;
7. unrelated geometry remains source-authoritative.

If Runner70 passes, promote a dedicated `automatic_region_inpaint` route and move to semantic multi-reference role separation before Character Lab.

If Runner70 fails, SDXL Inpainting is exhausted fairly. Preserve Runner69/70 evidence, remove the provisional ~12.1 GB SDXL payload under cleanup policy, and test the next dedicated mask-native backend behind the accepted masks. Do not add arbitrary extra step/prompt tuning.

## Current perception payload

Grounding DINO Tiny:

- `IDEA-Research/grounding-dino-tiny`;
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`;
- SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`;
- Apache-2.0.

SAM2.1 Hiera Small:

- `facebook/sam2.1-hiera-small`;
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`;
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`;
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
- keep Qwen2511 + shared Qwen2.5-VL + Qwen VAE as semantic editor;
- keep Grounding DINO Tiny + SAM2.1 while automatic perception remains active;
- Runner66 deterministic processor remains project code;
- keep SDXL Inpainting/Base payload through Runner70 because Runner69 was resolution-confounded;
- if Runner70 fails, preserve evidence then remove the ~12.1 GB SDXL payload before testing another inpainting backend.
