# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/PIXEL_ART_PRODUCTION.md`
6. `docs/ANIMATION_PIPELINE.md`
7. current tooling under `tools/`

After every material step: update thematic docs + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity

The game is a **systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a living world**.

Immediate gameplay baseline: **elevated 2D belt-scroller / false 3D**.

Character-art/animation feasibility remains the current priority because it is the largest production risk; code capability is not the current unknown.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite. Final visible art remains true modern pixel art; simple high-resolution generation followed by resize/quantization is not accepted as the final-sprite route.

## RefControl direct-frame route — REJECTED

FLUX.2 Klein + RefControl Pose is frozen after three controlled iterations.

### V1

- strong identity retention;
- four phases distinct;
- right-foot/toe error;
- left-arm inconsistency;
- small body drift;
- unstable chains/shackles.

Verdict: **CONDITIONAL PASS as research/upstream reference; FAIL as final walk.**

### V2

- feet/arms/body stability improved;
- left/right gait pairs collapsed to effectively two repeated poses.

Verdict: **FAIL as walk.**

### V3

- controls passed silhouette-uniqueness and restored real left/right geometry;
- generated `pose_01_passing_L_v3` contains **three visible legs / three feet**;
- chain/shackle drift remains.

Verdict: **catastrophic topology FAIL.**

### Locked decision

Do **not** create RefControl V4. No more prompt-tuning, skeleton micro-adjustment, seed fishing, inpainting or repeated repair of the same route.

RefControl is rejected as the production direct-frame generator because it does not reliably preserve body topology.

## Mandatory QA order — LOCKED

All future generated character frames are judged in this order:

1. exactly one head/torso, two arms, two hands, two legs, two feet; no extra/missing/fused major limbs;
2. pose/gait adherence;
3. identity continuity;
4. prop/equipment continuity;
5. visual quality/gameplay readability.

Failure at step 1 immediately fails the output.

## New active candidate — Qwen-Image-Edit-2509

The next and final diffusion-based direct-frame topology test changes architecture entirely.

Chosen model family:

**Qwen-Image-Edit-2509**.

Why 2509, not 2511:

- 2509 explicitly introduced native keypoint/control-image support for pose changes;
- it supports multi-image editing with identity image + keypoint map;
- current evidence indicates 2511 can regress on the OpenPose/keypoint behavior that is central to our use case;
- this gate is about topology + pose control, not general editing quality.

If Qwen 2509 fails the single difficult topology test, diffusion-based direct frame synthesis ends for this project.

## Qwen spike workspace — LOCKED

New isolated workspace:

`Z:\AI\QwenImageEditSpike`

Frozen RefControl evidence remains in:

`Z:\AI\Flux2RefControlSpike`

Repository remains:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Qwen 2509 hardware/model strategy

Target machine:

- Windows 11;
- RTX 3060 12 GB;
- ~48 GB RAM;
- SSD workspace on `Z:`.

First locked model set:

1. `Qwen-Image-Edit-2509-Q4_0.gguf` — ~11.9 GB;
2. `qwen_2.5_vl_7b_fp8_scaled.safetensors` — ~9.38 GB;
3. `qwen_image_vae.safetensors` — ~0.25 GB.

No Lightning LoRA in the first test.

Q4_0 is chosen instead of Q3 to avoid unnecessary quality degradation in a topology decision. Runtime will use controlled low-VRAM/offload behavior; if Q4_0 cannot run, do not silently substitute another quant.

## New tooling — READY IN REPOSITORY

Directory:

`tools/qwen-image-edit-2509-spike/`

Current scripts:

- `00_preflight.ps1`
- `01_install_runtime.ps1`
- `02_download_models.ps1`
- `03_prepare_inputs.ps1`
- `04_validate_runtime_schema.ps1`

### STEP 1 — preflight

Checks only:

- Windows 11;
- >=40 GB system RAM;
- ~12 GB NVIDIA VRAM;
- >=40 GB free SSD space on the workspace drive;
- canonical repo/master;
- git/curl/7-Zip prerequisites.

No downloads/install/inference.

### STEP 2 — isolated runtime

Installs only:

- official latest NVIDIA ComfyUI Portable under `Z:\AI\QwenImageEditSpike`;
- `city96/ComfyUI-GGUF` pinned to `6ea2651e7df66d7585f6ffee804b20e92fb38b8a`;
- its Python requirements.

No Qwen weights/inference.

### STEP 3 — model download

Downloads exactly three pinned files and SHA256-validates them:

- Q4_0 GGUF: `4f6cda402e1dbc36ee4b601b10b9ee0da2dbefedfbfa53eae3efb0ddff48c3e2`
- text encoder: `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`
- VAE: `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

No model load/inference.

### STEP 4 — hard input preparation

Creates one difficult passing-L topology stress test using:

- byte-identical canonical Exilada master;
- OpenPose-style COCO-18 keypoint map using the same structural passing case that produced the extra third leg in RefControl V3;
- fixed seed `20260904`;
- fixed `768×1024` control canvas;
- explicit topology prompt.

No model load/inference.

### STEP 5 — runtime schema gate

Starts isolated ComfyUI with `--lowvram` and performs only `GET /object_info`.

Validates:

- GGUF loader + Q4_0 visibility;
- Qwen text encoder + `qwen_image` CLIP mode;
- Qwen VAE;
- `TextEncodeQwenImageEditPlus` multi-image contract;
- required sampling/decode/save nodes;
- both prepared input images visible.

Zero `/prompt` submissions. No inference.

## Hard single-pose topology gate — queued after STEP 5 PASS

Only after runtime schema PASS will an executable one-pose workflow be built.

The first inference uses exactly **one difficult passing pose**.

One output. No retry. No seed fishing. No prompt iteration.

Pass requires:

- exactly 2 arms / 2 hands / 2 legs / 2 feet;
- no extra/fused/missing major limb;
- requested passing pose obeyed;
- full body visible;
- Exilada identity/hair/body/clothing recognizably preserved;
- no catastrophic prop-body fusion.

If topology fails: **reject Qwen-Image-Edit-2509 immediately as direct-frame generator.**

If it passes: only then run the four-pose set.

## Deterministic fallback — HARD STOP

If Qwen 2509 fails the one-pose topology gate, stop testing diffusion-based direct frame synthesis.

Next architecture becomes deterministic rig-first animation:

- 2D mesh/skeletal rig or hidden 3D rig;
- topology and gait guaranteed mechanically;
- generative tools used only for non-topological roles such as concept/reference, texture/style guidance or downstream native-pixel authoring.

## Exact next action — DO ONLY THIS

Run STEP 1 preflight:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\qwen-image-edit-2509-spike\00_preflight.ps1"
```

Then stop and report the output. Do not run STEP 2 yet.

## Gameplay-scale / Production Pixel Master gate — queued

Gameplay-scale/native-raster validation remains queued until an upstream animation representation passes the topology/pose gate.

High-resolution AI outputs remain motion/identity references unless and until a separate native-grid production route is validated.
