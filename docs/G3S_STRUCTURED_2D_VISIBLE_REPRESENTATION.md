# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A AUTHORED NATIVE SOURCE V1 READY**

## Why G3S exists

G3V-R proved deterministic transfer of real CMU motion into the MPFB humanoid. G3V then proved that hidden 3D is useful as motion/topology infrastructure but failed the visible-art kill switch: direct native-raster/palette translation still read as coarse 3D rather than intentional modern pixel art.

Final character pixels therefore come from persistent structured 2D assets.

Locked production architecture:

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D may own motion, topology, left/right identity, sockets, contacts, depth/occlusion, physics and semantic guides. It may not own final visible color pixels.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI operation by the user;
- no generic beauty-render shrink/pixel-filter route as final production method;
- no bilinear filtering;
- recurring production remains scriptable/headless;
- one-time native source authoring may use deterministic explicit pixel edits, but future animation must consume persistent structured assets rather than regenerate frames;
- **whenever a model is rejected/closed and no longer required, the same response must include an exact PowerShell cleanup command for its downloaded model-specific files.** Shared runtimes still in use must be preserved; small evidence outputs/logs remain unless explicitly removed.

## Current rejected-model cleanup commands

These are safe model/dependency cleanups for the G3S source experiments already closed. They intentionally preserve the small evidence outputs under `Z:\AI\RogueliteCharacterPipeline`.

### Alucard — isolated workspace

```powershell
Remove-Item -LiteralPath "Z:\AI\AlucardSpike" -Recurse -Force -ErrorAction SilentlyContinue
```

### PixelLock — isolated workspace

```powershell
Remove-Item -LiteralPath "Z:\AI\PixelLockSpike" -Recurse -Force -ErrorAction SilentlyContinue
```

### SD1.5 native re-author — shared ComfyUI runtime, model-specific files only

```powershell
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\checkpoints\v1-5-pruned-emaonly.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\loras\pixel-art-sd15.safetensors" -Force -ErrorAction SilentlyContinue
```

### Qwen-Image-Edit-2509 — direct sprite route closed, fixed control retained

The authored-native runner still reuses the ComfyUI embedded Python, so the shared portable runtime must remain. The three Qwen model weights are no longer needed once `g3s_a_control_official_raw.png` is pinned and retained:

```powershell
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\unet\Qwen-Image-Edit-2509-Q4_0.gguf" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\vae\qwen_image_vae.safetensors" -Force -ErrorAction SilentlyContinue
```

# G3S-A — static source sprite gate

Goal: obtain one approved Exilada source image for the locked presentation:

- gameplay canvas `640×360`;
- visible character height about `128 px`;
- lateral/slight-3/4 presentation facing screen-right;
- lean adult female anatomy;
- very long heavy black hair;
- degraded asymmetric beige cloth;
- wrist/ankle restraints and broken chain remnants;
- bare feet;
- no weapon;
- intentional modern pixel clusters at native 1×;
- recognizable Exilada identity derived from `assets/source/characters/exilada/reference/exilada_master.png`.

# Closed automated source experiments

## Qwen direct-native — FAIL / CLOSED

Corrected Qwen-Image-Edit-2509 inference at native `640×360` completed normally but produced a flat raster. Restoring Qwen's preferred-resolution preprocessing produced a coherent `1392×752` Exilada-like design control. That control proves the model/runtime works, but it is **reference/scaffold material only**, never an animation owner and never automatically promoted to final sprite art.

## SD1.5 native latent re-author — FAIL / CLOSED

The bounded SD1.5 + pixel-art LoRA run sampled final pixels directly at `640×360` and produced a coarse block/mannequin. Exilada identity, long hair, cloth, restraints, hands and feet did not survive. No further SD1.5 prompt/seed/CFG/LoRA tuning is allowed.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_sd15_failure.json`

## PixelLock initial-source generation — FAIL / CLOSED

The grammar-constrained `64 -> 128` test completed and was footprint-perfect, but the native output was a single-color silhouette:

- `128×128`;
- visible height `124 px`;
- `3416` opaque pixels;
- one opaque RGB value `[99,9,25]`;
- SHA256 `a77348f93b795eff1371d3960a9c23693b1667f20aa5c621ef795916e861858b`.

PixelLock is rejected as an **initial source author**. It may return later for footprint-safe recolor/restyle once a canonical sprite already exists.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_pixellock_failure.json`

## Alucard native-128 — FAIL / CLOSED

### Reference-conditioned attempt — INVALID

The first Alucard inference passed a Qwen-derived external design image through `ref`. Upstream uses `ref` as a previous sprite/animation frame, so that run is retained only as invalid harness evidence. The generated conditioning reduction also lost the mouth at `128×128`, which the user correctly identified.

Marker:

`tools/structured-2d-character-pipeline/g3s_a_alucard_reference_invalid.json`

### Text-only upstream control — FAIL

A second control exercised Alucard in documented text-to-sprite mode with **no reference input**:

- native `128×128 RGBA`;
- seed `20260905`;
- `20` Euler steps;
- text CFG `5.0`;
- reference `null`;
- code commit `02d1c60a16142015f7838a6a033da5e6ac9ce4f7`;
- model revision `b8e7602`;
- model SHA256 `2f502cc676c9fc34009d6c57caa4e782512a2643f436bc16408f477c352ccc2c`;
- raw SHA256 `c3143b76444abc7c5b6f7b1fe6c0d66a51e7f83d4fff7519018fe3a97739bc5a`;
- alpha bbox covers the full canvas `[0,0,127,127]`;
- `12525` opaque pixels;
- `12059` unique opaque RGB colors.

Visual verdict: full-canvas mottled/noisy texture, no coherent character silhouette, anatomy or production-readable sprite.

No Alucard prompt/seed/CFG/sampler fishing is permitted. The automated local generative-source search is now **closed**.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_alucard_failure.json`

# Authored native source — CURRENT

G3S-A is now explicitly an **authored canonical-source problem**, not another model search.

The useful evidence from the failed searches is that the Qwen official-resolution control contains coherent Exilada design information, and its deterministic `128×128` reduction already provides a much better *scaffold* than the native generators. The reduction itself is **not automatically final art**. It becomes a tracing/base canvas on which explicit native-grid authoring corrections are applied and reviewed at 1×.

This changes the workflow from:

`model search -> hope for a finished sprite`

to:

`fixed design scaffold -> explicit native pixel patch data -> review -> revise patch data -> approve canonical source`

The user does not need to learn a pixel editor. Native corrections are stored as deterministic data in the repository and applied headlessly.

## V1 authored corrections

`tools/structured-2d-character-pipeline/g3s_a_authored_patch_v1.json`

Current explicit corrections include:

- restore a readable mouth lost by the `128×128` reduction;
- add visible metal wrist cuffs;
- reinforce both ankle restraints;
- add short broken-chain remnants;
- preserve the existing long-hair / skin / degraded-cloth design scaffold.

The patch is pinned to the exact Qwen control SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

If the source changes, the runner hard-fails rather than silently applying coordinates to a different image.

## Tooling

- `tools/structured-2d-character-pipeline/g3s_a_authored_native_v1.py`
- `tools/structured-2d-character-pipeline/g3s_a_authored_patch_v1.json`
- `tools/structured-2d-character-pipeline/07_run_g3s_a_authored_native.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_authored`

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_authored\g3s_a_authored_contact_sheet.png`

## Review order

1. topology: one head/torso, two arms/hands, two legs/feet;
2. face: mouth now readable, eyes/head silhouette coherent;
3. identity: long heavy black hair, olive-brown skin, degraded beige cloth, wrist/ankle restraints, bare feet;
4. pixel language at native 1×;
5. gameplay readability at `640×360`;
6. only after visual approval: promote source and start G3S-B decomposition.

If changes are needed, edit the explicit native patch data. **Do not search another image model.**

# G3S-B — persistent part decomposition

Blocked until one static native source is approved. The approved source will be decomposed into stable side-aware parts: head/face, torso/pelvis, upper/lower limbs and hands/feet, hair masses, cloth pieces, wrist/ankle restraints. Parts own IDs, side, pivots, depth rules, palette/material families and attachment inheritance.

# G3S-C — four-phase walk proof

Blocked until G3S-B. Persistent parts will be driven by validated motion frames `1568,1588,1608,1628` using deterministic pixel-aware transforms/deformation and depth ordering. No frame may be independently regenerated by diffusion.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\07_run_g3s_a_authored_native.ps1"
```

Then STOP. If it reaches `G3S-A AUTHORED: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_authored\g3s_a_authored_contact_sheet.png`

Do not start G3S-B or G4 until the authored native source is visually approved.
