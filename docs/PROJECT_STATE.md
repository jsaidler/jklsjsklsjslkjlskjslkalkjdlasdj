# Roguelite — Current Project State

Status date: **2026-09-11**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER71_BIG_LAMA_OBJECT_REMOVAL_2026-09-11.md`
4. `docs/RUNNER70_SDXL_INPAINT_1024_PARITY_2026-09-11.md`
5. `docs/RUNNER69_SDXL_INPAINT_PRECISION_2026-09-11.md`
6. `docs/RUNNER68_QWEN2511_LATENT_MASK_REGION_EDIT_2026-09-11.md`
7. `docs/RUNNER67_QWEN2511_ATOMIC_REGION_EDIT_2026-09-11.md`
8. `docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`
9. `docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`
10. `docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`
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
- SDXL evidence: `Z:\AI\SDXLInpaint`
- Big-LaMa: `Z:\AI\LaMaInpaint`
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

The uncertainty is now only which specialist should execute a physical remove/fill operation behind those accepted masks.

## Qwen regional precision branch — CLOSED

Runner67 rejected colored visual locator conditioning because the guide leaked into the output.

Runner68 removed the colored guide and used native latent masking. Containment passed perfectly, but Qwen remained semantically too conservative to remove the plank or break the strap.

Final role: semantic editor, not exact mask-native remover.

## SDXL Inpainting 0.1 branch — EXHAUSTED

### Runner69 — subtraining-resolution test

Technical pass. Strong local response, perfect deterministic containment, wrong semantics:

- plank `256x512`, inside-allowed >Delta12 `0.539487`, shiny/vertical reconstruction artifact;
- strap `384x256`, inside-allowed >Delta12 `0.336265`, no clean central break;
- outside >Delta12 `0.0`.

Because SDXL Inpainting 0.1 was trained at 1024×1024, this was not used as the final verdict.

### Runner70 — 1024 training-resolution parity / FINAL VERDICT

Same masks and semantics, source-authoritative `512x512` context upscaled jointly with mask to `1024x1024`, same sampler/steps/CFG, then deterministic downsample/composite.

Plank:

- elapsed `34.071 s`;
- inside-allowed >Delta12 `0.316580`;
- outside >Delta12 `0.0`;
- visual: board remained present; local retexturing/deformation instead of a real opening.

Strap:

- elapsed `26.069 s`;
- inside-allowed >Delta12 `0.165934`;
- outside >Delta12 `0.0`;
- visual: strap remained structurally continuous.

Classification:

**TECHNICAL PASS / 1024 PARITY PASS / MASK+COMPOSITOR PASS / VISUAL OPERATION FAIL / SDXL INPAINTING EXHAUSTED.**

Do not add more arbitrary SDXL prompt/step tuning for this role.

Runner69/70 evidence is preserved under `Z:\AI\SDXLInpaint`. Runner71 removes the SDXL Inpainting UNet and SDXL Base checkpoint only after evidence validation and exact hash verification.

## CURRENT IMPLEMENTATION GATE — RUNNER71 / Big-LaMa object removal

Canonical record:

`docs/RUNNER71_BIG_LAMA_OBJECT_REMOVAL_2026-09-11.md`

Runner:

`tools/structured-2d-character-pipeline/71_bootstrap_and_run_big_lama_object_removal.ps1`

Adapter:

`tools/roguelite-asset-studio/lama_inpaint_adapter.py`

Executor:

`tools/roguelite-asset-studio/lama_object_removal_gate.py`

Hypothesis:

The current hard operations are fundamentally object removal/background continuation. Test a specialist that does not interpret prompt semantics and only receives the already-approved automatic mask.

Pinned model:

- upstream release: `enesmsahin/simple-lama-inpainting v0.1.0`;
- file: `big-lama.pt`;
- bytes: `205803670`;
- SHA256: `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`;
- Apache-2.0 LaMa lineage;
- TorchScript executable artifact: load only the pinned size/hash.

Runtime:

- direct `torch.jit.load` using existing embedded PyTorch;
- no ComfyUI server;
- CUDA when available;
- `512x512` source-authoritative contexts from Runner70;
- four cheap jobs: plank tight/expanded mask boundary, strap tight/expanded mask boundary.

Runner71 PASS requires at least one variant per task:

1. atomic plank actually disappears and reads as an opening/background continuation;
2. central strap section actually disappears and underlying aged door/wood is plausible;
3. outside strap ends survive;
4. unrelated geometry remains source-authoritative.

If Runner71 passes, promote `automatic_region_object_removal` as a lightweight specialist and keep prompt-driven semantic fill as a separate route.

If Runner71 fails, retain the accepted perception/mask/compositor architecture and replace only the removal backend.

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
- Runner69/70 SDXL generated evidence remains preserved;
- Runner71 removes the retired SDXL model payload before downloading Big-LaMa;
- keep Big-LaMa only if its object-removal gate is visually useful.
