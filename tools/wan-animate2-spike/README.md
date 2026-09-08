# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 PAINTERLY LOOK APPROVED / W1H GEOMETRY PASS / W1I POSE-END 0.70 NOT PREFERRED / W1J REF-ONLY TEST SUPERSEDED BEFORE RUN / W1K POSE-STRENGTH 0.80 CURRENT.**

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
- W1J: ref1.0-only tooling exists but is superseded before execution.

## Geometry note

Current ComfyUI center-resizes/crops pose video to generation geometry. W1H empirically improved body retention by switching from `640×800` to `512×912` while leaving the `480×854` driver untouched.

Wan upstream examples expose different dimensions (`640×800` YAML, `720×1280` demo CLI); do not use one upstream default as proof. Keep the empirical Comfy rule: preserve raw driver and use compatible generation aspect.

## `run_w1k_pose_strength80_ref15.py` — CURRENT

Runner:

`tools/structured-2d-character-pipeline/44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1`

Parent = exact W1H.

Only changed axis:

`pose_strength 1.00 -> 0.80`

Everything else stays W1H: raw driver untouched, `512×912`, ref1.5, pose start0, pose end1.0, seed0,20 steps,CFG1,Euler/simple,shift5,same Exilada reference/prompt,CLIP pose branch and negative prompt.

Purpose: directly reduce pose-video forcing because the remaining defect combines heavy motion-phase smear and structural deformation. ComfyUI defines pose strength as the direct scale of pose-video influence, and the Animate-2 model path scales pose-branch values accordingly.

Expected:

- `Z:\AI\WanAnimate2\w1k_exilada_posestrength080_ref15.mp4`
- `Z:\AI\WanAnimate2\w1k_run_manifest.json`
- `Z:\AI\WanAnimate2\w1k_api_prompt.json`
- `Z:\AI\WanAnimate2\w1k_executor.log`

Pass only if blur **and structural deformation** improve materially without unacceptable choreography/identity/hair/cloth loss.

## Current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1"
```

## Cleanup

No new large checkpoint. Preserve small evidence. Keep Base-BF16 while Wan is under exhaustion.
