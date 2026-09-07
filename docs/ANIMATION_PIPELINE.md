# Character Animation Production — Living Decision Record

Status date: **2026-09-07**

Status: **RAW-VIDEO DUAL-REFERENCE COMPLETE-CHARACTER GENERATION IS THE ACTIVE PRODUCTION CLASS. WAN-ANIMATE-2 BASE BF16 MUST BE EXHAUSTED BEFORE SWITCHING; SCAIL-2 IS NEXT OPEN/LOCAL CANDIDATE.**

Canonical screening/protocol:

`docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

Canonical state:

`docs/PROJECT_STATE.md`

## Hard production constraints

The production animation pipeline must:

- use `assets/source/characters/exilada/reference/exilada_master.png` as complete appearance/state reference;
- accept a separate real driving video for movement/performance;
- allow the driver performer to differ completely in identity, clothing, hair and accessories;
- preserve Exilada identity, proportions, hair mass, clothing, scars/restraints and accessories;
- infer locomotion, jiggle/soft motion, hair inertia, cloth/material/wind response and restraint/accessory motion automatically;
- require no manual rigging, keyframing, simulation, masks, repainting, per-frame cleanup or hand compositing;
- allow fully automatic preprocessing/postprocessing;
- output complete visible frames ready for spritesheet packing;
- run reproducibly through scripted local tooling where practical.

## Runtime contract — LOCKED

`complete generated frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

The runtime never assembles visible body/hair/clothing/equipment layers.

## No-manual rule — LOCKED

Allowed:

- automatic crop/resize/frame sampling;
- automatic segmentation/masks;
- automatic background removal;
- automatic alpha cleanup;
- automatic spritesheet packing;
- scripted QA/metadata;
- scripted inference settings.

Disallowed as required production work:

- manual rigging/weight painting;
- keyframes;
- hair bones;
- cloth/chain simulation setup or repair;
- manual pose alignment;
- manual mask fixes;
- frame repainting;
- hand compositing/cleanup.

## Motion-source rule — LOCKED

Final production motion must come from **real driving video consumed in a richer form than body skeleton alone**.

Internet footage is acceptable. Costume matching is not required.

Pose/SMPL/mocap may remain diagnostic inputs, but cannot be the sole production motion signal because they discard non-rigid temporal information.

## Model-exhaustion protocol — LOCKED

Do not change model families after a single ugly generation.

Before `EXHAUSTED_FAIL`:

1. reproduce official/reference behavior where practical;
2. validate local checkpoint/loader/input semantics;
3. test cross-identity in controlled stages;
4. change one high-leverage variable at a time;
5. keep seed/input fixed unless stochasticity itself is tested;
6. prohibit manual rescue;
7. require the decisive failure to persist across a finite valid matrix.

## Historical research

RefControl, Qwen edit, hidden-rig and Moore/SSD work remain research evidence. Runner 34 proved complete-character generation/packing but its pose-only motion path does not satisfy the final raw-video contract.

Exact public SSD remains separately `BLOCKED` by the absent custom pose-guider checkpoint.

## Current production-class candidate — Wan-Animate-2

Wan-Animate-2 directly consumes a reference image and raw driving video, so it belongs to the required model class.

Historical 2026-09-04 project run:

- Base INT8;
- UMT5 FP8;
- about `384×576`;
- 17 frames;
- seed 42;
- weak locomotion transfer;
- smooth/painted output.

That configuration failed but did not exhaust the model family.

## W0 checkpoint-quality lock — 2026-09-07

The RTX 3060 does not choose the checkpoint.

Canonical reference-quality W0 set:

- `wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `clip_vision_h.safetensors` — ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total ~45.7 GB.

Do not retain in the active W0 workspace:

- Base INT8;
- Distilled BF16;
- Distilled INT8;
- LightX2V distillation LoRA;
- UMT5 FP8.

Those variants are downloaded later only if W4 explicitly tests them.

## Execution-concession order

If 12 GB VRAM + 48 GB RAM cannot execute the reference set, reduce one variable at a time:

1. offload/cache behavior;
2. temporal window;
3. spatial resolution;
4. text-encoder precision;
5. main-model quantization only as a later explicit comparison.

Do not pre-emptively degrade the Base BF16 transformer.

## W0 upstream references

Official demo inputs:

- `examples/demo1/reference.png`;
- `examples/demo1/template.mp4`.

Repository Base YAML documents roughly `640×800`, 37 frames, 16 fps, 20 steps, seed 0. Upstream Diffusers separately demonstrates Base BF16 at `640×800` with 40 steps. Each W0 attempt must state which documented path it follows.

## Runner 35 — ACTIVE PREPARATION

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Runner 35:

- requires 70 GB free-space headroom;
- rebuilds/restores isolated `D:\AI\WanAnimate2`;
- removes superseded Wan INT8/Distilled/LoRA/FP8 files if found;
- downloads only the ~45.7 GB BF16/FP16 W0 set;
- downloads official demo1 inputs;
- copies Exilada master for W1;
- removes completed HF/Xet cache;
- launches ComfyUI headlessly;
- saves exact installed node schemas;
- stops before inference.

Expected marker:

`RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

This schema-first stop prevents stale-template/widget assumptions.

## Wan exhaustion stages after Runner 35

- **W0:** official reference + official driver baseline;
- **W1:** same driver/settings, Exilada reference only;
- **W2:** clean real Internet walking driver;
- **W3:** non-rigid secondary-motion stress driver;
- **W4:** finite hypothesis-driven variants only.

After W4: `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## SCAIL-2 — NEXT ONLY IF WAN EXHAUSTS

SCAIL-2 remains the next selected open/local candidate because it also supports end-to-end raw-video character animation. Do not install it before Wan closes.

## Mandatory complete-sequence QA

Judge the whole sequence on:

1. Exilada identity/proportions;
2. motion adherence/grounding;
3. limb/hands/feet topology;
4. hair persistence/inertia;
5. cloth topology/material behavior;
6. jiggle/soft response;
7. chains/restraints/accessory coherence;
8. no driver identity/costume/body leakage;
9. stable camera/background for extraction;
10. game-art readability near 128 px;
11. automatic loop/segment/spritesheet suitability;
12. zero manual repair.

## Cleanup discipline — LOCKED

Do not accumulate unused large model variants/materials.

- Keep only files tied to active hypotheses.
- Remove superseded local model-specific files.
- Preserve small logs/manifests/results.
- Do not delete the current Wan BF16 route after one poor run.
- Keep SSD comparison evidence until Wan W0 is established or SSD research is explicitly abandoned.

## Immediate next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\35_prepare_wan_animate2_bf16_w0.ps1"
```

After it passes, use the captured schema to author and run W0. Do not run the historical 384×576/17-frame INT8 scripts.
