# Local Spritesheet Authoring Workflow — Living Specification

Status date: **2026-09-08**

Status: **CANONICAL TARGET WORKFLOW / ALL-LOCAL AUTHORING / H3 BASE50 MOTION MASTER LOCKED / FLUX KONTEXT ACTIVE / RUNNER51 LAYOUT CONCEPT REJECTED / RUNNER52 SINGLE-ACTION 1x12 CURRENT GATE / UI AFTER RENDERER PASS**

Canonical project state: `docs/PROJECT_STATE.md`.

Renderer spike: `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`.

Runner50 visual-failure record: `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`.

Runner51 layout-correction record: `docs/RUNNER51_LAYOUT_CONCEPT_REJECT_2026-09-08.md`.

## Purpose

Define one local authoring application that takes a character concept plus a real action video and returns a runtime-ready pixel-art action asset.

Target operator experience:

1. provide an existing character reference **or** describe a new character in text;
2. provide the character/creature's relative world scale;
3. provide a real reference video containing the desired action;
4. choose the action type from a preset list or `custom`;
5. run one local job;
6. receive the finished transparent pixel-art action row, preview, frames and metadata.

The same workflow must support humanoids, animals, monsters, fantastic creatures and bosses of materially different sizes.

## All-local requirement — LOCKED

Normal asset production must run locally after model installation. Hosted generation APIs are not part of the production dependency chain.

Current local stages:

- character reference generation: model choice still open;
- motion generation: MiniMax H3 Base Ref2VA;
- frame extraction/selection: Python automation;
- alpha/alignment/pivot: Python automation;
- pixel-art reconstruction: FLUX.1 Kontext [dev] active validation;
- packing/preview/manifest: Python automation;
- authoring UI: Gradio after renderer pass.

## Canonical pipeline

`character source -> approved complete reference -> real action video + action metadata -> MiniMax H3 Base50 motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> pixel-art reconstruction -> one horizontal spritesheet row for that action + frames/preview/atlas metadata`

The H3 video is an **intermediate motion master**, not final runtime art.

## Stage A — Character source

### A1. Existing reference image

Upload a complete approved character reference image.

For the Exilada:

`assets/source/characters/exilada/reference/exilada_master.png`

### A2. Text-described character generation

Enter a description and generate a complete local reference before action generation.

The exact text-to-image model is not yet locked. SDXL-class and FLUX text-to-image families remain candidates.

The generated reference must be approved before H3 action generation.

## Stage B — Relative world scale

The UI must expose a numeric **relative scale** independent of image resolution.

Baseline:

- `1.0` = adult-human/Exilada baseline;
- approximately `128px` visible height in canonical gameplay composition;
- larger/smaller creatures change intended world/render scale rather than being stretched arbitrarily.

Scale influences target sprite height, cell/atlas size, source resolution and metadata.

## Stage C — Action input

Upload a real reference video containing the desired action.

The **video is authoritative for motion**. The action preset names/organizes the asset and chooses extraction heuristics; it does not replace the driver.

Preferred driver properties:

- fixed camera when practical;
- complete action visible;
- extremities remain in frame;
- margin for hair, cloth, weapons and accessories;
- performer identity/costume/body may differ from the target character.

## Stage D — Action presets

Initial presets:

- `idle`
- `walk`
- `run`
- `jump`
- `land`
- `dodge`
- `roll`
- `punch`
- `kick`
- `block`
- `parry`
- `hit_react`
- `knockdown`
- `get_up`
- `death`
- `taunt`
- `dance_or_gesture`
- `sword_slash`
- `sword_overhead`
- `sword_thrust`
- `axe_swing`
- `spear_thrust`
- `bow_shot`
- `staff_attack`
- `cast_spell`
- `special_attack`
- `custom`

Preset responsibilities:

- asset naming;
- loop/non-loop policy;
- suggested frame count;
- action/cycle detection heuristic;
- pivot policy;
- optional gameplay events such as foot contacts, hit frames, release frames or guard windows.

## Stage E — Motion master: MiniMax H3 Base Ref2VA

### Canonical quality configuration — LOCKED

- MiniMax H3 Base Ref2VA;
- `448×800`;
- `124 frames @24fps`;
- `ref_image_size=match`;
- `50 steps`;
- sampler `res_multistep`;
- scheduler `beta`;
- seed `0` as current deterministic baseline;
- no Turbo LoRA;
- no FL2VA;
- no style embedding;
- schema-required audio VAE wired, no audio reference/decode for the current job.

Canonical H0 evidence:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H0 elapsed: `4504.8s`.

Turbo4 was run and visually rejected. It is not the production default.

## Stage F — Automatic action distillation

The 124-frame H3 motion master is not the runtime animation.

Downstream automation must:

1. decode all frames;
2. locate the desired action interval or cycle;
3. select a compact ordered frame set for that action;
4. reject obvious crop/structure failures where confidence permits;
5. preserve timing metadata.

### Spritesheet layout invariant — HARD LOCK

**One action = one spritesheet row.**

Frames inside the row read left-to-right in time.

For the current H0 `dance_or_gesture` proof:

- all 12 selected frames belong to the same action;
- final layout = `12 columns × 1 row`;
- cell size = `192×192`;
- final review sheet = `2304×192`;
- frame timing is stored in metadata/JSON.

A later multi-action sheet may stack several distinct actions vertically, for example:

- row 1 = idle;
- row 2 = walk;
- row 3 = run;
- row 4 = jump;
- row 5 = punch;
- row 6 = kick;
- additional rows = weapon attacks, defenses, hit/death, specials.

Do **not** split one action across several final rows merely because the renderer processes it in chunks.

### Internal processing chunks — HARD DISTINCTION

The renderer may use temporary high-resolution `2×2` tiles internally.

For a 12-frame action:

- chunk 1 = final action frames 1–4;
- chunk 2 = final action frames 5–8;
- chunk 3 = final action frames 9–12.

These chunks are processing devices only. After inference the 12 cells are extracted and concatenated into a single horizontal action row.

Runner51 was rejected before execution because it incorrectly promoted three processing/temporal chunks into three final spritesheet rows.

Record:

`docs/RUNNER51_LAYOUT_CONCEPT_REJECT_2026-09-08.md`

## Stage G — Automatic alpha, alignment and pivot

The system must automatically:

- isolate the complete visible character;
- preserve hair, cloth, weapons/accessories;
- produce RGBA frames;
- choose a stable action-appropriate pivot/root;
- preserve legitimate body bob/airborne motion;
- allocate cells large enough for action envelope and relative scale.

No routine manual masks or per-frame alignment.

## Stage H — Final pixel-art reconstruction

### Active renderer family

**FLUX.1 Kontext [dev] remains the active first renderer family.**

Runner50 proved local operability but failed the production contract.

### Runner50 result — MODEL/TASK FAIL

Completed evidence:

- prompt id `56576cf4-165a-4ad2-8a96-ec28bf75da1e`;
- elapsed `296.63s`;
- FP8-scaled Kontext;
- 20 steps;
- guidance `2.5`;
- CFG `1.0`;
- Euler/simple;
- seed0;
- denoise `1.0`.

Useful evidence:

- local Kontext inference works;
- pixel-art-like rendering quality is promising;
- alpha extraction is viable enough to continue.

Failures:

- adult body/identity proportions drifted and became juvenile/infantilized;
- the output layout was not a correct one-action row;
- mature 1980s sword-and-sorcery charge weakened;
- denoise1.0 gave excessive redraw freedom.

### Approved adult-body invariant — HARD LOCK

The renderer changes rendering language, not approved body design.

For adult characters:

- preserve adult age and head-to-body ratio;
- preserve torso/limb length and major proportions;
- preserve adult bust/hips/pelvis/legs relationship;
- no shortened/thickened juvenile reinterpretation;
- no enlarged head, rounded/widened childlike face, cute/chibi/adolescent drift;
- preserve character-specific maturity, severity and physical presence.

### Art-direction invariant — HARD LOCK

The final renderer must preserve the active inspiration lineage:

- Heavy Metal;
- Conan;
- Red Sonja;
- Frank Frazetta;
- Julie Bell.

The desired charge includes mature adult anatomy, danger, grime, sensuality, pulp-fantasy excess and tactile skin/cloth/metal.

A clean pixel-art result that loses this charge is not a PASS.

## Runner51 — REJECTED BEFORE EXECUTION

Runner51 is retained only as history.

Its useful structure-preservation ideas are carried forward, but its final `4×3` layout interpretation is wrong for a single action.

Classification:

**CONFIGURATION / TASK-FORMULATION FAIL — PRE-INFERENCE**.

No model-quality evidence exists from Runner51.

## Runner52 — CURRENT GATE

Runner:

`tools/structured-2d-character-pipeline/52_run_flux_kontext_h0_dance12_single_action_row.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance12_single_action_row_structure_lock.py`

Runner52 keeps:

- same installed FP8-scaled Kontext runtime;
- canonical Exilada reference;
- 20 steps;
- guidance `2.5`;
- CFG `1.0`;
- Euler/simple;
- seed0;
- `denoise=0.45`;
- mature-adult body lock;
- Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell lock.

Runner52 corrects the layout:

1. the complete H0 is treated as one known `dance_or_gesture` action interval;
2. 12 ordered samples span that action;
3. frames are grouped into three internal 4-frame `2×2` Kontext tiles only for working resolution;
4. all 12 rendered cells are concatenated into one final horizontal action row;
5. final sheet = `2304×192`, `12×1`, transparent RGBA plus opaque QA version;
6. one full-action GIF preview is generated;
7. per-frame source index and duration are recorded in the manifest.

### Runner52 expected outputs

Under `Z:\AI\FluxKontext`:

- `h0_dance12_source_action_strip.png`
- `h0_dance12_action_selection_manifest.json`
- `h0_dance12_chunk01_input_2x2.png`
- `h0_dance12_chunk02_input_2x2.png`
- `h0_dance12_chunk03_input_2x2.png`
- three chunk-specific Kontext outputs/prompts/manifests;
- `h0_dance12_pixelart_sheet_opaque.png`
- `h0_dance12_pixelart_sheet_rgba.png`
- `h0_dance12_preview.gif`
- `h0_dance12_kontext_manifest.json`
- `h0_dance12_kontext_executor.log`

### Runner52 pass boundary

PASS requires:

- all 12 cells read as one coherent dance_or_gesture action left-to-right;
- mature Exilada anatomy/proportions remain materially stable;
- no infantilization/cute/chibi drift;
- H0 poses/silhouettes remain recognizably preserved;
- cross-chunk style/body consistency is acceptable;
- deliberate high-quality pixel-art reading;
- locked 1980s sword-and-sorcery charge remains visible;
- hair/cloth/restraints readable;
- automatic alpha usable without routine manual repair.

If Runner52 still changes adult body structure at denoise0.45, classify that exact renderer failure before changing precision/model family.

### License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is acceptable; commercial shipping later requires appropriate BFL licensing or a renderer with compatible terms.

SDXL/img2img remains a fallback candidate if Kontext ultimately fails quality, hardware or licensing requirements.

## Stage I — Runtime packaging

Every completed action job should return at minimum:

- `<character>_<action>_motion_master.mp4`
- `<character>_<action>_frames/`
- `<character>_<action>_pixelart_row.png`
- `<character>_<action>_preview.gif`
- `<character>_<action>_atlas.png` optionally;
- `<character>_<action>_atlas.json` with rectangles, pivots, durations/events;
- `<character>_<action>_manifest.json` with source hashes, model/settings, scale, action preset and provenance.

Runtime-visible cells remain complete precomposed character images.

## Local interface — REQUIRED

The production workflow must be exposed through one local UI.

Minimum controls:

### Character

- mode: `reference image` / `generate from text`;
- image upload or text description;
- character name/id;
- relative world scale;
- optional category (`humanoid`, `creature`, `monster`, `boss`, `other`).

### Motion

- reference-video upload;
- action-type dropdown;
- direction/facing metadata where relevant;
- optional custom action name;
- optional final-frame-count override.

### Generation

Default H3 controls remain hidden/locked to Base50. Advanced controls may expose controlled experimental settings, but production defaults must not silently drift.

### Output

- job progress/stage status;
- motion-master preview;
- selected source-action strip preview;
- final one-row pixel-art action preview;
- direct frames/sheet/JSON/manifest access.

## UI implementation

**Gradio remains the V1 implementation choice**, after renderer behavior passes.

## Failure classification

Use project-wide vocabulary:

- `INFRASTRUCTURE FAIL`
- `INTEGRATION FAIL`
- `CONFIGURATION FAIL`
- `BLOCKED`
- `MODEL/TASK FAIL`
- `EXHAUSTED_FAIL`

A renderer failure does not retroactively invalidate a good H3 motion master.

## Immediate implementation order

1. do not run Runner51;
2. run Runner52 on the existing H0 dance/gesture motion master;
3. inspect `h0_dance12_source_action_strip.png` first to confirm one ordered action row;
4. inspect the full-action GIF for temporal coherence;
5. inspect opaque final sheet for body maturity/proportions, pose fidelity, cross-chunk consistency, pixel-art quality and art direction;
6. inspect RGBA/alpha;
7. if renderer passes, build the Gradio orchestration UI around H3 Base50 + the proven renderer formulation;
8. then implement action-specific cycle detection, text-reference generation and creature-scale cases;
9. do not spend another Base50 H3 hour solely to debug the renderer.

## Current validation question

> Can Runner52 preserve the Exilada's mature adult physical identity and locked 1980s sword-and-sorcery direction while converting the existing H0 dance_or_gesture motion into one correct 12-frame horizontal pixel-art action row automatically?
