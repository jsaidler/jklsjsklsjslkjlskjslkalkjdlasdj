# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN PAUSED AFTER W1L / MINIMAX H3 BASE REF2VA ACTIVE / RUNNER47 PRE-INFERENCE INTEGRATION FAIL / RUNNER48 CURRENT / SCAIL-2 LATER IF NEEDED**

## Purpose

Select a production model that generates the complete Exilada from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

The model must consume richer information than skeleton-only pose and automatically infer locomotion, soft-body response, long-hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

## Screening order — LOCKED 2026-09-08

1. **MiniMax H3 Base Ref2VA** — active screening route.
2. Wan-Animate-2 — **PAUSED AFTER W1L**, not exhausted.
3. SCAIL-2 — later only if H3 does not satisfy the production contract.

## Comparison protocol

- distinguish infrastructure, integration, configuration and model/task failures;
- fixed inputs/seeds unless the variable is intentionally changed;
- one-variable experiments by default;
- compound configuration searches allowed when explicitly labeled;
- no seed fishing or manual rescue;
- successful inference is not automatically a model-quality PASS;
- no pre-inference integration failure counts as model-quality evidence.

## Wan canonical history

- W0: local Base-BF16 route passed with `--disable-pinned-memory`.
- W1 ref1.0: approved painterly/motion language; crop/restraint/limb issues.
- W1A ref1.5: stronger apparent topology but more ghosting under old geometry.
- W1F: whole-frame letterbox failed crop; closed.
- W1G: tracked/recentered raw driver worsened ghosting and temporal anatomy; closed permanently.
- W1H: `512×912` with untouched raw driver fixed dominant crop and became best documented Wan geometry baseline.
- W1I: pose-end0.70 did not materially improve blur/structural failures.
- W1J/W1K: prepared, never executed.
- W1L: completed compound branch ref1.0 + pose0.80 +30 steps; Wan paused after completion. Preserve local evidence; visual verdict not invented without review.

## MiniMax H3 Base Ref2VA — ACTIVE

Canonical procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Incident record:

`docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`

Ref2VA remains directly relevant because `<Picture 1>` can define Exilada appearance while `<Video 1>` supplies motion/performance and the model generates a complete character video.

## Runner46 — BOOTSTRAP PASS, NOT FULL GRAPH-INTEGRATION PROOF

Runner46 successfully installed/verified:

- ComfyUI v0.34.0;
- Ref2VA INT8 ConvRot diffusion weights;
- NVFP4 Qwen3-VL encoder;
- H3 video VAE;
- Exilada input and normalized 24fps/124f driver;
- required node classes/object-info.

The later Runner47 prompt submission showed that object/class availability was insufficient as a complete integration proof because the actual `MiniMaxH3ReferenceToVideo` graph also required `audio_vae`.

## Runner47 — PRE-INFERENCE INTEGRATION FAIL

Exact failure:

```text
HTTP 400
prompt_outputs_failed_validation
MiniMaxH3ReferenceToVideo
Required input is missing: audio_vae
```

Classification: **INTEGRATION_FAIL / PROMPT VALIDATION / PRE-INFERENCE**.

No `prompt_id` was returned; no H3 denoising occurred. This is not a quality failure.

## Corrected minimal Ref2VA dependency set

- diffusion: `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (~21GB);
- text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (~15.7GB);
- video VAE: `minimax_h3_video_vae_fp16.safetensors` (~5.21GB);
- **required audio VAE:** `minimax_h3_audio_vae_fp32.safetensors`, `605,254,808` bytes, SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`.

Corrected payload is approximately **42.5GB**.

The audio VAE is required by the node schema even though H0 uses no audio reference and does not decode audio.

## H0 quality baseline — UNCHANGED

- Base Ref2VA;
- `<Picture 1>` = canonical Exilada appearance;
- `<Video 1>` = same Wan comparison driver, timestamp-resampled to24fps/124f with no crop/resize/tracking/recentering;
- `448×800`;
-124 frames @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep`;
- `beta`;
- seed0;
- sigma shifts video12/audio3;
- no FL2VA, Turbo or style embedding;
- no audio reference or audio decode.

## CURRENT — Runner48

Runner48 repairs only the integration dependency and reruns the same H0 quality experiment:

`tools/structured-2d-character-pipeline/48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1`

If it reaches `H3-H0: prompt_id=...`, prompt validation passed and real H3 inference began.

## Finite H3 next decisions

Only after a completed H0 video:

- strong topology/motion + weak identity only -> `ref_image_size=max`;
- under-resolved anatomy/detail -> `480×864`, then `512×896`, then at most one 768-short-edge control;
- good H0 -> advance to a game-relevant walking/secondary-motion driver;
- major model/task failure after integration is proven -> diagnose once, not endless grid search.

## Required QA

Judge completed H3 video at full source scale and at the gameplay-scale proxy. Missing/reordered body parts, topology changes, detached limbs, broken silhouette or identity drift remain failures even if downsampling hides detail.

## Cleanup

- do not accumulate alternate H3 task families/quantizations;
- keep the audio VAE as part of the minimal active Ref2VA dependency set;
- preserve W1L proof/results/manifests;
- remove paused Wan large checkpoints only after H3 is technically proven active enough that immediate return is unnecessary;
- keep SSD comparison evidence until explicit abandonment/final verdict.
