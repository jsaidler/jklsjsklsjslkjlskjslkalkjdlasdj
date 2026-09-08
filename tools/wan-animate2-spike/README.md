# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 PAINTERLY LOOK APPROVED / W1A 1.5 STRUCTURAL BRANCH RETAINED / W1F LETTERBOX CLOSED / W1G TRACKED DRIVER REFRAMING CLOSED FAIL / W1H ASPECT-MATCHED RAW-DRIVER GEOMETRY PASS / W1I POSE-END BLUR TEST CURRENT.**

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

`run_w1g_subject_framing_ref15.py` + Runner 40 generated a valid tracked/recentered result, but it materially worsened ghosting, limb topology and temporal coherence.

Conclusion: do not continue tracking/repositioning/affine camera-follow manipulation of raw driving footage. Preserve raw spatiotemporal motion.

## Geometry finding — LOCKED

Current ComfyUI `WanAnimate2ToVideo` center-resizes/crops `pose_video` to requested output geometry.

- raw driver: `480×854`, aspect ≈ 0.5621
- upstream Wan demo default: `720×1280`, aspect 0.5625
- old W1/W1A canvas: `640×800`, aspect 0.8

Old geometry retained only about 70.3% of source height before pose conditioning.

Policy: **leave the raw driver untouched and match Wan generation aspect to that driver.**

## `run_w1h_aspect_matched_ref15.py` — GEOMETRY PASS

Runner 41 changed only `640×800 -> 512×912` on the exact W1A branch.

Completed result:

- prompt id `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46 s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- estimated pose-video retention `99.88%`.

Visual review: catastrophic top/head/right-body crop resolved; body topology/temporal coherence materially improved; hair/cloth remain dynamic; later frames are cleaner. Residual high-motion blur remains mainly around frames ~8–10 and chain topology remains imperfect. A few lateral edge contacts follow source performer traversal and should be handled by selecting production drivers with safe real margins, not by tracking.

Classification: **W1H geometry PASS / current best baseline.**

## `run_w1i_pose_end70_ref15.py` — CURRENT

Runner:

`tools/structured-2d-character-pipeline/42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1`

Parent = exact W1H prompt.

Only changed axis:

`pose_end_percent 1.00 -> 0.70`

Native WanAnimate2ToVideo docs state motion is mostly established early and give ~0.7 as an example that can loosen fine detail while retaining choreography. W1I therefore isolates residual blur without changing raw driver, geometry, pose strength, prompt, seed or model.

The executor:

1. requires completed W1H evidence;
2. verifies `512×912`, ref strength 1.5, pose strength 1.0, pose start 0.0, pose end 1.0;
3. changes only `pose_end_percent` to 0.70 plus output prefix;
4. runs the same BF16 graph/seed/sampler/settings;
5. writes `w1i_api_prompt.json`, `w1i_run_manifest.json` and canonical output.

Expected:

- `Z:\AI\WanAnimate2\w1i_exilada_poseend70_ref15.mp4`
- `Z:\AI\WanAnimate2\w1i_run_manifest.json`
- `Z:\AI\WanAnimate2\w1i_api_prompt.json`
- `Z:\AI\WanAnimate2\w1i_executor.log`

Prefer W1I over W1H only if destructive blur falls without losing topology, motion adherence, hair/cloth dynamics or framing.

## Current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1"
```

## Cleanup

Remove large model variants when they no longer belong to the active hypothesis. Preserve small evidence. Keep the current Base-BF16 route while Wan is under exhaustion.
