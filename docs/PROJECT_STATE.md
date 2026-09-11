# Roguelite — Current Project State

Status date: **2026-09-11**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`
4. `docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`
5. `docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`
6. `docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`
7. `docs/VISUAL_DIRECTION.md`
8. `docs/CHARACTERS.md`
9. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
10. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

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

`Studio UI -> asset spec/state -> model router -> specialized adapters -> local runtimes -> deterministic processing -> candidate/version store -> explicit approval -> runtime export`

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
- visual: clear improvement; a narrow vertical gap is produced and source preservation is strong; still only partial evidence of universal component precision.

Strap:

- 20 steps: 375.293 s, changed ratio >24 `0.014082`;
- 40 steps: 777.197 s, changed ratio >24 `0.013060`;
- visual: FAIL at both settings; instead of breaking only the named lower-right strap, Qwen creates a large replacement/transverse bar across the lower doorway.

Runner63 final classification:

**TECHNICAL PASS / PLANK IMPROVED / STRAP PRECISION FAIL / GLOBAL-PROMPT-ONLY PRECISION HYPOTHESIS CLOSED.**

Do not add more blind 2511 step/prompt tests. Keep Qwen2511 installed as the current strongest semantic editor, but precision must be provided by control architecture rather than unrestricted global prompting.

## CURRENT IMPLEMENTATION GATE — RUNNER64 / automatic localization + region control

Canonical record:

`docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`

Runner:

`tools/structured-2d-character-pipeline/64_bootstrap_and_run_automatic_region_control.ps1`

Perception/localization:

`tools/roguelite-asset-studio/automatic_region_localizer.py`

Regional editor/compositor:

`tools/roguelite-asset-studio/qwen2511_region_control_gate.py`

New architecture:

`semantic target -> Grounding DINO Tiny -> deterministic instance selector -> SAM2.1 Hiera Small -> contextual Qwen2511 crop edit -> deterministic automatic regional composite`

### Hard production rule

The user does **not** draw masks or boxes. Localization/masking is a model/pipeline responsibility.

### New perception payload

Grounding DINO Tiny:

- `IDEA-Research/grounding-dino-tiny`
- pinned revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`
- safetensors SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`
- ~689 MB
- Apache-2.0.

SAM2.1 Hiera Small:

- `facebook/sam2.1-hiera-small`
- pinned revision `e07df6aa19f5c6545121551bf89957b7663ee715`
- 184,305,280-byte safetensors
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`
- Apache-2.0.

Perception runs and exits before Qwen starts, so it does not compete with the large editor for VRAM.

### Runner64 first execution

The first execution reached Qwen ComfyUI startup. Because the launcher only starts ComfyUI after the perception process exits successfully and all expected localization files exist, the following is already proven technically:

**Grounding DINO Tiny + SAM2.1 local localization pipeline = TECHNICAL PASS.**

Visual correctness of the selected plank/strap masks remains pending.

The regional Qwen phase did **not** run. `qwen2511_region_control_gate.py` instantiated `QwenImageEdit2511Adapter` with the nonexistent keyword `timeout_seconds`; the inherited constructor accepts `timeout_minutes`. Python therefore exited with `TypeError` before any Qwen prompt submission. This is a harness/API mismatch, not editor evidence.

Fix is committed: the regional executor now passes `timeout_minutes=args.timeout_minutes`. Existing perception weights/cache/localization outputs are reusable; no model needs to be redownloaded.

Runner64 tests the same plank/strap facts. It persists detector candidates, selected boxes, SAM masks, crops and provenance. Qwen edits only a context crop and receives a second automatically generated target-guide image. Final full-image modification is deterministically constrained to a dilated/feathered automatic mask neighborhood.

PASS requires both automatic perception and exact edit behavior to be useful. A wrong mask is classified as perception failure, not editor failure.

If localization is correct but Qwen still cannot execute the local semantic change, the next editor hypothesis must be a region-aware/inpainting backend behind the same mask contract; no return to manual masking.

## Future perception candidate — SAM3.1

SAM3.1 directly supports text/exemplar/visual prompt segmentation and is a strong later replacement candidate, but its official checkpoint is gated and ~3.5 GB under the SAM License. Do not make it mandatory before the public Apache-2.0 GroundingDINO+SAM2 Runner64 architecture is evaluated.

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
- Qwen2509 diffusion is retired/deleted; preserve its generated evidence;
- keep Qwen2511 + shared Qwen2.5-VL + Qwen VAE;
- keep Runner64 compact perception models/cache while localization hypothesis remains active;
- do not download Step1X while Runner64 is active.
