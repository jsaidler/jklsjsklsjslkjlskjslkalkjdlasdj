# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN ACTIVE / W1 PAINTERLY LOOK APPROVED / W1H GEOMETRY PASS / W1I POSE-END 0.70 NOT PREFERRED / W1J AND W1K SUPERSEDED BEFORE RUN / W1L REF1.0 + POSE0.80 + 30 STEPS CURRENT / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

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
- one high-leverage variable at a time by default;
- compound tests are allowed when explicitly labeled as configuration search rather than causal attribution;
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

Runner 42 changed only `pose_end_percent: 1.00 -> 0.70`.

- prompt `5d4f23ed-f4bf-4b01-a13f-108b2bf31fe0`;
- elapsed `1526.52s`;
- SHA256 `9a9052f40221878ded69f61e452abeda87cfaa42bde475bb5e9809c04763d054`.

Frame-by-frame output remained extremely close to W1H. Blur and structural deformation persisted. **Not preferred.**

## W1J / W1K — PREPARED BUT SUPERSEDED BEFORE EXECUTION

- W1J / Runner43 prepared `reference_image_strength 1.5 -> 1.0` alone.
- W1K / Runner44 prepared `pose_strength 1.0 -> 0.80` alone.

Neither was executed. The user requested a combined quality search because the remaining defect is broad: heavy motion blur plus multiple structural changes. Keep both as small diagnostic tooling, not as current gates.

## W1L — CURRENT: COMPOUND QUALITY SEARCH

Runner:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Executor:

`tools/wan-animate2-spike/run_w1l_ref10_pose80_steps30.py`

Parent = exact completed W1H.

Deliberate compound changes:

- `reference_image_strength: 1.5 -> 1.0`;
- `pose_strength: 1.00 -> 0.80`;
- `steps: 20 -> 30`.

Everything else remains W1H: untouched raw driver, `512×912`, pose start0.0, pose end1.0, seed0, CFG1, Euler/simple, shift5, same Exilada reference/prompt/negative/CLIP pose branch.

Experiment policy: **COMPOUND_CONFIGURATION_SEARCH**. W1L is not a causal one-variable experiment. It asks whether a materially better operating point exists when identity tightness, pose forcing and sampling budget are adjusted together.

Pass only if destructive blur **and** structural deformation fall materially while choreography, identity, hair/cloth dynamics and framing remain acceptable.

If W1L succeeds, isolate contributing controls later only if needed. If W1L fails, do not blindly grid-search nearby values; reassess whether the failure is intrinsic to this model/task/driver regime.

## Sequence

- W0 — PASS_BASELINE
- W1 — approved visual/motion baseline
- W1A — ref1.5 structural branch under old geometry
- W1F — CLOSED FAIL
- W1G — CLOSED VALID METHOD FAIL
- W1H — **GEOMETRY PASS / BEST BASELINE**
- W1I — **NOT PREFERRED**
- W1J — **SUPERSEDED BEFORE RUN**
- W1K — **SUPERSEDED BEFORE RUN**
- W1L ref1.0 + pose0.80 + 30steps — **CURRENT**
- separate 1980s/torn-clothing/body-exposure art gate only after technical quality is adequate
- W2 real walking driver with safe margins
- W3 secondary-motion stress driver

## Cleanup

No large asset added by W1F–W1L tooling. Keep small proof/failure evidence; do not pre-download alternate Wan checkpoints. Keep SSD comparison evidence until Wan verdict.
