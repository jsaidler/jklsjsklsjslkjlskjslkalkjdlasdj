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

## Local path topology — LOCKED 2026-09-07

Project Git repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model workspace root:

`Z:\AI`

Known retained workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- active Wan rebuild: `Z:\AI\WanAnimate2`

**`D:\AI` is not a valid/current AI workspace root.** Current scripts must derive working directories from the configured workspace path and must not hard-code `D:\AI`.

2026-09-07 infrastructure incident: the first BF16 Wan runner-35 preparation attempt failed before installation because `bootstrap.ps1` still contained the stale historical `D:\AI` / `D:\AI\WanAnimate2` hard-code. No inference was attempted and no model-quality conclusion is associated with that failure. Runner/bootstrap/inspect defaults were corrected to `Z:\AI\WanAnimate2`, with comfy-cli working directory derived dynamically from the workspace parent.

## Model exhaustion protocol — LOCKED

A bad output from one configuration is not enough to declare a model family incapable.

Classify failures as:

- `INFRASTRUCTURE FAIL` — install/runtime/loader/OOM/path/dependency;
- `INTEGRATION FAIL` — wrong graph/checkpoint/preprocessing/input contract;
- `CONFIGURATION FAIL` — valid run, inadequate tested settings;
- `BLOCKED` — exact intended route cannot currently be reproduced;
- `MODEL/TASK FAIL` — repeated decisive failure only after baseline/integration/input/meaningful parameter checks.

Rules:

1. exhaust one relevant model family before switching;
2. reproduce official/reference baseline first where practical;
3. change one meaningful variable at a time with fixed input/seed;
4. separate motion, identity, topology, secondary motion and art-language failures;
5. no random seed fishing;
6. no manual rescue;
7. do not delete the currently investigated model after one bad configuration.

## Disk/model cleanup rule — LOCKED / USER RECONFIRMED 2026-09-07

Do not accumulate unused large checkpoints/materials.

- Keep only model variants that belong to the current diagnostic hypothesis.
- When a variant is superseded and no longer needed, remove its local weights/materials.
- Preserve small manifests, logs and result evidence.
- Shared dependencies are retained only while an active route uses them.
- A model family under active exhaustion is not deleted after one poor output.
- Download a later comparison variant only when its gate is actually reached.

## Game / presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- `72 deg` remains the current intended game-facing baseline.

## Runtime animation architecture — LOCKED

Runtime consumes only **complete precomposed character frames**:

`complete authored frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

Runtime construction from body/hair/clothing/equipment layers is abolished.

Every exported frame must already bake:

- body motion;
- soft-tissue/jiggle where appropriate;
- hair motion;
- clothing/bindings motion;
- shackles/chains/restraints/accessories;
- final occlusion.

## Exilada appearance reference — LOCKED

`assets/source/characters/exilada/reference/exilada_master.png`

This is the complete initial-state appearance reference.

## Complete-character generation contract — LOCKED

Production animation uses two distinct references:

1. Exilada master for complete target appearance/state;
2. arbitrary real driving video for movement/performance.

The driving performer may come from Internet video and does not need matching clothing, hair or body type.

The production model must consume richer motion information than a body skeleton and automatically infer convincing:

- locomotion/weight transfer;
- soft-body/jiggle response;
- long-hair inertia/follow-through;
- cloth deformation/lag/material response;
- wind response where present;
- chain/restraint/accessory dynamics.

No manual keyframing, rigging, cloth/hair simulation, manual masks, frame repainting, per-frame cleanup, hand compositing or other routine manual animation repair is allowed. Automatic preprocessing is allowed.

## Runner 34 — retained evidence

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 proved:

- complete-character generation/packing architecture: **PASS**;
- RGBA frames/spritesheet/runtime playback: **PASS**;
- current Moore+SSD pose-only result quality: **not sufficient**.

Moore/AnimateAnyone pose-only conditioning is now research-only for the final contract because it discards the raw-video non-rigid dynamics required for hair, cloth, jiggle, wind and accessories.

Exact upstream SSD remains independently `BLOCKED` by the unavailable custom pose-guider checkpoint.

## Raw-video candidate ranking

1. **Wan-Animate-2** — exhaust first.
2. **SCAIL-2** — next open/local candidate only after Wan reaches `EXHAUSTED_FAIL`.
3. DreamActor-M2 — relevant benchmark but no current public self-hostable production route confirmed.
4. Kling Motion Control — hosted benchmark only.

Do not install another pose-only model as the next production candidate.

## Wan-Animate-2 — CURRENT ACTIVE MODEL FAMILY

The old 2026-09-04 Base INT8 run remains valid negative evidence for that constrained configuration, but not proof that the model family is exhausted.

Historical local test approximately used:

- Base INT8 ConvRot;
- UMT5 FP8;
- `384×576`;
- `17` frames;
- seed `42`;
- 20 steps.

The upstream Base route is materially different. Current repository semantics include Base BF16, `640×800`, `37` frames, 16 fps, 20 steps, base seed `0`; the upstream Diffusers example also demonstrates Base BF16 at `640×800` with 40 steps.

## Checkpoint-quality decision — LOCKED 2026-09-07

Hardware no longer chooses the checkpoint.

Canonical W0 model set is the highest-quality Base route available in the ComfyUI repack:

- `wan_animate_2_bf16.safetensors` — about 32.8 GB;
- `umt5_xxl_fp16.safetensors` — about 11.4 GB;
- `clip_vision_h.safetensors` — about 1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` — about 0.254 GB.

Total model payload: approximately **45.7 GB**.

Not part of W0 and intentionally removed if found:

- `wan_animate_2_int8_convrot.safetensors`;
- `wan_animate_2_distill_bf16.safetensors`;
- `wan_animate_2_distill_int8_convrot.safetensors`;
- LightX2V distillation LoRA;
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`.

If W0 later proves that the 48 GB RAM / 12 GB VRAM machine cannot execute this exact set, reduce **execution** one controlled variable at a time. Do not pre-emptively replace the Base BF16 checkpoint with a lower-precision main model.

## Runner 35 — ACTIVE PREPARATION GATE

Runner:

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Active workspace:

`Z:\AI\WanAnimate2`

It performs only setup/preflight, not inference:

1. verifies at least 70 GB free on the workspace drive;
2. rebuilds/restores isolated `Z:\AI\WanAnimate2` ComfyUI;
3. removes superseded Wan INT8/Distilled/LoRA/FP8 model material if found;
4. downloads only the canonical ~45.7 GB BF16/FP16 model set;
5. downloads upstream `examples/demo1/reference.png` and `template.mp4` for W0;
6. copies `exilada_master.png` for future W1;
7. removes completed Hugging Face/Xet download cache after target files are present;
8. starts ComfyUI headlessly and records the exact installed `WanAnimate2ToVideo`/loader schemas;
9. stops before inference so the W0 workflow can be authored from the actual fresh node contract rather than guessed widget semantics.

Expected proof files:

- `Z:\AI\WanAnimate2\wan_bf16_route.json`;
- `Z:\AI\WanAnimate2\object_info_wan_bf16.json`.

Expected final marker:

`RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

## Wan exhaustion sequence after preparation

- **W0** official upstream reference + official driving video;
- **W1** same known-good driver/settings, replace only reference with Exilada master;
- **W2** clean real Internet walking clip;
- **W3** real secondary-motion stress video with body bounce/hair/cloth/wind;
- **W4** finite hypothesis-driven variants only (Base vs Distilled, hardware-safe window, one justified quantization, documented viewpoint/reference controls).

After W4: `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Retention decision for SSD workspace

Do **not** delete `Z:\AI\SpriteSheetDiffusionSpike` yet.

Reason: it remains comparison/evidence and a fallback research branch while Wan has not passed W0. Once Wan establishes a viable production candidate or the project explicitly abandons SSD research, delete its large model/runtime material while preserving small result evidence.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\35_prepare_wan_animate2_bf16_w0.ps1"
```

The runner now defaults to `Z:\AI\WanAnimate2`. This command downloads about **45.7 GB** of canonical model payload plus ComfyUI/runtime overhead and intentionally stops before the expensive BF16 inference.
