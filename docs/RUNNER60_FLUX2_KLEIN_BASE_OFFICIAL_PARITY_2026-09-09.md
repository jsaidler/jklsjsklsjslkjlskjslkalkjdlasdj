# Runner60 — FLUX.2 Klein 4B Base official-parity diagnostic

Status date: **2026-09-09**

Status: **PREPARED / CURRENT GATE / NO NEW DOWNLOAD**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner60 exists

Runner59 proved that the installed FLUX.2 Klein 4B Base FP8 branch can execute on the RTX 3060 12 GB workstation, but all outputs showed a severe cyan/blue posterized appearance.

The project initially could have interpreted this as a Base-model failure. That would be premature.

Comparison against the current official ComfyUI `image_flux2_klein_image_edit_4b_base` graph found a concrete recipe mismatch in the custom Base adapter used by Runner59.

### Official Base conditioning

The current official graph uses:

- positive: `CLIPTextEncode(prompt)`;
- negative: separate `CLIPTextEncode("")`;
- same reference latent appended to both positive and negative through `ReferenceLatent`;
- reference image scaled with `ImageScaleToTotalPixels` / `nearest-exact` / `1.0` MP;
- scheduler and empty latent dimensions derived from the scaled first reference;
- Euler;
- CFG 5;
- 20 steps.

### Runner59 divergence

Runner59's first Base adapter used the distilled shortcut:

`ConditioningZeroOut(positive)`

for the negative branch before adding the reference latent.

At CFG 5 that is not equivalent to an empty-prompt negative CLIP encoding.

Runner59 also kept the edit raster fixed at 768×768 rather than following the official 1-MP reference geometry path.

Therefore Runner59 is retained as hardware/runtime evidence but is **invalid as a final visual model verdict**.

## Runner60 purpose

Isolate the cyan/posterized failure and issue the first parity-valid Base verdict without changing model family or downloading anything new.

## Runtime and payload — unchanged

Workspace:

`Z:\AI\Flux2Klein`

ComfyUI commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

The commit is from 2026-09-09 and is sufficiently current for the tested native Klein nodes.

Required existing files:

### Base diffusion

- `flux-2-klein-base-4b-fp8.safetensors`
- SHA256 `44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840`

### Qwen text encoder

- `qwen_3_4b.safetensors`
- SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`

### Base edit VAE

- `full_encoder_small_decoder.safetensors`
- SHA256 `ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62`

### Proven full FLUX.2 VAE control

- `flux2-vae.safetensors`
- SHA256 `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`

Runner60 downloads **nothing**.

## Corrected Base adapter

File:

`tools/roguelite-asset-studio/flux2_klein_base_adapter.py`

The Base adapter now:

- separately text-encodes positive and negative prompts;
- uses empty negative text by default;
- scales references through `ImageScaleToTotalPixels` using `nearest-exact` at `1.0` MP;
- uses `GetImageSize` from the first scaled reference for edit scheduler/latent geometry;
- appends each encoded reference latent to both positive and negative conditioning;
- keeps semantic reference roles in the Asset Studio layer rather than hard-coding them into ComfyUI nodes.

## Diagnostic matrix

Runner60 performs five jobs.

### A — Base small-decoder VAE round-trip

No diffusion model is sampled.

Path:

`original -> ImageScaleToTotalPixels(1 MP) -> VAEEncode(full_encoder_small_decoder) -> VAEDecode(same VAE)`

Purpose:

Determine whether the cyan/posterized behavior already exists in the Base VAE path itself.

### B — full FLUX.2 VAE control round-trip

Same source and scaling, but using the previously proven:

`flux2-vae.safetensors`

Purpose:

Provide a direct control for VAE round-trip behavior on the same source/raster geometry.

### C — Base T2I control

No reference image.

Settings:

- 1024×1024;
- 20 steps;
- CFG 5;
- Euler;
- seed 6001;
- empty negative prompt.

Prompt asks for natural gray stone, brown timber, dark iron and muted green vegetation on a neutral background.

Purpose:

If VAE round-trips are sane but Base T2I is cyan/posterized, the issue lies above the VAE round-trip layer in Base sampling/model integration.

### D — Base official-parity single-reference edit

Source:

Runner56 original ruined gate.

Reference role:

`previous_approved_state`

Settings:

- first reference scaled to 1 MP / nearest-exact;
- square source therefore resolves to 1024×1024;
- Euler;
- CFG 5;
- 20 steps;
- seed 0;
- separate empty negative CLIP encoding.

Binary requested changes remain:

1. remove one full-height plank from left door leaf;
2. remove one large top-left capstone/lintel mass;
3. break/partially remove lower strap on right door leaf;
4. stronger rust/grime;
5. warped/split water-damaged timber.

### E — Base official-parity multi-reference edit

References:

- Image 1 `structure` = original gate;
- Image 2 `material` = Runner58 decay board.

Same 20-step / CFG 5 / Euler recipe and corrected negative/reference semantics.

## Expected outputs

Directory:

`Z:\AI\Flux2Klein\base_official_parity`

Files:

- `base_small_decoder_roundtrip.png`
- `full_flux2_vae_roundtrip.png`
- `base_official_t2i_steps20.png`
- `base_official_single_steps20.png`
- `base_official_multi_steps20.png`
- `runner60_official_parity_contact_sheet.png`
- `runner60_official_parity_manifest.json`
- `runner60_executor.log`
- Python stdout/stderr logs
- ComfyUI stdout/stderr logs

## Decision tree

### Case 1 — Base VAE round-trip itself is cyan/posterized

Do not judge the Base diffusion model yet.

Investigate the Base VAE/decode path or model/VAE compatibility while retaining full-VAE control evidence.

### Case 2 — both round-trips are sane, Base T2I is cyan/posterized

Classify the problem as Base sampling/checkpoint integration, not reference-edit semantics.

### Case 3 — round-trips and Base T2I are sane, edits are cyan/broken

Classify the remaining defect specifically in reference-edit conditioning/graph behavior.

### Case 4 — all outputs are sane and edits obey structure/material requests

Base becomes eligible for production `single_reference_edit` / `multi_reference_edit` routing after human visual approval.

### Case 5 — all outputs are technically sane but Base editing remains weak/non-obedient

The Klein Base hypothesis is then genuinely exhausted for strong editing on the current workstation/recipe.

Only then move the production edit role to the next specialized branch, currently Qwen-Image-Edit.

## Runner

`tools/structured-2d-character-pipeline/60_run_flux2_klein_base_official_parity_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_base_official_parity_gate.py`

Expected terminal completion:

`RUNNER60-FLUX2-KLEIN-BASE-PARITY: PASS - DIAGNOSTIC MATRIX COMPLETE / VISUAL VERDICT PENDING`
