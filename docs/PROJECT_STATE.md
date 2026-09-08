# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
4. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`
7. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
8. `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`
9. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active MiniMax H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Runtime / game presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native game raster `640×360`;
- pitch `26°`;
- protagonist about `128 px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- `72°` current screen-left baseline;
- runtime consumes **complete precomposed character sprites** only.

Production contract:

`complete appearance reference + raw driving video + automatic preprocessing -> complete animated frames -> automatic extraction/packing -> spritesheet/atlas + metadata -> ordinary sprite playback`

No routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing.

## Visual direction — LOCKED

- painterly / illustrated 2D dark fantasy;
- explicit 1980s sword-and-sorcery charge;
- Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell lineage;
- adult sensuality/nudity legitimate;
- localized restrained blur may be positive;
- destructive blur/ghosting that erases anatomy/topology/readability is a defect;
- later Exilada art gate may use more severely torn cloth, more body exposure and possible partial breast exposure consistent with captivity/damage.

## Complete-character production contract — LOCKED

The production model must combine the complete Exilada appearance reference with an arbitrary real driving video, consuming richer motion than a skeleton-only pose stream and automatically inferring locomotion, soft response, long-hair inertia, cloth/material behavior and restraint/accessory dynamics. Final runtime artifacts are complete precomposed sprite frames.

## Model-screening order — UPDATED / LOCKED 2026-09-08

1. **MiniMax H3 Base Ref2VA is the active screening route.**
2. Wan-Animate-2 is **PAUSED AFTER W1L**, not `EXHAUSTED_FAIL`.
3. SCAIL-2 remains later only if H3 does not satisfy the production contract.

## Wan history — compact canonical record

- W0 / Runner36: local Base-BF16 direct-driving integration PASS with `--disable-pinned-memory`.
- W1 / Runner37 ref1.0: approved painterly visual/motion language; crop, restraint and limb artifacts remained.
- W1A / Runner38 ref1.5: structurally stronger under the old geometry but more ghosted.
- W1F / Runner39: whole-frame letterbox did not solve crop; CLOSED.
- W1G / Runner40: tracked/recentered driver worsened ghosting and temporal anatomy; CLOSED.
- W1H / Runner41: `512×912` with untouched raw driver resolved dominant crop and became best documented Wan geometry baseline.
- W1I / Runner42: pose-end0.70 did not materially improve blur/structural failure; NOT PREFERRED.
- W1J / Runner43 and W1K / Runner44 were prepared but never executed.
- W1L / Runner45: completed compound branch ref1.0 + pose0.80 +30 steps; Wan paused afterward. Preserve local proof. No visual verdict invented without reviewing the local video.

## MiniMax H3 Ref2VA — ACTIVE

Canonical procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Why it qualifies:

- Ref2VA natively accepts image and video references;
- `<Picture 1>` maps to Exilada appearance/identity;
- `<Video 1>` maps to real motion/performance;
- output is a complete generated video character rather than a skeleton-only representation.

### Runner46 / bootstrap — PASS WITH LATER-DISCOVERED GRAPH OMISSION

Runner46 completed local install/preflight successfully and verified:

- pinned ComfyUI v0.34.0;
- Ref2VA diffusion checkpoint;
- NVFP4 Qwen3-VL encoder;
- video VAE;
- prepared Exilada and 24fps/124f driver;
- presence of required node classes and object-info.

This remains an **INFRASTRUCTURE BOOTSTRAP PASS**, but it was **not a complete graph-integration proof**: the live node class existed, yet the first actual API prompt later revealed a required `audio_vae` input that Runner46 had not wired or downloaded.

### Runner47 / first H0 submission — PRE-INFERENCE INTEGRATION FAIL

Observed terminal error:

```text
HTTP 400
prompt_outputs_failed_validation
MiniMaxH3ReferenceToVideo
Required input is missing: audio_vae
```

Classification: **INTEGRATION_FAIL / PROMPT VALIDATION / PRE-INFERENCE**.

Important:

- no `prompt_id` was issued;
- no H3 denoising/inference occurred;
- this is **zero model-quality evidence**;
- H0 quality settings were never exercised.

Root cause: pinned ComfyUI v0.34.0 declares `MiniMaxH3ReferenceToVideo.audio_vae` as required even when H0 provides no audio reference and does not decode audio.

Incident record:

`docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`

### Corrected H0 required model set

The original three files remain:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (~21 GB);
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (~15.7 GB);
- `minimax_h3_video_vae_fp16.safetensors` (~5.21 GB).

A fourth **schema-required** file is now added:

- `minimax_h3_audio_vae_fp32.safetensors`;
- size `605,254,808` bytes (~605 MB);
- SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`.

Corrected H0 H3 payload is approximately **42.5 GB**.

The audio VAE does **not** change the experiment into an audio task. H0 still:

- supplies no audio reference;
- performs no audio decode/output;
- uses the audio VAE only because the Ref2VA node schema requires the input.

### H0 exact quality settings — UNCHANGED

- Base Ref2VA;
- canvas `448×800`;
- 124 frames @24fps;
- `ref_image_size=match`;
- 50 steps;
- sampler `res_multistep`;
- scheduler `beta`;
- seed0;
- H3 default sigma shifts video12/audio3;
- canonical Exilada master as Picture1;
- same raw Wan comparison driver as Video1, timestamp-resampled to24fps/124f with **no crop, resize, tracking or recentering**;
- no FL2VA;
- no Turbo LoRA;
- no style embedding.

## CURRENT GATE — Runner48 H0 integration repair + inference

New tooling:

- `tools/minimax-h3-spike/run_h0_ref2va_audio_vae_required.py`
- `tools/structured-2d-character-pipeline/48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1`

Runner48:

1. downloads/resumes the official 605 MB audio VAE if absent;
2. verifies SHA256 and byte size;
3. launches the same pinned ComfyUI v0.34.0 environment;
4. wires `audio_vae` into `MiniMaxH3ReferenceToVideo`;
5. leaves every H0 quality variable unchanged;
6. submits H0.

Exact operator action:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1"
```

If terminal reaches:

```text
H3-H0: prompt_id=...
```

the integration fix passed prompt validation and actual H3 inference started.

Expected proof after successful completion:

- `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`
- `Z:\AI\MiniMaxH3\h0_run_manifest.json`
- `Z:\AI\MiniMaxH3\h0_api_prompt.json`
- `Z:\AI\MiniMaxH3\h0_executor.log`
- `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4` when preview encoding succeeds.

## H3 resolution strategy — LOCKED

First target remains `448×800`; do not change resolution because of the Runner47 integration failure.

Finite escalation only after successful H0 inference and visual evidence:

1. `480×864` if specifically under-resolved;
2. `512×896` if still needed;
3. one 768-short-edge control only if needed to distinguish low-resolution failure from model/task failure.

If motion/topology is excellent and identity alone is weak, test `ref_image_size=max` before increasing output resolution.

## Gameplay-scale QA — REQUIRED

Judge H3 candidates twice:

1. source scale — anatomy, temporal topology, identity, motion adherence, hair/cloth/restraint dynamics;
2. gameplay-scale proxy — silhouette/readability near the ~128px runtime character target.

Downsampling may make minor local blur irrelevant. It cannot excuse missing/reordered body parts, topology changes, detached limbs, broken silhouette or identity drift.

## Failure classification

- download/hash/extract/version → infrastructure;
- missing/changed Comfy node/API graph → integration;
- CUDA/DynamicVRAM/host-buffer/OOM/runtime crash → infrastructure until diagnosed;
- completed video with bad topology/motion/identity → model/task or configuration evidence according to the observed defect.

No pre-inference integration or infrastructure failure counts as model-quality evidence.

## Cleanup

- do not accumulate alternate H3 task families/quantizations;
- audio VAE is now part of the minimal Ref2VA dependency set and must be kept while H3 is active;
- preserve Wan W1L proof/results/manifests;
- after H3 is technically proven active enough that immediate Wan return is unnecessary, remove paused Wan large checkpoint weights while preserving proof/results;
- keep SSD comparison evidence until explicit abandonment/final model verdict.
