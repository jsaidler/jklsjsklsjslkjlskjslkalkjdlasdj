# Character Animation Production — Living Decision Record

Status: **RefControl is rejected as a direct animation-frame generator after repeated structural failures, culminating in an extra third leg in V3. The next and final diffusion-based direct-frame test changes architecture to Qwen-Image-Edit-2509 using its native multi-image/keypoint-edit behavior. Qwen-Image-Edit-2511 is not the primary pose-control candidate because current evidence indicates its OpenPose/keypoint behavior is less reliable than 2509 for this exact use case. If the single hard 2509 topology test fails, direct diffusion frame synthesis ends and the project moves to deterministic rig-first animation.**

This document is canonical across chats. Update it after every material animation test, PASS/FAIL decision or pipeline change.

## Hard production constraints

The animation pipeline must:

- start from the approved Exilada identity reference;
- preserve adult anatomy, face, long black hair mass, clothing state, scars/restraints and equipment state;
- provide explicit inspectable pose/motion control;
- run reproducibly on Windows 11 / RTX 3060 12 GB / ~48 GB RAM;
- avoid routine manual frame-by-frame repainting, seed fishing and artistic retry loops;
- use free/local/self-hosted code and weights unless explicitly approved otherwise;
- scale to many characters, equipment states and actions.

Canonical Exilada identity reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design master, not the final gameplay sprite.

## Architecture principle

The useful decomposition remains:

`motion/key poses -> explicit structure/control -> controlled character renderer/editor -> gameplay-scale/native-raster translation -> temporal completion if needed -> QA`

The renderer/editor must preserve **body topology first**. Identity, pose quality, props and visual polish are irrelevant if the frame invents or loses major limbs.

## Mandatory QA order — LOCKED

Every future generated pose/frame is evaluated in this order:

1. **topology/anatomy count:** exactly one head, one torso, two arms, two hands, two legs, two feet; no extra/duplicated/fused/missing major limbs;
2. **pose adherence:** requested contact/passing/support/swing geometry is actually present;
3. **identity continuity:** same Exilada face, body type, hair mass, clothing language and scars;
4. **prop continuity:** shackles/chains/equipment remain on stable anatomical sides;
5. **visual quality/gameplay readability.**

Failure at level 1 is immediately eliminatory.

## RefControl research history — FROZEN

### V1

FLUX.2 Klein Base 4B FP8 + RefControl Pose, fixed seed `20260904`, four COCO-18 gait poses, one-shot/no-retry.

Result:

- identity retention strong;
- four phases distinct;
- right-foot/toe error;
- left-arm inconsistency;
- small body drift;
- chain/shackle drift.

Verdict: **CONDITIONAL PASS as research/upstream reference; FAIL as final walk.**

### V2

Changed control geometry + stricter anatomy/continuity prompt while holding model/seed/render settings constant.

Improvements:

- feet better;
- arms better;
- body stability better;
- identity remained strong.

Critical failure:

- `contact_L` ≈ `contact_R`;
- `passing_L` ≈ `passing_R`.

Root cause: opposite phases used nearly identical screen-space silhouettes and relied too heavily on COCO semantic left/right labels.

Verdict: **FAIL as usable walk.**

### V3

Changed actual screen-space geometry so all four controls had unique color-independent silhouettes.

STEP 8A controls: PASS.

Generated result:

- phase differentiation returned;
- identity remained strong;
- `pose_01_passing_L_v3` contains **three visible legs / three feet**;
- chain/shackle drift remains.

Verdict: **catastrophic topology FAIL.**

### RefControl final decision — LOCKED

Do **not** create V4. Do not prompt-tune, seed-fish, inpaint, or iterate further on direct RefControl frame generation.

RefControl is frozen as:

- research history;
- possible non-final upstream pose/identity reference support only.

It is **rejected as the production direct-frame generator** because it does not reliably preserve body topology.

## New candidate architecture — Qwen-Image-Edit-2509

The final diffusion-based direct-frame topology test uses:

**Qwen-Image-Edit-2509**, local/self-hosted, Apache 2.0.

Why 2509 rather than 2511 for this gate:

- 2509 explicitly introduced native support for keypoint/control images and pose transformation;
- its multi-image edit path can take the Exilada identity image together with a keypoint map;
- 2511 improves general consistency/drift, but current evidence shows its OpenPose/keypoint behavior can regress relative to 2509;
- this spike tests **pose-controlled topology**, not general image-edit quality.

This is materially different from FLUX RefControl:

- image-editing architecture;
- identity image and keypoint map are native multi-image edit inputs;
- no RefControl LoRA/reference-latent chain;
- no attempt to rescue the FLUX route through another prompt or skeleton revision.

## RTX 3060 12 GB model strategy — LOCKED FOR FIRST TEST

Canonical new workspace:

`Z:\AI\QwenImageEditSpike`

First model set:

1. `Qwen-Image-Edit-2509-Q4_0.gguf` — ~11.9 GB transformer;
2. `qwen_2.5_vl_7b_fp8_scaled.safetensors` — ~9.38 GB text encoder;
3. `qwen_image_vae.safetensors` — ~0.25 GB VAE.

No Lightning LoRA in the first topology test.

Rationale:

- Q4_0 is chosen over Q3 to avoid degrading the topology test more than necessary;
- the 12 GB GPU is expected to require low-VRAM / CPU offload;
- the machine has ~48 GB RAM and the workspace is on SSD;
- if Q4_0 cannot run under controlled low-VRAM offload, do not silently change quantization. Reassess the runtime gate explicitly.

## New tooling — `tools/qwen-image-edit-2509-spike/`

### `00_preflight.ps1`

Checks only:

- Windows 11;
- >=40 GB visible system RAM for this spike;
- ~12 GB NVIDIA VRAM;
- >=40 GB free on the `Z:` workspace drive;
- repository/master paths;
- git/curl/7-Zip prerequisites.

No downloads or installs.

### `01_install_runtime.ps1`

Creates an isolated runtime in:

`Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`

Installs:

- latest official NVIDIA ComfyUI Portable;
- `city96/ComfyUI-GGUF` pinned to commit `6ea2651e7df66d7585f6ffee804b20e92fb38b8a`;
- only the custom-node Python requirements.

No Qwen weights and no inference.

### `02_download_models.ps1`

Downloads exactly the three locked files and validates SHA256:

- `Qwen-Image-Edit-2509-Q4_0.gguf`
  - SHA256 `4f6cda402e1dbc36ee4b601b10b9ee0da2dbefedfbfa53eae3efb0ddff48c3e2`
- `qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - SHA256 `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`
- `qwen_image_vae.safetensors`
  - SHA256 `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

No model load or inference.

### `03_prepare_inputs.ps1`

Creates one deliberately difficult topology stress-test input:

- identity: byte-identical canonical `exilada_master.png`;
- keypoint map: the same difficult passing-L structural case that caused the RefControl V3 extra-leg failure;
- fixed seed `20260904`;
- fixed `768×1024` control canvas;
- explicit prompt requiring exactly two arms/hands/legs/feet and full-body visibility.

No model load or inference.

### `04_validate_runtime_schema.ps1`

Starts isolated ComfyUI with `--lowvram`, performs only `GET /object_info`, and validates:

- `UnetLoaderGGUF` with the Q4_0 model visible;
- `CLIPLoader` with `qwen_image` type and the locked encoder visible;
- `VAELoader` with the locked VAE visible;
- `TextEncodeQwenImageEditPlus` multi-image edit contract;
- required sampler/decode/save nodes;
- both prepared input images visible to `LoadImage`.

It sends **zero `/prompt` requests** and performs no inference.

## Hard single-pose topology gate

Do not generate four frames first.

The first Qwen inference, only after STEP 5 schema PASS, will use exactly one difficult passing pose — the same structural case that produced the V3 extra leg.

Inputs:

1. canonical Exilada identity image;
2. explicit OpenPose-style COCO-18 keypoint map;
3. fixed prompt and seed.

One output only. No retry. No seed fishing. No prompt iteration.

### Acceptance criteria

The single-pose spike passes only if all are true:

- exactly **2 arms / 2 hands / 2 legs / 2 feet**;
- no extra, fused or missing major limb;
- requested passing pose is visibly obeyed;
- Exilada identity/hair/body/clothing remain recognizably stable;
- complete body remains visible;
- no catastrophic prop-body fusion.

If it fails topology, **reject Qwen-Image-Edit-2509 as a direct-frame generator immediately**.

If it passes, only then run the four-pose set.

## Deterministic fallback — HARD STOP

If the Qwen one-pose topology gate fails, stop testing diffusion-based direct frame synthesis.

Next architecture becomes **deterministic rig-first animation**:

- 2D mesh/skeletal rig or hidden 3D rig;
- body topology and gait guaranteed mechanically;
- generative tools allowed only for non-topological roles such as concept/reference, texture/style guidance or downstream native-pixel authoring.

This prevents an endless sequence of models hallucinating limbs while the project repeatedly repairs prompts.

## Exact next gate

Run only STEP 1 preflight:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\qwen-image-edit-2509-spike\00_preflight.ps1"
```

Do not run STEP 2 or download models until STEP 1 output is reviewed and recorded.
