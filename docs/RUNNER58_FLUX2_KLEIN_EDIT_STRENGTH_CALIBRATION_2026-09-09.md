# Runner58 — FLUX.2 Klein 4B edit-strength calibration

Status date: **2026-09-09**

Status: **PREPARED / CURRENT GATE / NO NEW MODEL DOWNLOAD**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner58 exists

Runner57 proved that the installed FLUX.2 Klein 4B distilled runtime can execute both single-reference and ordered two-reference editing on the RTX 3060 12 GB workstation.

Actual Runner57 technical results:

- single-reference edit: 768×768, 4 steps, CFG 1.0, Euler, seed 0, **14.063 s**;
- multi-reference edit: 768×768, 4 steps, CFG 1.0, Euler, seed 0, **16.025 s**;
- no OOM, graph failure or runtime crash;
- both outputs preserved the source gate very strongly.

Visual review did **not** accept the edit recipe for production routing because the requested structural/material changes were too weak. The single and multi outputs remained too close to the original gate.

Therefore Runner57 is classified as:

**technical PASS / visual-strength PARTIAL-FAIL**.

This does not reject the Klein family and does not activate edit capabilities in the Studio router.

## Runner58 purpose

Determine whether the already-installed **FLUX.2 Klein 4B distilled FP8** can produce strong, explicit and useful reference edits through recipe calibration before any model switch is considered.

No new checkpoint is downloaded. No new model family is introduced.

## Runtime — unchanged

Workspace:

`Z:\AI\Flux2Klein`

ComfyUI commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

Weights remain exactly:

- `flux-2-klein-4b-fp8.safetensors`
- `qwen_3_4b.safetensors`
- `flux2-vae.safetensors`

All existing SHA256 checks remain mandatory.

## Calibration design

Runner58 executes seven controlled jobs.

### A. Single-reference binary edit matrix

Source: Runner56 ruined gate.

Role: `previous_approved_state`.

Three jobs use identical prompt, seed, CFG and sampler while varying only steps:

- 4 steps;
- 8 steps;
- 12 steps.

The prompt intentionally requests binary, visually verifiable edits instead of vague additional weathering:

1. remove one entire vertical plank from the **left door leaf**, leaving a full-height gap;
2. break away one large **top-left capstone/lintel block**, clearly altering the top silhouette;
3. snap and partially remove the **lower iron strap on the right door leaf**;
4. add strong orange-brown corrosion and dark grime;
5. make surviving timber visibly warped, split and water-damaged.

Identity/camera/overall construction remain authoritative from the source image.

### B. Automatically generated material authority

One independent T2I job creates a severe-decay material reference board containing:

- flaking orange-brown wrought-iron corrosion;
- black grime;
- warped split wet timber;
- fractured gray masonry;
- dirt, moss and opportunistic roots.

The material reference is explicitly **not** a gate or scene. This gives the subsequent multi-reference test a genuinely distinct visual authority instead of recycling a weak first edit.

### C. Ordered multi-reference matrix

References:

- Image 1 role `structure`: original gate — authority for identity, camera, silhouette, masonry footprint and doorway proportions;
- Image 2 role `material`: generated material board — authority only for decay/material severity.

Again three jobs vary only steps:

- 4;
- 8;
- 12.

The multi prompt also requests the same large missing plank/block/strap edits so semantic influence is easy to judge.

## Fixed settings

Except for the step matrix:

- output: 768×768;
- CFG: 1.0;
- sampler: Euler;
- seed: 0 for edit variants;
- material-board seed: 5801.

The 768×768 resolution is a calibration setting, not a production-resolution lock.

## Automatic measurements

For each edit output, Runner58 records simple image-difference metrics against the original:

- mean absolute RGB difference;
- mean absolute luma difference;
- ratio of pixels with luma delta >12;
- ratio of pixels with luma delta >24.

These metrics do **not** decide quality. They only reveal whether a recipe is producing materially different pixels. Human visual review remains authoritative for identity preservation, requested-edit compliance and useful art quality.

## Outputs

Under:

`Z:\AI\Flux2Klein\edit_strength_calibration`

Expected files:

- `single_binary_steps04.png`
- `single_binary_steps08.png`
- `single_binary_steps12.png`
- `material_decay_reference.png`
- `multi_structure_material_steps04.png`
- `multi_structure_material_steps08.png`
- `multi_structure_material_steps12.png`
- `runner58_contact_sheet.png`
- `runner58_manifest.json`
- `runner58_executor.log`
- Python stdout/stderr logs;
- ComfyUI stdout/stderr logs.

## Technical PASS

All seven jobs must complete through the same generic Klein adapter with no OOM, graph failure or runtime crash, and all comparison/manifest outputs must be written.

Expected terminal line:

`RUNNER58-FLUX2-KLEIN-EDIT-CALIBRATION: PASS - TECHNICAL MATRIX COMPLETE / VISUAL VERDICT PENDING`

## Visual PASS

### Single-reference

At least one of 4/8/12 steps must:

- remain recognizably the same gate;
- preserve the camera and main construction;
- clearly remove a full door plank;
- clearly remove a large top-left block;
- clearly break/remove the specified iron strap;
- visibly intensify corrosion/timber damage.

### Multi-reference

At least one of 4/8/12 steps must:

- retain Image 1 identity/camera/construction;
- visibly import severe material qualities from Image 2;
- avoid duplicated gates or material-board-as-scenery contamination;
- execute the requested binary structural edits strongly enough for interactive art direction.

## Decision after review

If a useful single and multi recipe pass visually:

- activate `single_reference_edit`, `multi_reference_edit` and `interactive_variant` for Klein in the model registry;
- expose the adapter through the first generic Asset Studio UI/state layer;
- proceed to the Exilada as the first high-difficulty Character Lab validation.

If all calibrated recipes remain visually too weak:

- keep Klein distilled active for `text_to_image` only;
- record the editing limitation explicitly;
- only then evaluate the next stronger editing branch instead of changing models prematurely.
