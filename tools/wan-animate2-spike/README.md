# Wan-Animate-2 validation / exhaustion tooling

Status: **PAUSED AFTER W1L. THE USER REPORTED W1L COMPLETE AND MINIMAX H3 BASE REF2VA IS NOW THE ACTIVE COMPLETE-CHARACTER SCREENING ROUTE. WAN IS NOT `EXHAUSTED_FAIL`.**

## Paths / hardware

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- Windows 11 / RTX 3060 12 GB / 48 GB RAM
- `D:\AI` stale.

## Wan retained BF16 set

- `models/diffusion_models/wan_animate_2_bf16.safetensors`
- `models/text_encoders/umt5_xxl_fp16.safetensors`
- `models/clip_vision/clip_vision_h.safetensors`
- `models/vae/Wan2_1_VAE_bf16.safetensors`

These large weights are temporarily retained only until H3 is technically proven active enough that immediate Wan return is unnecessary. W1L proof/results must be preserved even after eventual large-weight cleanup.

## Canonical evidence

- W0: local BF16 route passed with `--disable-pinned-memory`.
- W1/W1A: approved painterly direction; old geometry confounded crop/structure.
- W1F: letterbox failed crop; closed.
- W1G: tracked/recentered driver worsened temporal anatomy; closed.
- W1H: `512×912` with untouched raw driver became best documented Wan geometry baseline.
- W1I: pose-end0.70 produced no material improvement.
- W1J / W1K: prepared but never run.

## W1L / Runner45 — OPERATOR-REPORTED COMPLETE

Runner:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Parent = exact W1H.

Compound changes:

- `reference_image_strength 1.5 -> 1.0`
- `pose_strength 1.00 -> 0.80`
- `steps 20 -> 30`

Everything else stayed W1H: raw driver untouched, `512×912`, pose start0, pose end1.0, seed0, CFG1, Euler/simple, shift5, same Exilada reference/prompt, CLIP pose branch and negative prompt.

The user reported completion and chose to move to H3. The repo does not invent W1L's visual verdict without local review.

Preserve:

- `Z:\AI\WanAnimate2\w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4`
- `Z:\AI\WanAnimate2\w1l_run_manifest.json`
- `Z:\AI\WanAnimate2\w1l_api_prompt.json`
- `Z:\AI\WanAnimate2\w1l_executor.log`

Runner46 verifies these local files before H3 bootstrap proceeds.

## Transition decision

Wan is **PAUSED AFTER W1L**, not exhausted. Do not launch another Wan inference while H3 is active.

Current H3 procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Current runners:

- `tools/structured-2d-character-pipeline/46_prepare_minimax_h3_ref2va.ps1`
- `tools/structured-2d-character-pipeline/47_run_minimax_h3_ref2va_h0.ps1`

H3 starts at `448×800`, Base50 Ref2VA, with dual full-resolution/gameplay-scale QA. SCAIL-2 remains later only if H3 fails the production contract.

## Cleanup

After H3 is technically proven active and immediate Wan return is no longer needed, remove this paused Wan BF16 large asset set to recover disk. Preserve W1L and earlier proof outputs/manifests/logs required for comparison. Do not accumulate H3 FL2VA or multiple quantizations without an explicit hypothesis.
