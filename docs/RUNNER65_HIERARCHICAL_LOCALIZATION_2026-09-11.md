# Runner65 — Hierarchical subcomponent localization gate

Status date: **2026-09-11**

Status: **PREPARED / CURRENT PERCEPTION GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner65 exists

Runner64 proved three useful facts:

1. Grounding DINO Tiny + SAM2.1 execute locally and quickly on the target machine.
2. The deterministic regional compositor successfully constrains edits: pixels outside the automatically allowed region remained effectively unchanged.
3. The first flat full-image localization strategy failed semantically. It selected stone blocks instead of the requested door plank and lower-right strap.

Runner64 therefore does **not** justify changing the Qwen editor or downloading another perception model yet. The current stack has not exhausted the most obvious architectural correction: hierarchical localization.

Runner65 tests only perception. It deliberately does **not** launch Qwen2511, so another 20-step regional generation is not spent until target selection is visually correct.

## Runner64 visual result that triggered this gate

### Plank

Runner64 selected box:

`[62.7451, 540.7537, 329.1651, 704.2875]`

That is the lower-left stone pedestal, not a vertical wooden door plank.

The resulting SAM2 mask had:

- predicted IoU `0.92298`;
- mask area ratio `0.04672`.

SAM2 segmented the selected stone region well; the semantic failure happened earlier in target localization/instance selection.

### Strap

Runner64 selected box:

`[543.9662, 513.4839, 696.7905, 621.7897]`

That is the lower-right stone block, not the lower-right iron door strap.

The resulting SAM2 mask had:

- predicted IoU `0.95213`;
- mask area ratio `0.01900`.

Again, segmentation quality was high for the wrong object.

### Regional compositor

Runner64 did validate the compositor contract:

- plank final: outside allowed region changed ratio above Δ12 = `0.0`;
- strap final: outside allowed region changed ratio above Δ12 = `0.0`.

The region-control mechanism therefore remains useful. The bottleneck is perception.

## Runner65 architecture

The new perception sequence is:

`full asset -> parent grounding -> parent crop/upscale -> subcomponent grounding -> SAM2 candidate masks -> geometry/containment rerank -> diagnostics`

For this gate the parent object is the wooden double door. The production idea is generic: a user request for a small component should be interpreted relative to its parent object rather than against the entire asset image.

## Stage A — parent object localization

Grounding DINO Tiny first searches the full asset for phrases including:

- `wooden double door`
- `double wooden door`
- `wooden door`
- `double door`
- `door`

Parent candidates are ranked by:

- detector confidence;
- centrality;
- plausible parent area;
- vertical door-like aspect;
- semantic label/phrase match;
- rejection of very large whole-gateway boxes.

The selected parent box is expanded slightly and persisted.

## Stage B — child component grounding inside the parent

The selected parent crop is upscaled to a maximum long side of 1280 pixels before the second Grounding DINO pass. This gives the detector materially more pixels for thin/small components.

Component thresholds are intentionally lower than Runner64 to maximize recall. Geometry, spatial relation and SAM2 segmentation are then responsible for precision.

### Plank

Phrases include:

- `single vertical wooden plank`
- `vertical wooden plank`
- `wooden door plank`
- `vertical wooden board`
- `single wooden board`

Expected relation is represented as data:

- vertical;
- left side of parent;
- middle vertical zone;
- narrow component aspect.

### Strap

Phrases include:

- `lower horizontal iron strap`
- `horizontal iron strap`
- `metal door strap`
- `horizontal iron hinge strap`
- `iron hinge`

Expected relation:

- horizontal;
- right side of parent;
- lower vertical zone;
- narrow component aspect.

## Stage C — SAM2 reranking

Runner64 used SAM2 only after one Grounding DINO box had already been chosen. Runner65 instead sends up to the top ten child proposals to SAM2.

For each candidate the pipeline records:

- DINO detector score;
- pre-SAM selector score;
- SAM predicted IoU;
- mask bounding box;
- mask orientation/aspect;
- mask area relative to the parent;
- percentage of mask pixels contained inside the parent;
- mask center relative to the parent;
- automatic validity reasons;
- final reranked score.

This lets SAM2 participate in target choice instead of merely segmenting a potentially wrong detector box.

## Automatic geometry gate

A candidate can only become `auto_valid=true` if it satisfies the parent-relative containment, area, orientation and side/zone constraints for the task.

This is a fail-closed behavior: an invalid thin-component hypothesis should be reported as such rather than silently turning a stone block into the target.

The automatic geometry gate is still only a machine sanity check. **Human visual review remains authoritative before any Qwen regional edit is run.**

## Models/downloads

No new model is downloaded.

Runner65 reuses the exact Runner64 cache:

Grounding DINO Tiny:

- `IDEA-Research/grounding-dino-tiny`
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`
- SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`

SAM2.1 Hiera Small:

- `facebook/sam2.1-hiera-small`
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`
- SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`

Runner65 runs with Hugging Face/Transformers offline flags and should therefore not access the network in normal use.

## Files

Hierarchical localizer:

`tools/roguelite-asset-studio/hierarchical_region_localizer.py`

Runner:

`tools/structured-2d-character-pipeline/65_run_hierarchical_localization_gate.ps1`

Output root:

`Z:\AI\RogueliteAssetStudio\localization\runner65_gate`

Expected diagnostics:

- `parent_detection.png`
- `parent_crop.png`
- `parent_crop_upscaled.png`
- `plank_hierarchical_detection.png`
- `plank_mask.png`
- `plank_mask_overlay.png`
- `plank_crop.png`
- `plank_crop_mask.png`
- `strap_hierarchical_detection.png`
- `strap_mask.png`
- `strap_mask_overlay.png`
- `strap_crop.png`
- `strap_crop_mask.png`
- `runner65_hierarchical_localization_contact_sheet.png`
- `runner65_hierarchical_localization_manifest.json`

## PASS criteria

Technical PASS requires:

- cached Grounding DINO Tiny loads locally;
- parent door localization completes;
- parent crop/upscale is produced;
- both child searches return candidates;
- SAM2 evaluates/reranks component candidates;
- diagnostics and manifest are written;
- no user box or mask is used;
- no Qwen generation is launched.

Visual PASS requires:

1. parent selection corresponds to the wooden door, not the entire gateway/stone frame;
2. plank mask corresponds to one actual vertical wooden door plank;
3. strap mask corresponds to the intended lower-right horizontal iron strap;
4. neither mask includes stone pedestal/frame regions as the target.

Only after both component masks visually pass should the regional Qwen editor be reintroduced, using these approved automatic masks/crops as the next gate.

If hierarchical localization still fails, the next action is to improve/replace the **perception backend** behind the same parent/component contract. Do not return to global prompt-only editing and do not add manual masks.
