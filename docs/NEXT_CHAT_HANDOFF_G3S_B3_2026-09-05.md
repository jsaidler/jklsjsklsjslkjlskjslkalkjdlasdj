# Next-chat handoff — local complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext workspace: `Z:\AI\FluxKontext`
- paused Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Read first

- `docs/PROJECT_STATE.md`
- `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
- `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`
- `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`
- `docs/VISUAL_DIRECTION.md`
- `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

## Core production contract

`reference image or local text-generated reference + relative world scale + real action driver + action preset -> H3 Base50 motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> local pixel-art reconstruction -> one horizontal row for that action + frames/preview/JSON/manifest`

No routine manual rigging/keyframing/mask repair/per-frame repainting/hand compositing.

## Hard visual locks

Final runtime art = deliberate high-quality pixel art.

H3 video = motion master only.

One action = one horizontal spritesheet row.

Approved adult body design may not be infantilized or redesigned.

Active art lineage remains Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell, with mature adult anatomy, danger, grime, sensuality and tactile materials.

## H3 motion baseline

MiniMax H3 Base Ref2VA remains locked:

- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no Turbo LoRA.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Turbo4 was visually rejected. Base50 remains production default.

The current H0 is a dance/gesture-like action, not a walk.

## Kontext runtime

Installed/proven at `Z:\AI\FluxKontext`:

- ComfyUI v0.34.0 / port8191;
- Kontext FP8;
- CLIP-L;
- T5XXL FP16;
- Flux VAE.

Reuse this installation.

## Runner52 — COMPLETED / PARTIAL PASS

Runner52 correctly produced one `12×1` action row from three internal `2×2` chunks.

Evidence:

- source frames one-based `1,12,23,35,46,57,68,79,90,102,113,124`;
- prompt ids `0cb61aec-f6f9-4073-9941-970186ff7d15`, `10bff98b-7453-4064-9e30-95b76dfd38b5`, `65b26095-ccf5-4874-80d0-ca624b9cdb4b`;
- elapsed `288.49s + 280.52s + 280.34s = 849.35s`;
- 20 steps, guidance2.5, CFG1, Euler/simple, seed0, denoise0.45.

Verdict:

- one-action layout: PASS;
- mature body preservation: PASS_CANDIDATE;
- pose fidelity: PASS_CANDIDATE;
- cross-chunk consistency: PASS_CANDIDATE;
- alpha: PASS_CANDIDATE;
- final deliberate high-level pixel art: NOT YET PASS.

The remaining problem is art construction, not body/layout. Result still reads too much like reduced/filtered raster with noisy miniature detail.

Runner52 timing values around `250–479ms` are provenance/source-coverage evidence, not final game timing.

## CURRENT GATE — Runner53

Goal: strengthen pixel-art language without losing Runner52 structure preservation.

Runner:

`tools/structured-2d-character-pipeline/53_run_flux_kontext_h0_dance_chunk2_modern_pixelart_lora_probe.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance_chunk2_modern_pixelart_lora_probe.py`

Only one representative chunk runs:

- source frames `46,57,68,79`;
- same Exilada reference;
- same Kontext FP8;
- same 20 steps / guidance2.5 / CFG1 / Euler-simple / seed0 / denoise0.45;
- only new variable: `ume_modern_pixelart.safetensors` strength1.0;
- SHA256 `ed226c149dca6286ae345b6900d807f791a52b1746ed8f524af41efdfda6f0a4`;
- ~344MB.

Expected outputs:

- `h0_dance12_chunk02_pixelart_lora_full.png`
- `h0_dance12_chunk02_pixelart_lora_strip_opaque.png`
- `h0_dance12_chunk02_pixelart_lora_strip_rgba.png`
- `h0_dance12_chunk02_pixelart_lora_preview.gif`
- `h0_dance12_chunk02_pixelart_lora_manifest.json`
- `h0_dance12_chunk02_pixelart_lora_executor.log`

## Exact next operator command

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\53_run_flux_kontext_h0_dance_chunk2_modern_pixelart_lora_probe.ps1"
```

First run downloads only the ~344MB style LoRA if absent. No H3 generation and no new Kontext base download.

When Runner53 finishes, compare directly against Runner52 chunk2. PASS requires visibly stronger authored pixel clusters while adult anatomy/pose fidelity remain intact.

If the adapter passes, apply it to all 12 frames. If it fails, reject that adapter before changing denoise/precision/model family.

## Later stages

After renderer quality passes:

1. implement action-specific frame distillation/runtime timing;
2. build Gradio UI;
3. add text-to-reference generation;
4. validate creature/monster relative-scale cases.

## License caveat

FLUX.1 Kontext [dev] remains non-commercial open-weight. The Modern Pixel Art LoRA is MIT, but the base-model commercial caveat still applies.
