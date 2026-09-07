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

`D:\AI` is stale/historical.

## Runtime / character contract — LOCKED

Final runtime uses complete-character spritesheets. The production model receives Exilada appearance/state separately from arbitrary raw driving video and must automatically infer body dynamics, jiggle, long-hair inertia, cloth/material/wind response and restraints/accessories. Routine manual repair is forbidden.

## Candidate order

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after Wan reaches `EXHAUSTED_FAIL`.

## Active Wan Base-BF16 model set

- `wan_animate_2_bf16.safetensors` ~32.8 GB
- `umt5_xxl_fp16.safetensors` ~11.4 GB
- `clip_vision_h.safetensors` ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB

Lower precision/Distilled variants are not retained in advance.

## Runner 35 — PASS

BF16 assets and native ComfyUI schemas are present under `Z:\AI\WanAnimate2`.

## Runner 36 / W0 — PASS_BASELINE

Runner: `tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Attempt 1 failed in ComfyUI AIMDO host-buffer streaming with `hostbuf_file_reader_read failed`.

Attempt 2 changed only the ComfyUI launch flag `--disable-pinned-memory` and completed successfully.

Successful W0 facts:

- official upstream demo1 reference + driver;
- Base BF16 + UMT5 FP16 + CLIP Vision H + VAE BF16;
- `640×800`, 37 frames, 16 fps;
- 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0;
- elapsed ~1896.94 s (~31m37s).

Evidence:

- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\object_info_w0_live.json`

Visual result is good enough to pass the integration baseline: substantial movement transfer, stable cat identity/costume, no catastrophic topology collapse. Some blur/framing movement exists. This is not yet proof of Exilada/project fitness.

## CURRENT GATE — RUNNER 37 / W1 EXILADA

Runner:

`tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Executor:

`tools/wan-animate2-spike/run_w1_from_w0_prompt.py`

W1 is derived from the exact successful W0 API prompt.

Because the W0 positive prompt literally describes the official cat, the target appearance package changes coherently:

- `LoadImage` reference -> `exilada_master.png`;
- positive appearance description -> canonical Exilada description;
- output prefix.

Everything else remains identical to successful W0: official driving video, Base BF16 stack, `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, conditioning strengths and negative prompt. ComfyUI continues to launch with `--disable-pinned-memory`.

Expected output:

- `Z:\AI\WanAnimate2\w1_exilada_official_driver.mp4`
- `Z:\AI\WanAnimate2\w1_run_manifest.json`
- `Z:\AI\WanAnimate2\w1_api_prompt.json`

Judge W1 on Exilada identity/body proportions, complete initial-state preservation, long hair, ragged cloth, soft-body response, shackles/chains, motion adherence, topology, driver leakage and especially preservation of the approved discrete pixel/game-art language.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\37_run_wan_animate2_bf16_w1_exilada.ps1"
```

After W1 completes, share `w1_exilada_official_driver.mp4` and `w1_run_manifest.json`.

## Wan sequence after W1

- W2: Internet walking driver.
- W3: secondary-motion stress footage.
- W4: finite high-leverage variants only if needed.

## Cleanup discipline

Unused large models/materials must not accumulate. Keep the active BF16 route while Wan is being exhausted. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a useful production verdict.