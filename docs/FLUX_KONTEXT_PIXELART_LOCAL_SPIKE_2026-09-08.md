# FLUX.1 Kontext [dev] — Local Pixel-Art Reconstruction Spike

Status date: **2026-09-08**

Status: **CANONICAL / LOCAL INFERENCE PROVEN / RUNNER50 MODEL-TASK VISUAL FAIL / RUNNER51 LAYOUT CONCEPT REJECTED PRE-INFERENCE / RUNNER52 SINGLE-ACTION 1x12 CURRENT GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

Canonical end-to-end workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Runner50 visual-failure record: `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`.

Runner51 layout-correction record: `docs/RUNNER51_LAYOUT_CONCEPT_REJECT_2026-09-08.md`.

Historical pre-inference incidents:

- `docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`
- `docs/RUNNER50_CLIP_L_SHA256_PREFLIGHT_FAIL_2026-09-08.md`

## Purpose

Prove the all-local downstream pixel-art renderer without regenerating H3 motion.

Current source remains:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

The H0 video is a dance/gesture-like action, not a walk. It remains useful because this spike tests motion-master-to-pixel-art conversion rather than locomotion quality.

## Motion source — LOCKED FOR THIS SPIKE

H3 H0 Base50 remains the preferred motion master:

- `448×800`;
- `124f@24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`.

No new H3 generation is required while the renderer is being debugged.

## Local renderer runtime

Workspace:

`Z:\AI\FluxKontext`

ComfyUI:

- pinned portable v0.34.0;
- isolated renderer port `8191`;
- no custom nodes for the current native Kontext path.

Installed/verified model set:

- `flux1-dev-kontext_fp8_scaled.safetensors` ~11.9GB, SHA256 `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`;
- `clip_l.safetensors` ~246MB, SHA256 `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`;
- `t5xxl_fp16.safetensors` ~9.79GB, SHA256 `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`;
- `ae.safetensors` ~335MB, SHA256 `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`.

The model/runtime installation is proven and reusable. Do not redownload or reinstall it for every renderer iteration.

## Runner50 — COMPLETED INFERENCE / VISUAL FAIL

Runner50 completed successfully at the infrastructure/integration layer.

Evidence:

- prompt id `56576cf4-165a-4ad2-8a96-ec28bf75da1e`;
- elapsed `296.63s`;
- 20 steps;
- guidance `2.5`;
- CFG `1.0`;
- Euler/simple;
- seed0;
- denoise `1.0`.

Useful evidence:

- local Kontext inference works on the current machine;
- FP8-scaled Kontext can produce a recognizable pixel-art-like rendering language;
- neutral-background alpha extraction is viable enough to continue.

Failures:

1. adult identity/body proportions drifted shorter/thicker and more juvenile-looking;
2. final packing did not represent one action as one horizontal row;
3. mature 1980s sword-and-sorcery charge weakened;
4. denoise1.0 gave excessive redraw freedom.

Classification: **MODEL/TASK FAIL**.

Runner50 is closed as a production formulation, not as evidence that Kontext cannot work.

## Spritesheet layout — HARD LOCK

**One action = one spritesheet row.**

The current `dance_or_gesture` proof must end as:

- 12 frames;
- one horizontal row;
- left-to-right temporal order;
- `192×192` cells;
- `2304×192` final review sheet;
- per-frame durations in JSON.

A later character sheet may stack distinct actions vertically. One action must not be split into multiple final rows merely because the renderer processes it in smaller chunks.

## Runner51 — REJECTED BEFORE INFERENCE

Runner51 incorrectly promoted three short temporal/processing chunks into three final rows of the same action.

Classification: **CONFIGURATION / TASK-FORMULATION FAIL — PRE-INFERENCE**.

No model-quality evidence exists from Runner51.

Useful ideas retained:

- four-frame high-resolution internal renderer tiles;
- canonical Exilada as second reference;
- denoise reduced to `0.45`;
- explicit adult-body preservation;
- explicit 1980s sword-and-sorcery art-direction lock.

## Runner52 — CURRENT GATE

Runner:

`tools/structured-2d-character-pipeline/52_run_flux_kontext_h0_dance12_single_action_row.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance12_single_action_row_structure_lock.py`

### Runner52 source selection

The complete 124-frame H0 is treated as one known `dance_or_gesture` action interval.

Selected source frames one-based:

`1,12,23,35,46,57,68,79,90,102,113,124`

These 12 frames are one ordered action sequence. Source timing is converted into per-frame duration metadata.

### Internal processing topology

The 12 frames are divided only to give Kontext more working resolution:

- chunk1 = final action frames1–4;
- chunk2 = frames5–8;
- chunk3 = frames9–12;
- each chunk = temporary `2×2` `1024×1024` input.

The `2×2` topology has no semantic meaning in the final asset.

After inference, all 12 rendered cells are extracted and concatenated into one horizontal action row.

### Runner52 Kontext settings

- same FP8-scaled model;
- 20 steps;
- guidance `2.5`;
- CFG `1.0`;
- Euler/simple;
- seed0;
- **denoise `0.45`**.

### Hard prompt locks

- internal `2×2` tiles are processing devices only;
- final asset = one 12-frame horizontal `dance_or_gesture` row;
- preserve mature adult age and body proportions;
- preserve adult head-to-body ratio, torso/limb length, bust/hips/legs relationship;
- no enlarged head, shortened/thickened juvenile body, rounded childlike face, cute/chibi/adolescent drift;
- preserve pose/silhouette/foot placement/hair/cloth/restraints;
- retain Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell mature sword-and-sorcery charge;
- preserve danger, grime, sensuality, heroic adult anatomy and tactile materials;
- change rendering language only.

### Runner52 output packing

Final outputs under `Z:\AI\FluxKontext`:

- `h0_dance12_source_action_strip.png`
- `h0_dance12_action_selection_manifest.json`
- `h0_dance12_chunk01_input_2x2.png`
- `h0_dance12_chunk02_input_2x2.png`
- `h0_dance12_chunk03_input_2x2.png`
- chunk-specific Kontext outputs/prompts;
- `h0_dance12_pixelart_sheet_opaque.png`
- `h0_dance12_pixelart_sheet_rgba.png`
- `h0_dance12_preview.gif`
- `h0_dance12_kontext_manifest.json`
- `h0_dance12_kontext_executor.log`.

Final sheet:

- `12×1`;
- `192×192` cells;
- `2304×192` total;
- one complete action left-to-right;
- opaque + RGBA outputs;
- individual RGBA frames;
- full-action GIF preview;
- exact source frame/duration provenance.

## Runner52 pass criteria

Inference completion alone is not a PASS.

Visual PASS requires:

1. all 12 cells read as one coherent action sequence;
2. Exilada remains unmistakably mature/adult with materially preserved body proportions;
3. no infantilization/cute/chibi drift;
4. source poses/silhouettes remain materially recognizable;
5. cross-chunk body/style consistency is acceptable;
6. deliberate high-quality pixel-art reading;
7. Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell mature sword-and-sorcery charge remains visible;
8. long hair, torn cloth, cuffs, shackles and chains remain readable;
9. automatic alpha remains usable without routine manual masks.

If Runner52 still changes adult physical structure at denoise `0.45`, classify that specifically before switching model precision or renderer family.

## License boundary

FLUX.1 Kontext [dev] open weights are governed by the FLUX.1 dev non-commercial license.

Technical validation is acceptable. Commercial game shipping later requires appropriate BFL commercial licensing or a renderer with compatible terms.

## Immediate next decision

Run Runner52 and inspect in this order:

1. `h0_dance12_source_action_strip.png` — verify the source 12-frame action sequence first;
2. `h0_dance12_preview.gif` — verify full-action temporal coherence;
3. `h0_dance12_pixelart_sheet_opaque.png` — judge anatomy/art direction/cross-chunk consistency without alpha distractions;
4. RGBA sheet — judge automatic background removal;
5. manifest — confirm exact selected frames, durations and settings.

Do not generate another H3 action solely to debug this renderer stage.
