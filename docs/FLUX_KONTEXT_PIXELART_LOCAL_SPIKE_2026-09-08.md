# FLUX.1 Kontext [dev] — Local Pixel-Art Reconstruction Spike

Status date: **2026-09-08**

Status: **CANONICAL / LOCAL INFERENCE PROVEN / RUNNER50 MODEL-TASK VISUAL FAIL / RUNNER51 TEMPORAL-ROW + BODY-STRUCTURE REPAIR PREPARED**

Canonical project state: `docs/PROJECT_STATE.md`.

Canonical end-to-end workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Runner50 visual-failure record: `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`.

Historical pre-inference incidents:

- `docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`
- `docs/RUNNER50_CLIP_L_SHA256_PREFLIGHT_FAIL_2026-09-08.md`

## Purpose

Prove the missing all-local downstream renderer without regenerating H3 motion.

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

- pinned portable v0.34.0 cloned from the proven H3 runtime;
- isolated renderer port `8191`;
- no custom nodes for the current native Kontext path.

Installed/verified model set:

- `flux1-dev-kontext_fp8_scaled.safetensors` ~11.9GB, SHA256 `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`;
- `clip_l.safetensors` ~246MB, SHA256 `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`;
- `t5xxl_fp16.safetensors` ~9.79GB, SHA256 `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`;
- `ae.safetensors` ~335MB, SHA256 `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`.

The model/runtime installation is now proven and reusable. Do not redownload or reinstall it for every renderer iteration.

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
- denoise `1.0`;
- output `1024×1024`;
- final review sheet `768×576` with `192×192` cells.

### Runner50 input strategy

Runner50 selected frames:

`1, 12, 23, 35, 46, 57, 68, 79, 90, 102, 113, 124`

These were evenly distributed over the whole H0. They were packed into one square `4×3` contact sheet and rendered in one Kontext pass together with the canonical Exilada reference.

### Runner50 useful evidence

- local Kontext inference works on the current machine;
- FP8-scaled Kontext can produce a recognizable pixel-art-like rendering language;
- neutral-background alpha extraction is viable enough to continue;
- the renderer family is not rejected solely because of one bad task formulation.

### Runner50 failures

Classification: **MODEL/TASK FAIL**.

1. **Adult identity/body drift**
   - the Exilada became physically shorter/thicker and more juvenile-looking;
   - approved adult proportions were changed instead of only the rendering language.

2. **Wrong spritesheet semantics**
   - a global evenly spaced contact sheet is not a correct animation organization;
   - project rule is now hard-locked: **one temporally coherent animation sequence per row**.

3. **Art-direction loss**
   - some pixel-art qualities were useful, but the mature 1980s sword-and-sorcery charge weakened;
   - Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell remain mandatory inspiration anchors.

4. **Too much redraw freedom**
   - denoise `1.0` allowed extensive reinterpretation;
   - 12 relatively small characters in one `1024×1024` sheet limited per-character working detail.

Runner50 is closed as a production formulation, not as evidence that Kontext cannot work.

## Runner51 — CURRENT GATE

Runner:

`tools/structured-2d-character-pipeline/51_run_flux_kontext_h0_dance3x4_temporal_rows_structure_lock.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance3x4_temporal_rows_structure_lock.py`

No new model download and no new H3 generation should be required if Runner50 installation remains intact.

### Runner51 temporal-row selection

The 124-frame H0 is divided into three thirds.

Inside each third:

1. compute simple per-frame motion energy from low-resolution grayscale differences;
2. find the highest-motion 16-frame local window;
3. select four ordered frames from that window at offsets `0,5,10,15`;
4. assign that sequence to one final spritesheet row.

Thus:

- row1 = one coherent early action segment;
- row2 = one coherent middle action segment;
- row3 = one coherent late action segment.

This is a proof policy. Later action presets will replace it with action-specific cycle/segment detection.

### Runner51 renderer formulation

Each four-frame row is rendered **separately**.

Input per row:

- `1024×1024` square;
- four temporally ordered frames arranged as `2×2`;
- each character occupies materially more pixels than Runner50;
- canonical Exilada reference remains the second identity/art-direction reference.

Kontext settings:

- same FP8-scaled model;
- 20 steps;
- guidance `2.5`;
- CFG `1.0`;
- Euler/simple;
- seed0;
- **denoise `0.45`**.

The denoise reduction is the key controlled structure-preservation change.

### Runner51 hard prompt locks

The renderer is instructed to change rendering language, not character design.

Hard requirements:

- mature adult age and proportions remain unambiguous;
- preserve adult head-to-body ratio, torso/limb length, bust/hips/legs relationship;
- no enlarged head, shortened/thickened juvenile body, rounded childlike face, cute/chibi/adolescent drift;
- preserve pose/silhouette/foot placement/hair/cloth/restraints;
- retain Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell mature sword-and-sorcery charge;
- preserve danger, grime, sensuality, heroic adult anatomy and tactile materials;
- one temporal animation sequence per final row.

### Runner51 output packing

Each `2×2` row result is split into four cells and repacked left-to-right into one final row.

Final sheet:

- `4×3`;
- `192×192` runtime review cells;
- `768×576` total;
- one coherent temporal sequence per row;
- opaque + RGBA outputs;
- individual RGBA frames;
- one GIF per row;
- selection + inference manifest.

Expected outputs under `Z:\AI\FluxKontext`:

- `h0_dance3x4_source_temporal_rows.png`
- `h0_dance3x4_temporal_selection_manifest.json`
- `h0_dance_row01_input_2x2.png`
- `h0_dance_row02_input_2x2.png`
- `h0_dance_row03_input_2x2.png`
- `h0_dance_row01_kontext_full.png`
- `h0_dance_row02_kontext_full.png`
- `h0_dance_row03_kontext_full.png`
- `h0_dance_row01_preview.gif`
- `h0_dance_row02_preview.gif`
- `h0_dance_row03_preview.gif`
- `h0_dance3x4_pixelart_sheet_opaque.png`
- `h0_dance3x4_pixelart_sheet_rgba.png`
- `h0_dance3x4_kontext_manifest.json`
- `h0_dance3x4_kontext_executor.log`

## Runner51 pass criteria

Inference completion alone is not a PASS.

Visual PASS requires:

1. each row reads as one coherent four-frame animation sequence;
2. Exilada remains unmistakably mature/adult with materially preserved body proportions;
3. no infantilization/cute/chibi drift;
4. source poses/silhouettes remain materially recognizable;
5. deliberate high-quality pixel-art reading;
6. Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell mature sword-and-sorcery charge remains visible;
7. long hair, torn cloth, cuffs, shackles and chains remain readable;
8. automatic alpha remains usable without routine manual masks.

If Runner51 still changes adult physical structure at denoise `0.45`, classify that specifically before switching model precision or renderer family.

## License boundary

FLUX.1 Kontext [dev] open weights are governed by the FLUX.1 dev non-commercial license.

Technical validation is acceptable. Commercial game shipping later requires appropriate BFL commercial licensing or a renderer with compatible terms.

## Immediate next decision

Run Runner51 and inspect in this order:

1. `h0_dance3x4_source_temporal_rows.png` — verify the source row sequences first;
2. the three row GIFs — verify temporal coherence;
3. `h0_dance3x4_pixelart_sheet_opaque.png` — judge anatomy/art direction without alpha distractions;
4. RGBA sheet — judge automatic background removal;
5. manifest — confirm exact selected frames/settings.

Do not generate another H3 action solely to debug this renderer stage.
