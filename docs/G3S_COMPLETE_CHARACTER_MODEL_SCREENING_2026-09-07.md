# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN PAUSED AFTER OPERATOR-REPORTED W1L COMPLETION / MINIMAX H3 BASE REF2VA ACTIVE / RUNNER46 BOOTSTRAP NEXT / H0 448×800 BASE50 DEFINED / SCAIL-2 LATER IF NEEDED**

## Purpose

Select a production model that generates the complete Exilada from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

The model must consume richer information than skeleton-only pose and automatically infer locomotion, soft-body response, long-hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

## Screening order — LOCKED 2026-09-08

1. **MiniMax H3 Base Ref2VA** — active screening route.
2. Wan-Animate-2 — **PAUSED AFTER W1L**, not exhausted.
3. SCAIL-2 — later only if H3 does not satisfy the production contract.

The prior rule that Wan had to reach `EXHAUSTED_FAIL` before another family could be screened is superseded.

## Comparison protocol

- distinguish infrastructure, integration, configuration and model/task failures;
- fixed inputs/seeds unless the variable is intentionally changed;
- one-variable experiments by default;
- compound configuration searches allowed when explicitly labeled;
- no seed fishing or manual rescue;
- successful inference is not automatically a model-quality PASS;
- do not delete proof/results while a family comparison is still active.

## Wan canonical history

- W0: local Base-BF16 route passed with `--disable-pinned-memory`.
- W1 ref1.0: approved painterly/motion language; crop/restraint/limb issues.
- W1A ref1.5: stronger apparent topology but more ghosting under old geometry.
- W1F: whole-frame letterbox failed crop; closed.
- W1G: tracked/recentered raw driver worsened ghosting and temporal anatomy; closed permanently.
- W1H: `512×912` with untouched `480×854` driver fixed dominant crop and became best Wan geometry baseline; heavy fast-motion smear plus structural changes remained.
- W1I: pose-end0.70 did not materially improve those defects; not preferred.
- W1J / W1K: prepared, never executed, superseded before run.

## W1L — OPERATOR-REPORTED COMPLETE / WAN PAUSED

Runner45 used the exact W1H parent and deliberately changed:

- `reference_image_strength 1.5 -> 1.0`;
- `pose_strength 1.00 -> 0.80`;
- `steps 20 -> 30`.

The user reported completion and chose to move immediately to H3. The repository does **not** invent a W1L visual verdict without seeing the local result. Runner46 requires the local W1L video/prompt/manifest and verifies `status=INFERENCE_COMPLETE` before H3 bootstrap proceeds.

Preserve W1L evidence in `Z:\AI\WanAnimate2` for comparison. Do not launch another Wan inference while H3 is active.

## MiniMax H3 Base Ref2VA — ACTIVE

Canonical procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Why it qualifies:

- `MiniMaxH3ReferenceToVideo` natively accepts image/video references;
- `<Picture 1>` can define Exilada appearance/identity;
- `<Video 1>` can define real movement/performance;
- output is a complete generated video character;
- current ComfyUI supplies a pruned/quantized local route appropriate for controlled consumer-GPU screening.

Only **Ref2VA** is installed for H0. Do not download FL2VA in parallel.

## H3 pinned H0 stack

- ComfyUI NVIDIA Windows portable **v0.34.0**, dedicated workspace;
- H3 workspace: `Z:\AI\MiniMaxH3`;
- H3 API port: `8190`;
- default DynamicVRAM behavior; no inherited Wan flags;
- diffusion: `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (~21 GB);
- text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (~15.7 GB);
- video VAE: `minimax_h3_video_vae_fp16.safetensors` (~5.21 GB).

Selected H0 model payload is ~41.9 GB. H0 does not install FL2VA, Turbo LoRA, embeddings, alternate quantizations or audio VAE.

## H0 — CURRENT EXPERIMENT

Exact baseline:

- Base Ref2VA;
- `<Picture 1>` = canonical Exilada appearance only;
- `<Video 1>` = motion/performance only;
- same raw driver used for the Wan comparison branch, timestamp-resampled to 24fps/124 frames with no spatial crop/resize/tracking/recentering;
- output `448×800`;
- 124 frames at24fps;
- `ref_image_size=match`;
- 50 steps;
- sampler `res_multistep`;
- scheduler `beta`;
- seed0;
- H3 model default sigma shifts video12/audio3;
- no Turbo LoRA.

Runner46 prepares/verifies the environment and performs no inference. Runner47 runs H0 only after Runner46 PASS.

## H3 local-resolution strategy

The game uses a protagonist around `128 px` tall, so screening optimizes for final sprite use rather than blindly generating at the maximum resolution.

First local target: **`448×800`**.

Rationale:

- both dimensions divisible by32;
- aspect close to the portrait driver;
- 358,400 pixels;
- visual latent grid `28×50=1400` cells versus `84×48=4032` at `1344×768`, about34.7% of that spatial cell count;
- still several times larger than final runtime character scale.

This reduces spatial activation work but not model-weight size or all offload/RAM cost.

Finite escalation only if H0 is under-resolved:

1. `480×864`;
2. `512×896`;
3. one 768-short-edge control.

If motion/topology is strong and identity alone is weak, test `ref_image_size=max` before increasing output resolution.

## Required H3 QA

Judge every H3 candidate at:

1. full generated resolution — stable body topology/anatomy, identity, motion adherence, hair/cloth/restraint dynamics, absence of destructive whole-body smear;
2. gameplay-scale proxy — silhouette/readability near the ~128px runtime character target.

Downsampling may erase harmless texture noise or restrained local blur. Missing/reordered body parts, topology changes, detached limbs, broken silhouette or identity drift remain failures.

## Failure classification

- download/hash/extraction/version → infrastructure;
- missing/changed Comfy node/API graph → integration;
- CUDA/DynamicVRAM/host-buffer/OOM/runtime crash → infrastructure until diagnosed;
- completed video with bad topology/motion/identity → model/task or configuration evidence according to the observed defect.

No infrastructure failure counts as model-quality evidence.

## Current sequence

- Wan W0–W1I — documented history;
- Wan W1L — **operator-reported complete; visual verdict not invented; Wan paused**;
- H3 Runner46 — **CURRENT: bootstrap/preflight**;
- H3 Runner47 / H0 Base50 `448×800` — next after Runner46 PASS;
- if needed: identity-only `ref_image_size=max` or finite resolution ladder;
- walking/secondary-motion driver only after H0 proves the family technically useful;
- SCAIL-2 only later if H3 fails the contract.

## Cleanup

- do not accumulate alternate H3 task families/quantizations;
- preserve W1L proof/results/manifests;
- after H3 is technically proven active enough that immediate Wan return is unnecessary, remove paused Wan **large checkpoint weights** while keeping proof/results;
- keep SSD comparison evidence until explicit abandonment/final model verdict.
