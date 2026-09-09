# Runner62 — Qwen-Image-Edit-2509 FP8 low-VRAM + atomic precision gate

Status date: **2026-09-09**

Status: **PREPARED / CURRENT GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner62 exists

Runner61 exhausted the parity-valid FLUX.2 Klein 4B Base hypothesis for **precise structural editing**.

Klein Base did demonstrate useful coarse semantic editing:

- it recognized a request to remove door material;
- it recognized a request to remove upper masonry;
- it recognized a request to alter hardware;
- sequential candidates generally preserved the overall gate identity/camera;
- the final material pass could import stronger rust/material language.

However, the atomic precision contract failed:

- `remove one plank` removed almost the entire left door leaf/opening rather than one plank-width;
- `remove one capstone` modified a much larger upper-masonry region than the requested single mass;
- `break one lower-right strap` broadly reinterpreted the door hardware instead of isolating the named strap.

The sequential chain therefore composes **coarse edits**, not the precise edits needed for routine Asset Studio art direction without masks/manual repainting.

Klein Base remains useful as:

- a valid Base/T2I branch;
- a future LoRA/project-specialization training base;
- possible coarse concept revision research.

It is not approved as the production structural editor.

## Next specialized editor

Qwen-Image-Edit-2509 is now the active structural/semantic editing hypothesis.

Reasons:

- Apache-2.0 model family;
- native ComfyUI support in the pinned runtime;
- `TextEncodeQwenImageEditPlus` supports up to three images;
- the text/vision encoder semantically reads the reference image(s), while VAE/reference conditioning also carries appearance;
- intended for explicit semantic image editing rather than only style-preserving regeneration.

## Native ComfyUI parity

The project pins the same ComfyUI commit already used for the Klein branch:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

At that exact commit, native Qwen support includes:

- `TextEncodeQwenImageEditPlus`;
- `FluxKontextImageScale`;
- `ModelSamplingAuraFlow`;
- `CFGNorm`;
- native Qwen image CLIP/VAE handling.

The adapter follows the pinned `Image Edit (Qwen 2509)` blueprint rather than inventing an equivalent graph.

Native non-Lightning recipe used by Runner62:

- diffusion: `qwen_image_edit_2509_fp8_e4m3fn.safetensors`;
- text/vision encoder: `qwen_2.5_vl_7b_fp8_scaled.safetensors`;
- VAE: `qwen_image_vae.safetensors`;
- Qwen encoder device: **CPU** to reduce 12 GB VRAM pressure;
- primary image -> `FluxKontextImageScale` -> VAE latent;
- positive/negative -> `TextEncodeQwenImageEditPlus` with the same image references;
- `ModelSamplingAuraFlow` shift 3;
- `CFGNorm` strength 1;
- Euler;
- simple scheduler;
- denoise 1;
- 20 steps;
- CFG 4;
- no Lightning LoRA.

## Payload

Runner62 creates an isolated workspace:

`Z:\AI\QwenImageEdit`

Required model files:

### Diffusion

`qwen_image_edit_2509_fp8_e4m3fn.safetensors`

- bytes: `20,430,698,424`
- SHA256: `318568f61951ab9da21100c7b896e3c1da67f0d2efad6421545e022cfaa2b2b4`

### Text/vision encoder

`qwen_2.5_vl_7b_fp8_scaled.safetensors`

- bytes: `9,384,670,680`
- SHA256: `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`

### VAE

`qwen_image_vae.safetensors`

- bytes: `253,806,246`
- SHA256: `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

Total model payload:

`30,069,175,350` bytes (~30.07 GB decimal / ~28.00 GiB).

Downloads are resumable and SHA256-verified.

The existing Klein/H3/Kontext workspaces are not modified.

## Low-VRAM strategy

Target workstation:

- Windows 11;
- RTX 3060 12 GB;
- 48 GB system RAM.

Runner62 launches ComfyUI with:

- `--lowvram`;
- `--reserve-vram 1.0`;
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.

The 9.38 GB Qwen2.5-VL encoder is loaded explicitly on CPU.

This first gate uses the full native FP8 editor rather than Nunchaku/int4 or Lightning so the project can separate **model capability** from later acceleration/quantization choices.

## Precision tests

Runner62 compares Qwen directly against Runner61 Klein outputs.

### Atomic plank

Request:

- remove exactly **one plank-width** from the left door leaf;
- leave one narrow full-height gap;
- preserve every neighboring plank;
- preserve right leaf, masonry and straps.

Klein Runner61 failure reference:

`Z:\AI\Flux2Klein\base_atomic_sequence\atomic_plank.png`

### Atomic strap

Request:

- break only the **lower horizontal strap on the right door leaf**;
- remove a substantial middle section of that strap;
- leave snapped/deformed surviving metal;
- preserve every plank, other hardware and upper masonry.

Klein Runner61 failure reference:

`Z:\AI\Flux2Klein\base_atomic_sequence\atomic_strap.png`

## Outputs

Directory:

`Z:\AI\QwenImageEdit\feasibility_gate`

Expected:

- `qwen2509_atomic_plank.png`
- `qwen2509_atomic_strap.png`
- `runner62_qwen2509_vs_klein_contact_sheet.png`
- `runner62_qwen2509_manifest.json`
- `runner62_executor.log`
- Python stdout/stderr logs
- ComfyUI stdout/stderr logs

## PASS criteria

### Technical

- isolated runtime starts on RTX 3060 12 GB;
- no OOM/runtime crash;
- both native 20-step edits complete;
- valid images/manifests are written.

### Visual

Qwen must materially improve precision over Runner61:

- one-plank request removes approximately one plank-width rather than an entire leaf/opening;
- one-strap request isolates the intended lower-right strap instead of redesigning the hardware set;
- gate identity/camera/unrelated geometry remain substantially intact.

## Decision after Runner62

### Technical + visual PASS

Promote Qwen 2509 to the next Asset Studio validation stage:

1. multi-reference semantic-role test;
2. high-difficulty Character Lab test with Exilada identity/anatomy/style references;
3. second non-character class;
4. generic Studio UI exposure/candidate history/approval.

### OOM/runtime failure

Do not reject the model semantically. Investigate a lower-memory implementation such as Nunchaku/int4 while preserving this native FP8 evidence.

### Technical PASS / visual precision FAIL

Do not blindly increase steps. Reconsider the specialized editor branch/control strategy before integrating it into the Studio.

## Runner

`tools/structured-2d-character-pipeline/62_bootstrap_and_run_qwen_image_edit_2509_feasibility.ps1`

Executor:

`tools/roguelite-asset-studio/qwen_image_edit_2509_feasibility_gate.py`

Adapter:

`tools/roguelite-asset-studio/qwen_image_edit_2509_adapter.py`

Expected technical completion:

`RUNNER62-QWEN2509: PASS - TECHNICAL ATOMIC MATRIX COMPLETE / VISUAL VERDICT PENDING`
