# Runner68 — Qwen2511 automatic latent-mask regional edit gate

Status date: **2026-09-11**

Status: **PREPARED / CURRENT PRECISION-EDIT GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner68 exists

Runner67 was the first edit gate to consume visually approved automatic component masks from Runner66.

Technical execution completed, but visual review exposed two different failures that are not perception failures:

### Plank

The Qwen raw crop did create a narrow opening, but the generated geometry shifted relative to the approved mask. The deterministic full-resolution composite then sampled misaligned edited pixels through the correct mask, producing narrow distorted strips rather than a clean same-width removed plank.

Runner67 plank metrics:

- Qwen elapsed: `639.175 s`;
- final changed ratio >Δ12: `0.011878`;
- inside-allowed changed ratio >Δ12: `0.272004`;
- outside-allowed changed ratio >Δ12: `0.0`.

### Strap

The second red-overlay reference was treated as visual content. The raw crop and final result contain a red rectangular patch over the target strap instead of a physical break.

Runner67 strap metrics:

- Qwen elapsed: `601.176 s`;
- final changed ratio >Δ12: `0.001682`;
- inside-allowed changed ratio >Δ12: `0.124109`;
- outside-allowed changed ratio >Δ12: `0.0`.

Therefore Runner67 proves that the perception masks and deterministic compositor are not the remaining problem. The weak link is how Qwen receives target control.

## Runner67 final classification

**TECHNICAL PASS / APPROVED AUTOMATIC MASKS PASS / DETERMINISTIC COMPOSITOR PASS / RED VISUAL GUIDE LEAK FAIL / CROP-TO-MASK GEOMETRY ALIGNMENT FAIL / PRECISION EDIT FAIL.**

Do not return to global prompt-only editing and do not weaken the masks.

## Runner68 control change

Runner68 removes the colored locator reference completely.

Architecture:

`Runner66 automatic target -> source crop -> automatic operation mask -> same image scaling path -> ImageToMask -> SetLatentNoiseMask on source latent -> Qwen2511 -> deterministic final composite`

Qwen receives only the source crop as semantic image conditioning. The automatic mask is not shown as red, colored, alpha-overlay or second semantic reference.

The mask becomes sampler control rather than image content.

## Native ComfyUI mechanism

Runner68 uses built-in nodes already expected in the pinned ComfyUI runtime:

- `ImageToMask`;
- `SetLatentNoiseMask`.

The white-on-black control mask is passed through the same `FluxKontextImageScale` path as the source crop so source latent and mask remain geometrically aligned after Qwen's standard reference scaling.

`SetLatentNoiseMask` attaches the resulting mask to the VAE-encoded source latent before `KSampler`.

The Qwen recipe otherwise remains the proven 2511 recipe:

- FP8mixed checkpoint;
- Qwen2.5-VL 7B FP8 on CPU;
- Qwen image VAE;
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`;
- low-VRAM mode;
- AuraFlow shift `3.1`;
- CFGNorm `1`;
- Euler/simple;
- 20 steps;
- CFG `4`;
- seed `0`.

## Operation-aware automatic masks

Runner66 masks remain semantic target authority.

### Plank removal

The complete Runner66 atomic plank mask is the operation target.

A small deterministic dilation/feather is used as the latent noise region to allow synthesis at the plank boundaries.

### Strap break

The requested operation is not "replace the entire strap"; it is "break the strap in the middle".

Runner68 therefore derives an operation submask automatically from the approved strap:

- keep the original full strap mask as provenance;
- compute its bounding box;
- intersect the mask with the central `40%` of its horizontal extent;
- only that middle section receives latent noise.

This guarantees the outer strap ends remain outside the edit region and cannot become another full-width replacement bar.

No user mask or box is introduced.

## Double containment

Runner68 has two containment layers:

1. native latent noise masking during Qwen sampling;
2. deterministic final full-resolution composite through a slightly dilated/feathered operation mask.

Even if the decoded Qwen crop drifts outside the operation region, the final asset restores source pixels outside the deterministic neighborhood.

## Files

Masked adapter:

`tools/roguelite-asset-studio/qwen_image_edit_2511_masked_adapter.py`

Executor:

`tools/roguelite-asset-studio/qwen2511_latent_mask_region_gate.py`

Runner:

`tools/structured-2d-character-pipeline/68_run_qwen2511_latent_mask_region_edit.ps1`

Output root:

`Z:\AI\QwenImageEdit\runner68_latent_mask_region_edit`

Principal expected outputs:

- `plank_source_crop.png`
- `plank_latent_noise_mask.png`
- `plank_approved_target_overlay.png`
- `plank_latent_operation_overlay.png`
- `plank_masked_raw_crop_edit.png`
- `plank_latent_mask_region_final.png`
- `plank_allowed_region.png`
- `strap_source_crop.png`
- `strap_latent_noise_mask.png`
- `strap_approved_target_overlay.png`
- `strap_latent_operation_overlay.png`
- `strap_masked_raw_crop_edit.png`
- `strap_latent_mask_region_final.png`
- `strap_allowed_region.png`
- `runner68_latent_mask_contact_sheet.png`
- `runner68_latent_mask_manifest.json`
- `runner68_executor.log`

## PASS criteria

Technical PASS requires:

- Runner66 automatic masks validate;
- Qwen runtime/hash/commit validate;
- `ImageToMask` and `SetLatentNoiseMask` are present in the pinned ComfyUI runtime;
- both 20-step masked jobs complete;
- final deterministic composites and diagnostics are written;
- no download and no manual mask/box occur.

Visual PASS requires both tasks.

### Plank

- the one approved plank is replaced by a clean narrow open gap;
- the gap remains aligned with the approved mask;
- neighboring planks and broader door geometry remain stable;
- no thin duplicated/reconstructed plank artifact remains.

### Strap

- a clear central section of the intended lower-right strap is absent;
- both outside strap ends survive because they were never in the operation mask;
- no replacement bar appears;
- no red/colored locator artifact can appear because no locator image is conditioned.

### Preservation

Manifest outside-region changed ratio >Δ12 must remain effectively zero by construction.

## Decision after Runner68

If both tasks pass, the project has a complete automatic precision-control route:

`semantic hierarchy -> automatic segmentation/decomposition -> operation-aware latent mask -> semantic editor -> deterministic composite`.

Then `automatic_region_edit` can be promoted and the next static-system gate is semantic multi-reference role separation before the Exilada Character Lab.

If masks are correct but masked Qwen2511 still fails semantically, the perception and control architecture remain accepted and the next branch is a dedicated mask-native/inpainting editor behind the same automatic-mask contract. Do not return to red guide images, unrestricted global prompting or user-drawn production masks.
