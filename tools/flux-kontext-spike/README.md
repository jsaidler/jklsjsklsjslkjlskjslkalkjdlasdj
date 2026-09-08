# FLUX.1 Kontext local pixel-art reconstruction tooling

Status date: **2026-09-08**

Status: **ACTIVE / RUNNER50 PREPARED / FIRST DOWNSTREAM PROOF USES EXISTING H0 DANCE-GESTURE VIDEO / NO NEW H3 INFERENCE**

Canonical workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Detailed spike: `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`.

## Purpose

Validate the missing downstream stage:

`existing H3 Base50 motion master -> 12-frame action sheet + canonical character reference -> FLUX.1 Kontext [dev] -> final-style pixel-art sheet -> automatic alpha/splitting -> runtime review spritesheet`

This proof deliberately reuses the completed H0 dance/gesture video. It does not spend another ~75 minutes generating a new H3 action.

## Workspace

- H3 evidence/source: `Z:\AI\MiniMaxH3`
- separate Kontext workspace: `Z:\AI\FluxKontext`
- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- `D:\AI` remains invalid/stale.

Runner50 clones only the already-proven pinned ComfyUI v0.34.0 runtime from the H3 portable install while excluding H3 models/input/output/user data. Kontext remains isolated from the H3 model payload.

## First model set

Quality-first practical local set for RTX 3060 12GB / 48GB RAM:

- `flux1-dev-kontext_fp8_scaled.safetensors` — official ComfyUI repack, ~11.9GB, SHA256 `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`;
- `clip_l.safetensors` — ~246MB, SHA256 `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c8576cd796491d9a6cdd`;
- `t5xxl_fp16.safetensors` — ~9.79GB, SHA256 `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`;
- `ae.safetensors` — ~335MB, SHA256 `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`.

Total model payload for the first proof: about **22.3GB**.

Why this combination:

- native/core ComfyUI workflow, no custom GGUF node dependency;
- official FP8-scaled Kontext diffusion is the practical 12GB-VRAM starting point;
- T5XXL stays FP16 because the machine has 48GB system RAM and quality is more important than minimizing every byte;
- if the FP8-scaled diffusion itself is the identified quality bottleneck, full BF16 Kontext is the next controlled quality branch, not an immediate duplicate download.

## Runner50

`tools/structured-2d-character-pipeline/50_run_flux_kontext_h0_dance12_pixelart_proof.ps1`

Runner50:

1. checks the canonical Base50 H0 video and Exilada reference;
2. creates an isolated `Z:\AI\FluxKontext` portable runtime from the proven H3 ComfyUI v0.34.0 install without copying H3 models;
3. downloads/verifies only the four Kontext dependencies above;
4. launches the isolated ComfyUI on port `8191`;
5. invokes `run_h0_dance12_pixelart_proof.py`;
6. stops the managed ComfyUI after completion/failure.

## Executor

`run_h0_dance12_pixelart_proof.py`

The executor:

- decodes the existing 124-frame H0 Base50 video;
- deterministically selects 12 frames across the current dance/gesture action: `1, 12, 23, 35, 46, 57, 68, 79, 90, 102, 113, 124`;
- automatically estimates the simple H0 background and creates complete-character cutouts;
- uses one global scale and preserves relative horizontal/vertical movement rather than independently resizing every pose;
- builds a square `1024×1024` Kontext input with a centered `4×3` grid of `256×256` working cells;
- loads the action sheet as the output-composition latent authority;
- loads the canonical Exilada as a second `ReferenceLatent` identity/style authority;
- uses native Kontext nodes, `20` steps, guidance `2.5`, CFG `1`, `euler/simple`, seed `0`;
- asks Kontext to preserve the exact 12 poses/grid while reconstructing the full set as coherent high-quality pixel art;
- crops the centered grid, downsamples the whole set by exact nearest-neighbor to `4×3` `192×192` runtime review cells (`768×576` total);
- attempts automatic neutral-background alpha extraction;
- writes individual RGBA frames, opaque/RGBA sheets, GIF preview and manifest.

The 12-frame selection is intentionally simple for this first downstream renderer proof. Semantic action/cycle distillation is a later stage and must not be confused with this renderer test.

## Expected outputs

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

The model is not accepted just because inference completes.

PASS requires:

- the 12 source action poses remain recognizable;
- Exilada identity/design stays coherent across cells;
- the result actually reads as authored high-quality pixel art;
- no destructive pose rewriting or extra/missing limbs;
- hair/cloth/restraint masses survive;
- gameplay-scale review remains legible;
- automatic alpha is usable without routine manual masks.

## License

FLUX.1 Kontext [dev] open weights are governed by the FLUX.1 dev non-commercial license. This is a technical R&D validation. Commercial shipping requires appropriate BFL commercial licensing or a renderer with compatible commercial rights.
