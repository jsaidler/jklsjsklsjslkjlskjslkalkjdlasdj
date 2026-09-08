# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / MINIMAX H3 REF2VA H0 PASS_CANDIDATE / H1 GAME-RELEVANT WALK NEXT / WAN PAUSED / SCAIL-2 LATER IF NEEDED**

## Purpose

Select a production model that generates the complete Exilada from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

The model must consume richer information than skeleton-only pose and automatically infer locomotion, soft-body response, long-hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

## Screening order — LOCKED 2026-09-08

1. **MiniMax H3 Base Ref2VA — ACTIVE / PASS_CANDIDATE after H0.**
2. Wan-Animate-2 — **PAUSED AFTER W1L**, not exhausted.
3. SCAIL-2 — later only if H3 fails a later production gate.

## Comparison protocol

- distinguish infrastructure, integration, configuration and model/task failures;
- fixed inputs/seeds unless a variable is intentionally changed;
- no seed fishing or manual rescue;
- successful inference is not automatically a model-quality PASS;
- pre-inference integration failures are zero model-quality evidence;
- after a family shows a strong baseline, advance to more game-relevant drivers instead of endlessly tuning nearby settings.

## Wan canonical history

- W0 local Base-BF16 integration passed with `--disable-pinned-memory`.
- W1 established approved painterly/motion language.
- W1A ref1.5 appeared structurally stronger but more ghosted under old geometry.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H `512×912` with untouched driver solved dominant crop and became best documented Wan geometry baseline.
- W1I pose-end0.70 did not materially improve blur/structure.
- W1J/W1K prepared but never executed.
- W1L completed ref1.0 + pose0.80 +30 steps; Wan paused afterward. Preserve proof/results.

## MiniMax H3 Base Ref2VA — ACTIVE

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

Incident record: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

### Integration history

- Runner46 installed/prepared the pinned environment and H0 inputs.
- Runner47 was rejected before inference because `MiniMaxH3ReferenceToVideo.audio_vae` is required by ComfyUI v0.34.0 even with no audio references.
- classification: **INTEGRATION_FAIL / PRE-INFERENCE**; no `prompt_id`, no sampling, no quality evidence.
- Runner48 added the official audio VAE as a schema dependency only and reran the otherwise unchanged H0.

### Correct minimal H3 Ref2VA set

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (~21GB)
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (~15.7GB)
- `minimax_h3_video_vae_fp16.safetensors` (~5.21GB)
- `minimax_h3_audio_vae_fp32.safetensors` (~605MB; schema-required)

Total active payload ~42.5GB. No FL2VA, Turbo, style embedding or alternate quantization is installed.

## H0 / Runner48 — COMPLETE

Exact baseline:

- Base Ref2VA;
- Picture1 = canonical Exilada master;
- Video1 = same raw Wan comparison driver, timestamp-resampled to24fps/124f only;
- `448×800`;
-124 frames @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep` + `beta`;
- seed0;
- sigma shifts video12/audio3;
- no crop/resize/tracking/recentering;
- no audio reference/decode;
- no FL2VA/Turbo/style embedding.

Completion:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

## H0 visual verdict — PASS_CANDIDATE

The uploaded full-resolution H0 and gameplay proxy were reviewed across the sequence.

**Family advances.**

Strengths:

- materially stable body topology over 124 frames;
- no destructive global smear/ghost-double;
- face, torso, limbs, body proportions, hair mass and costume language remain coherent;
- hair and torn cloth show secondary motion while staying attached;
- restraints/chains remain accessory geometry rather than morphing into body parts;
- sharpness remains high enough that anatomy stays readable during motion;
- painterly dark-fantasy output matches the locked visual direction well;
- gameplay-scale silhouette remains clear near the ~128px target.

Residual defects:

- chain curvature/length/attachment details still drift somewhat;
- late in the clip the character reaches the right edge and the right foot becomes partially cropped. Treat this as a **driver/framing-envelope issue**, not body-topology collapse;
- exact reference fidelity remains an art-finalization check, although internal identity is stable throughout H0.

## Resolution verdict

`448×800` passes. Do not raise output resolution now. The proxy remains readable and H0 does not show an under-resolution failure. `ref_image_size=max` is also deferred because identity does not show a clear collapse warranting the extra cost.

## NEXT — H1 GAME-RELEVANT WALK

Use a real fixed-camera full-body walking/performance video with safe margins and at least one complete gait cycle. Target screen-left, mostly lateral/slight3/4, consistent with the locked `72°` first locomotion baseline.

Keep H0 quality settings initially:

- `448×800`;
- Base50;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`.

H1 pass criteria:

- walk timing/weight transfer follows the real driver;
- full body remains in-frame without driver-forced crop;
- topology remains H0-level stable through a full gait cycle;
- hair/cloth/restraints respond dynamically;
- gameplay-scale silhouette supports an actual locomotion spritesheet.

After H1 passes, advance to stronger secondary-motion/wind/restraint stress. Speed/Turbo experiments come only after quality is locked.

## Cleanup

H3 is now technically and visually proven active enough that paused Wan **large model weights may be deleted** while preserving W1H/W1L videos, prompts, manifests and logs. Keep the minimal H3 four-file Ref2VA set. Do not accumulate alternate H3 families/quantizations without an explicit hypothesis. Keep SSD comparison evidence until explicit abandonment/final verdict.
