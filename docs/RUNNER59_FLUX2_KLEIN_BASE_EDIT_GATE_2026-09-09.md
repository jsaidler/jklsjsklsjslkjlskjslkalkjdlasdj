# Runner59 — FLUX.2 Klein 4B Base strong reference-edit gate

Status date: **2026-09-09**

Status: **PREPARED / CURRENT GATE / ~4.34 GB ADDITIONAL DOWNLOAD**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner59 exists

Runner58 completed the distilled 4B calibration and failed the production edit-strength gate.

The important distinction is:

- distilled 4B **can** execute reference-edit graphs;
- it preserves source identity/camera well;
- increasing 4 -> 8 -> 12 steps increases broad image drift;
- that extra drift does **not** reliably execute explicit structural edits;
- multi-reference material authority remains too weak.

Therefore the next test stays inside the same Apache-2.0 Klein 4B family and evaluates the **non-distilled Base variant**, rather than jumping immediately to a different model family.

## Why Base is a legitimate separate hypothesis

Current official ComfyUI material distinguishes:

- 4B Distilled: speed-first, 4-step path;
- 4B Base: non-distilled / higher-flexibility path.

The current official Base image-edit template uses:

- Euler sampler;
- CFG 5;
- 20 steps;
- Qwen3-4B text encoder;
- `full_encoder_small_decoder.safetensors`.

The broader Base family is also documented as the full-step/fine-tuning branch, so Runner59 includes a controlled 50-step comparison rather than treating 20 steps as the only possible operating point.

## Runtime

Existing isolated workspace:

`Z:\AI\Flux2Klein`

Existing ComfyUI commit remains pinned:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

Existing Qwen3-4B encoder is reused and hash-verified.

No H3 or Kontext runtime is modified.

## Additional payload

Runner59 downloads only:

### Base diffusion

- file: `flux-2-klein-base-4b-fp8.safetensors`
- bytes: `4,089,498,488`
- SHA256: `44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840`
- license: Apache-2.0

### Base edit VAE path

- file: `full_encoder_small_decoder.safetensors`
- bytes: `249,519,092`
- SHA256: `ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62`
- license: Apache-2.0

### Total additional payload

`4,339,017,580` bytes (~4.34 GB decimal / ~4.04 GiB).

The existing `qwen_3_4b.safetensors` is reused; it is not downloaded again.

## Adapter architecture

Runner59 does not mutate the already-proven distilled adapter.

New sibling adapter:

`tools/roguelite-asset-studio/flux2_klein_base_adapter.py`

It inherits the generic HTTP execution, reference preparation, output/provenance and reference-latent behavior from the distilled adapter, while explicitly selecting Base checkpoint/VAE assets.

This keeps the Studio architecture model-routed and avoids turning one adapter into an implicit mutable global mode.

## Test sources

### Structure/identity authority

Runner56 original gate:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_probe.png`

### Material authority

Runner58 severe-decay board:

`Z:\AI\Flux2Klein\edit_strength_calibration\material_decay_reference.png`

No new material board is generated, so the Base and distilled branches can be compared against the same semantic references.

## Matrix

Runner59 runs four jobs at 768×768, Euler, CFG 5, seed 0.

### Single-reference

- 20 steps
- 50 steps

Role:

`previous_approved_state`

Requested structural facts remain deliberately binary:

1. remove one full-height plank from the left door leaf;
2. remove one large top-left capstone/lintel mass;
3. break/partially remove the lower strap on the right door leaf;
4. strongly corrode surviving iron;
5. visibly warp/split/water-damage timber.

### Multi-reference

- 20 steps
- 50 steps

Roles:

- Image 1 = `structure`: original gate;
- Image 2 = `material`: Runner58 decay board.

The same structural changes are requested while the second image is explicitly authoritative only for material severity.

## PASS contract

### Technical PASS

Requires:

- both additional files download/resume and exact SHA256 checks pass;
- Base model loads on RTX 3060 12 GB without OOM;
- all four jobs complete;
- contact sheet and manifest are written.

### Visual PASS — single

At least one 20/50-step output must:

- preserve recognizable gate identity and camera;
- clearly remove a full door plank;
- clearly remove a large top-left block;
- clearly break/remove the requested strap;
- show materially stronger decay.

### Visual PASS — multi

At least one output must:

- preserve Image 1 structure/camera;
- visibly import severe material qualities from Image 2;
- execute the same structural facts;
- avoid duplicated gates or material-board contamination.

## Failure consequence

If Base also fails this gate:

- keep Klein distilled as T2I/concept backend;
- do not route either Klein variant as the production strong editor;
- retain Base as a future training/specialization candidate if useful;
- move the production reference-edit problem to the next stronger specialized editor branch, with Qwen-Image-Edit currently first in line for a controlled low-VRAM spike;
- do not keep increasing Klein steps without a new technical hypothesis.

## Runner

`tools/structured-2d-character-pipeline/59_bootstrap_and_run_flux2_klein_base_edit_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_base_edit_gate.py`

Expected terminal completion:

`RUNNER59-FLUX2-KLEIN-BASE-EDIT: PASS - TECHNICAL MATRIX COMPLETE / VISUAL VERDICT PENDING`

Expected output directory:

`Z:\AI\Flux2Klein\base_edit_gate`
