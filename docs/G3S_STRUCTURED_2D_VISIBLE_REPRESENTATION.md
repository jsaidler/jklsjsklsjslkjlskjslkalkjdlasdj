# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A QWEN OFFICIAL-RESOLUTION CONTROL READY**

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

- canvas `640×360`;
- visible character height about `128 px`;
- lateral/slight-3/4 view facing screen-right;
- lean adult female anatomy;
- very long heavy black hair;
- degraded asymmetric beige cloth;
- wrist/ankle restraints;
- bare feet;
- no weapon;
- intentional modern pixel clusters at native 1×;
- recognizably derived from `assets/source/characters/exilada/reference/exilada_master.png`.

Qwen-Image-Edit-2509 is allowed only as a bounded **one-time static-source experiment**. It remains forbidden as independent animation-frame generator.

Runtime:

`Z:\AI\QwenImageEditSpike`

Pinned model set:

- `Qwen-Image-Edit-2509-Q4_0.gguf`;
- `qwen_2.5_vl_7b_fp8_scaled.safetensors`;
- `qwen_image_vae.safetensors`.

## G3S-A V1 — INVALID / HARNESS FAIL

The first completed Qwen run produced an almost-black result. Inspection found the API graph differed materially from the official ComfyUI Qwen 2509 blueprint: primary conditioning image and sampled latent did not match, `CFGNorm` was missing, negative conditioning was wired differently and sampling settings mixed separate official presets.

V1 is therefore not a model-quality verdict.

## G3S-A V2 — NATIVE 640×360 FAIL

Workflow revision:

`QWEN2509_OFFICIAL_ALIGNED_NATIVE_V2`

V2 corrected the critical graph relationships:

- Picture 1 = `640×360` guide;
- Picture 1 also owns the sampled VAE latent;
- Picture 2 = canonical Exilada master;
- both positive and negative conditioning receive the same refs + VAE;
- `UnetLoaderGGUF -> ModelSamplingAuraFlow(3.0) -> CFGNorm(1.0)`;
- `20` steps / CFG `2.5` / Euler / simple / denoise `1.0`.

The only deliberate deviation from the official blueprint was omission of `FluxKontextImageScale`, because G3S-A specifically needed to test true native `640×360` output without later shrinking.

The inference itself completed successfully in ComfyUI on the RTX 3060. Runtime/model loading was normal. The saved raw output was nevertheless a genuinely collapsed, near-uniform image rather than a rejected threshold false positive.

Measured raw evidence:

- size: `640×360`;
- SHA256: `a5ecaf9db68fbb8370280c4b6c61a727aa5cd191134d6f508a34207f4c8d157e`;
- mean luma: `70.3017`;
- p99 luma: `71`;
- target mean luma: `70.2322`;
- target p95 luma: `71`;
- target stddev: `0.4336`.

Therefore the **direct native Qwen 640×360 route is rejected**. Do not change seed, threshold or prompt to rescue it.

## G3S-A official-resolution control — CURRENT

The official ComfyUI Qwen 2509 blueprint passes the primary image through `FluxKontextImageScale`, mapping it to one of the preferred roughly-one-megapixel rasters before VAE encoding/sampling.

A final diagnostic control now restores that node while keeping the rest of the corrected V2 relationships.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_a_qwen_official_control.py`
- `tools/structured-2d-character-pipeline/02_run_g3s_a_official_control.ps1`

Revision:

`QWEN2509_OFFICIAL_RESOLUTION_CONTROL_V1`

Purpose is narrow: determine whether Qwen works coherently under its official preferred-resolution preprocessing.

Hard rule: **the control output is never eligible as final sprite art and must not be downscaled/promoted.** It exists only to decide the fate of Qwen as a source method.

Decision after control:

- if the official-resolution output is coherent: Qwen/model/runtime are functional, but Qwen is rejected for direct native sprite production because the native route collapsed and high-res shrink is already prohibited;
- if the official-resolution output also collapses: reject this Qwen route completely for G3S-A.

No additional Qwen prompt/seed fishing follows either outcome.

Control output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control`

Expected artifacts:

- `g3s_a_control_official_raw.png`;
- `g3s_a_control_result.json`.

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
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\02_run_g3s_a_official_control.ps1"
```

Then STOP. If it reaches `G3S-A CONTROL: REVIEW CONTROL`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

and optionally `g3s_a_control_result.json`. If it fails, share the console output. Do not run G3S-B or G4.
