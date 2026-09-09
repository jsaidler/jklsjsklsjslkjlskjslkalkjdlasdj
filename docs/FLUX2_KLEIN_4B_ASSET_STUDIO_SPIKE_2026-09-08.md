# FLUX.2 Klein 4B — Roguelite Asset Studio local feasibility spike

Status date: **2026-09-08**

Status: **RUNNER56 PREPARED / DOWNLOAD + TECHNICAL T2I TEST PENDING LOCAL EXECUTION / NO ACCEPTANCE YET**

Canonical umbrella architecture: `docs/ROGUELITE_ASSET_STUDIO.md`.

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Validate whether **FLUX.2 Klein 4B distilled FP8** can become the first generic static generation/editing backend for the Roguelite Asset Studio on the actual production workstation:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB system RAM.

This is deliberately not an Exilada-only test. The first generated asset is a reference-free `architecture_module`, proving text-to-image generation outside character work before the adapter is exposed to Character Lab.

## Why this model is being tested first

The 4B Klein family is a strong fit for the general Studio contract because it combines:

- text-to-image generation;
- image editing;
- single/multi-reference editing;
- consumer-GPU intent;
- Apache-2.0 licensing for the 4B line;
- a distilled 4-step path suitable for interactive authoring;
- a related Base 4B model suitable for later project-specific fine-tuning.

The model is not accepted merely because these capabilities exist on paper. Runner56 tests the exact local machine and exact runtime path.

## Deliberate first-spike scope

Runner56 tests **only reference-free text-to-image**.

Reason: generation, single-reference editing and multi-reference editing are separate execution contracts. Testing all three simultaneously would make failures ambiguous.

If T2I passes technically and visually enough to continue, the next spike adds single/multi-reference editing through the same isolated runtime before the registry status is promoted to an installed Studio adapter.

## Exact first payload

Runner56 downloads only these model files:

### Diffusion

- file: `flux-2-klein-4b-fp8.safetensors`
- source: official Black Forest Labs `FLUX.2-klein-4b-fp8`
- size: `4,070,624,520` bytes (~4.07 GB decimal)
- SHA256: `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6`
- license: Apache-2.0

### Text encoder

- file: `qwen_3_4b.safetensors`
- source: Comfy-Org Klein 4B repack
- size: `8,044,982,048` bytes (~8.04 GB decimal)
- SHA256: `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`

The first spike intentionally uses the **full** Qwen3-4B encoder rather than the smaller FP4 encoder. This avoids introducing encoder quantization as a second quality variable during the first model-feasibility test.

### VAE

- file: `flux2-vae.safetensors`
- source: Comfy-Org Klein 4B repack
- size: `336,211,292` bytes (~336 MB decimal)
- SHA256: `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`

### Total model payload

`12,451,817,860` bytes, approximately `12.45 GB` decimal / `11.60 GiB` binary.

No Base 4B diffusion checkpoint and no Qwen FP4 encoder are downloaded by Runner56.

## Isolated runtime

Workspace:

`Z:\AI\Flux2Klein`

Runner56 does not modify the existing H3 or Kontext workspaces.

It creates:

`Z:\AI\Flux2Klein\ComfyUI_windows_portable`

The already-proven embedded Python from the Kontext portable installation is copied once as the starting Python runtime. The copy is then independent; dependency installation occurs only in the copied runtime.

ComfyUI itself is cloned separately and pinned to:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

This prevents future upstream Comfy changes from silently altering the spike after evidence is recorded.

## Native ComfyUI graph

The probe uses current native/core nodes rather than a third-party custom-node stack:

- `UNETLoader`;
- `CLIPLoader` with `type=flux2`;
- `VAELoader`;
- `CLIPTextEncode` positive/negative;
- `CFGGuider`;
- `RandomNoise`;
- `KSamplerSelect`;
- `Flux2Scheduler`;
- `EmptyFlux2LatentImage`;
- `SamplerCustomAdvanced`;
- `VAEDecode`;
- `SaveImage`.

## Controlled inference configuration

- model: FLUX.2 Klein 4B distilled FP8;
- output: `768×768`;
- steps: `4`;
- CFG: `1.0`;
- sampler: `euler`;
- seed: `0`;
- one image only.

The reduced 768×768 first probe is a feasibility setting, not an Asset Studio production-resolution lock.

## Probe asset

Asset class:

- `asset_type=architecture_module`;
- `output_contract=static_master`;
- no input references.

Subject: one complete modular ruined stone gate suitable as a source asset for the living belt-scroller world.

The prompt requests a neutral authoring background, complete object visibility, strong silhouette, believable construction and tactile dark-fantasy materials. It explicitly avoids people, characters and a full flattened gameplay-map composition.

## Runner

`tools/structured-2d-character-pipeline/56_bootstrap_and_run_flux2_klein_4b_spike.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_t2i_probe.py`

## Expected output

Under:

`Z:\AI\Flux2Klein\spike`

- `flux2_klein_4b_t2i_probe.png`;
- `flux2_klein_4b_t2i_prompt.json`;
- `flux2_klein_4b_t2i_manifest.json`;
- `flux2_klein_4b_t2i_executor.log`;
- isolated Comfy stdout/stderr logs.

## PASS / FAIL contract

### Technical PASS

Requires all of the following:

- pinned isolated ComfyUI starts normally;
- exact model/text-encoder/VAE hashes pass;
- all required native nodes exist;
- no OOM/runtime crash;
- one valid 768×768 image is decoded and saved;
- manifest/provenance is written.

### Technical FAIL classifications

- insufficient disk space;
- download/hash failure;
- pinned-Comfy integration failure;
- missing native node;
- model-load failure;
- OOM or CUDA failure;
- inference/API failure;
- output decode/integration failure.

A failure here rejects or modifies the **runtime configuration being tested**, not automatically the entire Klein family.

### Visual continuation gate

After technical PASS, human review decides whether quality is sufficient to justify the editing spike.

Review:

- coherent architectural construction;
- useful specificity rather than generic noise;
- strong silhouette;
- useful material detail;
- no catastrophic text/composition artifacts;
- enough source quality to make iterative static asset authoring plausible.

This first image does **not** need to prove final project pixel-art language. Rendering-language specialization/reconstruction remains a separate downstream problem.

## Next step after PASS

If Runner56 passes technically and its source quality is useful:

1. retain the installed isolated runtime;
2. change the registry status only after recorded review;
3. add one generic Klein adapter supporting `text_to_image`;
4. immediately test `single_reference_edit` and `multi_reference_edit` using semantic reference roles;
5. then expose the adapter to Character Lab, Prop/Equipment and Environment workflows;
6. keep Base 4B/fine-tuning as a later controlled specialization branch rather than downloading it now.
