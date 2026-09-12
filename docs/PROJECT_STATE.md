# Roguelite — Current Project State

Status date: **2026-09-12**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER72_POWERPAINT_OBJECT_REMOVAL_2026-09-12.md`
4. `docs/RUNNER71_BIG_LAMA_OBJECT_REMOVAL_2026-09-11.md`
5. `docs/RUNNER70_SDXL_INPAINT_1024_PARITY_2026-09-11.md`
6. `docs/RUNNER68_QWEN2511_LATENT_MASK_REGION_EDIT_2026-09-11.md`
7. `docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`
8. `docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`
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
- SDXL evidence: `Z:\AI\SDXLInpaint`
- Big-LaMa evidence/workspace: `Z:\AI\LaMaInpaint`
- PowerPaint: `Z:\AI\PowerPaint`
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
- no OOM.

Routable:

- `text_to_image`
- `interactive_concept`

Not routable for production precision editing; Runners57/58 closed that role.

## FLUX.2 Klein 4B Base — retained training/base branch

Runner60 fixed the Base graph and proved healthy parity. Runner61 proved atomic/sequential edits remain too coarse.

Retain for T2I/base research and future project LoRA/fine-tuning. Do not route exact component edits to it.

## Qwen-Image-Edit-2511 — installed semantic editor

Installed and technically proven on RTX 3060 12 GB.

Keep for:

- higher-level semantic revision;
- appearance/reference-driven editing;
- future Character Lab multi-reference role tests.

Do not route exact component removal/fill to Qwen. Runner68 proved native mask containment but semantic near-no-op inside the mask:

- plank inside-allowed >Delta12 `0.059154`;
- strap inside-allowed >Delta12 `0.052066`;
- outside >Delta12 `0.0`.

Qwen2509 remains retired/deleted with evidence preserved.

## Precision-control architecture — ACCEPTED THROUGH MASK/COMPOSITOR

Canonical precision architecture:

`semantic request -> parent/component perception -> automatic segmentation/decomposition -> operation-specific mask -> specialized regional backend -> deterministic full-resolution composite`.

No user-drawn production mask/box is allowed.

### Runner64

Flat full-image localization failed, but deterministic regional compositor proved exact outside-region preservation.

### Runner65

Hierarchical localization passed for parent door and lower-right strap. Plank request reduced to the correct repeated left leaf.

### Runner66 — STRUCTURAL PERCEPTION PASS

Project-owned repeated-element decomposition resolved one actual board:

- seam peaks `x=358`, `x=388`;
- selected interval `[358,388]`;
- width `30 px`;
- bbox `[358,295,388,644]`;
- area relative to parent `0.08923`;
- vertical aspect `11.633`;
- elapsed `0.321 s`.

Visual: **PASS — exactly one plank**.

Runner65 strap mask remains visually correct.

Accepted precision components:

1. semantic hierarchy;
2. Grounding DINO parent/component localization where appropriate;
3. SAM2.1 box-prompt segmentation;
4. project-owned repeated-element decomposition;
5. operation-aware automatic submask derivation;
6. deterministic full-resolution composite.

The only unresolved component in this gate is the specialist that actually executes physical removal behind a correct mask.

## Qwen regional precision branch — CLOSED

Runner67 rejected colored locator conditioning because the guide leaked into the image.

Runner68 used native latent masking. Exact containment passed, but Qwen remained semantically too conservative to remove the plank or break the strap.

Final role: semantic/reference editor, not exact mask-native remover.

## SDXL Inpainting 0.1 branch — EXHAUSTED / PAYLOAD REMOVED

Runner69 showed strong masked response but wrong reconstruction on tiny crops.

Runner70 removed the resolution confound with source-authoritative `512x512` contexts upscaled jointly to `1024x1024` before inference.

Runner70 final evidence:

### Plank

- elapsed `34.071 s`;
- inside-allowed >Delta12 `0.316580`;
- outside >Delta12 `0.0`;
- visual: board remained present; local retexturing/deformation instead of a real opening.

### Strap

- elapsed `26.069 s`;
- inside-allowed >Delta12 `0.165934`;
- outside >Delta12 `0.0`;
- visual: strap remained structurally continuous.

Classification:

**TECHNICAL PASS / 1024 PARITY PASS / MASK+COMPOSITOR PASS / VISUAL OPERATION FAIL / SDXL INPAINTING EXHAUSTED.**

Runner69/70 generated evidence remains under `Z:\AI\SDXLInpaint`. Runner71 removed the SDXL Inpainting UNet and SDXL Base checkpoint only after exact-hash verification.

## Runner71 — Big-LaMa / COMPLETE FAIL FOR EXACT REMOVAL

Canonical record:

`docs/RUNNER71_BIG_LAMA_OBJECT_REMOVAL_2026-09-11.md`

Pinned model:

- `big-lama.pt`;
- bytes `205803670`;
- SHA256 `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`.

Technical result:

- all four tight/expanded jobs completed on CUDA;
- total gate time `7.478 s`;
- deterministic outside-region change >Delta12 remained `0.0`.

Metrics:

- plank tight inside >Delta12 `0.275328`;
- plank expanded `0.276856`;
- strap tight `0.125950`;
- strap expanded `0.156337`.

Visual verdict:

- plank: Big-LaMa reconstructed local door/wood continuity rather than an empty one-board opening;
- strap: it reconstructed/smoothed local ferrage rather than a clean absent middle section exposing wood;
- tight vs expanded masks did not change the semantic conclusion.

Classification:

**TECHNICAL PASS / VERY FAST / MASK+COMPOSITOR PASS / VISUAL OBJECT-REMOVAL FAIL.**

Big-LaMa is not routable as exact object remover. Runner72 preserves its evidence and removes the model only by exact-hash verification.

## CURRENT IMPLEMENTATION GATE — RUNNER72 / PowerPaint v2.1 task-conditioned object removal

Canonical record:

`docs/RUNNER72_POWERPAINT_OBJECT_REMOVAL_2026-09-12.md`

Runner:

`tools/structured-2d-character-pipeline/72_bootstrap_and_run_powerpaint_object_removal.ps1`

Adapter:

`tools/roguelite-asset-studio/powerpaint_brushnet_adapter.py`

Executor:

`tools/roguelite-asset-studio/powerpaint_object_removal_gate.py`

Portable dependency launcher:

`tools/roguelite-asset-studio/python_overlay_launcher.py`

### Why this is a different hypothesis

Big-LaMa is blind context completion. PowerPaint has learned task modes. In `object removal`, the pinned native ComfyUI implementation uses learned `P_ctxt` positive and `P_obj` negative task conditioning.

Runner72 therefore tests whether explicit removal semantics prevent the backend from simply rebuilding the object that the mask erased.

### Runtime isolation — FIRST PREFLIGHT FIXED

Reuse ComfyUI code at:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

Pin custom node:

`nullquant/ComfyUI-BrushNet@505d8ef917ddf3896afd1926770ecc9b099704e2`

The first Runner72 bootstrap attempted `venv --system-site-packages`. The venv interpreter did not inherit Torch from the Windows embedded Python and failed before any multi-GB model download with:

`ModuleNotFoundError: No module named 'torch'`

This was an integration/preflight failure, not a model verdict. The venv strategy is retired.

Corrected isolation:

- keep the proven embedded Python/Torch runtime unchanged;
- install only Runner72-specific version overrides under `Z:\AI\PowerPaint\pydeps` using `pip --target --no-deps`;
- prepend that directory explicitly to `sys.path` through `python_overlay_launcher.py` for the ComfyUI and executor processes only;
- do not rely on `PYTHONPATH`, because embedded Python `_pth` isolation can ignore it;
- delete only the failed Runner72-owned `Z:\AI\PowerPaint\venv`;
- do **not** downgrade or modify Qwen portable site-packages.

Pinned process-local overlay:

- `diffusers==0.29.2`;
- `accelerate==0.31.0`;
- `peft==0.11.1`.

The runner independently confirms that the base embedded interpreter imports Torch, then asserts all three exact overlay versions before any model download.

### New payload

SD1.5 base:

- `v1-5-pruned-emaonly.safetensors`;
- bytes `4265146304`;
- SHA256 `6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa`.

PowerPaint v2.1 BrushNet:

- bytes `3544366408`;
- SHA256 `530f2886ef5bcdf199269ec344155a517639ba64219b85eeb23fd86aab93147f`.

PowerPaint learned text encoder:

- bytes `492401329`;
- SHA256 `73709b4360ca06ef990a67d090e8d81a4310943d67a88845653fc4e9f7f26b65`.

SD1.5 FP16 CLIP:

- bytes `246144864`;
- SHA256 `77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e`.

Total new model payload: approximately `8.55 GB`.

### Matrix

Exact Runner71 source contexts and masks are reused:

- plank / tight;
- plank / expanded;
- strap / tight;
- strap / expanded.

Recipe:

- PowerPaint function `object removal`;
- fitting `1.0`;
- BrushNet scale `1.0`;
- `save_memory=max`;
- 20 steps;
- CFG `7.5`;
- Euler / normal;
- denoise `1.0`;
- seed `0`.

Runner72 PASS requires at least one variant per hard operation:

1. one actual plank disappears and becomes a narrow opening/background continuation;
2. the central strap section disappears and underlying aged wood is visible;
3. external strap ends survive;
4. unrelated source geometry remains source-authoritative.

If Runner72 passes, promote `automatic_region_object_removal` and move to semantic multi-reference role separation before Character Lab.

If Runner72 fails, preserve evidence, clean the provisional PowerPaint payload and replace only the removal backend. Do not reopen perception/masks/compositor or return to manual masks.

## Current perception payload

Grounding DINO Tiny:

- Apache-2.0;
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`;
- SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`.

SAM2.1 Hiera Small:

- Apache-2.0;
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`;
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`.

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
- keep Runner66 deterministic processor as project code;
- SDXL model payload is removed; preserve Runner69/70 generated evidence;
- Big-LaMa model is rejected and may already be removed by the first Runner72 verified cleanup; preserve Runner71 evidence;
- delete the failed Runner72-owned legacy `venv`; use process-local `pydeps` overlay instead;
- keep PowerPaint payload only if Runner72 proves a useful production role.

## Immediate implementation order

1. rerun corrected Runner72 and review task-conditioned object-removal results;
2. if both hard operations pass, promote `automatic_region_object_removal`;
3. validate semantic multi-reference role separation with the installed Qwen semantic editor;
4. validate reopened Exilada as first difficult Character Lab case;
5. validate another non-character asset class;
6. expose approved adapters through the generic Studio UI/state/candidate/history/approval layer;
7. wrap proven H3 Ref2VA behind the same orchestration boundary;
8. resume final rendering-language/pixel-art specialization from approved masters.