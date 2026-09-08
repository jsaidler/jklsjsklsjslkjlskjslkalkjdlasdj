# Wan-Animate-2 validation / exhaustion tooling

Status: **ACTIVE — W0 PASS_BASELINE / W1 PAINTERLY LOOK APPROVED / W1H ASPECT-MATCHED RAW-DRIVER GEOMETRY PASS / W1I POSE-END 0.70 NOT PREFERRED / W1J REF-1.0 CORRECTED-GEOMETRY TEST CURRENT.**

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

## Proven/closed routes

- W0: local Base-BF16 integration passed with `--disable-pinned-memory`.
- W1: approved painterly visual/motion language, but old geometry crop/restraint/limb issues.
- W1A ref1.5: structurally stronger than ref1.0 under old geometry, but blurrier.
- W1F: whole-frame letterbox did not solve crop; closed.
- W1G: tracked/recentered raw driver worsened ghosting/limb topology/temporal coherence; closed. Do not track/recenter raw driver for framing.

## Geometry rule — LOCKED

`WanAnimate2ToVideo` center-resizes/crops `pose_video` to generation geometry.

- raw driver `480×854`, aspect≈0.5621;
- upstream default `720×1280`, aspect0.5625;
- old project `640×800`, aspect0.8.

Old geometry retained only ~70.3% of source height. **Leave raw driver untouched and match generation aspect to driver.**

## `run_w1h_aspect_matched_ref15.py` — GEOMETRY PASS / BEST BASELINE

Runner 41 changed only `640×800 -> 512×912` on W1A.

- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- estimated pose-video retention `99.88%`.

Visual: catastrophic crop resolved; body topology/coherence materially improved; hair/cloth remain dynamic. Residual fast-motion blur ~frames8–10 and chain topology issues remain.

## `run_w1i_pose_end70_ref15.py` — VALID / NOT PREFERRED

Runner 42 changed only `pose_end_percent 1.00 -> 0.70` from W1H.

- prompt `5d4f23ed-f4bf-4b01-a13f-108b2bf31fe0`;
- elapsed `1526.52s`;
- SHA256 `9a9052f40221878ded69f61e452abeda87cfaa42bde475bb5e9809c04763d054`.

Frame-by-frame output is extremely close to W1H; high-motion blur remains and no material topology/framing gain appears. Return pose end to1.0.

## `run_w1j_ref10_aspectmatched.py` — CURRENT

Runner:

`tools/structured-2d-character-pipeline/43_run_wan_animate2_bf16_w1j_aspectmatched_ref10.ps1`

Parent = exact W1H.

Only changed axis:

`reference_image_strength 1.5 -> 1.0`

Everything else stays W1H: raw driver untouched, `512×912`, pose strength1.0, pose start0, pose end1.0, seed0, 20 steps, CFG1, Euler/simple, shift5, same Exilada reference/prompt, CLIP pose branch and negative prompt.

Purpose: retest the earlier cleaner ref1.0 branch after removing the old 640×800 geometry confound.

Expected:

- `Z:\AI\WanAnimate2\w1j_exilada_aspectmatched_ref10.mp4`
- `Z:\AI\WanAnimate2\w1j_run_manifest.json`
- `Z:\AI\WanAnimate2\w1j_api_prompt.json`
- `Z:\AI\WanAnimate2\w1j_executor.log`

Prefer ref1.0 only if blur/ghosting improves materially without missing/displaced anatomy, identity loss or weaker hair/cloth motion.

## Current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\43_run_wan_animate2_bf16_w1j_aspectmatched_ref10.ps1"
```

## Cleanup

Remove large model variants when they no longer belong to active hypotheses. Preserve small evidence. Keep Base-BF16 while Wan is under exhaustion.
