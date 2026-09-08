# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN ACTIVE / W1 PAINTERLY LOOK APPROVED / W1A REF-1.5 STRUCTURAL BRANCH RETAINED / W1F DRIVER LETTERBOX CLOSED / W1G TRACKED DRIVER REFRAMING CLOSED FAIL / W1H ASPECT-MATCHED RAW-DRIVER GEOMETRY PASS / W1I RESIDUAL-BLUR TEST CURRENT / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

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

Runner 40 eventually produced a valid W1G v3.1 inference on the W1A ref-1.5 branch.

Valid run:

- detector-agnostic foreground tracker;
- `29/37` detections;
- constant scale `0.420722...`;
- target bottom y `580`;
- prompt id `e6d3e6a8-553d-4317-80b1-102881624276`;
- elapsed `1838.11 s`;
- output SHA256 `4450a4737f437aa80e3aef53c8fa66dfc5d4b103b0b41a70c4cc82c1856c30d0`.

Visual verdict: **worse than W1/W1A** — stronger ghosting, unstable/elongated limbs, detached/duplicated-looking extremities and degraded temporal body coherence.

Classification: **VALID METHOD FAIL FOR TRACKED DRIVER REFRAMING**, not Wan family failure. Synthetic frame-to-frame affine translation corrupts the rich spatiotemporal motion signal. Driver tracking/recentering is closed.

## Framing root cause / production geometry rule

ComfyUI's current `WanAnimate2ToVideo` center-resizes `pose_video` to the requested Wan width/height.

- official raw driver: `480×854`, aspect ≈ `0.5621`;
- upstream Wan demo default: `720×1280`, aspect `0.5625`;
- our old W1/W1A canvas: `640×800`, aspect `0.8`.

A center crop from 480×854 to aspect 0.8 keeps only about **70.3% of source height**, discarding about **29.7% vertically**. This is the leading explanation for the inherited top/body crop.

Production rule learned: **preserve raw-driver pixels/trajectory and choose a Wan generation canvas whose aspect closely matches that driver.** Do not impose the old `640×800` generation aspect on arbitrary portrait footage.

## W1H — ASPECT-MATCHED RAW DRIVER / GEOMETRY PASS + CURRENT BEST BASELINE

Runner 41 changed only:

- Wan geometry `640×800 -> 512×912`.

Everything else remained exact W1A, including original raw driver and `reference_image_strength=1.5`.

Completed evidence:

- status `INFERENCE_COMPLETE`;
- prompt id `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46 s`;
- output SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- raw driver aspect `0.562061`;
- W1H canvas aspect `0.561404`;
- estimated pose-video retention `99.88%`, versus `70.26%` under W1A geometry.

Full-sequence visual verdict:

- previous catastrophic top/head/right-body crop is resolved;
- complete body retention is materially better than W1/W1A/W1F/W1G;
- body topology/temporal coherence is substantially stronger than W1G and generally better than W1A;
- long hair and cloth remain non-rigid/dynamic;
- later frames are cleaner and more readable;
- residual destructive blur remains around the fastest motion phase (~frames 8–10);
- restraint/chain topology is still imperfect, especially a loose knotted/chain-like mass near the raised hand late in the sequence;
- a few extremities approach/touch lateral edges because the source performer itself traverses the frame. This should be solved by choosing W2 production drivers with real safe margins, not by reintroducing tracker/recentering.

Classification: **W1H = PASS for the canvas/aspect hypothesis and new best Wan baseline.**

## W1I — CURRENT: NATIVE POSE-END BLUR ISOLATION

Runner:

`tools/structured-2d-character-pipeline/42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1i_pose_end70_ref15.py`

Parent = exact W1H prompt.

Only experimental axis:

- `pose_end_percent: 1.00 -> 0.70`.

Rationale: W1H solved the dominant framing/aspect failure and left residual high-motion blur. Native WanAnimate2ToVideo documentation states motion is mostly established early and explicitly gives `pose_end_percent≈0.7` as an example that can loosen fine detail while retaining choreography. This is a smaller, more controlled blur intervention than lowering `pose_strength`, changing prompt, seed or model.

Everything else stays W1H:

- raw driver untouched;
- `512×912` geometry;
- ref strength 1.5;
- pose strength 1.0;
- pose start 0.0;
- same Exilada reference/prompt;
- same BF16 stack;
- 37 frames / 16 fps;
- 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0;
- same CLIP pose branch and negative prompt.

Success criterion: reduce destructive blur/ghosting in fast-motion phases **without** losing W1H topology, motion adherence, hair/cloth dynamics or framing behavior.

Expected evidence:

- `Z:\AI\WanAnimate2\w1i_exilada_poseend70_ref15.mp4`
- `Z:\AI\WanAnimate2\w1i_run_manifest.json`
- `Z:\AI\WanAnimate2\w1i_api_prompt.json`
- `Z:\AI\WanAnimate2\w1i_executor.log`

## Sequence

- W0 — PASS_BASELINE
- W1 ref 1.0 — approved painterly/motion baseline
- W1A ref 1.5 — structural branch retained
- W1F whole-frame letterbox — CROP FAIL / CLOSED
- W1G tracked driver reframing — VALID METHOD FAIL / CLOSED
- W1H aspect-matched generation canvas + raw driver + ref 1.5 — **GEOMETRY PASS / BEST BASELINE**
- W1I pose_end_percent 0.70 — **CURRENT BLUR TEST**
- separate 1980s/torn-clothing/body-exposure art gate
- W2 clean Internet walking driver with safe real margins
- W3 secondary-motion stress driver
- finite W4 variants if still justified

After the finite Wan matrix, classify `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup

No new large asset was added by W1F/W1G/W1H/W1I tooling. Keep small failure/proof evidence. Do not download alternate large Wan variants in advance. Keep SSD comparison evidence until Wan reaches a production verdict.
