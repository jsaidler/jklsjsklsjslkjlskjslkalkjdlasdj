# FLUX.1 Kontext [dev] — Local Pixel-Art Reconstruction Spike

Status date: **2026-09-08**

Status: **CANONICAL / LOCAL INFERENCE PROVEN / RUNNER52 STRUCTURE+LAYOUT PASS / FINAL PIXEL-ART QUALITY STILL OPEN / RUNNER53 STYLE-ADAPTER PROBE CURRENT GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

Canonical workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Runner52 result: `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`.

Historical records:

- `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`
- `docs/RUNNER51_LAYOUT_CONCEPT_REJECT_2026-09-08.md`
- `docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`
- `docs/RUNNER50_CLIP_L_SHA256_PREFLIGHT_FAIL_2026-09-08.md`

## Purpose

Prove an all-local downstream renderer:

`existing H3 Base50 motion master -> selected action frames -> FLUX Kontext structure-preserving edit -> deliberate high-quality pixel art -> one horizontal action row + RGBA/preview/metadata`

Current source remains:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

The H0 video is a dance/gesture-like action, not a walk. No new H3 generation is needed while the renderer is being debugged.

## Locked motion source

H3 H0 Base50 remains preferred:

- `448×800`;
- `124f@24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`.

## Local renderer runtime

Workspace: `Z:\AI\FluxKontext`

ComfyUI:

- pinned portable v0.34.0;
- port `8191`;
- native/core Kontext nodes.

Installed/verified model set:

- `flux1-dev-kontext_fp8_scaled.safetensors` ~11.9GB, SHA256 `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`;
- `clip_l.safetensors` ~246MB, SHA256 `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`;
- `t5xxl_fp16.safetensors` ~9.79GB, SHA256 `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`;
- `ae.safetensors` ~335MB, SHA256 `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`.

Reuse this installation.

## Spritesheet layout — HARD LOCK

**One action = one spritesheet row.**

Frames read left-to-right. Internal `2×2` Kontext tiles are processing topology only and never define final action rows.

Current H0 proof:

- 12 selected action frames;
- final `12×1` layout;
- `192×192` cells;
- `2304×192` local review row.

## Runner50 — CLOSED / MODEL-TASK FAIL

Technical inference worked, but denoise1.0 allowed adult body drift/infantilization and the task/layout formulation was wrong. Pixel-art quality was only partial.

## Runner51 — CLOSED PRE-INFERENCE

Rejected because it split one action into three final rows. No model-quality evidence.

## Runner52 — COMPLETED / PARTIAL PASS

Runner:

`tools/structured-2d-character-pipeline/52_run_flux_kontext_h0_dance12_single_action_row.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance12_single_action_row_structure_lock.py`

Source frames one-based:

`1,12,23,35,46,57,68,79,90,102,113,124`

Renderer settings:

- FP8 Kontext;
- 20 steps;
- guidance2.5;
- CFG1;
- Euler/simple;
- seed0;
- denoise0.45;
- canonical Exilada as second reference;
- three internal four-frame `2×2` processing chunks.

Completed evidence:

- prompt ids:
  - `0cb61aec-f6f9-4073-9941-970186ff7d15`;
  - `10bff98b-7453-4064-9e30-95b76dfd38b5`;
  - `65b26095-ccf5-4874-80d0-ca624b9cdb4b`;
- elapsed chunk times `288.49s`, `280.52s`, `280.34s`;
- total Kontext time `849.35s` (~14m09s).

Visual verdict:

- one-action layout: **PASS**;
- mature adult body preservation: **PASS_CANDIDATE**;
- pose fidelity: **PASS_CANDIDATE**;
- cross-chunk consistency: **PASS_CANDIDATE**;
- automatic alpha: **PASS_CANDIDATE**;
- final deliberate high-level pixel art: **NOT YET PASS**.

The main remaining problem is stylistic construction: residual painterly/raster microtexture and noisy miniature detail still dominate instead of clean authored pixel clusters and controlled material grouping.

Runner52 timing metadata (`250–479ms`) preserves broad source-video coverage only; it is not the final runtime action-timing solution.

## Current controlled hypothesis

Do **not** increase denoise first. `0.45` is what currently preserves adult structure.

Instead add a dedicated pixel-art style LoRA while holding all structure variables fixed.

Candidate:

- `UmeAiRT/FLUX.1-dev-LoRA-Modern_Pixel_art`;
- `ume_modern_pixelart.safetensors`;
- ~344MB;
- SHA256 `ed226c149dca6286ae345b6900d807f791a52b1746ed8f524af41efdfda6f0a4`;
- LoRA license MIT;
- underlying Kontext non-commercial license remains the governing base-model caveat.

Ordinary FLUX.1-dev LoRA compatibility with Kontext is not assumed as guaranteed. Therefore test one representative chunk first.

## Runner53 — CURRENT GATE

Runner:

`tools/structured-2d-character-pipeline/53_run_flux_kontext_h0_dance_chunk2_modern_pixelart_lora_probe.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance_chunk2_modern_pixelart_lora_probe.py`

Controlled inputs/settings:

- source frames `46,57,68,79` only;
- canonical Exilada reference;
- same Kontext FP8;
- same 20 steps / guidance2.5 / CFG1 / Euler-simple / seed0 / denoise0.45;
- only new variable = Modern Pixel Art LoRA strength1.0 + its style trigger wording.

Expected outputs under `Z:\AI\FluxKontext`:

- `h0_dance12_chunk02_pixelart_lora_full.png`
- `h0_dance12_chunk02_pixelart_lora_strip_opaque.png`
- `h0_dance12_chunk02_pixelart_lora_strip_rgba.png`
- `h0_dance12_chunk02_pixelart_lora_preview.gif`
- `h0_dance12_chunk02_pixelart_lora_manifest.json`
- `h0_dance12_chunk02_pixelart_lora_executor.log`

PASS requires materially better intentional pixel-art construction without reintroducing body/pose drift or losing the mature Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell charge.

If Runner53 fails, reject the adapter specifically before changing denoise, precision or renderer family.

## License boundary

FLUX.1 Kontext [dev] open weights are governed by the FLUX.1 dev non-commercial license. Technical validation is acceptable; commercial shipping later requires appropriate BFL licensing or a renderer with compatible terms.
