# Runner65 — Hierarchical subcomponent localization gate

Status date: **2026-09-11**

Status: **COMPLETE / PARENT PASS / STRAP PASS / PLANK TOO COARSE / HANDOFF TO RUNNER66**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner65 exists

Runner64 proved three useful facts:

1. Grounding DINO Tiny + SAM2.1 execute locally and quickly on the target machine.
2. The deterministic regional compositor successfully constrains edits: pixels outside the automatically allowed region remained effectively unchanged.
3. The first flat full-image localization strategy failed semantically. It selected stone blocks instead of the requested door plank and lower-right strap.

Runner64 therefore did **not** justify changing the Qwen editor or downloading another perception model. Runner65 tested the most obvious architectural correction: hierarchical localization.

Runner65 is perception-only and deliberately launches no Qwen2511 generation.

## Architecture tested

`full asset -> parent grounding -> parent crop/upscale -> subcomponent grounding -> SAM2 multi-candidate rerank -> geometry/containment gate -> visual review`

The parent object is the wooden double door. The production principle is generic: a request for a small component should be interpreted relative to its parent object rather than against the entire asset image.

## Models

No new model was downloaded.

Grounding DINO Tiny:

- `IDEA-Research/grounding-dino-tiny`
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`
- SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`

SAM2.1 Hiera Small:

- `facebook/sam2.1-hiera-small`
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`

The gate used the Runner64 local cache in offline mode.

## Stage A — parent localization

Grounding DINO Tiny searched the full asset for:

- `wooden double door`
- `double wooden door`
- `wooden door`
- `double door`
- `door`

The selected raw parent box was:

`[311.3596, 272.5457, 547.8800, 649.2131]`

Expanded parent box:

`[292, 253, 567, 669]`

Visual review: **PASS**. It corresponds to the wooden double door rather than the complete gateway or a side stone block.

## Stage B — child grounding inside the parent

The parent crop was upscaled to a long side of 1280 before child grounding. Lower component thresholds were used for recall; geometry and SAM2 then participated in reranking.

### Plank phrases

- `single vertical wooden plank`
- `vertical wooden plank`
- `wooden door plank`
- `vertical wooden board`
- `single wooden board`

### Strap phrases

- `lower horizontal iron strap`
- `horizontal iron strap`
- `metal door strap`
- `horizontal iron hinge strap`
- `iron hinge`

## Stage C — SAM2 reranking

Up to ten child proposals were segmented with SAM2. The manifest records detector score, parent-relative geometry, SAM IoU, mask area/aspect/center, containment, validity reasons and final score.

This was a material improvement over Runner64 because SAM2 participated in candidate selection rather than merely segmenting one already-selected wrong full-image proposal.

## Actual result

### Parent door — PASS

The hierarchy corrected the flat-localization failure. Side stone pedestals were no longer selected as the parent.

### Lower-right strap — PASS

Selected component box:

`[456.0091, 552.5553, 548.3988, 592.1567]`

Selected mask metrics:

- detector score `0.05398`;
- SAM predicted IoU `0.89715`;
- mask area relative to parent `0.01753`;
- parent containment `1.0`;
- horizontal mask aspect `2.186`;
- center relative to parent approximately `[0.766, 0.757]`.

Visual review confirms that the red mask corresponds to the intended lower-right horizontal iron strap.

Classification: **VISUAL PASS**.

### Plank — FAIL AT ATOMIC GRANULARITY

Selected mask bounding box:

`[325, 285, 422, 651]`

Mask metrics:

- SAM predicted IoU `0.96534`;
- mask area relative to parent `0.27724`;
- parent containment `1.0`;
- vertical aspect `3.773`.

Visual review shows that this mask corresponds to the **entire left door leaf**, including multiple vertical boards and hardware, not one actual plank.

Runner65's machine `auto_valid=true` was therefore semantically too permissive. A repeated structure can satisfy orientation/containment/area heuristics while still being too coarse for an atomic-member request.

Classification: **SEMANTIC HIERARCHY PASS / ATOMIC GRANULARITY FAIL**.

## Final Runner65 classification

**TECHNICAL PASS / PARENT PASS / STRAP PASS / PLANK REPEATED-STRUCTURE LEAF FOUND / ONE-PLANK GRANULARITY FAIL.**

This result does **not** justify replacing Grounding DINO or SAM2 yet. The system has already found the correct repeated structure. The missing operation is decomposition of that structure into one repeated member.

## Handoff to Runner66

Runner66 adds deterministic repeated-element decomposition after semantic localization:

`parent -> repeated structure/leaf -> persistent oriented seam profile -> atomic intervals -> one repeated element`

Current first proof:

`door -> left leaf -> vertical board joints -> one plank`

Runner65's visually correct strap mask is retained unchanged. Runner66 remains perception/structure-only and does not run Qwen.

Canonical next record:

`docs/RUNNER66_REPEATED_ELEMENT_DECOMPOSITION_2026-09-11.md`

## Files retained

Localizer:

`tools/roguelite-asset-studio/hierarchical_region_localizer.py`

Runner:

`tools/structured-2d-character-pipeline/65_run_hierarchical_localization_gate.ps1`

Evidence root:

`Z:\AI\RogueliteAssetStudio\localization\runner65_gate`

Key evidence:

- `parent_detection.png`
- `plank_hierarchical_detection.png`
- `plank_mask_overlay.png`
- `strap_hierarchical_detection.png`
- `strap_mask_overlay.png`
- `runner65_hierarchical_localization_contact_sheet.png`
- `runner65_hierarchical_localization_manifest.json`

## Production invariant

The user draws no boxes or masks. Parent localization, repeated-structure identification, atomic decomposition and later regional composition remain pipeline responsibilities.
