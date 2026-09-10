# Runner62 — Qwen-Image-Edit-2509 FP8 low-VRAM + atomic precision gate

Status date: **2026-09-10**

Status: **COMPLETE / TECHNICAL PASS / VISUAL PRECISION FAIL**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner62 tested Qwen-Image-Edit-2509 as the first specialized semantic/structural editor after FLUX.2 Klein Base exhausted its precise structural-edit hypothesis.

The gate was deliberately narrow: reproduce two atomic edits that Klein handled too coarsely, without masks or manual localization.

## Runtime

Workspace:

`Z:\AI\QwenImageEdit`

ComfyUI commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

Payload:

- `qwen_image_edit_2509_fp8_e4m3fn.safetensors`
  - bytes `20,430,698,424`
  - SHA256 `318568f61951ab9da21100c7b896e3c1da67f0d2efad6421545e022cfaa2b2b4`
- `qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - bytes `9,384,670,680`
  - SHA256 `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`
- `qwen_image_vae.safetensors`
  - bytes `253,806,246`
  - SHA256 `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

Low-VRAM recipe:

- diffusion FP8;
- Qwen2.5-VL encoder on CPU;
- ComfyUI `--lowvram`;
- `--reserve-vram 1.0`;
- expandable CUDA segments;
- `TextEncodeQwenImageEditPlus`;
- `ModelSamplingAuraFlow`, shift 3;
- `CFGNorm`, strength 1;
- Euler / simple / denoise 1;
- 20 steps;
- CFG 4;
- no Lightning LoRA.

## Actual technical result

**PASS.**

Both 1024×1024 jobs completed on RTX 3060 12 GB without OOM or graph/runtime failure.

### Atomic one-plank request

Elapsed: **498.011 s**.

Output SHA256:

`19f6ff99f31b34db73fa357e17587f4ca10498f62b442ccdbd403fd41e8f7e97`

Difference from original:

- mean abs luma: `5.8785`;
- changed ratio >12: `0.112901`;
- changed ratio >24: `0.054299`.

### Atomic lower-right-strap request

Elapsed: **455.408 s**.

Output SHA256:

`f7351216b9d40d8cc6580122901e950a90c596b2b581deb43fed1d52cf3665d8`

Difference from original:

- mean abs luma: `6.3035`;
- changed ratio >12: `0.117374`;
- changed ratio >24: `0.057031`.

Total gate elapsed:

**1026.346 s**.

Contact-sheet SHA256:

`34da1a8a1e56992b902c736c41988d063b4b90348c0a5b328ef73b5e041f3db1`

## Visual verdict

**PRECISION FAIL**, despite materially better source preservation/localization than Klein Base.

### One-plank request

Qwen 2509 preserved gate identity, camera, masonry and most door geometry extremely strongly. This is a real improvement over Klein's broad deletion of most of the left leaf.

However, it did **not** produce the required unambiguous narrow, full-height opening of approximately one existing plank-width. The requested structural fact is not reliably present.

Therefore source preservation alone is not enough for PASS.

### Lower-right strap request

Qwen 2509 localized more tightly than Klein but did not simply break the named strap while leaving the remainder untouched. It reinterpreted the lower hardware/door-bottom region and produced a different broad bar/wood-damage configuration rather than the required missing middle segment with snapped surviving ends.

Again, localization improved, exact structural compliance did not.

## Final Runner62 classification

**TECHNICAL PASS / LOCALIZATION-PRESERVATION IMPROVED / EXACT STRUCTURAL FACT FAIL.**

Qwen 2509 is not promoted to the production structural-edit route.

Do not blindly increase 2509 steps. The next same-family hypothesis is Qwen-Image-Edit-2511, whose official revision specifically targets lower drift, better consistency and stronger geometric reasoning.

## Cleanup decision

Runner62 generated evidence and manifest are sufficient to preserve this result.

When Runner63 activates Qwen 2511, the rejected 2509 diffusion checkpoint may be removed after its hash and preserved evidence are verified. Retain the shared Qwen2.5-VL encoder and Qwen image VAE because Qwen 2511 reuses them.

## Successor

`docs/RUNNER63_QWEN_IMAGE_EDIT_2511_PRECISION_2026-09-10.md`

Runner:

`tools/structured-2d-character-pipeline/63_bootstrap_and_run_qwen_image_edit_2511_precision.ps1`
