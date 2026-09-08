# Next-chat handoff — local complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- active H3 motion workspace: `Z:\AI\MiniMaxH3`
- active Kontext renderer workspace: `Z:\AI\FluxKontext`
- paused Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Read first

- `docs/PROJECT_STATE.md`
- `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
- `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`
- `docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`
- `docs/VISUAL_DIRECTION.md`
- `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
- `docs/ANIMATION_PIPELINE.md`
- `docs/CHARACTER_PRODUCTION_PIPELINE.md`
- `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
- `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`

## Current production contract

Final local pipeline:

`existing or locally generated character reference + relative world scale + real action driver + action preset -> H3 Base50 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> FLUX.1 Kontext [dev] pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

No routine manual rigging/keyframing/mask repair/per-frame repainting/hand compositing.

## Final visible art

Runtime characters are deliberate high-quality pixel art.

H3/Wan painterly/raster outputs are intermediate motion/pictorial masters only. The tiny H0 proxy is historical QA, not a production asset.

Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell and mature 1980s sword-and-sorcery direction remain active.

## H3 H0 / Runner48 — COMPLETE / PREFERRED QUALITY BASELINE

Canonical Base50 configuration:

- Picture1 = canonical Exilada;
- Video1 = raw comparison driver, timestamp-resampled only;
- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- video `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / preferred motion-master quality baseline.** Stable body topology, coherent hair/cloth response, no destructive global smear. Chain detail still drifts somewhat. Late foot crop follows driver/source envelope.

## Turbo4 / Runner49 — REJECTED

The 4-step Ref2V Turbo experiment was run and visually rejected by the user.

The user wants the original H0 Base50 quality back.

Therefore:

- Turbo4 is closed as default production setting;
- Base50 is restored;
- do not invent Turbo4 timing/hash/prompt evidence if not recovered locally;
- preserve local output/log/manifest if available, then the Turbo LoRA may be removed.

Record: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

## Existing H0 action clarification

The existing H0 result is a **dance/gesture-like action**, not a walk.

This is now the renderer proof source. Do not generate a new walk merely to test spritesheet conversion.

## CURRENT GATE — Runner50 / FLUX.1 Kontext [dev]

Canonical renderer spike:

`docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`

Runner:

`tools/structured-2d-character-pipeline/50_run_flux_kontext_h0_dance12_pixelart_proof.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance12_pixelart_proof.py`

### Runner50 initial parser incident — FIXED

The first operator invocation failed immediately in the PowerShell parser at two `$Label:` interpolations.

Classification: **INTEGRATION FAIL / PRE-INFERENCE**. No downloads, ComfyUI launch or Kontext inference occurred; zero model-quality evidence.

Repair: delimit the variable as `${Label}:` in the two affected status strings only.

Repair commit: `300f39179ceb01d5689f6c5ba7cc52ca2aaf38d2`.

Do not change renderer settings because of this incident. Pull and rerun the same Runner50 command.

### Workspace/runtime

- renderer workspace: `Z:\AI\FluxKontext`;
- isolated ComfyUI port: `8191`;
- Runner50 clones the proven H3 ComfyUI v0.34.0 portable runtime while excluding H3 models/input/output/user state;
- no custom nodes for this first renderer proof.

### First model set

- `flux1-dev-kontext_fp8_scaled.safetensors` ~11.9GB;
- `clip_l.safetensors` ~246MB;
- `t5xxl_fp16.safetensors` ~9.79GB;
- `ae.safetensors` ~335MB.

Total ~22.3GB.

The native FP8-scaled diffusion is the practical official starting point for RTX 3060 12GB. T5 is kept FP16 because system RAM is 48GB and quality is prioritized. Full BF16 Kontext is the next controlled branch only if completed evidence shows the FP8 diffusion itself is the quality bottleneck.

### First proof contract

No new H3 inference.

Runner50 uses deterministic H0 frames:

`1, 12, 23, 35, 46, 57, 68, 79, 90, 102, 113, 124`

It builds a square `1024×1024` input with a centered `4×3` action grid, conditions Kontext on:

1. the 12-frame action sheet as pose/composition authority;
2. canonical Exilada as identity/style authority.

Kontext baseline:

- 20 steps;
- guidance2.5;
- CFG1.0;
- Euler/simple;
- seed0.

Expected outputs under `Z:\AI\FluxKontext`:

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

### Pass criteria

Runner50 is not accepted just because inference completes. Review separately:

- 12 source poses preserved;
- Exilada identity/design coherent;
- true high-quality pixel-art reading;
- no destructive pose/topology rewrite;
- hair/cloth/restraints retained;
- runtime review readable;
- automatic alpha usable without routine manual masks.

## Exact next operator command

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\50_run_flux_kontext_h0_dance12_pixelart_proof.ps1"
```

The first successful execution downloads about 22.3GB of renderer models plus creates the separate portable runtime. Subsequent runs reuse verified files.

## License caveat

The open-weight Kontext [dev] release is non-commercial. Technical validation is fine; commercial game shipping later requires BFL commercial licensing or a renderer with compatible terms.

SDXL/img2img remains fallback.

## Local authoring UI — REQUIRED AFTER RENDERER PASS

The finished tool must expose one local interface with:

- reference image **or** text-described local reference generation;
- character name/category;
- numeric relative world scale;
- action reference video upload;
- action preset dropdown including common locomotion/combat/weapon/defense/taunt/dance/custom actions;
- locked H3 Base50 production preset by default;
- progress/previews;
- final sheet/frames/preview/JSON/manifest file access.

Gradio is the current V1 UI scaffold choice. Build it after the renderer behavior is proven so the UI orchestrates validated stages instead of hiding unresolved failures.

The exact local text-to-reference model is not yet locked. SDXL-class and FLUX text-to-image families are candidates.

## Relative scale

`relative_scale=1.0` = baseline adult-human/Exilada size, about128px visible height in the canonical gameplay composition.

Scale affects target sprite occupancy, cell/atlas dimensions and source-resolution policy. It is not arbitrary image stretching. Exact min/max remains open.

## Immediate next actions

1. pull the repaired Runner50 and rerun it;
2. inspect the generated sheet/preview/manifest;
3. classify renderer result by layout/pose, identity, pixel-art quality, alpha and gameplay-scale readability;
4. only if FP8 is specifically under-resolved, test full BF16 Kontext;
5. after renderer PASS, build Gradio orchestration UI;
6. then expand semantic action distillation, reference generation and creature scales;
7. do not spend another Base50 H3 hour solely to debug the renderer.
