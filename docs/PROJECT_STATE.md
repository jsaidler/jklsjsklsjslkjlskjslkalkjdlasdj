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
8. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

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

1. **MiniMax H3 Base Ref2VA is now the active screening route.**
2. Wan-Animate-2 is **PAUSED AFTER W1L**, not `EXHAUSTED_FAIL`.
3. SCAIL-2 remains a later candidate only if H3 does not satisfy the production contract.

This supersedes the earlier rule that Wan had to reach `EXHAUSTED_FAIL` before another family could be screened.

## Wan history — compact canonical record

- W0 / Runner36: local Base-BF16 direct-driving integration PASS with `--disable-pinned-memory`.
- W1 / Runner37 ref1.0: approved painterly visual/motion language; crop, restraint and limb artifacts remained.
- W1A / Runner38 ref1.5: structurally stronger under the old geometry but more ghosted.
- W1F / Runner39: whole-frame letterbox did not solve crop; CLOSED.
- W1G / Runner40: tracked/recentered driver worsened ghosting and temporal anatomy; CLOSED. Never return to synthetic camera-follow/recentering.
- W1H / Runner41: changed only `640×800 -> 512×912` with untouched `480×854` raw driver and ref1.5. Major crop resolved; best Wan geometry baseline. Prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`, elapsed `1672.46s`, SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`.
- W1I / Runner42: `pose_end_percent 1.0 -> 0.70`; blur/structural failure materially unchanged; NOT PREFERRED.
- W1J / Runner43 and W1K / Runner44 were prepared but never executed; superseded before run.

## W1L / Runner45 — OPERATOR-REPORTED COMPLETE / WAN PAUSED

Parent = exact completed W1H.

Compound configuration search:

- `reference_image_strength 1.5 -> 1.0`;
- `pose_strength 1.00 -> 0.80`;
- `steps 20 -> 30`;
- everything else remains W1H: raw driver untouched, `512×912`, pose window0–1, seed0, CFG1, Euler/simple, shift5, same Exilada reference/prompt/negative/CLIP pose branch.

The user reported the run finished on 2026-09-08 and explicitly chose to move to MiniMax H3. **No W1L visual verdict is invented in the repository without reviewing its local evidence.** Runner46 requires and verifies the local W1L video/prompt/manifest before H3 downloads proceed.

Preserve:

- `Z:\AI\WanAnimate2\w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4`
- `Z:\AI\WanAnimate2\w1l_run_manifest.json`
- `Z:\AI\WanAnimate2\w1l_api_prompt.json`
- `Z:\AI\WanAnimate2\w1l_executor.log`

Do not launch another Wan inference while H3 is active.

## MiniMax H3 Ref2VA — ACTIVE

Canonical procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Why it qualifies:

- Ref2VA natively accepts image and video references;
- `<Picture 1>` maps to Exilada appearance/identity;
- `<Video 1>` maps to real motion/performance;
- the final output is a complete generated video character rather than a skeleton-only representation.

### Pinned H0 local stack

- ComfyUI Windows NVIDIA portable **v0.34.0**;
- dedicated workspace `Z:\AI\MiniMaxH3`;
- port `8190`;
- default ComfyUI DynamicVRAM behavior;
- no custom nodes for H0;
- `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (~21 GB);
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (~15.7 GB);
- `minimax_h3_video_vae_fp16.safetensors` (~5.21 GB).

H0 deliberately does **not** download FL2VA, Turbo LoRA, style embeddings, alternate Ref2VA quantizations or the audio VAE. Selected H3 model payload is ~41.9 GB.

### H0 exact settings

- task: Base Ref2VA;
- canvas: **`448×800`**;
- length: **124 frames**;
- FPS: **24**;
- `ref_image_size=match`;
- 50 inference steps;
- sampler `res_multistep`;
- scheduler `beta`;
- seed0;
- H3 default sigma shifts video12/audio3;
- appearance = canonical `exilada_master.png`;
- motion = same raw driver used by W1H, automatically timestamp-resampled to 24fps/124f with **no crop, resize, tracking or recentering**.

## H3 resolution strategy — LOCKED FOR FIRST SPIKE

Runtime character height is about `128 px`, so full 768p-class generation is not automatically useful. Lower H3 generation resolution is deliberately part of the local production strategy, but **do not generate directly at 128 px**.

First H3 Ref2VA target: **`448×800`**.

- both dimensions are multiples of32;
- aspect `0.56`, close to the current portrait driver;
- 358,400 output pixels;
- H3 visual latent grid about `28×50 = 1400` spatial cells versus `84×48 = 4032` at `1344×768`, about 34.7% of that spatial cell count.

This reduces spatial activation/token work but does not reduce model-weight size or eliminate RAM/offload cost.

Fallback resolution ladder only if H0 is under-resolved:

1. `480×864`;
2. `512×896`;
3. one 768-short-edge control only if needed to separate low-resolution failure from model/task failure.

If H0 motion/topology is excellent and identity alone is weak, test `ref_image_size=max` **before** raising output resolution.

## Gameplay-scale QA — REQUIRED

Every H3 candidate is judged twice:

1. full generated resolution: anatomy, temporal topology, hair/cloth/restraint dynamics, identity and motion adherence;
2. small gameplay proxy: frame downsampled to ~160px high so a subject occupying ~80% of the frame appears around the game's `128 px` character target.

This first proxy is not alpha extraction. Final production still requires automatic extraction/packing.

Downsampling may make minor local blur irrelevant, but it cannot excuse missing/reordered body parts, topology changes, detached limbs, broken silhouette or identity drift.

## Current gates / exact operator action

### Runner46 — bootstrap/preflight only

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\46_prepare_minimax_h3_ref2va.ps1"
```

Runner46 verifies W1L evidence, installs/verifies only the pinned H3 H0 stack, prepares the 24fps driver, validates live Comfy nodes/system stats and **does not infer**.

### Runner47 — H0 inference, only after Runner46 PASS

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\47_run_minimax_h3_ref2va_h0.ps1"
```

Expected H0 evidence:

- `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`
- `Z:\AI\MiniMaxH3\h0_run_manifest.json`
- `Z:\AI\MiniMaxH3\h0_api_prompt.json`
- `Z:\AI\MiniMaxH3\h0_executor.log`
- `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4` when preview encoding succeeds.

Inference completion is a technical pass only; model quality remains a visual gate.

## Failure classification

- hash/download/extract/version failure → infrastructure;
- missing node/API contract failure → integration;
- CUDA/DynamicVRAM/host-buffer/OOM/runtime crash → infrastructure until diagnosed;
- successful video with bad topology/motion/identity → model/task or configuration evidence according to the observed defect.

Do not treat a local H3 infrastructure failure as a model-quality failure.

## Cleanup

- H3 H0 installs one Ref2VA quantization only; do not accumulate FL2VA/alternate H3 variants.
- Do not delete Wan W1L result/manifests/logs.
- Once H3 is technically proven active enough that a return to Wan is not immediately needed, remove the paused Wan **large checkpoint set** to recover disk while preserving proof/results.
- Preserve small manifests/logs/results.
- Keep SSD comparison evidence until explicit abandonment/final model verdict.
