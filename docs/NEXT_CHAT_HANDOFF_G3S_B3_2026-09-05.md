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

## Wan W0 quality decision — LOCKED 2026-09-07

Ignore the RTX 3060 when choosing the checkpoint.

Canonical W0 model set:

- `wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `clip_vision_h.safetensors` — ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total ~45.7 GB.

Do not retain for W0:

- Base INT8;
- Distilled BF16;
- Distilled INT8;
- LightX2V distillation LoRA;
- UMT5 FP8.

The active bootstrap deletes those superseded Wan-specific files if found.

If the BF16 set cannot execute on 12 GB VRAM + 48 GB RAM, reduce execution one variable at a time: offload/cache -> temporal window -> spatial resolution -> text encoder precision -> only then consider main-model quantization as an explicit W4 comparison.

## Upstream W0 semantics

Repository Base YAML documents roughly:

- `640×800`;
- 37 frames;
- 16 fps;
- 20 steps;
- seed 0.

Upstream Diffusers separately documents Base BF16 at `640×800` / 40 steps. Do not mix the two paths silently; W0 will record the exact one reproduced.

Official W0 inputs:

- upstream `examples/demo1/reference.png`;
- upstream `examples/demo1/template.mp4`.

## CURRENT GATE — RUNNER 35 PREPARATION

Runner:

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

It:

1. requires at least 70 GB free on the workspace drive;
2. rebuilds/restores `D:\AI\WanAnimate2`;
3. cleans superseded Wan INT8/Distilled/LoRA/FP8 assets if present;
4. downloads only the canonical ~45.7 GB BF16/FP16 set;
5. downloads official W0 reference + driver;
6. copies `exilada_master.png` for later W1;
7. removes completed Hugging Face/Xet cache;
8. starts ComfyUI headlessly;
9. records the exact installed Wan/loader node schemas;
10. stops before inference.

Expected files:

- `D:\AI\WanAnimate2\wan_bf16_route.json`;
- `D:\AI\WanAnimate2\object_info_wan_bf16.json`.

Expected marker:

`RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\35_prepare_wan_animate2_bf16_w0.ps1"
```

This downloads ~45.7 GB of model payload plus ComfyUI/runtime overhead. It does **not** run the expensive inference yet.

After runner 35 passes, share the terminal output or the two JSON proof files. The next code action is to author W0 from the captured fresh schema and then run the official Base BF16 baseline.

## Cleanup discipline

User reconfirmed that unused models/materials must not accumulate.

- superseded Wan-specific variants are deleted by the bootstrap;
- completed HF download cache is removed;
- small manifests/logs/evidence remain;
- do not delete the current Wan BF16 route after one poor result;
- do not delete `Z:\AI\SpriteSheetDiffusionSpike` yet: keep as comparison/fallback evidence until Wan W0 is established or SSD research is explicitly abandoned.
