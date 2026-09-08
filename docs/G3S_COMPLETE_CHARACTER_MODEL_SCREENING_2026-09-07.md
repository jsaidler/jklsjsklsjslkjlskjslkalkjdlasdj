# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / MINIMAX H3 REF2VA H0 PASS_CANDIDATE / H0T TURBO4 THROUGHPUT GATE CURRENT / H1-S WALK AFTER SPEED DECISION / WAN PAUSED / SCAIL-2 LATER IF NEEDED**

## Purpose

Select a production family that generates a coherent complete Exilada motion master from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

The motion model must consume richer information than skeleton-only pose and automatically infer locomotion, soft-body response, long-hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

Final runtime pixel-art reconstruction is now explicitly a **separate downstream rendering gate**; H3 is screened here primarily as the motion-master family.

## Screening order

1. **MiniMax H3 Ref2VA — ACTIVE / H0 PASS_CANDIDATE.**
2. Wan-Animate-2 — **PAUSED AFTER W1L**, not exhausted.
3. SCAIL-2 — later only if H3 fails a later production gate.

## Comparison protocol

- distinguish infrastructure, integration, configuration and model/task failures;
- fixed inputs/seeds unless a variable is intentionally changed;
- no seed fishing or manual rescue;
- successful inference is not automatically a model-quality PASS;
- pre-inference integration failures are zero model-quality evidence;
- after a family shows a strong quality baseline, test production throughput before spending long runs on new action families.

## Wan compact history

- W0 local Base-BF16 integration passed with `--disable-pinned-memory`.
- W1 established useful painterly/motion language.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H `512×912` with untouched driver solved dominant crop and became best Wan geometry baseline.
- W1I pose-end0.70 did not materially improve blur/structure.
- W1J/W1K prepared but never executed.
- W1L completed ref1.0 + pose0.80 +30 steps; Wan paused afterward.

## MiniMax H3 Base Ref2VA — H0 COMPLETE

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

H1-S production definition: `docs/H1S_MINIMAX_H3_SPRITESHEET_PRODUCTION_PASS_2026-09-08.md`.

Integration incident: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

Minimal Base stack:

- Ref2VA INT8 ConvRot diffusion ~21GB;
- Qwen3-VL NVFP4 AWQ encoder ~15.7GB;
- video VAE ~5.21GB;
- schema-required audio VAE ~605MB.

## H0 exact completed baseline

- Picture1 = canonical Exilada master;
- Video1 = same raw comparison driver, timestamp-resampled only;
- `448×800`;
-124f @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep/beta`;
- seed0;
- no spatial driver transforms;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

## H0 visual verdict

**PASS_CANDIDATE / FAMILY ADVANCES AS MOTION-MASTER CANDIDATE.**

Strengths:

- stable complete-body topology across the sequence;
- no destructive global smear/ghost-double;
- coherent face/torso/limbs/body proportions/hair/costume language;
- visible hair and torn-cloth secondary motion;
- restraints remain accessory geometry;
- materially sharper motion than problematic Wan branches.

Residuals:

- chain detail still drifts somewhat;
- late right-foot crop follows driver/source envelope;
- H3 painterly appearance is no longer treated as the final runtime raster style.

`448×800` passes as motion-master generation size.

## Production-throughput problem

H0 took ~75 minutes. That is acceptable as an offline quality baseline but not as the ordinary action-iteration loop.

Do not solve this by assuming H3 should generate only 8–12 frames. Current H3 uses the `17k+5` temporal grid and documents its trained range around124–362 frames @24fps.

Production plan:

`fast 124-frame motion master -> automatic action/cycle distillation -> ~12 selected game frames -> pixel-art reconstruction`

## CURRENT — H0T / Runner49

Runner49 compares the exact H0 references/geometry/prompt against the official Ref2V Turbo4 path.

Changes:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` ~1.96GB;
- SHA256 `5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c`;
- LoRA strength1.0;
-4 steps;
- `res_multistep/simple`.

Unchanged:

- Picture1/Video1;
-448×800;
-124f@24fps;
- `ref_image_size=match`;
- seed0;
- same prompt.

Pass requires substantial wall-clock reduction **and** H0-level topology/identity/motion quality.

Runner:

`tools/structured-2d-character-pipeline/49_run_minimax_h3_ref2va_h0t_turbo4.ps1`

## H1-S after H0T

If H0T passes, use Turbo4 for a real screen-left walk motion master with fixed camera, full body, safe real margins, mostly lateral/slight3/4 near `72°`, and one clear gait cycle.

A clean gait cycle may be automatically repeated/tiled to fill the proven 124-frame H3 conditioning regime.

Then distill one coherent generated gait cycle to about **12 unique sprite frames** before the separate final pixel-art renderer.

## Final-runtime art boundary

The project now explicitly separates:

- H3 motion quality;
- frame/cycle extraction quality;
- final pixel-art rendering quality.

A family does not need to preserve literal input pixel clusters inside its intermediate video if the downstream pixel-art renderer can reconstruct the selected coherent poses consistently. Conversely, a beautiful H3 video is not sufficient unless the pixel-art runtime stage succeeds.

## Cleanup

- keep Base H3 set;
- add only the official Ref2V Turbo4 LoRA for the current throughput hypothesis;
- do not accumulate FL2VA/style/alternate quantizations;
- paused Wan large weights may be deleted while preserving W1H/W1L proof;
- keep SSD comparison evidence until explicit abandonment/final verdict.
