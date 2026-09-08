# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN ACTIVE / W1 PAINTERLY LOOK APPROVED / W1H ASPECT-MATCHED GEOMETRY PASS / W1I POSE-END 0.70 NOT PREFERRED / W1J REF-1.0 RETEST CURRENT / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

## Purpose

Select a production model that generates the complete Exilada from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

It must consume richer information than skeleton-only pose and automatically infer locomotion, soft-body response, long-hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

## Candidate order

1. Wan-Animate-2 / Wan2.2-Animate-2-14B — active exhaustion.
2. SCAIL-2 — only after documented Wan `EXHAUSTED_FAIL`.

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

`--disable-pinned-memory` retained.

## W0 — PASS_BASELINE

Runner 36 proved local direct-driving Base-BF16 integration.

## W1 — APPROVED VISUAL/MOTION BASELINE

Runner 37, Exilada + official raw driver, ref strength 1.0. Strong raw-video motion transfer, long-hair secondary motion, cloth drape changes and approved painterly dark-fantasy result. Problems: crop, restraint/chain drift, some limb blur/stretch.

## W1A — REF 1.5 / STRUCTURAL BRANCH RETAINED BEFORE GEOMETRY FIX

Runner 38 changed only `reference_image_strength: 1.0 -> 1.5`. User review found 1.5 structurally stronger but more ghosted; 1.0 cleaner but with more missing/displaced anatomy. This comparison is now known to have been confounded by the old `640×800` canvas.

## W1F — WHOLE-FRAME SAFE80 / CROP FAIL

Runner 39 letterboxed the raw driver inside 640×800. Generated crop remained. Closed.

## W1G — TRACKED RAW-DRIVER REFRAMING / VALID METHOD FAIL / CLOSED

Runner 40 final v3.1 generated a valid ref-1.5 result but became materially worse: stronger ghosting, unstable/elongated limbs, detached/duplicated-looking extremities and degraded temporal body coherence. Do not track/recenter/affine-shift raw-driver footage to solve framing.

## Framing root cause / production geometry rule

ComfyUI `WanAnimate2ToVideo` center-resizes `pose_video` to requested width/height.

- raw driver: `480×854`, aspect ≈ `0.5621`;
- upstream Wan demo: `720×1280`, aspect `0.5625`;
- old project canvas: `640×800`, aspect `0.8`.

The old center crop kept only ~70.3% of source height. Production rule: **preserve raw-driver pixels/trajectory and choose generation geometry whose aspect closely matches the driver.**

## W1H — GEOMETRY PASS / CURRENT BEST BASELINE

Runner 41 changed only `640×800 -> 512×912` from W1A, leaving raw driver untouched and ref strength at 1.5.

Evidence:

- `INFERENCE_COMPLETE`;
- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46 s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- estimated raw-driver retention `99.88%` vs `70.26%` under old geometry.

Visual verdict: catastrophic head/right-body crop resolved; body topology materially better than W1G and generally better than W1A; hair/cloth remain dynamic. Residual blur remains mainly around frames ~8–10; chain/restraint topology still imperfect. W1H is the current best baseline.

## W1I — POSE END 0.70 / VALID CONFIGURATION TEST / NOT PREFERRED

Runner 42 changed only `pose_end_percent: 1.00 -> 0.70` from W1H.

Evidence:

- `INFERENCE_COMPLETE`;
- prompt `5d4f23ed-f4bf-4b01-a13f-108b2bf31fe0`;
- elapsed `1526.52 s`;
- SHA256 `9a9052f40221878ded69f61e452abeda87cfaa42bde475bb5e9809c04763d054`;
- geometry `512×912`, pose strength 1.0, ref strength 1.5 unchanged.

Frame-by-frame comparison: W1I is extremely close to W1H; destructive blur around frames ~8–10 remains; no meaningful topology/framing gain. Simple sharpness diagnostics are mixed rather than decisive. Classification: **valid test, no material blur improvement, not preferred**. Return baseline `pose_end_percent` to 1.0.

## W1J — CURRENT: RETEST REF STRENGTH 1.0 ON CORRECTED GEOMETRY

Runner:

`tools/structured-2d-character-pipeline/43_run_wan_animate2_bf16_w1j_aspectmatched_ref10.ps1`

Executor:

`tools/wan-animate2-spike/run_w1j_ref10_aspectmatched.py`

Parent = exact W1H, not W1I.

Only changed variable:

- `reference_image_strength: 1.5 -> 1.0`.

Everything else remains W1H: untouched raw driver, `512×912`, pose strength 1.0, pose start 0.0, pose end 1.0, seed 0, 20 steps, CFG1, Euler/simple, shift5, same Exilada ref/prompt/negative/CLIP pose branch.

Rationale: the earlier 1.0-vs-1.5 test occurred under the wrong `640×800` geometry. W1J tests whether 1.0 can recover cleaner rendering while the corrected aspect now preserves complete body conditioning.

Prefer 1.0 only if blur/ghosting improves materially without reintroducing missing/displaced body parts, identity loss or weaker hair/cloth motion.

## Sequence

- W0 — PASS_BASELINE
- W1 ref1.0 — approved visual/motion baseline
- W1A ref1.5 — structural branch retained under old geometry
- W1F letterbox — CLOSED FAIL
- W1G tracked reframing — CLOSED VALID METHOD FAIL
- W1H 512×912 + ref1.5 — **GEOMETRY PASS / BEST BASELINE**
- W1I pose_end0.70 — **NOT PREFERRED**
- W1J 512×912 + ref1.0 — **CURRENT**
- separate 1980s/torn-clothing/body-exposure art gate
- W2 clean Internet walking driver with safe real margins
- W3 secondary-motion stress driver
- finite W4 variants if still justified

## Cleanup

No new large asset from W1F–W1J tooling. Keep small proof/failure evidence; do not pre-download alternate large Wan variants. Keep SSD comparison evidence until Wan verdict.
