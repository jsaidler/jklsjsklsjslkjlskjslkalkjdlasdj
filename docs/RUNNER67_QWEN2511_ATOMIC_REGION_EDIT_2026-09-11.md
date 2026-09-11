# Runner67 — Qwen2511 approved automatic atomic-region edit gate

Status date: **2026-09-11**

Status: **PREPARED / CURRENT PRECISION-EDIT GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner67 exists

Runner64 proved that deterministic regional compositing can prevent unrelated full-image drift, but its flat localization selected the wrong objects.

Runner65 fixed semantic hierarchy:

- parent wooden double door: visual PASS;
- lower-right iron strap: visual PASS;
- plank request: correct repeated structure/left leaf found, but still too coarse.

Runner66 then decomposed that repeated structure into a true atomic plank without any new model or manual mask.

Runner66 actual atomic plank evidence:

- persistent internal seam peaks: `x=358` and `x=388`;
- selected interval: `[358, 388]`;
- selected width: `30 px`;
- atomic mask bbox: `[358, 295, 388, 644]`;
- area relative to parent: `0.08923`;
- vertical aspect: `11.633`;
- width relative to parent: `0.10909`;
- height relative to localized leaf: `0.95355`;
- visual: **PASS — one actual vertical plank**.

Runner65/66 strap evidence remains visually correct and is retained unchanged.

Therefore Runner67 is the first gate where both automatic target regions are accepted before Qwen generation begins.

## Architecture

`approved automatic atomic mask -> contextual source crop -> automatic red target guide -> Qwen-Image-Edit-2511 -> deterministic masked neighborhood composite -> full-resolution candidate`

There is no user-drawn mask or box.

Qwen is no longer asked to decide where the requested component is. The automatic control stack owns target geometry. Qwen only performs the local semantic transformation.

## Inputs

Source asset:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_probe.png`

Runner66 evidence root:

`Z:\AI\RogueliteAssetStudio\localization\runner66_gate`

Required automatic masks:

- `plank_atomic_mask.png`
- `strap_retained_mask.png`

Required manifest:

- `runner66_repeated_element_manifest.json`

Runner67 refuses to execute if Runner66's geometry gate, atomic plank validity or retained strap validity is false.

## Editor

Existing installed Qwen-Image-Edit-2511 FP8mixed runtime is reused.

- diffusion: `qwen_image_edit_2511_fp8mixed.safetensors`;
- Qwen2.5-VL 7B FP8 encoder on CPU;
- Qwen image VAE;
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`;
- `--lowvram`;
- reserve VRAM `1.0 GB`;
- AuraFlow shift `3.1`;
- CFGNorm `1`;
- Euler/simple;
- 20 steps;
- CFG `4`;
- seed `0`.

Runner63 already proved that 40 steps materially increase runtime without solving the difficult localization/semantic failure, so Runner67 uses only the efficient 20-step recipe.

## Context crops

Runner67 derives each crop automatically from the accepted mask bbox and adds deterministic context margins.

The crop must include enough neighboring structure for Qwen to understand the requested change while remaining materially smaller than the whole asset.

The crop and crop mask are persisted for provenance.

## Target guide

For each task, Runner67 produces a second visual reference consisting of the same source crop with a translucent red overlay over the approved automatic mask.

The prompt explicitly states that red is only a locator and must not be copied into the result.

References passed to Qwen are:

1. source crop = `previous_approved_state`;
2. red target guide = `structure`.

## Plank edit contract

Qwen must:

- remove exactly the one automatically isolated plank;
- create a narrow open gap approximately equal to that plank's width;
- preserve neighboring planks;
- preserve the broader door/frame/stone/vine geometry;
- avoid widening the deletion into a door-leaf removal.

Nearby hardware may be reconstructed locally where necessary for physical coherence, but the surrounding door design must not be globally redesigned.

## Strap edit contract

Qwen must:

- break only the automatically localized lower-right horizontal iron strap;
- remove a clear central section;
- leave short broken/bent surviving ends;
- not create a replacement bar;
- preserve other hinges/straps/planks/frame/stone/vines.

## Deterministic regional composite

The raw Qwen crop is never pasted unrestricted into the asset.

Runner67 dilates and feathers the approved automatic target mask by a small deterministic reconstruction margin, composites the edited crop only through that blend mask, and restores original full-resolution pixels everywhere else.

This preserves the Runner64 compositor property: unrelated full-image pixels cannot drift because the original source remains authoritative outside the allowed neighborhood.

## Files

Executor:

`tools/roguelite-asset-studio/qwen2511_atomic_region_gate.py`

Runner:

`tools/structured-2d-character-pipeline/67_run_qwen2511_atomic_region_edit.ps1`

Output root:

`Z:\AI\QwenImageEdit\runner67_atomic_region_edit`

Expected principal outputs:

- `plank_source_crop.png`
- `plank_crop_mask.png`
- `plank_approved_mask_overlay.png`
- `plank_target_guide.png`
- `plank_raw_crop_edit.png`
- `plank_atomic_region_final.png`
- `plank_allowed_region.png`
- `strap_source_crop.png`
- `strap_crop_mask.png`
- `strap_approved_mask_overlay.png`
- `strap_target_guide.png`
- `strap_raw_crop_edit.png`
- `strap_atomic_region_final.png`
- `strap_allowed_region.png`
- `runner67_atomic_region_contact_sheet.png`
- `runner67_atomic_region_manifest.json`
- `runner67_executor.log`

## PASS criteria

Technical PASS requires:

- all Runner66 prerequisites validate;
- installed Qwen2511 runtime/hash/commit validate;
- both crop edits complete;
- both deterministic full-resolution composites are produced;
- manifest/contact sheet/log are written;
- no manual mask/box and no new download occur.

Visual PASS requires both tasks:

### Plank

- one narrow same-width opening replaces the one approved plank;
- adjacent planks remain;
- no door-leaf-scale deletion or unrelated redesign occurs.

### Strap

- only the approved lower-right strap is visibly broken;
- no large replacement/transverse bar appears;
- unrelated hardware and geometry remain stable.

### Preservation

- unrelated full-image geometry remains visually identical outside the automatic allowed neighborhoods;
- manifest outside-region difference metrics must remain effectively zero by construction.

## Decision after Runner67

If both tasks pass, `automatic_region_edit` becomes a proven precision-control capability for the Asset Studio and the next static-system gate is semantic multi-reference role separation before the Exilada Character Lab.

If the masks are correct but a local Qwen edit still fails semantically, keep the now-proven perception/mask/compositor contract and replace only the regional editor with a mask-native/inpainting backend. Do not return to unrestricted global prompt editing and do not introduce user-drawn production masks.
