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

- final runtime = ordinary playback of **complete-character spritesheets**;
- no runtime body/hair/clothing/equipment layer assembly;
- every frame already contains body, hair, clothing, restraints/accessories, secondary motion and final occlusion.

## Complete-character generation contract — LOCKED

Two distinct references:

1. `assets/source/characters/exilada/reference/exilada_master.png` = complete appearance/state;
2. arbitrary real driving video = movement/performance.

The model must infer body dynamics, jiggle, long-hair inertia, cloth/material response, wind and restraint/accessory behavior automatically. No routine manual rigging, keyframing, simulation, masks, repainting, frame cleanup or hand compositing may be required.

## Candidate order

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after Wan reaches `EXHAUSTED_FAIL`.

Do not install another pose-only model.

## Wan old test

2026-09-04 Base INT8/FP8 remains a configuration-level negative result: approximately `384×576`, 17 frames, seed 42, weak locomotion transfer and smooth/painted output. It did not exhaust the model family.

## Wan W0 quality decision — LOCKED

Canonical model set:

- `wan_animate_2_bf16.safetensors` — ~32.8 GB
- `umt5_xxl_fp16.safetensors` — ~11.4 GB
- `clip_vision_h.safetensors` — ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB

Total ~45.7 GB.

Do not retain Base INT8, Distilled BF16/INT8, LightX2V distillation LoRA or UMT5 FP8 for W0.

## Runner 35 — PASS 2026-09-07

Preparation runner:

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

User-observed terminal result:

- `WAN BF16 SCHEMA PREFLIGHT: PASS`
- `RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

Proof files now exist locally:

- `Z:\AI\WanAnimate2\wan_bf16_route.json`
- `Z:\AI\WanAnimate2\object_info_wan_bf16.json`

No inference happened in Runner 35.

## CURRENT GATE — RUNNER 36 / OFFICIAL W0 BF16

Runner:

`tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Builder/executor:

`tools/wan-animate2-spike/build_and_run_w0.py`

W0 uses:

- official upstream demo1 reference;
- official upstream demo1 driving video;
- Base BF16 + UMT5 FP16 + CLIP Vision H + Wan VAE BF16;
- `640×800`;
- 37 frames;
- 16 fps;
- 20 steps;
- CFG `1.0` / no CFG;
- Euler + simple scheduler;
- shift `5.0`;
- seed `0`;
- driving strength `1.0`;
- reference-image strength `1.0`.

The builder queries live `/object_info` and authors the API prompt against the actual installed schema. Raw driving-video frames are wired directly into native `WanAnimate2ToVideo`; no DWPose/custom motion preprocessor is installed for W0.

Expected files after successful W0:

- `Z:\AI\WanAnimate2\object_info_w0_live.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`

Expected marker:

`RUNNER36-WAN-W0: PASS — OFFICIAL BF16 BASELINE GENERATED`

W0 must be visually judged before W1. Do not use the Exilada master until the official baseline proves credible local motion transfer.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\36_run_wan_animate2_bf16_w0.ps1"
```

This is the first expensive Base-BF16 inference. If it fails because of memory/runtime, classify that first as execution/infrastructure and change only one execution variable at a time.

## Wan exhaustion sequence after W0

- W1: same W0 driver/settings, replace only reference with Exilada master.
- W2: target Internet walking clip.
- W3: secondary-motion stress footage.
- W4: finite high-leverage execution/model variants only.

## Cleanup discipline

Unused large models/materials must not accumulate. Preserve small manifests/logs/evidence. Keep the active Wan BF16 workspace throughout the exhaustion pass. Retain `Z:\AI\SpriteSheetDiffusionSpike` only as comparison/fallback evidence until Wan passes W0 or SSD research is explicitly abandoned.