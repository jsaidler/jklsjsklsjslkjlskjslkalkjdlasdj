# Runner61 — FLUX.2 Klein 4B Base atomic + sequential edit obedience

Status date: **2026-09-09**

Status: **PREPARED / CURRENT GATE / NO NEW DOWNLOAD**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner61 exists

Runner60 established the first parity-valid visual verdict for the installed FLUX.2 Klein 4B Base branch.

Runner60 proved:

- `full_encoder_small_decoder.safetensors` VAE round-trip is sane;
- the previously proven full `flux2-vae.safetensors` control is also sane;
- Base T2I at 1024×1024 / Euler / CFG 5 / 20 steps produces natural color and coherent output;
- parity-correct Base reference editing no longer has the cyan/posterized Runner59 failure;
- single-reference editing can make a substantial structural change while preserving gate identity/camera;
- multi-reference editing can preserve structure and import some material language.

However, the full production edit contract still did not pass. A single prompt asked the model to perform several independent structural operations at once:

1. remove one full-height left-door plank;
2. remove one large top-left capstone/lintel mass;
3. break/partially remove the lower strap on the right door leaf;
4. increase corrosion and timber damage.

Runner60 visibly achieved only part of that request. The single result changed the upper masonry and materials substantially, but the missing-plank and broken-strap facts were not both unambiguous. The multi result preserved identity/material direction but remained structurally conservative.

Therefore the remaining same-family hypothesis is **instruction decomposition**, not sampling, VAE compatibility or recipe parity.

## Purpose

Determine whether parity-valid Klein Base is useful as an **iterative editor** when each inference is asked to perform one structural fact only, and whether complex revisions can be composed through successive approved-state edits.

This is directly relevant to the Asset Studio UI: an artist may request a sequence of discrete changes while the Studio automatically uses each accepted candidate as the next `previous_approved_state`. No masks, manual repainting or per-pixel intervention are introduced.

If atomic editing itself remains unreliable, the Klein Base structural-edit hypothesis is considered exhausted and the project may move the strong-edit role to a specialized editor family.

## Runtime — unchanged

Workspace:

`Z:\AI\Flux2Klein`

ComfyUI commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

Existing required files only:

- `flux-2-klein-base-4b-fp8.safetensors`
  - SHA256 `44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840`
- `qwen_3_4b.safetensors`
  - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
- `full_encoder_small_decoder.safetensors`
  - SHA256 `ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62`

Runner61 downloads **nothing**.

## Adapter / recipe

Uses the same corrected Base adapter as Runner60:

`tools/roguelite-asset-studio/flux2_klein_base_adapter.py`

Recipe remains:

- separate positive `CLIPTextEncode`;
- separate empty negative `CLIPTextEncode`;
- reference scaling `ImageScaleToTotalPixels`, `nearest-exact`, 1 MP;
- `ReferenceLatent` appended to positive and negative branches;
- edit geometry derived from first scaled reference;
- Euler;
- CFG 5;
- 20 steps;
- seed 0.

No new graph hypothesis is introduced.

## Test A — independent atomic edits

Three independent jobs start from the Runner56 original gate.

### Atomic plank

Only requested structural fact:

**remove one entire vertical plank from the LEFT door leaf**, leaving a clear full-height open gap.

The prompt explicitly forbids merely splitting, darkening or weathering a plank.

### Atomic capstone

Only requested structural fact:

**remove one large top-left capstone/lintel block**, creating a conspicuous missing mass/open notch in the upper silhouette.

The prompt explicitly forbids merely adding cracks/recoloring.

### Atomic strap

Only requested structural fact:

**break and partially remove the lower iron strap on the RIGHT door leaf**, leaving a substantial section absent and a visibly snapped/deformed surviving end.

These independent outputs reveal whether the model can follow each command when prompt competition is removed.

## Test B — sequential complex revision

The same edits are then composed as a chain.

### Stage 1

`original -> remove left-door plank`

Output:

`chain_stage1_plank.png`

### Stage 2

`stage 1 -> preserve missing plank + remove top-left capstone`

Output:

`chain_stage2_capstone.png`

The prompt explicitly instructs the model not to restore the earlier missing-plank gap.

### Stage 3

`stage 2 -> preserve missing plank + preserve missing capstone + break lower-right strap`

Output:

`chain_stage3_strap.png`

The prompt explicitly instructs the model not to restore either earlier structural change.

### Stage 4 — material pass

References:

- Image 1 `structure` = Stage 3 current geometry;
- Image 2 `material` = Runner58 severe-decay material board.

The material prompt requests corrosion/grime/timber/stone aging only and explicitly requires every accumulated structural opening/removal from Image 1 to remain unchanged.

Output:

`chain_stage4_material.png`

## Outputs

Directory:

`Z:\AI\Flux2Klein\base_atomic_sequence`

Expected files:

- `atomic_plank.png`
- `atomic_capstone.png`
- `atomic_strap.png`
- `chain_stage1_plank.png`
- `chain_stage2_capstone.png`
- `chain_stage3_strap.png`
- `chain_stage4_material.png`
- `runner61_atomic_sequence_contact_sheet.png`
- `runner61_atomic_sequence_manifest.json`
- `runner61_executor.log`
- Python stdout/stderr logs
- ComfyUI stdout/stderr logs

## Visual PASS contract

### Atomic

Each independent result should:

- execute its single requested structural fact visibly;
- retain recognizable gate identity and camera;
- leave unrelated geometry substantially intact.

### Sequential

The chain should:

- retain every successful previous structural edit;
- add the requested new fact at each stage;
- not silently restore previously removed pieces;
- remain one coherent recognizable gate.

### Material

Final Stage 4 should:

- preserve all Stage 3 geometry;
- visibly import stronger decay/material qualities from the material board;
- avoid turning the material board into scenery or averaging away the gate identity.

## Decision after Runner61

### If atomic + sequential pass

Klein Base can be exposed in the Asset Studio as an **iterative single-reference structural editor**. The UI/orchestrator should decompose compound structural requests into discrete candidate stages rather than depending on one-shot multi-edit prompts.

Multi-reference material transfer may be routed only to the extent demonstrated by Stage 4.

### If atomic edits pass but sequential preservation fails

Retain Base for isolated atomic variants, but do not automatically chain them. Strong production compositing/structural editing still requires another editor branch.

### If atomic edits themselves fail

The Klein Base strong structural-edit hypothesis is exhausted for the current workstation/recipe. Keep Klein distilled for fast T2I/concept and Base for future training/specialization, then move strong reference editing to the next specialized editor candidate, currently Qwen-Image-Edit.

## Runner

`tools/structured-2d-character-pipeline/61_run_flux2_klein_base_atomic_sequence_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_base_atomic_sequence_gate.py`

Expected terminal completion:

`RUNNER61-FLUX2-KLEIN-BASE-ATOMIC: PASS - MATRIX COMPLETE / VISUAL VERDICT PENDING`
