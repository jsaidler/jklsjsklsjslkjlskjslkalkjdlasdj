# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
5. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
6. `docs/ANIMATION_PIPELINE.md`
7. `docs/CHARACTERS.md`
8. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

## Local path topology — LOCKED

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model root: `Z:\AI`

Retained workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- active Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current tooling.

## Runtime / production architecture — LOCKED

Final runtime consumes complete precomposed character frames/spritesheets only. No runtime body/hair/clothing/equipment layer assembly.

The complete-character generation contract is:

1. `exilada_master.png` owns complete appearance/state;
2. arbitrary real driving video owns motion/performance;
3. the production model must consume richer information than a body skeleton and automatically infer locomotion, soft-body/jiggle, long-hair inertia, cloth/material response, wind and restraint/accessory behavior;
4. no routine manual keyframing, rigging, simulation, masks, repainting, frame cleanup or hand compositing is allowed.

## Model exhaustion protocol — LOCKED

A single bad run does not kill a model family. Distinguish infrastructure, integration, configuration and model/task failures. Exhaust one relevant family before switching. No random seed fishing and no manual rescue.

## Disk/model cleanup rule — LOCKED

Do not accumulate unused large checkpoints/materials. Keep only variants tied to an active diagnostic hypothesis. Preserve small manifests/logs/evidence. Do not delete the active family after one poor result.

## Current candidate order

1. **Wan-Animate-2** — exhaust first.
2. **SCAIL-2** — only after Wan reaches documented `EXHAUSTED_FAIL`.

Moore/AnimateAnyone pose-only and the current Moore+SSD compatibility route remain research evidence only for the final raw-video contract. Exact public SSD remains independently `BLOCKED` by the absent custom SSD pose-guider checkpoint.

## Wan canonical W0 model set

- `wan_animate_2_bf16.safetensors` — ~32.8 GB
- `umt5_xxl_fp16.safetensors` — ~11.4 GB
- `clip_vision_h.safetensors` — ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB

Total ~45.7 GB.

Base INT8, Distilled BF16/INT8, LightX2V distillation LoRA and UMT5 FP8 are not retained for the active Base-BF16 route.

## Runner 35 — PREPARATION PASS

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Result: **PASS**. BF16 assets installed and native ComfyUI schema captured under `Z:\AI\WanAnimate2`.

## Runner 36 — W0 OFFICIAL BASELINE PASS

`tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Builder: `tools/wan-animate2-spike/build_and_run_w0.py`

### Attempt 1

Infrastructure failure only:

`RuntimeError: hostbuf_file_reader_read failed`

inside `comfy_aimdo/host_buffer.py` during host-buffer/dynamic weight streaming.

### Attempt 2

The runner changed exactly one execution variable: ComfyUI started with `--disable-pinned-memory`.

Result: **PASS — official Base-BF16 W0 generated.**

Observed W0 manifest facts:

- Base BF16 main model;
- UMT5 XXL FP16;
- CLIP Vision H;
- Wan VAE BF16;
- official upstream demo1 reference + official demo1 driving video;
- `640×800`;
- 37 frames;
- 16 fps;
- 20 steps;
- CFG `1.0`;
- Euler/simple;
- shift `5.0`;
- seed `0`;
- pose/reference strength `1.0`;
- elapsed inference ~`1896.94 s` (~31m37s).

Canonical evidence:

- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\object_info_w0_live.json`

### Visual W0 diagnosis — PASS_BASELINE

The uploaded W0 video shows a coherent complete character over all 37 frames with substantial transferred body/arm motion, persistent face/species identity, persistent uniform/bow/skirt design and no catastrophic limb/topology collapse. Some motion blur and framing/crop movement are visible, but not enough to invalidate the integration baseline.

W0 therefore proves that the local Base-BF16/raw-driving-video path is operational and capable of meaningful motion transfer.

W0 does **not** yet prove the project task: it does not test Exilada identity, pixel/game-art preservation, long black hair, ragged cloth, soft-body response or chains/restraints.

## Runner 37 — CURRENT GATE: W1 EXILADA CROSS-IDENTITY

Runner:

`tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Executor:

`tools/wan-animate2-spike/run_w1_from_w0_prompt.py`

W1 is derived directly from the successful W0 API prompt. It preserves the successful official driver and all execution/model settings, including the `--disable-pinned-memory` workaround.

The W0 target appearance package must change as a unit because the W0 positive prompt literally describes the official cat character. W1 therefore changes:

- reference image -> `exilada_master.png`;
- positive appearance description -> matching canonical Exilada description;
- output prefix only.

It keeps unchanged:

- official W0 driving video;
- Base BF16 / UMT5 FP16 / CLIP Vision H / VAE BF16;
- `640×800`, 37 frames, 16 fps;
- 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose/reference strengths;
- W0 negative prompt.

Expected outputs:

- `Z:\AI\WanAnimate2\w1_exilada_official_driver.mp4`
- `Z:\AI\WanAnimate2\w1_run_manifest.json`
- `Z:\AI\WanAnimate2\w1_api_prompt.json`

W1 QA must judge complete initial-state preservation, face/body identity, long-hair mass and inertia, ragged cloth behavior, shackles/chains, driver leakage, topology, motion adherence and whether the approved pixel/game-art language survives rather than becoming smooth/painterly.

## Wan exhaustion sequence

- **W0** official baseline — **PASS_BASELINE**.
- **W1** Exilada + same official driver — **CURRENT**.
- **W2** target Internet walking driver.
- **W3** secondary-motion stress footage.
- **W4** finite high-leverage variants only if needed.

After W4: `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## SSD retention

Keep `Z:\AI\SpriteSheetDiffusionSpike` for now as comparison/fallback evidence. Do not delete it merely because Wan W0 passed; decide cleanup only after Wan reaches a useful production verdict.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\37_run_wan_animate2_bf16_w1_exilada.ps1"
```
