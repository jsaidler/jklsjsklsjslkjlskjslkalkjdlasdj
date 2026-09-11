# Runner67 — Qwen2511 approved automatic atomic-region edit gate

Status date: **2026-09-11**

Status: **COMPLETE / TECHNICAL PASS / VISUAL PRECISION FAIL**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner67 was the first edit gate where both target regions were accepted before Qwen generation:

- Runner65 parent door: PASS;
- Runner65 lower-right strap: PASS;
- Runner66 one-plank decomposition: PASS.

Architecture tested:

`approved automatic mask -> contextual crop -> red locator reference -> Qwen-Image-Edit-2511 -> deterministic regional composite`.

No user-drawn mask or box was used.

## Inputs

Source:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_probe.png`

Runner66 masks:

- `plank_atomic_mask.png`
- `strap_retained_mask.png`

Editor recipe:

- Qwen-Image-Edit-2511 FP8mixed;
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`;
- Qwen2.5-VL 7B FP8 on CPU;
- low-VRAM / reserve 1 GB;
- AuraFlow shift 3.1;
- CFGNorm 1;
- Euler/simple;
- 20 steps;
- CFG 4;
- seed 0.

## Actual result

Runner67 completed both jobs and preserved source pixels outside the deterministic allowed neighborhoods.

### Plank

Qwen raw crop created a narrow opening, but the generated local geometry shifted relative to the approved automatic mask. The final mask-constrained composite therefore sampled misaligned edited pixels and produced thin elongated/reconstructed strips instead of a clean removed plank.

Metrics:

- Qwen elapsed: `639.175 s`;
- changed ratio >Δ12: `0.011878`;
- changed ratio >Δ24: `0.006610`;
- inside-allowed changed ratio >Δ12: `0.272004`;
- outside-allowed changed ratio >Δ12: `0.0`.

Visual verdict: **FAIL — target geometry correct, edit/composite alignment not clean enough.**

### Strap

The second red-overlay locator reference leaked into generated content. The raw Qwen crop reproduced a red rectangular patch over the strap and that patch survived inside the allowed region of the final composite.

Metrics:

- Qwen elapsed: `601.176 s`;
- changed ratio >Δ12: `0.001682`;
- changed ratio >Δ24: `0.001149`;
- inside-allowed changed ratio >Δ12: `0.124109`;
- outside-allowed changed ratio >Δ12: `0.0`.

Visual verdict: **FAIL — locator image treated as appearance/content.**

## What passed

The following components remain accepted:

1. Runner66 automatic plank mask;
2. Runner65/66 automatic strap mask;
3. contextual crop construction;
4. deterministic full-resolution regional composite;
5. outside-region preservation: `changed_ratio_gt_12 = 0.0` for both tasks.

The failure is not a perception regression.

## What failed

The control mechanism `colored locator image as second semantic reference` is rejected.

Two concrete problems were demonstrated:

- colored-guide leakage into output;
- Qwen crop geometry can shift relative to a separately applied full-resolution mask.

## Final classification

**TECHNICAL PASS / AUTOMATIC MASKS PASS / DETERMINISTIC COMPOSITOR PASS / RED GUIDE LEAK FAIL / CROP-TO-MASK ALIGNMENT FAIL / PRECISION EDIT FAIL.**

## Next gate

Runner68 replaces visual-guide conditioning with native latent control:

`automatic operation mask -> ImageToMask -> SetLatentNoiseMask -> Qwen2511 -> deterministic composite`.

Qwen receives only the source crop as semantic visual conditioning. No red or colored target guide is passed to the model.

For the strap-break operation, Runner68 derives the middle edit section automatically from the approved full strap mask so the two strap ends remain outside the latent-noise region.

Canonical next record:

`docs/RUNNER68_QWEN2511_LATENT_MASK_REGION_EDIT_2026-09-11.md`
