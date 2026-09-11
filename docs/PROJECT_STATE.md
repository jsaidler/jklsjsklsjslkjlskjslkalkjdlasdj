# Roguelite — Current Project State

Status date: **2026-09-11**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`
4. `docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`
5. `docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`
6. `docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`
7. `docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`
8. `docs/VISUAL_DIRECTION.md`
9. `docs/CHARACTERS.md`
10. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
11. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Historical spike documents remain evidence but do not override the current gate.

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

`Studio UI -> asset spec/state -> model router -> specialized model/perception adapters -> local runtimes -> deterministic processing -> candidate/version store -> explicit approval -> runtime export`

It must cover playable characters, NPCs, enemies, creatures, bosses, equipment, props, architecture, terrain, vegetation, set pieces, materials, VFX/environment animation and UI art.

Semantic reference roles remain a hard contract: `identity`, `anatomy`, `style`, `material`, `palette`, `structure`, `composition`, `pose`, `motion`, `camera`, `environment`, `previous_approved_state`.

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
- useful architecture authoring master.

Runners57/58 proved reference editing technically but failed production edit strength/obedience.

Routable:

- `text_to_image`
- `interactive_concept`

Not routable:

- production precision/reference editing.

## FLUX.2 Klein 4B Base — precision edit hypothesis exhausted

Runner60 corrected the original Base graph and proved healthy VAE/T2I/edit parity. Runner61 then proved that atomic and sequential requests remain too coarse.

Final role:

- valid Base/T2I research;
- future Roguelite-specific LoRA/fine-tuning;
- coarse concept revision R&D.

Not routable for exact component edits.

## Qwen-Image-Edit-2509 — retired precision candidate

Runner62:

**TECHNICAL PASS / BETTER PRESERVATION THAN KLEIN / EXACT STRUCTURAL FACT FAIL.**

The diffusion checkpoint has been removed after evidence preservation. Shared Qwen2.5-VL encoder and Qwen VAE remain because 2511 uses them.

## Qwen-Image-Edit-2511 — strongest installed semantic editor / global precision partial

Canonical record:

`docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`

Runtime:

- `qwen_image_edit_2511_fp8mixed.safetensors`
- 20,533,762,817 bytes
- SHA256 `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`
- Qwen2.5-VL 7B FP8 on CPU;
- `--lowvram`, reserve 1 GB;
- AuraFlow shift 3.1;
- CFGNorm 1;
- Euler/simple, CFG 4.

### Runner63 actual result

Technical matrix completed successfully on RTX 3060 12 GB.

Plank:

- 20 steps: 401.095 s, changed ratio >24 `0.018129`;
- 40 steps: 691.408 s, changed ratio >24 `0.018307`;
- visual: meaningful improvement; a narrow vertical gap is produced with strong source preservation.

Strap:

- 20 steps: 375.293 s, changed ratio >24 `0.014082`;
- 40 steps: 777.197 s, changed ratio >24 `0.013060`;
- visual: FAIL at both settings; a large replacement/transverse bar is created instead of breaking only the named lower-right strap.

Runner63 final classification:

**TECHNICAL PASS / PLANK IMPROVED / STRAP PRECISION FAIL / GLOBAL-PROMPT-ONLY PRECISION HYPOTHESIS CLOSED.**

Do not add more blind 2511 step/prompt tests. Keep Qwen2511 installed as the current strongest semantic editor, but precision must be supplied by control architecture rather than unrestricted global prompting.

## Runner64 — complete / perception failed / compositor validated

Canonical record:

`docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`

Architecture tested:

`semantic target -> Grounding DINO Tiny -> deterministic selector -> SAM2.1 -> contextual Qwen2511 crop edit -> deterministic regional composite`

### Actual result

Runner64 completed technically, including both Qwen crop edits and final composites.

However visual review proved that flat full-image subcomponent localization failed:

- `plank` selected `[62.7451, 540.7537, 329.1651, 704.2875]`, the lower-left **stone pedestal**, not a wooden plank;
- `strap` selected `[543.9662, 513.4839, 696.7905, 621.7897]`, the lower-right **stone block**, not the iron strap.

SAM2 then segmented those wrong objects with high predicted IoU (`0.92298` and `0.95213`). This is a target-localization failure, not a SAM execution failure.

The regional Qwen semantic result is **invalid evidence** because Qwen received incorrect targets.

The deterministic compositor did pass its preservation contract:

- plank outside-allowed changed ratio >Δ12 = `0.0`;
- strap outside-allowed changed ratio >Δ12 = `0.0`.

Runner64 final classification:

**TECHNICAL PASS / FLAT SUBCOMPONENT LOCALIZATION FAIL / SAM2-ON-SELECTED-BOX PASS / DETERMINISTIC REGIONAL COMPOSITOR PASS / QWEN REGIONAL VERDICT INVALID.**

No `automatic_region_edit` production route is activated yet.

## CURRENT IMPLEMENTATION GATE — RUNNER65 / hierarchical perception only

Canonical record:

`docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`

Runner:

`tools/structured-2d-character-pipeline/65_run_hierarchical_localization_gate.ps1`

Localizer:

`tools/roguelite-asset-studio/hierarchical_region_localizer.py`

Architecture:

`full asset -> parent door grounding -> parent crop/upscale -> child component grounding -> SAM2 multi-candidate rerank -> visual review`

### Why this is the correct next step

Runner64 failed because the small component was searched directly against the entire gateway and the spatial heuristic rewarded side/lower stone blocks. The next hypothesis keeps the same public compact models but gives the task the missing hierarchy: locate the parent first, then the component inside it.

This exhausts the existing perception stack more responsibly before downloading or switching to a larger detector/segmenter.

### Runner65 rules

- **No Qwen inference.** Do not spend another ~12 minutes per crop until perception itself passes.
- **No new model download.** Reuse Runner64 Grounding DINO Tiny + SAM2.1 cache.
- Hugging Face/Transformers are run offline for this gate.
- Parent object is localized first from the full image.
- Parent crop is upscaled to long side 1280 for component detection.
- Component Grounding DINO thresholds are lowered to improve recall.
- Up to ten component proposals are passed through SAM2.
- Final reranking uses SAM IoU, parent containment, mask aspect, mask area and parent-relative side/vertical zone.
- Geometry validation is fail-closed: an implausible mask is not silently accepted.
- User draws no boxes or masks.

Expected output root:

`Z:\AI\RogueliteAssetStudio\localization\runner65_gate`

Required visual PASS:

1. parent box corresponds to the wooden double door rather than the entire gateway;
2. plank mask corresponds to one actual vertical wooden plank;
3. strap mask corresponds to the intended lower-right horizontal iron strap;
4. neither mask selects stone pedestal/frame regions.

Only after those pass should the regional Qwen phase be reintroduced using Runner65's automatic masks/crops.

If Runner65 still fails, the next branch is a stronger **perception backend** behind the same parent/component contract, not more Qwen prompt tuning and not manual masking.

## Current perception payload

Grounding DINO Tiny:

- `IDEA-Research/grounding-dino-tiny`
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`
- safetensors SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`
- Apache-2.0.

SAM2.1 Hiera Small:

- `facebook/sam2.1-hiera-small`
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`
- safetensors SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`
- Apache-2.0.

## Future perception candidate — not active

A stronger concept/visual grounding backend may replace the compact pair later if Runner65 shows that hierarchy still cannot isolate difficult small parts. Do not add that payload speculatively before Runner65 evidence exists.

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

The old 128px Exilada baseline is retired. There is no universal 160/180/200/192/384px production sprite resolution.

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
- Qwen2509 diffusion is retired/deleted; preserve generated evidence;
- keep Qwen2511 + shared Qwen2.5-VL + Qwen VAE;
- keep Runner64/65 compact perception models/cache while the localization hypothesis remains active;
- do not download another precision editor or larger perception model until Runner65 is reviewed.
