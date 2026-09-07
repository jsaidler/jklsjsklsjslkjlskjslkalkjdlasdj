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

Project repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model root:

`Z:\AI`

Current workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- Wan W0: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current scripts.

## Runtime lock

- final runtime = ordinary playback of **complete-character spritesheets**;
- no runtime body/hair/clothing/equipment layer assembly;
- every frame already contains body, hair, clothing, restraints/accessories, secondary motion and final occlusion.

## Complete-character generation contract — LOCKED

Two distinct references:

1. `assets/source/characters/exilada/reference/exilada_master.png` = complete appearance/state;
2. arbitrary real driving video = movement/performance.

The video performer may come from Internet footage and need not resemble or dress like the Exilada.

The model must consume richer motion information than skeletons and automatically infer body dynamics, jiggle, long-hair inertia, cloth/material response, wind and restraint/accessory behavior.

No manual rigging, keyframing, simulation, masks, repainting, frame cleanup or hand compositing may be required.

## Candidate order

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after Wan reaches `EXHAUSTED_FAIL`.

Do not install another pose-only model.

## Wan old test

2026-09-04 Base INT8/FP8 test remains a configuration-level negative result:

- about `384×576`;
- 17 frames;
- seed 42;
- weak locomotion transfer;
- smooth/painted output.

It did not exhaust the model family.

## Wan W0 quality decision — LOCKED

Canonical W0 model set:

- `wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `clip_vision_h.safetensors` — ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total ~45.7 GB.

Do not retain for W0: Base INT8, Distilled BF16/INT8, LightX2V distillation LoRA or UMT5 FP8. The active bootstrap deletes those superseded Wan-specific files if found.

If BF16 cannot execute on 12 GB VRAM + 48 GB RAM, reduce execution one controlled variable at a time rather than silently changing the main checkpoint.

## Upstream W0 semantics

Repository Base YAML documents roughly:

- `640×800`;
- 37 frames;
- 16 fps;
- 20 steps;
- seed 0.

Official W0 inputs:

- upstream `examples/demo1/reference.png`;
- upstream `examples/demo1/template.mp4`.

## 2026-09-07 path incident — INFRASTRUCTURE FAIL / FIXED IN REPO

The first new runner-35 preparation attempt failed before ComfyUI installation because the rebuilt script still used the obsolete path `D:\AI\WanAnimate2` and `bootstrap.ps1` explicitly did `Push-Location 'D:\AI'`.

This is an **infrastructure/path failure only**. It says nothing about Wan model quality.

Corrections committed:

- runner default workspace -> `Z:\AI\WanAnimate2`;
- bootstrap default workspace -> `Z:\AI\WanAnimate2`;
- inspect default workspace -> `Z:\AI\WanAnimate2`;
- comfy-cli working directory is now derived from `Split-Path -Parent $Workspace`, so there is no fixed AI-drive hard-code.

## CURRENT GATE — RUNNER 35 PREPARATION

Runner:

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

It:

1. requires at least 70 GB free on `Z:`;
2. rebuilds/restores `Z:\AI\WanAnimate2`;
3. cleans superseded Wan INT8/Distilled/LoRA/FP8 assets if present;
4. downloads only the canonical ~45.7 GB BF16/FP16 set;
5. downloads official W0 reference + driver;
6. copies `exilada_master.png` for later W1;
7. removes completed Hugging Face/Xet cache;
8. starts ComfyUI headlessly;
9. records exact installed Wan/loader node schemas;
10. stops before inference.

Expected files:

- `Z:\AI\WanAnimate2\wan_bf16_route.json`;
- `Z:\AI\WanAnimate2\object_info_wan_bf16.json`.

Expected marker:

`RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\35_prepare_wan_animate2_bf16_w0.ps1"
```

The runner defaults to `Z:\AI\WanAnimate2`. It downloads ~45.7 GB of model payload plus runtime overhead and does **not** run inference yet.

## Cleanup discipline

User reconfirmed that unused models/materials must not accumulate.

- superseded Wan-specific variants are deleted by bootstrap;
- completed HF download cache is removed;
- small manifests/logs/evidence remain;
- do not delete the current Wan BF16 route after one poor result;
- retain `Z:\AI\SpriteSheetDiffusionSpike` only as comparison/fallback evidence until Wan W0 is established or SSD research is explicitly abandoned.
