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
- `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`
- `docs/VISUAL_DIRECTION.md`
- `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
- `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`

Historical Runner50 integration/preflight incidents:

- `docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`
- `docs/RUNNER50_CLIP_L_SHA256_PREFLIGHT_FAIL_2026-09-08.md`

## Current production contract

Final local pipeline:

`existing or locally generated character reference + relative world scale + real action driver + action preset -> H3 Base50 complete-character motion master -> automatic coherent action-sequence extraction -> automatic alpha/pivot/alignment -> local pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

No routine manual rigging/keyframing/mask repair/per-frame repainting/hand compositing.

## Final visible art — HARD LOCKS

Runtime characters are deliberate high-quality pixel art.

H3/Wan painterly/raster outputs are intermediate motion masters only.

Active inspiration lineage remains:

- Heavy Metal;
- Conan;
- Red Sonja;
- Frank Frazetta;
- Julie Bell.

Final renderer must preserve mature adult anatomy, danger, grime, sensuality, tactile materials and pulp-fantasy physicality.

Approved adult characters may not be infantilized, made cute/chibi/adolescent-looking, shortened/thickened into juvenile proportions, given enlarged heads or rounded childlike faces. Renderer changes rendering language, not physical identity.

## Spritesheet semantic lock

**One row = one temporally coherent animation sequence.**

Frames read left-to-right in time. A global contact sheet of scattered timestamps is not a valid final spritesheet.

## H3 H0 — COMPLETE / PREFERRED MOTION BASELINE

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
- elapsed `4504.8s`;
- video `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / preferred motion-master quality baseline**.

Turbo4 was run and visually rejected. Base50 remains production default.

## Existing H0 action

The current H0 is a **dance/gesture-like action**, not a walk.

Do not generate a new walk merely to debug the renderer.

## FLUX Kontext local runtime — INSTALLED / OPERATIONAL

Workspace:

`Z:\AI\FluxKontext`

Runtime/model set:

- ComfyUI v0.34.0;
- port `8191`;
- `flux1-dev-kontext_fp8_scaled.safetensors`;
- `clip_l.safetensors`;
- `t5xxl_fp16.safetensors`;
- `ae.safetensors`.

Local inference is proven; reuse this installation.

## Runner50 — COMPLETED / VISUAL FAIL

Runner50 completed technically:

- prompt id `56576cf4-165a-4ad2-8a96-ec28bf75da1e`;
- elapsed `296.63s`;
- 20 steps;
- guidance2.5;
- CFG1.0;
- Euler/simple;
- seed0;
- denoise1.0.

Useful evidence:

- Kontext local inference works;
- pixel-art-like output is promising;
- alpha extraction remains viable enough to continue.

User visual verdict: **REJECTED**.

Failures:

1. Exilada body proportions changed shorter/thicker and more juvenile/infantilized;
2. evenly distributed 12-frame H0 sample was a contact sheet, not correct animation rows;
3. mature Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell charge weakened;
4. denoise1.0 and 12 small figures in one square gave excessive redraw freedom.

Classification: **MODEL/TASK FAIL**.

Record:

`docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`

## CURRENT GATE — Runner51

Runner:

`tools/structured-2d-character-pipeline/51_run_flux_kontext_h0_dance3x4_temporal_rows_structure_lock.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance3x4_temporal_rows_structure_lock.py`

No new H3 generation. No new model download should be required if Runner50 installation remains intact.

### Runner51 source-row selection

- split 124-frame H0 into three thirds;
- inside each third calculate simple grayscale motion energy;
- choose the highest-motion 16-frame local window;
- select four ordered frames at offsets `0,5,10,15`;
- each sequence becomes one final spritesheet row.

This is a proof policy, not final action-specific cycle detection.

### Runner51 renderer formulation

Each row is rendered separately as a `2×2` `1024×1024` Kontext input:

- four temporally ordered frames;
- character materially larger during edit than Runner50;
- canonical Exilada remains identity/art-direction reference;
- same FP8-scaled Kontext model;
- 20 steps;
- guidance2.5;
- CFG1.0;
- Euler/simple;
- seed0;
- **denoise0.45**.

Hard prompt locks:

- mature adult body proportions and age;
- no infantilization/cute/chibi/adolescent drift;
- preserve pose/silhouette/hair/cloth/restraints;
- preserve Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell mature sword-and-sorcery charge;
- change rendering language only.

### Runner51 final packing

Three row outputs are split and repacked as:

- final `4×3` sheet;
- `192×192` cells;
- `768×576` total;
- one coherent animation sequence per row;
- opaque + RGBA outputs;
- one GIF preview per row;
- manifest with exact selected source frames/settings.

Expected outputs under `Z:\AI\FluxKontext`:

- `h0_dance3x4_source_temporal_rows.png`
- `h0_dance3x4_temporal_selection_manifest.json`
- `h0_dance_row01_input_2x2.png`
- `h0_dance_row02_input_2x2.png`
- `h0_dance_row03_input_2x2.png`
- row-specific Kontext full outputs/prompts;
- `h0_dance_row01_preview.gif`
- `h0_dance_row02_preview.gif`
- `h0_dance_row03_preview.gif`
- `h0_dance3x4_pixelart_sheet_opaque.png`
- `h0_dance3x4_pixelart_sheet_rgba.png`
- `h0_dance3x4_kontext_manifest.json`
- `h0_dance3x4_kontext_executor.log`.

### Runner51 pass criteria

Review separately:

- row temporal coherence;
- mature adult body preservation;
- no infantilization;
- pose/silhouette fidelity;
- high-quality deliberate pixel art;
- locked 1980s sword-and-sorcery art direction;
- hair/cloth/restraint readability;
- automatic alpha quality.

If Runner51 still changes adult structure at denoise0.45, classify that exact failure before switching precision/model family.

## Exact next operator command

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\51_run_flux_kontext_h0_dance3x4_temporal_rows_structure_lock.ps1"
```

## When Runner51 finishes

Ask for at least:

- `h0_dance3x4_source_temporal_rows.png`
- `h0_dance_row01_preview.gif`
- `h0_dance_row02_preview.gif`
- `h0_dance_row03_preview.gif`
- `h0_dance3x4_pixelart_sheet_opaque.png`
- `h0_dance3x4_pixelart_sheet_rgba.png`
- `h0_dance3x4_kontext_manifest.json`
- `h0_dance3x4_kontext_executor.log`

Inspect source-row semantics before blaming the renderer for a bad sequence selection.

## Local authoring UI — AFTER RENDERER PASS

Finished tool must expose:

- reference image or local text-to-reference generation;
- character name/category;
- numeric relative world scale;
- action video upload;
- action preset dropdown;
- locked H3 Base50 production preset by default;
- progress/previews;
- row animation previews;
- final sheet/frames/JSON/manifest access.

Gradio remains V1 choice.

## License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is fine; commercial shipping later requires BFL licensing or a compatible renderer.
