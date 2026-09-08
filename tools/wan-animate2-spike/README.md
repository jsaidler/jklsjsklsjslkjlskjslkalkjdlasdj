# Wan-Animate-2 validation / exhaustion tooling

Status: **W1L RUNNING. AFTER W1L, WAN IS PAUSED AND MINIMAX H3 REF2VA BECOMES THE ACTIVE COMPLETE-CHARACTER SCREENING ROUTE.**

## Paths / hardware

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- Wan workspace: `Z:\AI\WanAnimate2`
- planned H3 workspace: `Z:\AI\MiniMaxH3`
- Windows 11 / RTX 3060 12 GB / 48 GB RAM
- `D:\AI` stale.

## Wan active BF16 set

- `models/diffusion_models/wan_animate_2_bf16.safetensors`
- `models/text_encoders/umt5_xxl_fp16.safetensors`
- `models/clip_vision/clip_vision_h.safetensors`
- `models/vae/Wan2_1_VAE_bf16.safetensors`

Do not delete these while W1L is running.

## Canonical evidence

- W0: local BF16 route passed with `--disable-pinned-memory`.
- W1/W1A: approved painterly direction; old geometry confounded crop/structure.
- W1F: letterbox failed crop; closed.
- W1G: tracked/recentered driver worsened temporal anatomy; closed.
- W1H: `512×912` with untouched raw driver became best Wan geometry baseline.
- W1I: pose-end0.70 produced no material improvement.
- W1J / W1K: prepared but never run.

## W1L / Runner45 — RUNNING

Runner:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Parent = exact W1H.

Compound changes:

- `reference_image_strength 1.5 -> 1.0`
- `pose_strength 1.00 -> 0.80`
- `steps 20 -> 30`

Everything else stays W1H: raw driver untouched, `512×912`, pose start0, pose end1.0, seed0, CFG1, Euler/simple, shift5, same Exilada reference/prompt, CLIP pose branch and negative prompt.

Expected:

- `Z:\AI\WanAnimate2\w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4`
- `Z:\AI\WanAnimate2\w1l_run_manifest.json`
- `Z:\AI\WanAnimate2\w1l_api_prompt.json`
- `Z:\AI\WanAnimate2\w1l_executor.log`

After W1L, preserve evidence and **do not launch another Wan run before MiniMax H3 Ref2VA screening**.

## Transition decision

Wan does not need to reach `EXHAUSTED_FAIL` before switching families. After W1L it is classified **PAUSED AFTER W1L** while H3 is screened. SCAIL-2 remains later if H3 fails the production contract.

H3 first-spike resolution policy is documented in `docs/PROJECT_STATE.md` and `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`: start at `448×800`, evaluate full source quality and automatic ~128px gameplay-scale quality, then increase only if required.

## Cleanup

Once W1L evidence is secure and H3 is proven active, reevaluate removal of this Wan BF16 asset set. Preserve small proof files. Do not accumulate H3 FL2VA or multiple quantizations without an explicit hypothesis.
