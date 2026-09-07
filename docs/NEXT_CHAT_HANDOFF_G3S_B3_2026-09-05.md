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

Official demo1 reference + raw driver completed at `640×800`, 37 frames, 16 fps, 20 steps, seed 0 using Base BF16. The first attempt hit `hostbuf_file_reader_read failed`; relaunching ComfyUI with only `--disable-pinned-memory` fixed the infrastructure issue.

Visual W0: meaningful raw-video motion transfer, stable official-character identity/costume, no catastrophic topology collapse.

## Runner 37 / W1 — COMPLETE

Runner:

`tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Evidence:

- `Z:\AI\WanAnimate2\w1_exilada_official_driver.mp4`
- `Z:\AI\WanAnimate2\w1_run_manifest.json`
- `Z:\AI\WanAnimate2\w1_api_prompt.json`

Observed run:

- `INFERENCE_COMPLETE`;
- same W0 official driver and Base-BF16 execution settings;
- Exilada reference SHA256 `e8422ec9c7125eec8bf534e13cf0ceac9c2ade5e6e2f18cf26cd8f22e59755ab`;
- 37 frames / 16 fps / 20 steps / seed 0;
- pose strength 1.0 / reference strength 1.0;
- elapsed 1746.69 s (~29m07s).

### W1 diagnosis

Positive:

- substantial cross-identity motion transfer;
- no visible cat identity/costume leakage;
- long black hair visibly changes silhouette/trails over time, proving non-rigid inference beyond skeleton-only control;
- ragged hip cloth changes drape;
- coarse Exilada identity/state survives.

Insufficient for production:

- smooth/painterly output instead of discrete modern pixel/game-art;
- face/body/reference-detail drift;
- wrist restraints/chain largely lost; ankle chain morphs;
- some hand/foot blur/stretch and a detached transient artifact;
- later crop is inherited from the official driver/W0 framing trend, not Exilada-specific;
- official driver cannot decide walking/jiggle/strong cloth-wind quality.

Classification:

**W1 = production-appearance CONFIGURATION FAIL, but strong positive evidence for the raw-video motion/secondary-response architecture. Wan remains active.**

## Native control discovered

Current native ComfyUI `WanAnimate2ToVideo` documents `reference_image_strength` default 1.0 and states that values above 1.0 tighten reference/appearance adherence. This is separate from `pose_strength`.

Therefore do not jump to W2/model switching yet. First isolate whether native reference strength fixes the exact W1 failure.

## CURRENT GATE — RUNNER 38 / W1A REFERENCE STRENGTH 1.5

Runner:

`tools/structured-2d-character-pipeline/38_run_wan_animate2_bf16_w1a_refstrength15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1a_reference_strength.py`

One changed variable only:

`reference_image_strength: 1.0 -> 1.5`

Everything else remains exact W1:

- Exilada reference/prompt;
- official driver;
- Base BF16 + UMT5 FP16 + CLIP Vision H + VAE BF16;
- `640×800`, 37 frames, 16 fps, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- negative prompt;
- `--disable-pinned-memory`.

Expected output:

- `Z:\AI\WanAnimate2\w1a_exilada_refstrength15.mp4`
- `Z:\AI\WanAnimate2\w1a_run_manifest.json`
- `Z:\AI\WanAnimate2\w1a_api_prompt.json`

Compare W1 vs W1A primarily on identity/style/accessory persistence, then verify motion did not materially degrade.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\38_run_wan_animate2_bf16_w1a_refstrength15.ps1"
```

## Wan sequence after W1A

- if reference strength improves appearance, continue a small controlled reference-strength calibration before changing driver;
- then W2: target Internet walking driver;
- W3: secondary-motion stress footage;
- W4: only finite high-leverage variants still justified by evidence.

## Cleanup discipline

Unused large models/materials must not accumulate. Keep the active BF16 route while Wan is being exhausted. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a useful production verdict.