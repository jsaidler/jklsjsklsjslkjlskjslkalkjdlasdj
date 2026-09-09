# Roguelite — Current Project State

Status date: **2026-09-09**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/ROGUELITE_ASSET_STUDIO.md`
3. `docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`
4. `docs/RUNNER60_FLUX2_KLEIN_BASE_OFFICIAL_PARITY_2026-09-09.md`
5. `docs/RUNNER58_FLUX2_KLEIN_EDIT_STRENGTH_CALIBRATION_2026-09-09.md`
6. `docs/VISUAL_DIRECTION.md`
7. `docs/CHARACTERS.md`
8. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
9. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Historical screening/spike docs remain evidence but do not override the current gate.

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

The router/adapter boundary is UI-independent.

## Proven static baseline — FLUX.2 Klein 4B distilled

Runner56 proved fast local T2I on the RTX 3060 12 GB workstation:

- 768×768;
- 4 steps;
- CFG 1.0;
- Euler;
- seed 0;
- elapsed 12.054 s;
- coherent architecture-module authoring master;
- no OOM/runtime failure.

Runners57/58 proved that distilled single/multi-reference graphs execute technically, but **failed the production edit-strength/obedience gate**. More steps increased broad re-rendering/material drift without reliably executing explicit structural facts. Secondary material-reference authority remained weak.

Therefore distilled 4B remains:

- **ACTIVE** for `text_to_image` / `interactive_concept`;
- **NOT ROUTABLE** for production structural/reference editing.

Do not keep increasing distilled steps without a new technical hypothesis.

## FLUX.2 Klein 4B Base — current same-family edit branch

Installed files:

- `flux-2-klein-base-4b-fp8.safetensors`
  - SHA256 `44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840`
- `qwen_3_4b.safetensors`
  - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
- `full_encoder_small_decoder.safetensors`
  - SHA256 `ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62`

Runtime remains the isolated ComfyUI at commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

### Runner59 — hardware PASS / visual verdict INVALID

Runner59 proved that Base runs at 20/50 steps on the 3060 12 GB without OOM, but all outputs showed severe cyan/posterized drift.

Post-run comparison with the current official Base graph found recipe mismatches:

- Runner59 reused `ConditioningZeroOut(positive)` instead of a separate empty negative `CLIPTextEncode` at CFG 5;
- Runner59 fixed edit geometry at 768×768 instead of deriving geometry from the first reference scaled to 1 MP.

Therefore Runner59 is retained as hardware evidence only and is **not** a model-quality verdict.

### Runner60 — official-parity diagnostic PASS / visual PARTIAL

Canonical record:

`docs/RUNNER60_FLUX2_KLEIN_BASE_OFFICIAL_PARITY_2026-09-09.md`

Runner60 corrected the Base graph to match the official semantics:

- positive `CLIPTextEncode(prompt)`;
- separate negative `CLIPTextEncode("")`;
- references scaled with `ImageScaleToTotalPixels`, `nearest-exact`, 1 MP;
- same reference latent appended to positive and negative branches;
- scheduler/latent geometry derived from first scaled reference;
- Euler;
- CFG 5;
- 20 steps.

Actual Runner60 results:

#### VAE diagnostics

Base small-decoder round-trip:

- 1024×1024;
- elapsed 2.150 s;
- mean absolute luma difference vs original: **2.3844**;
- changed ratio >24: **0.005635**.

Full FLUX.2 VAE control:

- 1024×1024;
- elapsed 2.028 s;
- mean absolute luma difference: **2.6061**;
- changed ratio >24: **0.005726**.

Conclusion: **the Base VAE path is sane**. Runner59 cyan was not a VAE incompatibility.

#### Base T2I control

- 1024×1024;
- 20 steps / CFG 5 / Euler;
- elapsed 70.162 s;
- natural gray/brown/green color balance;
- coherent isolated gate.

Conclusion: **Base model/sampling integration is sane**.

#### Base single-reference edit

- elapsed 148.360 s;
- natural color restored;
- recognizable gate/camera preserved;
- substantial upper-masonry/material revision occurred;
- compound request was only partially obeyed: missing-plank + missing-capstone + broken-strap facts were not all unambiguous.

#### Base multi-reference edit

- elapsed 248.745 s;
- source identity/camera preserved strongly;
- some separate material language imported;
- explicit structural facts remained too conservative/incomplete.

Runner60 contact-sheet SHA256:

`5daa35952c6d8c5564c042174426a1679d4cf1ffb51836ffe159927bb421a404`

### Runner60 conclusion

The cyan/posterization hypothesis is closed: it was a recipe mismatch.

The Base model is **not rejected**. It demonstrates materially stronger edit behavior than distilled but does not yet pass the compound structural-edit contract.

The remaining same-family hypothesis is **instruction decomposition / iterative atomic editing**.

## CURRENT IMPLEMENTATION GATE — Runner61 / Base atomic + sequential edit

Canonical record:

`docs/RUNNER61_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE_2026-09-09.md`

Runner:

`tools/structured-2d-character-pipeline/61_run_flux2_klein_base_atomic_sequence_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_base_atomic_sequence_gate.py`

Runner61 downloads **nothing** and reuses the exact Runner60 parity-valid adapter/runtime.

### Independent atomic tests

Each starts from the original gate and requests only one structural fact:

1. remove one entire full-height plank from the left door leaf;
2. remove one large top-left capstone/lintel mass;
3. break and partially remove the lower iron strap on the right door leaf.

This isolates command obedience from multi-instruction prompt competition.

### Sequential chain

- Stage 1: original -> missing plank;
- Stage 2: preserve missing plank -> remove top-left capstone;
- Stage 3: preserve both -> break lower-right strap;
- Stage 4: preserve all accumulated geometry + import severe material language from the Runner58 decay board.

### Runner61 decision

If independent atomic edits work and the sequential chain preserves earlier edits, Base can be exposed as an **iterative structural editor** even if one-shot compound edits remain unsupported.

If atomic edits themselves remain unreliable, the Base strong structural-edit hypothesis is considered exhausted. Then:

- distilled remains the fast T2I/concept backend;
- Base remains useful for future LoRA/project specialization research;
- strong structural/reference editing moves to the next specialized editor candidate, currently Qwen-Image-Edit-2509 under a controlled low-VRAM feasibility spike.

## Model router authority

Machine-readable authority:

`tools/roguelite-asset-studio/model_registry.json`

Current Base status:

`installed_runner60_parity_valid_atomic_gate_pending`

Qwen-Image-Edit is **not yet downloaded**. Do not move to it before Runner61 yields a visual verdict.

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

MiniMax H3 FL2VA remains a future temporal candidate for environmental loops/VFX/first-last-frame tasks and must be validated per asset class.

## FLUX.1 Kontext [dev] — R&D ONLY

Existing Kontext remains useful for reconstruction/edit R&D. Its dev license prevents silently making it the commercial-production default without appropriate licensing.

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

## Environment/map production — LOCKED

Prefer modular independently useful pieces over one flattened AI-painted gameplay map: terrain patches, walls/cliffs, architecture modules, doors/gates, vegetation, rocks/debris, props, foreground/background set pieces, loops and damage-state variants.

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
- keep proven Klein distilled runtime;
- keep installed Klein Base FP8 + small-decoder VAE while Runner61 is active;
- do **not** download Qwen-Image-Edit or Step1X before the Base atomic hypothesis is resolved;
- remove rejected payloads only after evidence/manifests are preserved and a branch is explicitly abandoned.
