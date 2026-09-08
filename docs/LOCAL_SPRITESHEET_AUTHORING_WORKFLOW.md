# Local Spritesheet Authoring Workflow — Living Specification

Status date: **2026-09-08**

Status: **CANONICAL TARGET WORKFLOW / ALL-LOCAL AUTHORING / H3 BASE50 MOTION MASTER LOCKED / KONTEXT RUNNER50 VISUAL FAIL RECORDED / RUNNER51 TEMPORAL-ROW + BODY-STRUCTURE REPAIR PREPARED / UI AFTER RENDERER PASS**

Canonical project state: `docs/PROJECT_STATE.md`.

Renderer spike: `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`.

Runner50 visual-failure record: `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`.

## Purpose

Define the local authoring application that takes a character concept plus a real action video and returns a runtime-ready pixel-art animation asset.

Target operator experience:

1. provide an existing character reference **or** describe a new character in text;
2. provide the character/creature's relative world scale;
3. provide a real reference video containing the desired action;
4. choose the action type from a preset list or `custom`;
5. run one local job;
6. receive a finished transparent pixel-art spritesheet, previews and metadata.

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

`character source -> approved complete reference -> real action video + action metadata -> MiniMax H3 Base50 motion master -> automatic coherent action-sequence extraction -> automatic alpha/pivot/alignment -> pixel-art reconstruction -> transparent spritesheet/atlas + metadata`

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
- sequence/cycle detection heuristic;
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

## Stage F — Automatic action/sequence distillation

The 124-frame H3 motion master is not the runtime animation.

Downstream automation must:

1. decode all frames;
2. locate useful action intervals or loops;
3. select compact temporally coherent sequences;
4. reject obvious crop/structure failures where confidence permits;
5. preserve timing metadata.

### Spritesheet row invariant — HARD LOCK

**One row = one temporally coherent animation sequence.**

Frames inside each row read left-to-right in time.

Do not use a global evenly spaced sample of unrelated timestamps as a finished spritesheet.

If an action spans several rows, each row must be an explicitly meaningful temporal chunk and the manifest must describe the relationship between rows.

Runner50 violated this rule by sampling frames `1,12,23,35,46,57,68,79,90,102,113,124` across the entire H0 and treating the resulting `4×3` contact sheet as an animation asset.

### Runner51 temporary extraction policy

For the current H0 renderer proof only:

- split the 124-frame timeline into three thirds;
- inside each third, find the 16-frame window with highest simple motion energy;
- select four ordered frames at offsets `0,5,10,15`;
- each resulting four-frame sequence becomes one final spritesheet row.

This is a controlled proof of row semantics, not the final action-specific cycle detector.

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
- one global `4×3` contact sheet did not preserve correct animation-row semantics;
- the mature 1980s sword-and-sorcery charge weakened.

Therefore do not jump renderer family yet. The next test changes task formulation only.

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

### Runner51 — CURRENT GATE

Runner:

`tools/structured-2d-character-pipeline/51_run_flux_kontext_h0_dance3x4_temporal_rows_structure_lock.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance3x4_temporal_rows_structure_lock.py`

Controlled differences from Runner50:

1. one coherent temporal sequence per final row;
2. each four-frame row is rendered separately;
3. renderer input for each row is a `2×2` `1024×1024` square, giving each character much more working resolution;
4. same canonical Exilada reference remains the identity/art-direction authority;
5. Kontext denoise reduced from `1.0` to **`0.45`** to preserve source structure;
6. prompt explicitly forbids infantilization/body redesign;
7. prompt explicitly retains the mature 1980s sword-and-sorcery lineage;
8. three four-frame row results are repacked into a final `4×3` sheet.

Same model/runtime:

- `flux1-dev-kontext_fp8_scaled.safetensors`;
- `clip_l.safetensors`;
- `t5xxl_fp16.safetensors`;
- `ae.safetensors`;
- ComfyUI v0.34.0;
- workspace `Z:\AI\FluxKontext`;
- port `8191`.

No new H3 generation and no new model download should be required if Runner50 installation remains intact.

### Runner51 expected outputs

Under `Z:\AI\FluxKontext`:

- `h0_dance3x4_source_temporal_rows.png`
- `h0_dance3x4_temporal_selection_manifest.json`
- `h0_dance_row01_input_2x2.png`
- `h0_dance_row02_input_2x2.png`
- `h0_dance_row03_input_2x2.png`
- three row-specific Kontext outputs/prompts/manifests;
- `h0_dance_row01_preview.gif`
- `h0_dance_row02_preview.gif`
- `h0_dance_row03_preview.gif`
- `h0_dance3x4_pixelart_sheet_opaque.png`
- `h0_dance3x4_pixelart_sheet_rgba.png`
- `h0_dance3x4_kontext_manifest.json`

### Runner51 pass boundary

PASS requires:

- each row reads as one coherent four-frame animation;
- mature Exilada anatomy/proportions remain materially stable;
- no infantilization/cute/chibi drift;
- poses/silhouettes remain recognizably sourced from H0;
- deliberate high-quality pixel-art reading;
- locked 1980s sword-and-sorcery charge remains visible;
- automatic alpha packaging remains usable.

If Runner51 still fails body preservation at denoise `0.45`, classify that specific failure before changing precision/model family.

### License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is acceptable; commercial shipping later requires appropriate BFL licensing or a renderer with compatible terms.

SDXL/img2img remains a fallback candidate if Kontext ultimately fails quality, hardware or licensing requirements.

## Stage I — Runtime packaging

Every completed job should return at minimum:

- `<character>_<action>_motion_master.mp4`
- `<character>_<action>_frames/`
- `<character>_<action>_pixelart_sheet.png`
- row/action preview GIFs or equivalent;
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
- selected coherent-row/contact-sheet preview;
- row animation previews;
- final pixel-art spritesheet preview;
- direct file/manifest access.

## UI implementation

**Gradio remains the V1 implementation choice**, after the renderer behavior is proven.

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

1. run Runner51 on the existing H0 dance/gesture motion master;
2. inspect `h0_dance3x4_source_temporal_rows.png` first to confirm row semantics;
3. inspect each row GIF for temporal coherence;
4. inspect final sheet for adult-body preservation, pose fidelity, pixel-art quality, alpha and 1980s art direction;
5. if Runner51 passes, build the Gradio orchestration UI around H3 Base50 + the proven renderer formulation;
6. then implement action-specific cycle detection, text-reference generation and creature-scale cases;
7. do not spend another Base50 H3 hour solely to debug the renderer.

## Current validation question

> Can Runner51 keep one coherent temporal animation per row and preserve the Exilada's mature adult physical structure and locked 1980s sword-and-sorcery identity while converting the existing H0 motion into high-quality pixel art automatically?
