# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN ACTIVE / W1 PAINTERLY LOOK APPROVED / W1H ASPECT-MATCHED GEOMETRY PASS / W1I POSE-END 0.70 NOT PREFERRED / W1J REF-ONLY RETEST SUPERSEDED BEFORE RUN / W1K POSE-STRENGTH 0.80 CURRENT / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

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

## W0 / W1 / W1A

W0 proved the local BF16 route.

W1 ref1.0 established the approved painterly/motion language but had crop, restraint and limb artifacts.

W1A ref1.5 appeared structurally stronger but more ghosted. That comparison was performed under the old `640×800` geometry and is not treated as a clean final identity-vs-blur verdict.

## W1F / W1G — CLOSED

- W1F whole-frame letterbox failed to solve generated crop.
- W1G tracked/recentered raw-driver geometry produced a valid inference but materially worsened ghosting, elongated/unstable limbs and temporal coherence.

Do not return to tracked/recentered driver manipulation.

## Geometry rule from W1H

Current ComfyUI `WanAnimate2ToVideo` center-resizes/crops `pose_video` to generation geometry.

Raw driver `480×854` versus old project canvas `640×800` implies a large vertical center crop in the Comfy path. W1H changed only the generation canvas to `512×912` and the result materially improved full-body retention.

Upstream correction: Wan's repository contains different example defaults (`640×800` in the YAML and `720×1280` in the demo CLI), so no single upstream default is used as proof of the aspect rule. The rule is retained from Comfy preprocessing semantics plus W1H's empirical result.

Production rule: preserve raw-driver pixels/trajectory and choose generation geometry compatible with driver aspect.

## W1H — GEOMETRY PASS / CURRENT BEST BASELINE

Runner 41 changed only `640×800 -> 512×912`, kept raw driver untouched and ref strength1.5.

Evidence:

- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`.

Visual verdict:

- dominant crop fixed;
- body topology/temporal coherence materially improved;
- hair/cloth remain dynamic;
- residual high-motion blur/smear remains strong around frames ~8–10;
- structural deformation still appears in motion phases;
- chain/restraint topology remains imperfect.

Classification: **geometry PASS, best current Wan baseline, not yet production quality.**

## W1I — POSE END 0.70 / NOT PREFERRED

Runner 42 changed only `pose_end_percent 1.00 -> 0.70`.

- prompt `5d4f23ed-f4bf-4b01-a13f-108b2bf31fe0`;
- elapsed `1526.52s`;
- SHA256 `9a9052f40221878ded69f61e452abeda87cfaa42bde475bb5e9809c04763d054`.

Frame-by-frame output remained extremely close to W1H. Blur and structural deformation persisted. **Not preferred.**

## W1J — REF1.0 RETEST / SUPERSEDED BEFORE EXECUTION

Runner 43 and its executor remain as prepared small tooling, but the user correctly identified that the remaining defect is not merely identity tightness: blur is still heavy and several structural changes occur.

Therefore `reference_image_strength 1.5 -> 1.0` alone is not the next gate. Do not spend a full inference on W1J unless later evidence specifically justifies an isolated reference-strength comparison.

## W1K — CURRENT: POSE STRENGTH 0.80

Runner:

`tools/structured-2d-character-pipeline/44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1k_pose_strength80_ref15.py`

Parent = exact W1H.

Only changed variable:

- `pose_strength: 1.00 -> 0.80`.

Everything else remains W1H: raw driver untouched, `512×912`, ref strength1.5, pose window0.0–1.0, seed0, 20 steps, CFG1, Euler/simple, shift5, same reference/prompt/negative/CLIP pose branch.

Rationale:

- remaining failure is concentrated in motion phases and combines smear with structural deformation;
- ComfyUI defines `pose_strength` as the direct scale of pose-video influence;
- the Animate-2 model implementation directly scales pose-branch values when pose strength differs from1.0;
- W1I showed that ending pose influence earlier does not materially help.

W1K asks whether a moderate 20% reduction in pose forcing reduces destructive blur **and** anatomy deformation while keeping choreography and secondary dynamics acceptable.

If W1K fails decisively, the next high-leverage axis is sampling quality/steps, not another blind reference-strength tweak.

## Sequence

- W0 — PASS_BASELINE
- W1 — approved visual/motion baseline
- W1A — ref1.5 structural branch under old geometry
- W1F — CLOSED FAIL
- W1G — CLOSED VALID METHOD FAIL
- W1H — **GEOMETRY PASS / BEST BASELINE**
- W1I — **NOT PREFERRED**
- W1J — **SUPERSEDED BEFORE RUN**
- W1K pose_strength0.80 — **CURRENT**
- then sampling-quality test if W1K fails
- separate 1980s/torn-clothing/body-exposure art gate only after technical quality is adequate
- W2 real walking driver with safe margins
- W3 secondary-motion stress driver

## Cleanup

No large asset added by W1F–W1K tooling. Keep small proof/failure evidence; do not pre-download alternate Wan checkpoints. Keep SSD comparison evidence until Wan verdict.
