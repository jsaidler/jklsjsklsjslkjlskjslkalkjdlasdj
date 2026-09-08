# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **COMPLETE-CHARACTER RAW-VIDEO GENERATION ACTIVE. WAN IS PAUSED AFTER OPERATOR-REPORTED W1L COMPLETION. MINIMAX H3 BASE REF2VA IS ACTIVE. RUNNER46 BOOTSTRAP/PREFLIGHT IS CURRENT; RUNNER47 H0 FOLLOWS.**

Canonical state: `docs/PROJECT_STATE.md`.

Detailed H3 procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

## Hard production constraints

- complete Exilada appearance reference + separate real driving video;
- driver identity/clothing/hair may differ completely;
- infer body locomotion, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing;
- runtime consumes complete precomposed sprite frames.

## Visual direction

Painterly illustrated dark fantasy with explicit 1980s sword-and-sorcery charge: Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Adult sensuality/nudity is legitimate. Localized motion blur may be positive; global smear, anatomy loss and topology drift are defects.

## Wan record — PAUSED

- W1 established the approved painterly/motion language.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H changed generation geometry to `512×912` while keeping the raw `480×854` driver untouched; dominant crop was solved and temporal body coherence improved.
- W1I pose-end0.70 did not materially improve heavy motion blur/structural changes.
- W1J and W1K were prepared but never executed.
- W1L / Runner45 used ref1.0 + pose0.80 +30 steps on the W1H branch. The user reported completion and chose to switch to H3. A W1L visual verdict is not invented without local review.

W1L proof remains under `Z:\AI\WanAnimate2`. Runner46 verifies `status=INFERENCE_COMPLETE` locally before any H3 model download proceeds.

Do not launch another Wan inference while H3 is active.

## Screening transition — LOCKED 2026-09-08

1. MiniMax H3 Base Ref2VA — active;
2. Wan-Animate-2 — paused after W1L, not exhausted;
3. SCAIL-2 — later only if H3 fails the complete-character contract.

## MiniMax H3 Ref2VA production hypothesis

Ref2VA maps directly to the desired architecture:

`<Picture 1> Exilada appearance + <Video 1> real movement/performance -> complete generated character video -> automatic extraction/downsample/packing -> spritesheet`

The prompt treats Picture1 as the only appearance/identity/anatomy/clothing/hair/art-language source and Video1 as the only movement/timing/weight-transfer source. Driver identity/body/clothing/hair/style are explicitly ignored.

No FL2VA download is needed for the first spike.

## H3 pinned local H0 environment

Workspace:

`Z:\AI\MiniMaxH3`

Pinned components:

- ComfyUI Windows NVIDIA portable `v0.34.0`;
- dedicated port `8190`;
- default DynamicVRAM behavior;
- no custom nodes for H0;
- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`;
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`;
- `minimax_h3_video_vae_fp16.safetensors`.

No H3 FL2VA checkpoint, Turbo LoRA, style embedding, alternate Ref2VA quantization or audio VAE is installed for H0. Selected model payload is approximately 41.9GB.

## H0 exact baseline

- Base Ref2VA, no Turbo;
- output `448×800`;
- 124 frames;
-24fps;
- `ref_image_size=match`;
-50 steps;
- sampler `res_multistep`;
- scheduler `beta`;
- seed0;
- H3 default sigma shifts video12/audio3;
- canonical Exilada master as Picture1;
- same raw Wan comparison driver as Video1, automatically resampled to24fps/124f with **no crop, resize, tracking or recentering**.

H0 is a quality/reference baseline, not a speed test.

## H3 resolution policy — FIRST SPIKE

Runtime character height is about `128 px`. Generating at a 768px short edge is not automatically justified if the model remains structurally sound at a smaller source size.

Initial target: **`448×800`**.

Why:

- both dimensions multiples of32;
- portrait aspect near the current driver;
- 358,400 pixels;
- H3 visual latent grid `28×50=1400` spatial cells versus `84×48=4032` at `1344×768`, about34.7% of that spatial load;
- still substantial supersampling relative to final runtime character scale.

This reduces spatial activation/token work but does not reduce checkpoint size or eliminate RAM/offload cost.

If H0 is under-resolved, escalate only as needed:

`448×800 -> 480×864 -> 512×896 -> one 768-short-edge control`

If motion/topology is already excellent and identity alone is weak, use `ref_image_size=max` before raising output resolution.

Do not generate directly at128px because anatomy/identity/temporal coherence can fail before downsampling.

## Dual-resolution QA — REQUIRED

Every H3 result is evaluated at:

1. **source scale:** body topology, hands/feet, face/identity, torso/breast/hip stability, hair, cloth, restraints, motion adherence and temporal coherence;
2. **gameplay scale:** small whole-frame proxy near the ~128px character use case, followed later by proper automatic extraction/packing.

H0 automatically attempts a portrait-frame proxy of ~160px height; if the character occupies ~80% of the frame, its visible height is near128px. This proxy is not alpha extraction.

Downsampling may make minor texture/detail defects irrelevant. It is not allowed to hide topology loss, missing limbs, detached parts or identity drift.

## Current operational gates

### Runner46 — CURRENT / PREPARE ONLY

`tools/structured-2d-character-pipeline/46_prepare_minimax_h3_ref2va.ps1`

Responsibilities:

- verify completed W1L evidence;
- stop only the known managed Wan Comfy process;
- pin/install SHA-verified ComfyUI v0.34.0;
- download/verify only the selected three H3 H0 model files;
- prepare Exilada and the timing-normalized raw driver;
- validate required H3/core node schemas and system stats;
- write bootstrap evidence;
- perform **no H3 inference**.

### Runner47 — AFTER Runner46 PASS

`tools/structured-2d-character-pipeline/47_run_minimax_h3_ref2va_h0.ps1`

Runs H0 and writes canonical video, API prompt, manifest, logs and gameplay-scale proxy. Inference completion is not automatically a production PASS.

## Failure classification

- download/hash/extraction/pinned-version failure → infrastructure;
- missing H3/core node or invalid API graph → integration;
- CUDA/DynamicVRAM/host-buffer/OOM/runtime failure → infrastructure until diagnosed;
- completed video with poor topology/motion/identity → model/task or configuration evidence according to the failure.

Never classify a local infrastructure crash as a model-quality failure.

## Cleanup

- install only one H3 Ref2VA quantization initially;
- preserve W1L proof/results;
- once H3 is technically proven active enough that immediate return to Wan is unnecessary, remove paused Wan large checkpoint weights while keeping small proof/results;
- do not accumulate H3 FL2VA/Turbo/style assets without an explicit later hypothesis;
- keep SSD comparison material until explicit abandonment/final verdict.
