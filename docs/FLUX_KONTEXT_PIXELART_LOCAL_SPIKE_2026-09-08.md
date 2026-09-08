# FLUX.1 Kontext [dev] — Local Pixel-Art Reconstruction Spike

Status date: **2026-09-08**

Status: **CANONICAL / RUNNER50 PREPARED / EXISTING H0 DANCE-GESTURE VIDEO IS THE FIRST DOWNSTREAM PROOF INPUT**

Canonical project state: `docs/PROJECT_STATE.md`.

Canonical end-to-end workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Purpose

Prove the missing local downstream renderer without regenerating motion:

`existing approved H3 Base50 H0 motion master -> deterministic 12-frame action set -> canonical Exilada identity reference -> FLUX.1 Kontext [dev] -> coherent high-quality pixel-art set -> automatic alpha/split -> runtime review spritesheet`

This gate tests the renderer, not the motion model. A Kontext failure does not retroactively invalidate H3 H0.

## Why the existing H0 video is used

The current H0 video is a dance/gesture-like action, not a walk. That does not matter for this gate because the question is whether already-good generated motion can be converted into a final pixel-art animation asset.

Using the existing H0 avoids another ~75-minute Base50 video generation while proving the rest of the pipeline.

Canonical H0 source:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H0 remains the preferred motion-master quality baseline:

- `448×800`;
- `124f @24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed `0`;
- `ref_image_size=match`.

Turbo4 remains rejected for production quality.

## Why FLUX.1 Kontext [dev]

The final renderer problem is image editing/style reconstruction with pose and character preservation, not video generation.

Kontext is the preferred first technical candidate because the desired operation is:

- keep the action composition and pose;
- keep the character identity/design;
- change the visible rendering language to deliberate high-quality pixel art;
- keep a coherent set-level palette/style across multiple frames.

The first experiment intentionally conditions on both:

1. a square 12-frame H0 action sheet as the composition/pose authority;
2. the canonical Exilada image as a second identity/style reference latent.

## Runtime isolation

Workspace:

`Z:\AI\FluxKontext`

Runner50 reuses the already-proven **ComfyUI v0.34.0 code/runtime** by cloning the H3 portable install into a separate workspace while explicitly excluding H3 models, input, output, temp and user data.

This keeps the renderer isolated while avoiding a second unrelated ComfyUI version.

Server port for the isolated renderer:

`8191`

No custom nodes are required for this first proof; the graph uses native/core Kontext nodes.

## First local model payload

The first hardware-quality compromise is deliberately narrow.

### Diffusion

`flux1-dev-kontext_fp8_scaled.safetensors`

- official ComfyUI repack;
- approximately 11.9GB;
- SHA256 `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`.

This is selected as the practical native starting point for the RTX 3060 12GB. It avoids adding the GGUF custom-node stack before the official native path is tested.

If and only if completed visual evidence points specifically to FP8 diffusion quality as the renderer bottleneck, full BF16 Kontext becomes the next controlled quality branch.

### Text encoders

`clip_l.safetensors`

- ~246MB;
- SHA256 `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c8576cd796491d9a6cdd`.

`t5xxl_fp16.safetensors`

- ~9.79GB;
- SHA256 `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`.

T5 is intentionally kept at FP16 because the machine has 48GB system RAM and the project is quality-first.

### VAE

`ae.safetensors`

- ~335MB;
- SHA256 `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`.

Total first renderer payload: about **22.3GB**.

## Runner50

`tools/structured-2d-character-pipeline/50_run_flux_kontext_h0_dance12_pixelart_proof.ps1`

Runner50 performs the whole first local renderer proof:

1. verifies the canonical H0 video and Exilada reference;
2. creates/uses isolated `Z:\AI\FluxKontext` runtime;
3. downloads and SHA-verifies only the four model files above;
4. launches isolated ComfyUI on `127.0.0.1:8191`;
5. executes the H0 dance12 Kontext proof;
6. stops managed ComfyUI after completion/failure.

## Action-sheet preparation

The first proof intentionally avoids pretending semantic action distillation is already solved.

Deterministic selected H0 frames, 1-based:

`1, 12, 23, 35, 46, 57, 68, 79, 90, 102, 113, 124`

These provide even temporal coverage of the existing action.

Automatic preparation:

- estimate the simple H0 background from frame corners;
- derive complete-character cutouts;
- use one global scale for the whole set;
- preserve relative horizontal/vertical movement instead of independently resizing each pose;
- build a centered `4×3` grid inside a square `1024×1024` sheet;
- working cells are `256×256`;
- the grid occupies the central `1024×768` region, with 128px top/bottom margins.

The square input intentionally matches a native Kontext preferred resolution and avoids aspect-ratio deformation of the 4×3 grid.

## Kontext graph

Native/core nodes only:

- `UNETLoader`;
- `DualCLIPLoader`;
- `VAELoader`;
- `LoadImage`;
- `FluxKontextImageScale`;
- `VAEEncode`;
- `CLIPTextEncode`;
- `ConditioningZeroOut`;
- chained `ReferenceLatent` nodes for action sheet + canonical Exilada;
- `FluxGuidance`;
- `KSampler`;
- `VAEDecode`;
- `SaveImage`.

Initial sampling settings follow the official/basic Kontext structure:

- 20 steps;
- guidance 2.5;
- CFG 1.0;
- Euler;
- simple scheduler;
- seed 0;
- denoise 1.0.

This is a renderer-quality baseline, not an optimization sweep.

## Output finalization

After Kontext generation:

1. retain the full square output for diagnosis;
2. crop the expected centered 4×3 grid;
3. downscale the **whole grid together** by exact nearest-neighbor to `768×576`;
4. therefore each runtime review cell is `192×192`;
5. attempt automatic neutral-background removal independently per cell;
6. write individual RGBA frames;
7. write opaque and RGBA sheets;
8. write a GIF preview and provenance manifest.

Nearest-neighbor here is only the deterministic final grid reduction after the generative pixel-art reconstruction. It is not being used as a substitute for the renderer.

## Expected artifacts

Under `Z:\AI\FluxKontext`:

- `h0_dance12_input_sheet.png`
- `h0_dance12_selection_manifest.json`
- `h0_dance12_kontext_api_prompt.json`
- `h0_dance12_kontext_full.png`
- `h0_dance12_kontext_working_grid.png`
- `h0_dance12_pixelart_sheet_opaque.png`
- `h0_dance12_pixelart_sheet_rgba.png`
- `h0_dance12_pixelart_frames/`
- `h0_dance12_pixelart_preview.gif`
- `h0_dance12_kontext_manifest.json`
- `h0_dance12_kontext_executor.log`

## Pass criteria

Inference completion alone is not a renderer PASS.

Visual PASS requires:

1. all 12 source poses remain materially recognizable;
2. the same Exilada identity/design is coherent across the set;
3. output reads as deliberate high-quality pixel art rather than smooth/painterly miniature illustration;
4. no extra/missing/fused limbs or destructive pose rewriting;
5. long hair, torn cloth and restraint/accessory masses remain readable;
6. the `192×192` review cells survive near the intended ~128px gameplay character height;
7. automatic alpha is usable without routine manual masks.

Failure must be classified by layer: integration/runtime, layout/conditioning, model/style quality, identity, topology, alpha or gameplay-scale readability.

## License boundary

FLUX.1 Kontext [dev] open weights are governed by the FLUX.1 dev non-commercial license.

This spike is a local technical R&D validation. A commercial game release requires appropriate BFL commercial licensing or replacement of the renderer with a model whose commercial terms fit production.

## Next decision after Runner50

- If Kontext FP8 passes: make this the first renderer backend and build the Gradio orchestration UI around the proven H3 Base50 + Kontext stages.
- If the renderer is structurally good but visibly under-resolved: test full BF16 Kontext as the next controlled variable.
- If Kontext rewrites poses/layout/identity despite controlled prompting and multi-reference conditioning: classify the specific failure before trying another renderer family.
- Do not generate a new H3 walk/action merely to debug the renderer; continue using the existing H0 until this downstream stage is understood.
