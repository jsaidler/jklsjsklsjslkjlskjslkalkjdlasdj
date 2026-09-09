# Local Spritesheet Authoring Workflow — Living Specification

Status date: **2026-09-08**

Status: **CANONICAL TARGET WORKFLOW / ALL-LOCAL AUTHORING / H3 BASE50 LOCKED / KONTEXT STRUCTURE PASS / PIXEL-ART QUALITY STILL OPEN / 128PX BASELINE RETIRED / RUNNER53 STYLE-ADAPTER GATE / UI AFTER RENDERER PASS**

Canonical project state: `docs/PROJECT_STATE.md`.

Renderer spike: `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`.

Scale correction: `docs/GAMEPLAY_CHARACTER_SCALE_RECALIBRATION_2026-09-08.md`.

Runner52 result: `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`.

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
- action-frame extraction/selection: Python automation;
- alpha/alignment/pivot: Python automation;
- pixel-art reconstruction: FLUX.1 Kontext [dev] + active style-adapter validation;
- packing/preview/manifest: Python automation;
- authoring UI: Gradio after renderer pass.

## Canonical pipeline

`character source -> approved complete reference -> real action video + action metadata -> MiniMax H3 Base50 motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> pixel-art reconstruction at master scale -> one horizontal spritesheet row for that action + frames/preview/JSON/manifest -> gameplay-scale derivation/QA -> runtime`

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

Current contract:

- `1.0` = adult-human/Exilada **world scale**;
- no fixed gameplay pixel height is implied;
- larger/smaller creatures change intended world/render scale rather than being stretched arbitrarily.

The former `128px` Exilada gameplay baseline is retired.

First explicit gameplay benchmark at native `640×360` will compare approximately `160/180/200px` visible Exilada heights. These are test candidates only.

Scale influences target occupancy, cell/atlas size, source resolution and metadata.

## Stage B2 — Master scale vs gameplay apparent scale — HARD DISTINCTION

The authoring/render master must not be prematurely reduced to the eventual gameplay apparent size.

Until gameplay composition is locked:

- preserve roughly `256–320px` visible subject height in renderer/master review where practical;
- use `384×384` or larger cells when required by the action envelope;
- create gameplay-scale QA derivatives afterward.

The final gameplay baseline is selected from actual viewport composition with multiple enemies, depth-lane motion, attack envelopes, HUD-safe area and larger creature/boss cases.

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

- idle, walk, run, jump, land, dodge, roll;
- punch, kick, block, parry, hit_react, knockdown, get_up, death;
- taunt, dance_or_gesture;
- sword_slash, sword_overhead, sword_thrust, axe_swing, spear_thrust, bow_shot, staff_attack, cast_spell, special_attack;
- custom.

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
- seed `0`;
- no Turbo LoRA;
- no FL2VA;
- no style embedding;
- schema-required audio VAE wired, no audio reference/decode for the current job.

Canonical H0 evidence:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H0 elapsed: `4504.8s`.

Turbo4 was visually rejected and is not the production default.

## Stage F — Automatic action distillation

The 124-frame H3 motion master is not the runtime animation.

Downstream automation must:

1. decode all frames;
2. locate the desired action interval or cycle;
3. select a compact ordered frame set for that action;
4. reject obvious crop/structure failures where confidence permits;
5. derive **runtime-appropriate** timing/events rather than blindly preserving long source-video holds;
6. preserve provenance separately from runtime timing.

### Spritesheet layout invariant — HARD LOCK

**One action = one spritesheet row.**

Frames inside the row read left-to-right in time.

For the current H0 `dance_or_gesture` proof:

- 12 selected frames;
- final semantic layout = `12 columns × 1 row`.

Runner52 used `192×192` local diagnostic cells; this is historical packaging evidence only and is not a production-scale lock.

A later multi-action sheet may stack distinct actions vertically.

Do **not** split one action across several final rows merely because the renderer processes it in chunks.

### Internal processing chunks — HARD DISTINCTION

The renderer may use temporary high-resolution `2×2` tiles internally.

For a 12-frame action:

- chunk1 = frames1–4;
- chunk2 = frames5–8;
- chunk3 = frames9–12.

These chunks are processing devices only. Final packing always restores one horizontal action row.

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

**FLUX.1 Kontext [dev] remains active.**

Runner52 materially solved the previous layout/body problem but did **not** yet prove final high-level pixel art.

### Runner52 result — PARTIAL PASS

Evidence:

- three successful four-frame chunk inferences;
- total Kontext inference time `849.35s` (~14m09s);
- FP8-scaled Kontext;
- 20 steps;
- guidance2.5;
- CFG1;
- Euler/simple;
- seed0;
- denoise0.45;
- final semantic `12×1` action row.

Passes/candidates:

- one-action row semantics: **PASS**;
- adult body/identity preservation: **PASS_CANDIDATE**;
- pose fidelity: **PASS_CANDIDATE**;
- cross-chunk consistency: **PASS_CANDIDATE**;
- automatic alpha: **PASS_CANDIDATE**.

Remaining failure:

- final art still reads too much like reduced/filtered raster with residual painterly microtexture/noisy miniature detail;
- deliberate authored pixel-cluster quality is **NOT YET PASS**;
- the premature `192×192` diagnostic packing may contribute to this reading and is no longer used as a production assumption.

Do not call the downstream renderer solved yet.

### Approved adult-body invariant — HARD LOCK

The renderer changes rendering language, not approved body design.

For adult characters:

- preserve adult age/head-to-body ratio;
- preserve torso/limb length and major proportions;
- preserve adult bust/hips/pelvis/legs relationship;
- no shortened/thickened juvenile reinterpretation;
- no enlarged head, rounded childlike face, cute/chibi/adolescent drift.

### Art-direction invariant — HARD LOCK

Final art must preserve:

- Heavy Metal;
- Conan;
- Red Sonja;
- Frank Frazetta;
- Julie Bell.

Required charge includes mature adult anatomy, danger, grime, sensuality, pulp-fantasy excess and tactile skin/cloth/metal.

A clean pixel-art result that loses this charge is not a PASS.

## Runner53 — CURRENT GATE

Runner:

`tools/structured-2d-character-pipeline/53_run_flux_kontext_h0_dance_chunk2_modern_pixelart_lora_probe.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance_chunk2_modern_pixelart_lora_probe.py`

Purpose: determine whether a dedicated pixel-art style adapter can improve rendering language while preserving the Runner52 structure gains.

Controlled inference test:

- only Runner52 chunk2, source frames `46,57,68,79`;
- same canonical Exilada reference;
- same Kontext FP8;
- same 20 steps / guidance2.5 / CFG1 / Euler-simple / seed0 / denoise0.45;
- only model/style variable: `UmeAiRT/FLUX.1-dev-LoRA-Modern_Pixel_art`;
- file `ume_modern_pixelart.safetensors`;
- strength `1.0`;
- SHA256 `ed226c149dca6286ae345b6900d807f791a52b1746ed8f524af41efdfda6f0a4`;
- ~344MB;
- LoRA license MIT; Kontext base license caveat remains.

Packaging/master correction:

- final probe cells = `384×384` review/master cells;
- four-frame strip = `1536×384`;
- gameplay apparent character height remains explicitly unlocked;
- the larger master packing changes no model conditioning or denoise setting.

Why only one chunk: ordinary FLUX.1-dev LoRA compatibility with Kontext is not assumed as guaranteed, and there is no reason to spend another full three-chunk pass before seeing evidence.

Runner53 PASS requires:

- visibly stronger deliberate pixel clusters/material grouping than Runner52;
- adult anatomy remains materially unchanged;
- exact source poses remain recognizable;
- no cute/chibi/juvenile drift;
- locked 1980s sword-and-sorcery charge remains visible.

If it passes, apply the adapter to the full 12-frame action at master scale. If it fails, reject the adapter specifically before changing denoise, precision or renderer family.

### License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is acceptable; commercial shipping later requires appropriate BFL licensing or a renderer with compatible terms.

## Stage I — Runtime packaging

Every completed action job should return at minimum:

- `<character>_<action>_motion_master.mp4`
- `<character>_<action>_frames/`
- `<character>_<action>_pixelart_master_row.png`
- `<character>_<action>_preview.gif`
- gameplay-scale QA derivatives;
- optional atlas PNG;
- JSON with rectangles, pivots, runtime durations/events;
- provenance manifest with source hashes/model/settings/relative scale/action preset.

Runtime-visible cells remain complete precomposed character images.

## Local interface — REQUIRED

Minimum controls:

### Character

- mode: reference image / generate from text;
- image upload or text description;
- character name/id;
- relative world scale;
- optional category.

### Motion

- reference-video upload;
- action-type dropdown;
- direction/facing metadata where relevant;
- optional custom action name;
- optional final-frame-count override.

### Generation

Default H3 controls stay hidden/locked to Base50. Advanced controls may expose controlled experiments, but defaults must not silently drift.

### Output

- job progress/stage status;
- motion-master preview;
- selected source-action strip preview;
- final one-row pixel-art **master** preview;
- gameplay-scale comparison preview;
- direct frames/sheet/JSON/manifest access.

## UI implementation

**Gradio remains the V1 implementation choice after renderer quality passes.**

## Immediate implementation order

1. run the scale-corrected Runner53 only;
2. compare its four-frame master output to Runner52 chunk2;
3. if style improves without structure loss, run a full 12-frame LoRA pass at master scale;
4. benchmark gameplay apparent height at `160/180/200px` in real `640×360` viewport compositions;
5. solve action-specific frame distillation/runtime timing;
6. build the Gradio orchestration UI;
7. only after that expand to new actions and creature-scale cases.
