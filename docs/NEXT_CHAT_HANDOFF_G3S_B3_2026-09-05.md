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
- `docs/RUNNER51_LAYOUT_CONCEPT_REJECT_2026-09-08.md`
- `docs/VISUAL_DIRECTION.md`
- `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
- `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`

## Current production contract

Final local pipeline:

`existing or locally generated character reference + relative world scale + real action driver + action preset -> H3 Base50 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> local pixel-art reconstruction -> one horizontal row for that action + frames/preview/JSON/manifest -> runtime`

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

## Spritesheet layout — HARD LOCK

**One action = one spritesheet row.**

Frames read left-to-right in time.

Internal renderer tiles/chunks do not define final rows.

Current H0 `dance_or_gesture` proof:

- 12 frames;
- `12×1` final layout;
- `192×192` cells;
- `2304×192` final review sheet;
- per-frame timing stored in JSON.

A combined character sheet may later stack distinct actions vertically: idle, walk, run, jump, punch, kick, attacks, defenses, hit/death and specials.

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
2. final asset was not a correct one-action row;
3. mature Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell charge weakened;
4. denoise1.0 gave too much redraw freedom.

Classification: **MODEL/TASK FAIL**.

## Runner51 — DO NOT RUN

Runner51 was prepared but its final-layout concept is wrong: it split one action into three final rows.

Classification: **CONFIGURATION / TASK-FORMULATION FAIL — PRE-INFERENCE**.

No model-quality evidence exists from Runner51.

Record:

`docs/RUNNER51_LAYOUT_CONCEPT_REJECT_2026-09-08.md`

## CURRENT GATE — Runner52

Runner:

`tools/structured-2d-character-pipeline/52_run_flux_kontext_h0_dance12_single_action_row.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance12_single_action_row_structure_lock.py`

No new H3 generation. No new model download should be required if the current Kontext installation remains intact.

### Runner52 action selection

The complete 124-frame H0 is treated as one known `dance_or_gesture` action interval.

Selected source frames one-based:

`1,12,23,35,46,57,68,79,90,102,113,124`

They are one temporally ordered action sequence, not separate rows.

Source timing is preserved as per-frame duration metadata.

### Runner52 renderer formulation

The 12 frames are divided only for internal Kontext processing:

- chunk1 = final action frames1–4;
- chunk2 = frames5–8;
- chunk3 = frames9–12;
- each chunk = `2×2` `1024×1024` processing tile;
- canonical Exilada is the second identity/art-direction reference;
- same FP8-scaled Kontext model;
- 20 steps;
- guidance2.5;
- CFG1.0;
- Euler/simple;
- seed0;
- **denoise0.45**.

Hard prompt locks:

- internal `2×2` tile is not final layout;
- final asset = one 12-frame horizontal row;
- mature adult body proportions and age;
- no infantilization/cute/chibi/adolescent drift;
- preserve pose/silhouette/hair/cloth/restraints;
- preserve Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell mature sword-and-sorcery charge;
- change rendering language only.

### Runner52 final packing

Final output:

- `12×1` sheet;
- `192×192` cells;
- `2304×192` total;
- one full `dance_or_gesture` action left-to-right;
- opaque + RGBA outputs;
- 12 individual RGBA frames;
- one full-action GIF preview;
- manifest with exact source frames, durations and renderer settings.

Expected outputs under `Z:\AI\FluxKontext`:

- `h0_dance12_source_action_strip.png`
- `h0_dance12_action_selection_manifest.json`
- `h0_dance12_chunk01_input_2x2.png`
- `h0_dance12_chunk02_input_2x2.png`
- `h0_dance12_chunk03_input_2x2.png`
- chunk-specific Kontext full outputs/prompts;
- `h0_dance12_pixelart_sheet_opaque.png`
- `h0_dance12_pixelart_sheet_rgba.png`
- `h0_dance12_preview.gif`
- `h0_dance12_kontext_manifest.json`
- `h0_dance12_kontext_executor.log`.

### Runner52 pass criteria

Review separately:

- one-action temporal coherence left-to-right;
- mature adult body preservation;
- no infantilization;
- pose/silhouette fidelity;
- cross-chunk style/body consistency;
- high-quality deliberate pixel art;
- locked 1980s sword-and-sorcery art direction;
- hair/cloth/restraint readability;
- automatic alpha quality.

If Runner52 still changes adult structure at denoise0.45, classify that exact failure before switching precision/model family.

## Exact next operator command

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\52_run_flux_kontext_h0_dance12_single_action_row.ps1"
```

## When Runner52 finishes

Ask for at least:

- `h0_dance12_source_action_strip.png`
- `h0_dance12_preview.gif`
- `h0_dance12_pixelart_sheet_opaque.png`
- `h0_dance12_pixelart_sheet_rgba.png`
- `h0_dance12_kontext_manifest.json`
- `h0_dance12_kontext_executor.log`

Inspect the source `1×12` strip before blaming the renderer for a bad frame-selection sequence.

## Local authoring UI — AFTER RENDERER PASS

Finished tool must expose:

- reference image or local text-to-reference generation;
- character name/category;
- numeric relative world scale;
- action video upload;
- action preset dropdown;
- locked H3 Base50 production preset by default;
- progress/previews;
- final one-row action preview;
- final sheet/frames/JSON/manifest access.

Gradio remains V1 choice.

## License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is fine; commercial shipping later requires BFL licensing or a compatible renderer.
