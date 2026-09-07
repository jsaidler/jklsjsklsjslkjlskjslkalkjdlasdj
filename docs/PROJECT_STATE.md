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
- active Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current tooling.

The first BF16 runner-35 preparation attempt failed before installation because of a stale `D:\AI` hard-code. That was an **INFRASTRUCTURE/PATH FAIL** only. The bootstrap/inspect/runner defaults and working-directory logic were corrected to use the configured `Z:\AI\WanAnimate2` workspace.

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

Every exported frame must already bake body motion, soft-tissue response, hair motion, clothing/bindings motion, shackles/chains/restraints/accessories and final occlusion.

## Exilada appearance reference — LOCKED

`assets/source/characters/exilada/reference/exilada_master.png`

This is the complete initial-state appearance reference.

## Complete-character generation contract — LOCKED

Production animation uses two distinct references:

1. Exilada master for complete target appearance/state;
2. arbitrary real driving video for movement/performance.

The driving performer may come from Internet video and does not need matching clothing, hair or body type.

The production model must consume richer motion information than a body skeleton and automatically infer convincing locomotion/weight transfer, soft-body response, long-hair inertia, cloth/material response, wind where present and restraint/accessory dynamics.

No routine manual keyframing, rigging, cloth/hair simulation, masks, repainting, frame cleanup or hand compositing is allowed. Automatic preprocessing is allowed.

## Runner 34 — retained evidence

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 proved:

- complete-character generation/packing architecture: **PASS**;
- RGBA frames/spritesheet/runtime playback: **PASS**;
- current Moore+SSD pose-only result quality: **not sufficient**.

Moore/AnimateAnyone pose-only conditioning is research-only for the final contract. Exact upstream SSD remains independently `BLOCKED` by the unavailable custom SSD pose-guider checkpoint.

## Raw-video candidate ranking

1. **Wan-Animate-2** — exhaust first.
2. **SCAIL-2** — next open/local candidate only after Wan reaches `EXHAUSTED_FAIL`.
3. DreamActor-M2 — benchmark; no current public self-hostable production route confirmed.
4. Kling Motion Control — hosted benchmark only.

Do not install another pose-only model as the next production candidate.

## Wan-Animate-2 — CURRENT ACTIVE MODEL FAMILY

The old 2026-09-04 Base INT8 run remains valid negative evidence for that constrained configuration, but not proof that the model family is exhausted.

Historical local test approximately used Base INT8 ConvRot + UMT5 FP8 at `384×576`, 17 frames, seed 42 and 20 steps.

## W0 checkpoint-quality decision — LOCKED 2026-09-07

Canonical W0 model set:

- `wan_animate_2_bf16.safetensors` — about 32.8 GB;
- `umt5_xxl_fp16.safetensors` — about 11.4 GB;
- `clip_vision_h.safetensors` — about 1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` — about 0.254 GB.

Total model payload: approximately **45.7 GB**.

Not part of W0 and intentionally absent: Base INT8, Distilled BF16/INT8, LightX2V distillation LoRA and UMT5 FP8.

If this exact BF16 set cannot execute on 12 GB VRAM + 48 GB RAM, reduce execution one controlled variable at a time. Do not silently replace the main checkpoint.

## Runner 35 — PREPARATION PASS 2026-09-07

Runner:

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Result:

**PASS — BF16 assets installed and exact native ComfyUI schema captured.**

Observed terminal markers:

- `WAN BF16 SCHEMA PREFLIGHT: PASS`
- `RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

Proof files:

- `Z:\AI\WanAnimate2\wan_bf16_route.json`
- `Z:\AI\WanAnimate2\object_info_wan_bf16.json`

No inference was run by Runner 35.

## Runner 36 — CURRENT GATE: OFFICIAL W0 BF16 INFERENCE

Runner:

`tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Schema-driven builder:

`tools/wan-animate2-spike/build_and_run_w0.py`

Runner 36 reproduces the repository-YAML W0 path as closely as the current native ComfyUI integration permits:

- official upstream `examples/demo1/reference.png`;
- official upstream `examples/demo1/template.mp4`;
- Base BF16 main model;
- UMT5 XXL FP16;
- CLIP Vision H;
- Wan VAE BF16;
- `640×800`;
- 37 frames;
- 16 fps;
- 20 steps;
- CFG `1.0` = no classifier-free guidance;
- Euler sampler;
- simple scheduler;
- model-sampling shift `5.0`;
- seed `0`;
- pose/driving strength `1.0`;
- reference-image strength `1.0`.

The builder queries the **live** `/object_info` schema before creating the API prompt. It feeds the raw official driving-video frames directly into the native `WanAnimate2ToVideo` driving/`pose_video` branch and does not install or use DWPose/custom preprocessing for this Animate-2 W0 route.

Expected evidence after a successful run:

- `Z:\AI\WanAnimate2\object_info_w0_live.json`
- `Z:\AI\WanAnimate2\w0_api_prompt.json`
- `Z:\AI\WanAnimate2\w0_run_manifest.json`
- `Z:\AI\WanAnimate2\w0_official_baseline.mp4`

Expected terminal marker:

`RUNNER36-WAN-W0: PASS — OFFICIAL BF16 BASELINE GENERATED`

Runner 36 is **W0 only**. It must not use `exilada_master.png` yet.

## Wan exhaustion sequence after W0

- **W0** official upstream reference + official driving video;
- **W1** same known-good W0 driver/settings, replace only reference with Exilada master;
- **W2** clean real Internet walking clip;
- **W3** real secondary-motion stress video with body bounce/hair/cloth/wind;
- **W4** finite hypothesis-driven variants only.

After W4: `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Retention decision for SSD workspace

Do **not** delete `Z:\AI\SpriteSheetDiffusionSpike` yet. It remains comparison/evidence until Wan passes W0 or SSD research is explicitly abandoned.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\36_run_wan_animate2_bf16_w0.ps1"
```

This launches the first expensive Base-BF16 inference. If it fails for memory/runtime reasons, classify the result as an execution/infrastructure failure first and apply the locked one-variable-at-a-time exhaustion protocol.