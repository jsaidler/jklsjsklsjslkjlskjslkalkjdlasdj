# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN ACTIVE / W1 PAINTERLY LOOK APPROVED / W1A REF-1.5 STRUCTURAL BRANCH RETAINED / W1F DRIVER LETTERBOX CLOSED / W1G TRACKED DRIVER REFRAMING CLOSED FAIL / W1H RAW-DRIVER ASPECT-MATCHED CANVAS CURRENT / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

## Purpose

Select a production model that generates the complete Exilada from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

It must consume richer information than skeleton-only pose and automatically infer locomotion, soft-body response, long-hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

## Candidate order

1. Wan-Animate-2 / Wan2.2-Animate-2-14B — active exhaustion.
2. SCAIL-2 — only after documented Wan `EXHAUSTED_FAIL`.

Moore/AnimateAnyone/SSD compatibility paths remain research evidence only for the final raw-video contract.

## Model-exhaustion protocol — LOCKED

- one ugly run does not kill a family;
- distinguish infrastructure/integration/configuration/model-task failures;
- fixed seed/input unless that variable is explicitly tested;
- one high-leverage variable at a time;
- no manual rescue or seed fishing.

## Active Wan BF16 route

- `wan_animate_2_bf16.safetensors`
- `umt5_xxl_fp16.safetensors`
- `clip_vision_h.safetensors`
- `Wan2_1_VAE_bf16.safetensors`

`--disable-pinned-memory` is retained.

## W0 — PASS_BASELINE

Runner 36 proved local direct-driving Base-BF16 integration.

## W1 — APPROVED VISUAL/MOTION BASELINE

Runner 37, Exilada + official raw driver, ref strength 1.0.

Positive: substantial raw-video motion transfer, long-hair secondary motion, cloth drape changes, no cat/costume leakage, approved painterly dark-fantasy result.

Problems: crop, restraint/chain drift, some limb blur/stretch.

## W1A — REF 1.5 / STRUCTURAL BRANCH RETAINED

Runner 38 changed only `reference_image_strength: 1.0 -> 1.5`.

Current interpretation after user review:

- 1.5 preserves body structure/topology better;
- 1.0 is cleaner in several phases;
- 1.5 has more destructive blur/ghosting;
- preserve 1.5 as structural branch; solve blur separately.

## W1F — WHOLE-FRAME SAFE80 / CROP FAIL

Runner 39 letterboxed the full raw driver inside 640×800 with no temporal tracking. Generated crop remained. Whole-frame letterbox-only variants are closed.

## W1G — TRACKED RAW-DRIVER REFRAMING / CLOSED FAIL

Runner 40 progressed through several preprocessing diagnostics and finally produced a valid W1G v3.1 inference.

Final valid run:

- parent = W1A ref 1.5;
- detector-agnostic foreground tracker;
- `29/37` detections;
- constant scale `0.420722...`;
- target bottom y `580`;
- all pre-inference margin guards passed;
- prompt id `e6d3e6a8-553d-4317-80b1-102881624276`;
- elapsed `1838.11 s`;
- output SHA256 `4450a4737f437aa80e3aef53c8fa66dfc5d4b103b0b41a70c4cc82c1856c30d0`.

Visual verdict: **worse than W1/W1A**.

Failure signature:

- stronger ghosting/smearing;
- unstable/elongated body and limbs;
- detached/duplicated-looking extremities;
- degraded temporal body coherence;
- framing still not reliably solved.

Classification: **VALID CONFIGURATION/METHOD FAIL FOR TRACKED DRIVER REFRAMING**, not Wan family failure.

Interpretation: synthetic frame-to-frame affine translation cancels the performer's traversal but also corrupts the richer spatiotemporal signal Wan is supposed to consume. The branch that modifies raw-driver geometry for framing is closed. Do not tune the tracker further.

## Framing root cause now prioritized

ComfyUI's current `WanAnimate2ToVideo` applies:

`pose_video -> common_upscale(..., requested width, requested height, "area", "center")`

The official raw driver is `480×854` (aspect ≈ 0.5621).

Upstream Wan-Animate-2's own demo defaults are `720×1280` (aspect 0.5625), essentially the same portrait shape.

Our W0/W1/W1A canvas was `640×800` (aspect 0.8).

A center crop from 480×854 to aspect 0.8 keeps only about **70.3% of source height**, discarding about **29.7% vertically**. This is now the leading explanation for the inherited full-body crop.

W1F avoided direct center-crop loss by shrinking/letterboxing the driver, but that changed subject scale. W1G changed temporal geometry and damaged motion. The next test therefore fixes **generation-space aspect** while leaving the raw driver untouched.

## W1H — CURRENT: RAW DRIVER + ASPECT-MATCHED WAN CANVAS + REF 1.5

Runner:

`tools/structured-2d-character-pipeline/41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1h_aspect_matched_ref15.py`

Parent = exact W1A prompt.

Only experimental axis:

- Wan `width/height: 640×800 -> 512×912`.

The original raw driver remains byte-for-byte untouched.

Why 512×912:

- aspect ≈ 0.5614, within ~0.12% of 480×854;
- nearly eliminates center-crop loss in the raw pose-video path;
- total pixels are lower than 640×800;
- no tracking, letterboxing, translation cancellation or synthetic camera motion.

Everything else remains W1A:

- Exilada reference/prompt;
- original raw driver;
- BF16 stack;
- 37 frames, 16 fps output, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- reference strength 1.5;
- pose CLIP branch unchanged;
- negative prompt unchanged.

Success criterion:

1. materially better full-body framing than W1A;
2. no W1G-style motion/topology degradation;
3. retain stronger body structure from ref 1.5;
4. then isolate destructive-blur reduction.

Expected evidence:

- `Z:\AI\WanAnimate2\w1h_exilada_aspectmatched_ref15.mp4`
- `Z:\AI\WanAnimate2\w1h_run_manifest.json`
- `Z:\AI\WanAnimate2\w1h_api_prompt.json`
- `Z:\AI\WanAnimate2\w1h_executor.log`

## Sequence

- W0 — PASS_BASELINE
- W1 ref 1.0 — approved painterly/motion baseline
- W1A ref 1.5 — structural branch retained
- W1F whole-frame letterbox — CROP FAIL / CLOSED
- W1G tracked driver reframing — VALID METHOD FAIL / CLOSED
- W1H aspect-matched generation canvas + raw driver + ref 1.5 — **CURRENT**
- blur gate if W1H passes framing
- separate 1980s/torn-clothing/body-exposure art gate
- W2 clean Internet walking driver
- W3 secondary-motion stress driver
- finite W4 variants if still justified

After the finite Wan matrix, classify `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup

No large asset was added by W1G or W1H. Keep small W1G failure evidence. Do not download alternate large Wan variants in advance. Keep SSD comparison evidence until Wan reaches a production verdict.
