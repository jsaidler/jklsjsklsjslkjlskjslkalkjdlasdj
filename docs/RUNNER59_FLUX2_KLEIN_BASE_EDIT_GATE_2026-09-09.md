# Runner59 — FLUX.2 Klein 4B Base strong reference-edit gate

Status date: **2026-09-09**

Status: **TECHNICAL PASS / VISUAL OUTPUT ANOMALOUS / RECIPE-PARITY INVALID FOR MODEL VERDICT**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner59 tested the non-distilled Apache-2.0 FLUX.2 Klein 4B Base branch after Runner58 showed that the distilled 4B branch could not provide strong enough production reference editing.

The Base test reused the existing Qwen3-4B encoder and downloaded only:

- `flux-2-klein-base-4b-fp8.safetensors`
  - 4,089,498,488 bytes
  - SHA256 `44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840`
- `full_encoder_small_decoder.safetensors`
  - 249,519,092 bytes
  - SHA256 `ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62`

Existing:

- `qwen_3_4b.safetensors`
  - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`

Runtime remained:

- `Z:\AI\Flux2Klein`
- ComfyUI commit `672ba9e5e388bd6bfac5ceef61f89ffdd9467200`
- RTX 3060 12 GB / 48 GB RAM

## Actual technical result

All four Base jobs completed successfully with no OOM or graph/runtime crash.

Controlled settings:

- 768×768
- CFG 5
- Euler
- seed 0
- 20 and 50 steps

### Single-reference

20 steps:

- elapsed: **78.442 s**
- output SHA256: `9daeeb9b4922c0d368a6724bb2502343c49f4ef9066e327bc1ab1278f02917f9`
- mean abs luma vs original: `74.1022`
- changed ratio >24: `0.893911`

50 steps:

- elapsed: **188.464 s**
- output SHA256: `e2625714562cca1c9a56623a16434e4c6a38b9c06c2a5d7724472796fd5a7e2c`
- mean abs luma vs original: `80.1581`
- changed ratio >24: `0.900733`

### Multi-reference

20 steps:

- elapsed: **120.351 s**
- output SHA256: `57c7781d28bba6321f1ef2343552133d746d7948e80df1d689e4f256c1484111`
- mean abs luma vs original: `77.3237`
- changed ratio >24: `0.888847`

50 steps:

- elapsed: **294.981 s**
- output SHA256: `44f3dd103432b2691fc5dfc7b33538816dbd58e0ef78cc765211bb1953e8eac2`
- mean abs luma vs original: `81.2850`
- changed ratio >24: `0.895187`

Total elapsed: **695.251 s**.

Contact sheet SHA256:

`214c4633983f4eac8b1e2c5e7816b8b68df0ca4b44f179ee95fdb82a2f6e25fc`

## Visual result

All four Base outputs show a severe cyan/blue cast, extreme contrast/posterization and edge-emphasis unlike the source material or the valid distilled T2I output.

The effect is broadly shared by:

- single 20;
- single 50;
- multi 20;
- multi 50.

The requested structural edits also are not reliably executed strongly enough to satisfy the production contract.

However, **this visual result must not be interpreted as a valid rejection of the Base model itself**.

## Discovered graph-parity defect

After Runner59 completed, the project compared the custom Base adapter against the current official ComfyUI `image_flux2_klein_image_edit_4b_base` workflow.

The current official Base workflow uses:

- `CLIPTextEncode` for the positive prompt;
- a separate `CLIPTextEncode` with an empty string for the negative prompt;
- `ReferenceLatent` applied to both positive and negative conditioning;
- `ImageScaleToTotalPixels` using `nearest-exact`, target `1.0` MP;
- output scheduler/latent dimensions derived from the scaled reference image;
- Euler;
- CFG 5;
- 20 steps.

Runner59's original custom Base adapter instead inherited the distilled shortcut and built the negative branch with:

`ConditioningZeroOut(positive)`

before applying the same reference latent.

At CFG 5 this is not equivalent to the official empty-prompt negative conditioning and is a material recipe divergence.

Runner59 also kept the edit output at fixed 768×768 instead of following the official 1-MP reference geometry path.

## Classification

Runner59 is therefore classified as:

**technical PASS / recipe-parity mismatch / invalid as a model-quality verdict**.

It proves:

- Base FP8 loads on the RTX 3060 12 GB;
- full-encoder/small-decoder VAE loads;
- 20/50-step single and multi graphs execute without OOM;
- current payload/hardware feasibility is real.

It does **not** prove:

- that Base normally produces the cyan/posterized appearance;
- that Base is unsuitable as the production strong editor;
- that the project should move to Qwen immediately.

## Corrective action

The Base adapter is corrected in `main` to match the current official conditioning and reference-scaling semantics.

The next gate is Runner60:

`tools/structured-2d-character-pipeline/60_run_flux2_klein_base_official_parity_gate.ps1`

Runner60 does not download any new model. It isolates:

1. Base small-decoder VAE round-trip;
2. full FLUX.2 VAE round-trip control;
3. Base T2I with corrected graph;
4. Base single-reference edit at official 20-step recipe;
5. Base multi-reference edit at the same corrected recipe.

Only after Runner60 can the project issue a valid visual verdict on Base or activate the next specialized editor branch.
