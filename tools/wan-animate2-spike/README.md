# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 PAINTERLY LOOK APPROVED / W1H GEOMETRY PASS / W1I POSE-END 0.70 NOT PREFERRED / W1J/W1K SUPERSEDED BEFORE RUN / W1L REF1.0 + POSE0.80 + 30 STEPS CURRENT.**

## Paths / hardware

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- Wan workspace: `Z:\AI\WanAnimate2`
- Windows 11 / RTX 3060 12 GB / 48 GB RAM
- `D:\AI` stale.

## Active BF16 set

- `models/diffusion_models/wan_animate_2_bf16.safetensors`
- `models/text_encoders/umt5_xxl_fp16.safetensors`
- `models/clip_vision/clip_vision_h.safetensors`
- `models/vae/Wan2_1_VAE_bf16.safetensors`

Do not pre-download alternate large variants.

## Closed / retained evidence

- W0: local route passed with `--disable-pinned-memory`.
- W1/W1A: approved painterly direction; old geometry confounded crop/structure.
- W1F: letterbox failed crop.
- W1G: tracked/recentered driver worsened temporal anatomy; closed.
- W1H: `512×912` aspect-compatible raw-driver path is current best geometry baseline.
- W1I: `pose_end_percent=0.70` produced no material improvement.
- W1J: ref1.0-only tooling prepared but not run.
- W1K: pose_strength0.80-only tooling prepared but not run.

## Geometry note

Current ComfyUI center-resizes/crops pose video to generation geometry. W1H empirically improved body retention by switching from `640×800` to `512×912` while leaving the `480×854` driver untouched.

Wan upstream examples expose different dimensions (`640×800` YAML, `720×1280` demo CLI); do not use one upstream default as proof. Keep the empirical Comfy rule: preserve raw driver and use compatible generation aspect.

## `run_w1l_ref10_pose80_steps30.py` — CURRENT

Runner:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Parent = exact completed W1H.

Compound changes:

- `reference_image_strength 1.5 -> 1.0`
- `pose_strength 1.00 -> 0.80`
- `steps 20 -> 30`

Everything else stays W1H: raw driver untouched, `512×912`, pose start0, pose end1.0, seed0, CFG1, Euler/simple, shift5, same Exilada reference/prompt, CLIP pose branch and negative prompt.

Policy: **COMPOUND_CONFIGURATION_SEARCH**. This is intentionally not a one-variable causal test. Purpose: attack the remaining heavy motion-phase blur and structural deformation together and determine whether a materially better operating point exists.

Expected:

- `Z:\AI\WanAnimate2\w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4`
- `Z:\AI\WanAnimate2\w1l_run_manifest.json`
- `Z:\AI\WanAnimate2\w1l_api_prompt.json`
- `Z:\AI\WanAnimate2\w1l_executor.log`

Pass only if blur **and structural deformation** improve materially without unacceptable choreography/identity/hair/cloth/framing loss.

## Current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1"
```

## Cleanup

No new large checkpoint. Preserve small evidence. Keep Base-BF16 while Wan is under exhaustion.
