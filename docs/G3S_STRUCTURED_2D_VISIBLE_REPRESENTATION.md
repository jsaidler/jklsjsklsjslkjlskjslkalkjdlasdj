# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A PIXELLOCK NATIVE-GRID TEST READY**

## Why G3S exists

G3V-R proved deterministic transfer of real CMU motion into the MPFB humanoid. G3V then proved that hidden 3D is useful as motion/topology infrastructure but failed the visible-art kill switch: direct native-raster/palette translation still read as coarse 3D rather than intentional modern pixel art.

Therefore final character pixels must come from persistent structured 2D assets.

Locked target architecture:

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D may own motion, topology, left/right identity, sockets, contacts, depth/occlusion, physics and semantic guides. It may not own final visible color pixels.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting;
- no generic high-resolution beauty render followed by shrink/quantization as final art;
- no bilinear filtering;
- no required Blender/Aseprite/Spine GUI operation by the user;
- recurring production remains scriptable/headless.

# G3S-A — static source sprite gate

Goal: obtain one approved Exilada source image at the locked gameplay presentation:

- gameplay canvas `640×360`;
- visible character height about `128 px`;
- lateral/slight-3/4 presentation facing screen-right;
- lean adult female anatomy;
- very long heavy black hair;
- degraded asymmetric beige cloth;
- wrist/ankle restraints;
- bare feet;
- no weapon;
- intentional modern pixel clusters at native 1×;
- recognizably derived from `assets/source/characters/exilada/reference/exilada_master.png`.

# Qwen source experiment — CLOSED

Qwen-Image-Edit-2509 was tested only as a bounded static-source experiment. It remains forbidden as independent animation-frame generator.

## Qwen V1 — INVALID / HARNESS FAIL

The first run used a materially incorrect graph relative to the official ComfyUI Qwen 2509 workflow and produced an almost-black result. It is not a model-quality verdict.

## Qwen V2 — DIRECT NATIVE 640×360 FAIL / CLOSED

The corrected graph completed normally but produced a genuinely flat native output.

Measured evidence:

- size `640×360`;
- SHA256 `a5ecaf9db68fbb8370280c4b6c61a727aa5cd191134d6f508a34207f4c8d157e`;
- mean luma `70.3017`;
- p99 luma `71`;
- target stddev `0.4336`.

No seed/prompt/threshold rescue is permitted.

## Qwen official-resolution control — PASS AS MODEL-FUNCTION CONTROL / CLOSED

Restoring `FluxKontextImageScale` produced a coherent `1392×752` full-body Exilada-like woman rather than collapse. Long dark hair, beige degraded cloth, adult anatomy and bare feet were readable.

The control is conventional high-resolution illustration/pseudo-pixel styling. It is **not final-art eligible and must never be promoted by simple shrink/quantization**.

Conclusion: Qwen/model/runtime work, but Qwen is rejected as the direct native sprite generator. The coherent control is retained only as a one-time design/pose conditioning reference.

# SD1.5 native latent re-author — FAIL / CLOSED

Tooling retained for evidence:

- `tools/structured-2d-character-pipeline/g3s_a_sd15_native_reauthor.py`
- `tools/structured-2d-character-pipeline/03_bootstrap_and_run_g3s_a_sd15_native.ps1`
- failure marker: `tools/structured-2d-character-pipeline/g3s_a_sd15_failure.json`

The bounded test used the coherent Qwen control only as conditioning and sampled SD1.5 + a pixel-art LoRA directly at `640×360`, with no post-inference resize.

Recorded run:

- revision `SD15_NATIVE_PIXEL_REAUTHOR_V1`;
- seed `20260905`;
- `30` steps;
- CFG `6.0`;
- DPM++ 2M / Karras;
- denoise `0.72`;
- conditioning figure `48×128` on the gameplay canvas;
- raw SHA256 `294a412ffc0aa859c7fdf4128b13755e1e89fec4f3ea1d96c63e735a10ed92b0`.

Visual verdict: **FAIL**. The result was a coarse vertical block/mannequin. Exilada identity was lost; long hair, degraded cloth, restraints, hands and feet were not production-readable. It did not read as intentional modern pixel art.

Root lesson: putting a roughly 128-screen-pixel identity-rich human inside a standard latent-diffusion canvas leaves too little spatial representation for the detail/topology requirements. Do not seed-fish, prompt-tune or iterate SD1.5/LoRA variants for G3S-A.

# PixelLock native-grid source test — CURRENT

The next test changes representation instead of changing another latent-diffusion parameter.

PixelLock is a text LLM fine-tuned for palette-indexed pixel art. Its production engine serializes a sprite as a `PALETTE` plus `GRID`, and llama.cpp GBNF grammar locks transparent/opaque footprint cells. The model therefore authors discrete sprite cells rather than decoding an 8×-compressed image latent.

Pinned upstream:

- PixelLock code commit: `bb682f9919fcd302eaa5226b7e6965dfdf151beb`;
- PixelLock code license: MIT;
- model: `solarkyle/pixellock-gemma-12b-pixelart-gguf`, Q4_K_M, about `7.38 GB`, Gemma license;
- model revision: `d35e3bcc3c8651603393042df4dbf2a1d37173ea`;
- llama.cpp Windows CUDA build: `b10516`;
- llama.cpp CUDA 12.4 main ZIP SHA256 `96d64faeb5b8e655341f32b26ad3e51fbea8bff0bc8120ad3dbffdc0b05b8ad3`;
- CUDA runtime ZIP SHA256 `8c79a9b226de4b3cacfd1f83d24f962d0773be79f1e7b75c6af4ded7e32ae1d6`.

## Representation contract

1. The coherent Qwen control is used only to derive pose/footprint conditioning.
2. The subject is isolated into a transparent **64×64 logical scaffold**, target visible height about `62` logical pixels.
3. PixelLock runs its grammar-constrained **2× mode** and authors a **128×128 output grid**.
4. The 2× result is model-generated cell data, not a bitmap resize performed after generation.
5. The output alpha footprint must match the exact grammar-constrained 2× scaffold footprint.
6. The generated 128×128 asset is composited at 1 asset pixel = 1 screen pixel on the `640×360` gameplay preview.
7. No frame animation is generated in this gate.

Why `64 -> 128` is permitted: PixelLock is trained for small native grids and its 2× mode samples colors for the output cells under a footprint grammar. This is structurally different from taking a high-resolution illustration and resizing/filtering it after generation.

## Tooling

- `tools/structured-2d-character-pipeline/g3s_a_pixellock_native.py`
- `tools/structured-2d-character-pipeline/04_bootstrap_and_run_g3s_a_pixellock.ps1`

Dependency workspace:

`Z:\AI\PixelLockSpike`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_pixellock`

First run provisions about `7.4 GB` for the PixelLock model plus the pinned llama.cpp CUDA runtime. The runner is one-command/headless and automatically retries lower GPU offload if the full model cannot start within RTX 3060 12 GB VRAM.

## Hard automated checks

- pinned PixelLock code commit;
- pinned llama.cpp archive SHA256 values;
- pinned HF model revision plus locally recorded model SHA256;
- 64×64 scaffold generated from the Qwen control;
- generated output exactly `128×128`;
- `footprint_perfect == true` from PixelLock production validation;
- generated visible height between `116` and `128` px;
- no post-generation resize.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_pixellock\g3s_a_pixellock_contact_sheet.png`

Review order:

1. topology: one head/torso, two arms/hands, two legs/feet; hands and feet must read;
2. Exilada identity: dominant long black hair, olive-brown skin, degraded beige cloth, wrist/ankle restraints, bare feet;
3. intentional modern pixel-cluster language rather than a block mannequin;
4. gameplay readability in the 640×360 preview.

Kill rule: this is one bounded representation test. If PixelLock can only recolor the coarse scaffold and cannot produce a convincing identity-bearing Exilada sprite, close it without prompt/temperature fishing and reassess the static-source representation.

# G3S-B — persistent part decomposition

Blocked until one static native source is approved. The future source is decomposed into stable side-aware 2D parts: head/face, torso/pelvis, upper/lower limbs and hands/feet, hair masses, cloth pieces and wrist/ankle restraints. Parts own IDs, side, pivots, depth rules, palette/material families and attachment inheritance.

# G3S-C — four-phase walk proof

Blocked until G3S-B. Persistent parts will be driven by validated motion frames `1568,1588,1608,1628` using deterministic pixel-aware transforms/deformation and depth ordering. No frame may be independently regenerated by diffusion.

## G3S PASS criteria

- static source reads as intentional modern pixel art at 1×;
- major topology and left/right ownership remain stable;
- motion/grounding matches G2/G3V-R;
- hair/cloth/restraints remain persistent;
- joints avoid puppet gaps/rubbery collapse;
- authored clusters survive movement;
- recurring production remains headless/reproducible.

## G4 rescope

After G3S passes, G4 becomes the Exilada production 2D identity system: canonical sprite parts, palette/material families, hair/cloth/restraint variants, sockets/occlusion metadata and damage-ready layers.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\04_bootstrap_and_run_g3s_a_pixellock.ps1"
```

Then STOP. If it reaches `G3S-A PIXELLOCK: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_pixellock\g3s_a_pixellock_contact_sheet.png`

If it fails, share the complete console output. Do not start G3S-B or G4.
