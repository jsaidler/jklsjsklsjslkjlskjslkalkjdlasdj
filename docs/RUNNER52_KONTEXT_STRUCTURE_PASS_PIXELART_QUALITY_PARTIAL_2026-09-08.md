# Runner52 FLUX Kontext — Structure/Layout Pass, Pixel-Art Quality Partial

Status date: **2026-09-08**

Status: **PARTIAL PASS / STRUCTURE + LAYOUT PASS / FINAL PIXEL-ART QUALITY NOT YET PASS**

Canonical project state: `docs/PROJECT_STATE.md`.

Renderer spike: `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`.

## Completed inference evidence

Runner52 completed all three internal Kontext chunk inferences successfully.

Evidence from the local manifest/log:

- source action: `dance_or_gesture`;
- source H0: `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- source H0 SHA256: `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`;
- selected source frames one-based: `1,12,23,35,46,57,68,79,90,102,113,124`;
- Kontext model: `flux1-dev-kontext_fp8_scaled.safetensors`;
- 20 steps;
- guidance `2.5`;
- CFG `1.0`;
- Euler/simple;
- seed `0`;
- denoise `0.45`;
- chunk prompt ids:
  - `0cb61aec-f6f9-4073-9941-970186ff7d15`;
  - `10bff98b-7453-4064-9e30-95b76dfd38b5`;
  - `65b26095-ccf5-4874-80d0-ca624b9cdb4b`;
- chunk elapsed times: `288.49s`, `280.52s`, `280.34s`;
- total Kontext inference time: `849.35s` (~14m09s), excluding startup/preflight;
- final intended layout: `12 columns × 1 row`, `192×192` cells, `2304×192` locally.

This is genuine model/task evidence, not an infrastructure failure.

## What Runner52 proved

### 1. Final spritesheet semantics — PASS

The previous layout mistake is resolved.

- one action = one horizontal row;
- the 12 cells are ordered left-to-right;
- internal `2×2` tiles remain processing devices only;
- final packing no longer promotes processing chunks to semantic rows.

### 2. Adult body/identity preservation — PASS_CANDIDATE

At denoise `0.45`, the Exilada materially retains:

- mature adult proportions;
- adult head-to-body ratio;
- long torso/limb read;
- adult bust/hips/legs relationship;
- severe mature face/body presence;
- long heavy black hair and torn-cloth silhouette.

The Runner50 infantilization/shortening problem is materially corrected.

### 3. Pose fidelity — PASS_CANDIDATE

The rendered cells remain recognizably tied to the corresponding H0 source poses. No destructive whole-body rewrite, duplicated limbs or major topology collapse was observed in the submitted final row.

### 4. Cross-chunk consistency — PASS_CANDIDATE

The three independently rendered four-frame chunks remain sufficiently compatible in scale, body design and palette to support continued testing. There is no obvious catastrophic identity seam at chunk boundaries.

### 5. Automatic alpha — PASS_CANDIDATE

The RGBA output is usable enough to continue. No routine manual mask repair is justified at this stage.

## What Runner52 did NOT prove

### Final high-level pixel art — NOT YET PASS

The main remaining failure is art quality.

The result is structurally useful but still reads too much like a reduced/filtered raster frame with pixelated edges and noisy miniature detail. It does not yet meet the locked target of deliberate authored high-quality pixel art with:

- strong intentional pixel clusters;
- controlled palette/material grouping;
- clean readable large forms;
- stable sprite-artist decisions rather than residual painterly microtexture;
- a quality ceiling above the current canonical Exilada reference.

Do not classify Runner52 as the final renderer solution.

### Action distillation/timing — STILL OPEN

Runner52 intentionally uses 12 samples spread across the complete 124-frame H0 and preserves source-time coverage. That creates frame durations around `250–479ms` and is useful for provenance, but it is not evidence that final runtime action timing/cycle distillation is solved.

The future action preset stage must decide the actual runtime frame set and timings for each action independently.

## Next controlled experiment

Do not raise Kontext denoise immediately; denoise `0.45` is currently what preserves adult body structure.

The next test adds a dedicated FLUX pixel-art style LoRA while holding structure variables fixed.

Candidate:

- `UmeAiRT/FLUX.1-dev-LoRA-Modern_Pixel_art`;
- file `ume_modern_pixelart.safetensors`;
- ~344MB;
- SHA256 `ed226c149dca6286ae345b6900d807f791a52b1746ed8f524af41efdfda6f0a4`;
- license: MIT for the LoRA itself;
- base Kontext license caveat remains unchanged.

Compatibility of ordinary FLUX.1-dev LoRAs with Kontext is not treated as guaranteed. Therefore the first test uses only the middle four-frame chunk, not all 12 frames.

## Runner53 gate

Runner53 should:

- reuse source frames `46,57,68,79` from Runner52 chunk2;
- reuse the same canonical Exilada reference;
- reuse Kontext FP8, 20 steps, guidance2.5, CFG1, Euler/simple, seed0;
- keep denoise at `0.45`;
- add only the Modern Pixel Art LoRA at strength `1.0`;
- use its pixel-art trigger/style wording;
- generate one four-frame `2×2` probe and a `4×1` extracted preview row;
- compare against the existing Runner52 chunk2 before any full 12-frame rerun.

PASS requires materially stronger intentional pixel-art construction **without** reintroducing body/pose drift.

If the LoRA does not help or breaks structure, reject that style adapter specifically before changing denoise, precision or renderer family.
