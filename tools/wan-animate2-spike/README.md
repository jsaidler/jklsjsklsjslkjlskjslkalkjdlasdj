# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 PAINTERLY LOOK APPROVED / W1A 1.5 STRUCTURAL BRANCH RETAINED / W1F LETTERBOX CLOSED / W1G TRACKED DRIVER REFRAMING CLOSED FAIL / W1H ASPECT-MATCHED RAW-DRIVER GATE CURRENT.**

## Paths / hardware

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- Wan workspace: `Z:\AI\WanAnimate2`
- Windows 11 / RTX 3060 12 GB / 48 GB RAM
- `D:\AI` is stale.

## Active BF16 set

- `models/diffusion_models/wan_animate_2_bf16.safetensors`
- `models/text_encoders/umt5_xxl_fp16.safetensors`
- `models/clip_vision/clip_vision_h.safetensors`
- `models/vae/Wan2_1_VAE_bf16.safetensors`

Do not pre-download alternate large variants.

## W0 / W1 / W1A

W0 proved local Base-BF16 direct-driving integration with `--disable-pinned-memory`.

W1 produced the approved painterly visual language and strong raw-video motion, but crop/restraint/limb issues remain.

W1A (`reference_image_strength=1.5`) is retained as the stronger body-structure branch despite more destructive blur.

## W1F — CLOSED

`run_w1f_safe_framing.py`: whole-frame letterboxing did not solve generated crop.

## W1G — CLOSED VALID METHOD FAIL

`run_w1g_subject_framing_ref15.py` + Runner 40 eventually generated a valid v3.1 result after tracked subject-framing preflights passed.

The generated animation was materially worse: stronger ghosting/smearing, elongated/unstable body and limbs, detached/duplicated-looking extremities, degraded temporal coherence and no reliable framing solution.

Conclusion: do not continue tracking/repositioning/affine camera-follow manipulation of the raw driver. Wan is consuming richer spatiotemporal information; synthetic frame-to-frame camera motion damages it.

Keep W1G mp4/log/manifests only as small evidence.

## Geometry finding that motivates W1H

Current ComfyUI `WanAnimate2ToVideo` center-resizes `pose_video` to requested output geometry.

- raw driver: `480×854`, aspect ≈ 0.5621
- upstream Wan-Animate-2 demo default: `720×1280`, aspect 0.5625
- W1/W1A canvas: `640×800`, aspect 0.8

Center-cropping 480×854 to aspect 0.8 retains only about 70.3% of the original height. The next experiment therefore changes the Wan canvas aspect while leaving the driver untouched.

## `run_w1h_aspect_matched_ref15.py` — CURRENT

Runner:

`tools/structured-2d-character-pipeline/41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1`

Parent = exact W1A prompt.

Only changed axis:

`Wan width/height 640×800 -> 512×912`

The executor:

1. verifies W1A is complete and uses ref strength 1.5;
2. reads the original raw-driver geometry;
3. calculates source/parent/target aspect and estimated center-crop retention;
4. refuses an unexpectedly mismatched target aspect;
5. changes only `WanAnimate2ToVideo.width/height` plus output prefix;
6. leaves raw driver bytes and trajectory untouched;
7. runs the same BF16 graph/seed/sampler/settings;
8. writes `w1h_api_prompt.json`, `w1h_run_manifest.json` and canonical output.

Expected:

- `Z:\AI\WanAnimate2\w1h_exilada_aspectmatched_ref15.mp4`
- `Z:\AI\WanAnimate2\w1h_run_manifest.json`
- `Z:\AI\WanAnimate2\w1h_api_prompt.json`
- `Z:\AI\WanAnimate2\w1h_executor.log`

Pass only if full-body framing improves without W1G-style temporal/anatomical degradation. Blur is the next isolated axis only after framing passes.

## Current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1"
```

## Cleanup

Remove large model variants when they no longer belong to the active hypothesis. Preserve small evidence. Keep the current Base-BF16 route while Wan is under exhaustion.
