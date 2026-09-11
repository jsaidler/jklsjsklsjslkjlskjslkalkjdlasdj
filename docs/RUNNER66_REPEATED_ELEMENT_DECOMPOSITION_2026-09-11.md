# Runner66 — Atomic repeated-element decomposition gate

Status date: **2026-09-11**

Status: **COMPLETE / TECHNICAL PASS / VISUAL PASS / HANDED OFF TO RUNNER67**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner66 existed

Runner65 materially improved perception:

- parent wooden double door: **visual PASS**;
- lower-right iron strap: **visual PASS**;
- plank: **visual FAIL** because the selected SAM2 mask corresponded to the entire left door leaf, not one individual vertical plank.

Runner65 therefore proved that hierarchical semantic localization is useful but also exposed a different class of problem: a detector/segmenter can correctly identify a repeated structure while remaining too coarse to isolate one repeated atomic member.

Runner66 introduced a deterministic repeated-element decomposition stage after semantic localization.

## Runner65 evidence

### Parent

Selected raw door box:

`[311.3596, 272.5457, 547.8800, 649.2131]`

Expanded parent box:

`[292, 253, 567, 669]`

This visually corresponds to the wooden double door.

### Strap

Runner65 selected:

`[456.0091, 552.5553, 548.3988, 592.1567]`

The SAM2 mask visually corresponds to the intended lower-right horizontal iron strap.

Runner65 strap metrics:

- SAM predicted IoU: `0.89715`;
- mask area relative to parent: `0.01753`;
- mask aspect: `2.186`;
- mask center relative to parent: approximately `[0.766, 0.757]`;
- fully contained in the parent.

This mask was retained unchanged by Runner66.

### Plank

Runner65 selected mask bounding box:

`[325, 285, 422, 651]`

Mask area relative to parent:

`0.27724`

Visual result: the complete left door leaf was selected. Runner65's original `auto_valid=true` was therefore too permissive for the semantic requirement "one plank".

## Architecture

Runner66 added a structural decomposition layer:

`semantic parent -> repeated structure/leaf -> persistent oriented seam profile -> atomic intervals -> target-relative atomic member -> deterministic mask`

For the proof case:

`wooden double door -> left door leaf -> vertical seam energy -> individual vertical planks -> select one plank`

No new model was introduced.

## Why this is not a door-specific production hack

Many game assets contain repeated structural members that semantic detectors tend to collapse into one larger object:

- door/fence planks;
- prison/cage bars;
- railings;
- ribs/spines;
- repeated armor plates;
- roof slats;
- wall panels;
- columns or battens;
- repeated mechanical fins.

The production concept is therefore a generic `repeated_element_decomposition` processor behind the Asset Studio rather than a special-case hand mask.

## Method

Runner66 consumed the already-produced Runner65 files and did not run Grounding DINO, SAM2 or Qwen.

### 1. Localized repeated structure

The Runner65 plank mask was treated as a coarse repeated structure/leaf mask.

### 2. Persistent vertical seam profile

Inside the localized leaf:

- source image converted to grayscale;
- horizontal intensity difference measured between neighboring x positions;
- only positions supported by the leaf mask retained;
- top/bottom margins ignored;
- differences aggregated across height;
- resulting 1D profile smoothed.

A true vertical board joint persists over a large fraction of the leaf height and therefore survives this aggregation.

### 3. Seam peak detection

Local peaks above a fraction of the maximum persistent seam energy were retained with non-maximum suppression.

The leaf edges plus detected internal seams defined candidate repeated-element intervals.

### 4. Atomic member selection

Candidate intervals were ranked by:

- proximity to the semantic target position inherited from Runner65;
- strength of left/right seam boundaries;
- occupancy by the localized leaf mask;
- plausible width relative to the repeated structure.

### 5. Deterministic atomic mask

The selected interval was intersected with the Runner65 leaf mask. No user-drawn mask/box was accepted.

## Actual Runner66 result

Runner66 completed in approximately `0.321 s`.

Persistent seam peaks:

- `x=358`, energy `17.8333`;
- `x=388`, energy `17.6667`.

Selected atomic interval:

- left `358`;
- right `388`;
- center `373`;
- width `30 px`;
- width relative to localized leaf `0.30928`;
- candidate score `0.89282`.

Atomic plank mask:

- bbox `[358, 295, 388, 644]`;
- area relative to parent `0.08923`;
- vertical aspect `11.6333`;
- width relative to parent `0.10909`;
- height relative to localized leaf `0.95355`;
- automatic geometry gate: **PASS**.

Visual review:

- atomic plank: **PASS** — the mask corresponds to one actual vertical wooden plank rather than the whole leaf;
- vertical span: **PASS**;
- unrelated stone/frame exclusion: **PASS**;
- retained lower-right strap: **PASS**.

Final Runner66 classification:

**TECHNICAL PASS / REPEATED-ELEMENT DECOMPOSITION PASS / ATOMIC PLANK VISUAL PASS / RETAINED STRAP VISUAL PASS.**

## Files

Decomposer:

`tools/roguelite-asset-studio/repeated_element_decomposer.py`

Runner:

`tools/structured-2d-character-pipeline/66_run_repeated_element_decomposition_gate.ps1`

Output root:

`Z:\AI\RogueliteAssetStudio\localization\runner66_gate`

Principal evidence:

- `plank_atomic_decomposition.png`
- `plank_atomic_mask.png`
- `plank_atomic_mask_overlay.png`
- `plank_vertical_seam_profile.png`
- `strap_retained_mask.png`
- `strap_retained_mask_overlay.png`
- `runner66_repeated_element_contact_sheet.png`
- `runner66_repeated_element_manifest.json`

## Handoff

Runner66 has closed the perception/atomic-target prerequisite for this proof case.

The active gate is now Runner67:

`docs/RUNNER67_QWEN2511_ATOMIC_REGION_EDIT_2026-09-11.md`

Runner67 reconnects Qwen2511 behind these approved automatic masks and the deterministic regional compositor.

If Runner67 passes both local semantic tasks, the combined perception + atomic-decomposition + regional-edit architecture becomes the first proven precision-edit path for the Asset Studio without user-drawn masks.
