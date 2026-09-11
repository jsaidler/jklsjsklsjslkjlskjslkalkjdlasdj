# Runner66 — Atomic repeated-element decomposition gate

Status date: **2026-09-11**

Status: **PREPARED / CURRENT PERCEPTION GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner66 exists

Runner65 materially improved perception:

- parent wooden double door: **visual PASS**;
- lower-right iron strap: **visual PASS**;
- plank: **visual FAIL** because the selected SAM2 mask corresponds to the entire left door leaf, not one individual vertical plank.

Runner65 therefore proves that hierarchical semantic localization is useful but also exposes a different class of problem: a detector/segmenter can correctly identify a repeated structure while remaining too coarse to isolate one repeated atomic member.

This is not a reason to change Qwen or download another detector yet.

Runner66 introduces a deterministic repeated-element decomposition stage after semantic localization.

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

This mask is retained unchanged by Runner66.

### Plank

Runner65 selected mask bounding box:

`[325, 285, 422, 651]`

Mask area relative to parent:

`0.27724`

Visual result: the complete left door leaf is selected. Runner65's original `auto_valid=true` was therefore too permissive for the semantic requirement "one plank".

## New architecture

Runner66 adds a structural decomposition layer:

`semantic parent -> repeated structure/leaf -> persistent oriented seam profile -> atomic intervals -> target-relative atomic member -> deterministic mask`

For the current case:

`wooden double door -> left door leaf -> vertical seam energy -> individual vertical planks -> select one plank`

No new model is introduced.

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

Runner66 only proves the vertical-plank instance first.

## Method

Runner66 consumes the already-produced Runner65 files and does not run Grounding DINO, SAM2 or Qwen.

### 1. Localized repeated structure

The Runner65 plank mask is treated as a coarse repeated structure/leaf mask.

Its actual mask bounding box is recovered from the pixels rather than hard-coded.

### 2. Persistent vertical seam profile

Inside the localized leaf:

- convert the source image to grayscale;
- compute horizontal intensity difference between neighboring x positions;
- only include positions supported by the leaf mask;
- ignore small top/bottom margins;
- aggregate differences across height with a median;
- smooth the resulting 1D profile.

A true vertical board joint persists over a large fraction of the leaf height and therefore survives this aggregation. Local wood texture and horizontal iron hardware contribute less consistently.

### 3. Seam peak detection

Local peaks above a fraction of the maximum persistent seam energy are retained with non-maximum suppression.

The leaf edges plus detected internal seams define candidate repeated-element intervals.

### 4. Atomic member selection

Candidate intervals are ranked by:

- proximity to the semantic target position inherited from Runner65;
- strength of their left/right seam boundaries;
- occupancy by the localized leaf mask;
- plausible width relative to the repeated structure.

### 5. Deterministic atomic mask

The selected interval is intersected with the Runner65 leaf mask. No user-drawn mask/box is accepted.

The result must pass a stricter fail-closed geometry gate:

- area relative to parent between `0.02` and `0.12`;
- vertical aspect at least `5.0`;
- width relative to parent at most `0.18`;
- spans at least `80%` of the localized leaf height;
- selected interval width no more than `45%` of leaf width.

An entire door leaf can no longer silently pass as one plank.

## Strap handling

Runner65's visually correct lower-right strap mask is copied unchanged into Runner66 outputs. Runner66 is not allowed to regress a perception result that already passed visual review.

## Qwen remains disabled

Runner66 is perception/structure only.

Do not spend another 20-step Qwen2511 inference until the Runner66 atomic plank mask is visually confirmed together with the retained strap mask.

## Files

Decomposer:

`tools/roguelite-asset-studio/repeated_element_decomposer.py`

Runner:

`tools/structured-2d-character-pipeline/66_run_repeated_element_decomposition_gate.ps1`

Output root:

`Z:\AI\RogueliteAssetStudio\localization\runner66_gate`

Expected files:

- `plank_atomic_decomposition.png`
- `plank_atomic_mask.png`
- `plank_atomic_mask_overlay.png`
- `plank_vertical_seam_profile.png`
- `strap_retained_mask.png`
- `strap_retained_mask_overlay.png`
- `runner66_repeated_element_contact_sheet.png`
- `runner66_repeated_element_manifest.json`

## PASS criteria

Technical PASS requires:

- Runner65 evidence loads;
- at least two persistent internal vertical seams are detected;
- atomic intervals are produced and ranked;
- an atomic plank mask is written;
- retained strap evidence is written;
- manifest/contact sheet are written;
- no model inference and no manual input occurs.

Visual PASS requires:

1. the atomic red mask corresponds to **one actual wooden plank**, not the whole leaf;
2. it spans the plank vertically rather than selecting a small patch;
3. unrelated stone/frame areas are excluded;
4. the retained strap mask still corresponds to the intended lower-right strap.

If Runner66 visually passes, the next gate reconnects Qwen2511 to these now-valid automatic target regions.

If Runner66 cannot isolate one plank, then the next perception hypothesis must change the atomic-decomposition backend (for example learned dense correspondence/semantic segmentation), not return to manual masks or global prompt-only editing.
