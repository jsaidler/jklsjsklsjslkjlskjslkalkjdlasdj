# Roguelite — Current Project State

Status date: **2026-09-11**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`
4. `docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`
5. `docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`
6. `docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`
7. `docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`
8. `docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`
9. `docs/VISUAL_DIRECTION.md`
10. `docs/CHARACTERS.md`
11. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
12. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

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

## Runner64 — complete / flat perception failed / compositor validated

Canonical record:

`docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`

Architecture tested:

`semantic target -> Grounding DINO Tiny -> deterministic selector -> SAM2.1 -> contextual Qwen2511 crop edit -> deterministic regional composite`

### Actual result

Runner64 completed technically, including both Qwen crop edits and final composites.

Flat full-image localization failed visually:

- `plank` selected `[62.7451, 540.7537, 329.1651, 704.2875]`, the lower-left **stone pedestal**;
- `strap` selected `[543.9662, 513.4839, 696.7905, 621.7897]`, the lower-right **stone block**.

SAM2 segmented those wrong selected objects with high predicted IoU (`0.92298` and `0.95213`). The Qwen regional semantic result is therefore invalid evidence.

The deterministic compositor did pass its preservation contract:

- plank outside-allowed changed ratio >Δ12 = `0.0`;
- strap outside-allowed changed ratio >Δ12 = `0.0`.

Runner64 final classification:

**TECHNICAL PASS / FLAT SUBCOMPONENT LOCALIZATION FAIL / SAM2-ON-SELECTED-BOX PASS / DETERMINISTIC REGIONAL COMPOSITOR PASS / QWEN REGIONAL VERDICT INVALID.**

No `automatic_region_edit` production route is activated yet.

## Runner65 — complete / hierarchy works / atomic plank still too coarse

Canonical record:

`docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`

Architecture tested:

`full asset -> parent door grounding -> parent crop/upscale -> child component grounding -> SAM2 multi-candidate rerank -> geometry/containment gate -> visual review`

### Actual result

Parent door:

- raw selected box `[311.3596, 272.5457, 547.8800, 649.2131]`;
- expanded box `[292, 253, 567, 669]`;
- visual: **PASS**.

Lower-right strap:

- selected box `[456.0091, 552.5553, 548.3988, 592.1567]`;
- SAM predicted IoU `0.89715`;
- mask area relative to parent `0.01753`;
- full parent containment;
- visual: **PASS**. The mask corresponds to the intended lower-right horizontal iron strap.

Plank:

- selected mask bbox `[325, 285, 422, 651]`;
- SAM predicted IoU `0.96534`;
- mask area relative to parent `0.27724`;
- visual: **FAIL at requested atomic granularity**. The mask is the entire left door leaf, not one plank.

Runner65 final classification:

**TECHNICAL PASS / PARENT PASS / STRAP PASS / REPEATED-STRUCTURE LEAF FOUND / ONE-PLANK GRANULARITY FAIL.**

Important correction: Runner65's `auto_valid=true` for the plank was too permissive. A repeated structure can satisfy orientation/containment heuristics while still being too coarse for an atomic-member request.

This does not yet justify replacing Grounding DINO/SAM2. The semantic hierarchy has already localized the correct repeated structure; the missing operation is decomposition of that structure into one member.

## CURRENT IMPLEMENTATION GATE — RUNNER66 / deterministic repeated-element decomposition

Canonical record:

`docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`

Runner:

`tools/structured-2d-character-pipeline/66_run_repeated_element_decomposition_gate.ps1`

Processor:

`tools/roguelite-asset-studio/repeated_element_decomposer.py`

Architecture:

`Runner65 semantic repeated structure -> persistent oriented seam profile -> atomic intervals -> target-relative member -> deterministic mask -> visual review`

Current proof case:

`door -> left leaf -> vertical board joints -> one plank`

### Why this is the correct next step

Runner65 already found the correct parent and repeated structure. Downloading a larger detector now would discard useful semantic evidence and conflate two different tasks: semantic localization and repeated-member decomposition.

Runner66 therefore adds a deterministic structural processor behind the perception stack. The production concept generalizes to repeated slats, bars, ribs, panels, boards, fence elements, repeated armor plates and similar structures.

### Runner66 rules

- **No Qwen inference.** Do not spend another 20-step generation until perception/structure passes.
- **No model inference at all.** Runner66 consumes Runner65 evidence only.
- **No download.** It uses PIL/NumPy and existing files.
- Persistent vertical seam energy is computed across the Runner65 left-leaf mask.
- Detected internal seams plus leaf boundaries define atomic candidate intervals.
- Candidate intervals are ranked by target position, seam strength, leaf occupancy and width plausibility.
- The selected interval is intersected deterministically with the Runner65 leaf mask.
- The stricter atomic geometry gate rejects an entire door leaf as one plank.
- Runner65's visually correct strap mask is retained unchanged.
- User draws no box or mask.

Expected output root:

`Z:\AI\RogueliteAssetStudio\localization\runner66_gate`

Required visual PASS:

1. atomic plank mask corresponds to exactly one actual vertical wooden plank;
2. it spans the plank vertically rather than a small patch;
3. unrelated stone/frame areas are excluded;
4. the retained Runner65 strap mask remains on the lower-right iron strap.

Only after Runner66 visual PASS should Qwen2511 regional editing be reintroduced using the valid automatic target regions.

If Runner66 still cannot isolate one repeated member, change the atomic-decomposition/perception backend behind the same no-manual-mask contract. Do not return to global prompt-only editing.

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

Runner66 adds no model payload.

## Future perception candidate — not active

A stronger concept/visual grounding or dense-correspondence backend may replace/augment the compact pair later if semantic hierarchy plus repeated-element decomposition still cannot isolate difficult parts. Do not add that payload speculatively before Runner66 evidence exists.

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
- Runner66 adds no checkpoint and only deterministic evidence;
- do not download another precision editor or larger perception model until Runner66 is reviewed.
