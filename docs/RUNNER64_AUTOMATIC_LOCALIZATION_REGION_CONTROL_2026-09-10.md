# Runner64 — Automatic localization + region-control gate

Status date: **2026-09-10**

Status: **PREPARED / CURRENT GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner64 exists

Runner63 proved Qwen-Image-Edit-2511 technically viable on RTX 3060 12 GB and showed a meaningful improvement on the one-plank task, but failed the one-strap task badly: the model created a large replacement bar spanning the lower door region instead of breaking only the named lower-right strap.

That result closes the useful hypothesis of obtaining production-grade subcomponent precision from a global natural-language edit alone. More blind prompt/step tuning is not allowed.

The new hypothesis is architectural:

`semantic target -> automatic localization -> automatic segmentation -> contextual regional edit -> deterministic regional composite`

No user-drawn mask, manual box, repainting or per-asset retouching is part of the production contract.

## Perception stack

### Grounding DINO Tiny

Role: open-vocabulary text-grounded detection.

Model:

`IDEA-Research/grounding-dino-tiny`

Pinned revision:

`a2bb814dd30d776dcf7e30523b00659f4f141c71`

Safetensors SHA256:

`1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`

Approximate weight payload: 689 MB.

License: Apache-2.0.

### SAM2.1 Hiera Small

Role: convert the selected text-grounded box into a precise component mask.

Model:

`facebook/sam2.1-hiera-small`

Pinned revision:

`e07df6aa19f5c6545121551bf89957b7663ee715`

Safetensors:

- bytes: `184305280`
- SHA256: `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`

License: Apache-2.0.

Total new perception weights are under ~0.9 GB plus small processor/config files.

## Why SAM3.1 is not the first localization dependency

SAM3.1 is a stronger 2026 concept-segmentation candidate and supports text/exemplar/visual prompts directly. However its official checkpoint is gated and ~3.5 GB, while Runner64 only needs to prove the architecture. GroundingDINO + SAM2.1 are public, Apache-2.0, compact and sufficient for this first automatic-localization gate.

SAM3.1 may later replace the perception pair behind the same localizer interface if it materially improves difficult target selection.

## Runtime sequencing / VRAM

Target workstation remains Windows 11 / RTX 3060 12 GB / 48 GB RAM.

Perception runs **before** the Qwen ComfyUI server:

1. Grounding DINO runs and exits;
2. SAM2.1 runs and exits;
3. CUDA cache/process memory is released;
4. Qwen2511 ComfyUI starts with the already-proven low-VRAM recipe.

The perception models therefore do not compete with Qwen2511 for VRAM during generation.

## Automatic target selection

Runner64 tests two reusable selector classes:

### Plank

Text phrases include:

- `vertical wooden plank`
- `wooden door plank`
- `vertical wooden board`

Selector preference:

- vertical aspect;
- left side;
- middle door zone;
- reject excessively large regions.

### Strap

Text phrases include:

- `horizontal iron strap`
- `metal door strap`
- `horizontal iron hinge`

Selector preference:

- horizontal aspect;
- right side;
- lower door zone;
- reject excessively large regions.

Every candidate box, detector score, selector score and chosen target is written to the localization manifest. This is important: the system must be auditable and cannot silently pretend that a wrong automatic mask is a model-edit failure.

## Segmentation

The selected Grounding DINO box becomes the SAM2.1 box prompt. The highest-IoU mask is retained.

Outputs include:

- all-candidate detection image;
- selected mask;
- mask overlay;
- contextual crop;
- crop mask;
- JSON provenance.

No mask is drawn by the user.

## Regional Qwen2511 edit

The already-installed Qwen-Image-Edit-2511 FP8mixed remains the editor.

For each task it receives:

1. Image 1 = contextual crop from the original;
2. Image 2 = the same crop with an automatically generated red translucent locator overlay.

The prompt explicitly defines Image 2 as a locator only and forbids copying the red overlay.

Recipe stays at the efficient validated regime:

- 20 steps;
- CFG 4;
- Euler/simple;
- AuraFlow shift 3.1;
- CFGNorm 1;
- `index_timestep_zero` reference method;
- Qwen2.5-VL encoder on CPU;
- ComfyUI `--lowvram`.

Runner63 showed that 40 steps did not solve the hard localization problem, so Runner64 does not spend another ~2× runtime on that variable.

## Deterministic regional composite

The Qwen crop result is resized back to the original crop geometry.

The automatic SAM2 mask is deterministically dilated and feathered to allow reconstruction around removed/broken edges. The edited crop is then composited back onto the original.

**Pixels outside that automatically generated allowed region remain sourced from the original image by construction.**

This is the mechanism intended to prevent global side effects such as Runner63's giant replacement bar.

## Files

Automatic localizer:

`tools/roguelite-asset-studio/automatic_region_localizer.py`

Regional editor/compositor:

`tools/roguelite-asset-studio/qwen2511_region_control_gate.py`

Runner:

`tools/structured-2d-character-pipeline/64_bootstrap_and_run_automatic_region_control.ps1`

Localization root:

`Z:\AI\RogueliteAssetStudio\localization\runner64_gate`

Regional output root:

`Z:\AI\QwenImageEdit\automatic_region_control`

Expected final outputs:

- `plank_region_controlled_final.png`
- `strap_region_controlled_final.png`
- `runner64_automatic_region_control_contact_sheet.png`
- `runner64_automatic_region_control_manifest.json`

## PASS criteria

Technical PASS requires:

- Grounding DINO and SAM2.1 run locally;
- both target boxes/masks are produced automatically;
- Qwen2511 completes both crop edits;
- deterministic composites and manifests are written;
- no user-drawn mask/box is used.

Visual PASS requires both layers to pass:

1. **perception:** selected boxes/masks correspond to the intended plank and intended lower-right strap;
2. **edit:** final outputs execute the requested one-component change and preserve unrelated full-image geometry.

If localization fails, improve/replace the perception layer without blaming Qwen.

If localization is correct but the crop edit still fails semantically, evaluate a region-aware/inpainting editor behind the same mask contract.

If Runner64 passes, `automatic_region_edit` becomes a routable Asset Studio capability and the architecture can proceed to semantic multi-reference roles and the Exilada Character Lab without requiring manual masks.
