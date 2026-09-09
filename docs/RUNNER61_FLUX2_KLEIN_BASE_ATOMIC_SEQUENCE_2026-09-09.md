# Runner61 — FLUX.2 Klein 4B Base atomic + sequential edit obedience

Status date: **2026-09-09**

Status: **TECHNICAL PASS / VISUAL PRECISION FAIL / SAME-FAMILY STRUCTURAL-EDIT HYPOTHESIS EXHAUSTED**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner60 proved that FLUX.2 Klein 4B Base was technically healthy when used with the current official ComfyUI graph. Runner61 tested the final same-family hypothesis: whether structural requests become production-useful when decomposed into one atomic fact per inference and then chained sequentially.

No new model or graph variant was introduced.

## Runtime

Workspace:

`Z:\AI\Flux2Klein`

ComfyUI commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

Recipe:

- `flux-2-klein-base-4b-fp8.safetensors`;
- `qwen_3_4b.safetensors`;
- `full_encoder_small_decoder.safetensors`;
- reference target ~1 MP;
- separate empty negative CLIP encoding;
- Euler;
- CFG 5;
- 20 steps;
- seed 0.

## Matrix executed

Independent atomic tests from the same original gate:

1. remove one full-height plank from the left door leaf;
2. remove one large top-left capstone/lintel block;
3. break/partially remove the lower iron strap on the right door leaf.

Sequential chain:

1. original -> plank edit;
2. preserve plank edit -> capstone edit;
3. preserve both -> strap edit;
4. preserve accumulated geometry -> import Runner58 material-decay reference.

Output directory:

`Z:\AI\Flux2Klein\base_atomic_sequence`

Contact sheet:

`runner61_atomic_sequence_contact_sheet.png`

## Visual verdict

### Atomic plank — FAIL precision

The model understood the instruction as **remove door material/open the doorway**, but did not isolate one plank-width. It removed/reconstructed almost the entire left door leaf/opening.

This is a semantic response, but not sufficiently localized for production art direction.

### Atomic capstone — PARTIAL / FAIL precision

The model successfully removed obvious upper masonry mass and created a new silhouette notch, but the modification affected a broader upper region than the requested single capstone/lintel block.

### Atomic strap — FAIL precision

The model understood that door hardware should change, but reinterpreted a substantial portion of the hardware/door treatment instead of isolating only the requested lower-right strap.

### Sequential chain — PARTIAL continuity

The chain demonstrates that Klein Base can preserve the **coarse state** of earlier changes across subsequent passes. The missing/open left-door state and altered upper masonry generally survive later stages.

However, because the first atomic states are themselves too coarse, chaining them compounds coarse revisions rather than producing precise controlled edits.

### Final material pass — PARTIAL PASS

The final two-reference pass visibly increases orange rust/material decay while broadly preserving the accumulated gate state. This proves useful material-reference influence at a coarse level.

It does not repair the structural-precision limitation.

## Final Runner61 conclusion

**Klein Base is not approved as the Roguelite Asset Studio production structural editor.**

The model is capable of:

- coherent static generation;
- meaningful coarse semantic edits;
- useful upper-level structural variation;
- sequential preservation of broad state;
- material-transfer influence.

It is not reliable enough for instructions such as:

- remove exactly one plank;
- break exactly one named strap;
- modify one small structural component while preserving adjacent components.

This precision matters because routine manual masks, repainting and repair are outside the production contract.

Therefore the same-family strong-edit hypothesis is considered **exhausted**. Do not continue increasing Klein steps or adding prompt variants without a new technical mechanism.

## Role retained for Klein

### FLUX.2 Klein 4B distilled

Retain as the fast local T2I/concept backend.

### FLUX.2 Klein 4B Base

Retain for:

- Base/T2I research;
- future Roguelite-specific LoRA/fine-tuning;
- coarse concept-revision research if useful.

Do not route precision structural edits through it.

## Next gate

Strong structural/reference editing moves to:

**Qwen-Image-Edit-2509 FP8 low-VRAM + atomic precision spike.**

Canonical next record:

`docs/RUNNER62_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_2026-09-09.md`

The first Qwen gate deliberately compares the same failed atomic operations directly against Runner61 so the project can determine whether the new specialized editor actually improves localization/obedience rather than merely producing different-looking images.
