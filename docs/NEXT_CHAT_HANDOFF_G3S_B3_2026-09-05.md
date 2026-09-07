# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`

## Local paths — LOCKED

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model root: `Z:\AI`

Current workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- Wan: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current scripts.

## Runtime lock

Final runtime is ordinary playback of complete-character spritesheets. No runtime body/hair/clothing/equipment layer assembly.

## Complete-character generation contract — LOCKED

Use two separate references: Exilada master for appearance/state and arbitrary real driving video for motion/performance. The production model must infer body dynamics, jiggle, long-hair inertia, cloth/material response, wind and restraint/accessory behavior automatically. No routine manual animation repair is allowed.

## Candidate order

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after Wan reaches `EXHAUSTED_FAIL`.

## Wan W0 model set — LOCKED

- `wan_animate_2_bf16.safetensors` — ~32.8 GB
- `umt5_xxl_fp16.safetensors` — ~11.4 GB
- `clip_vision_h.safetensors` — ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB

Total ~45.7 GB. Do not retain Base INT8, Distilled BF16/INT8, LightX2V LoRA or UMT5 FP8 for W0.

## Runner 35 — PASS 2026-09-07

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Observed:

- `WAN BF16 SCHEMA PREFLIGHT: PASS`
- `RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

BF16 assets and installed node schemas are present under `Z:\AI\WanAnimate2`.

## CURRENT GATE — RUNNER 36 / W0 BF16 RETRY

Runner: `tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Builder: `tools/wan-animate2-spike/build_and_run_w0.py`

Locked W0 settings remain official upstream demo1 + Base BF16 + UMT5 FP16 + CLIP Vision H + VAE BF16 at `640×800`, 37 frames, 16 fps, 20 steps, seed 0, Euler/simple, shift 5.0, driving/reference strength 1.0.

### W0 attempt 1 — INFRASTRUCTURE FAIL

The first inference failed after ~74 seconds with:

`RuntimeError: hostbuf_file_reader_read failed`

Trace: `comfy_aimdo/host_buffer.py -> read_file_to_device`.

Classify strictly as **ComfyUI host-buffer/pinned-memory infrastructure failure**. No visual output was evaluated, so this says nothing about Wan model quality.

### W0 attempt 2 — exact one-variable retry

Current runner starts a fresh managed ComfyUI process with:

`--disable-pinned-memory`

Everything else is unchanged. This flag is an official current ComfyUI CLI option and is a documented workaround for contemporary Wan/ComfyUI host-buffer failures.

The runner will stop the previous managed server recorded in `Z:\AI\WanAnimate2\.wan_animate2_spike.pid` so the flag definitely takes effect. It refuses to kill an unmanaged process if port 8188 is occupied without the matching managed PID.

Do not add `--disable-dynamic-vram`, lower resolution/frame count or quantize yet. If this retry fails, inspect the next traceback first and change only one additional execution variable.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\36_run_wan_animate2_bf16_w0.ps1"
```

Expected success marker:

`RUNNER36-WAN-W0: PASS — OFFICIAL BF16 BASELINE GENERATED`

Expected output:

- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`

W0 must be visually accepted before W1 uses `exilada_master.png`.

## Cleanup discipline

Unused large models/materials must not accumulate. Keep the active BF16 route while Wan is being exhausted. Retain the SSD workspace only as comparison/fallback evidence until Wan passes W0 or SSD research is explicitly abandoned.