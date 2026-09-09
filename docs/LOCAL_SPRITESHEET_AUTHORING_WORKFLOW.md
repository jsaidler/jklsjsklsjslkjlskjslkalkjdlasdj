# Local Spritesheet Authoring Workflow — Living Specification

Status date: **2026-09-08**

Status: **CANONICAL TARGET WORKFLOW / ALL-LOCAL AUTHORING / CHARACTER MASTER REVISION NOW PRECEDES H3 / H3 BASE50 MOTION BASELINE / KONTEXT PIXEL-ART QUALITY STILL OPEN / 128PX ASSET BASELINE RETIRED**

Canonical project state: `docs/PROJECT_STATE.md`.

Active Exilada master-revision gate: `docs/EXILADA_MASTER_REVISION_LOCAL_EDITOR_2026-09-08.md`.

## Purpose

Define one local authoring system that can take a character concept plus real action video and return runtime-ready complete-character action assets without routine manual art/animation labor.

The workflow must also support an earlier design phase: before animation, the user must be able to refine a character master locally with visual references and explicit state/design controls.

## All-local requirement — LOCKED

Normal asset production must run locally after model installation. Hosted generation APIs are not part of the production dependency chain.

Current local stages:

- character-master visual revision: FLUX.1 Kontext local editor, active for the Exilada;
- future text-to-new-character reference generation: exact model still open;
- motion generation: MiniMax H3 Base Ref2VA;
- action-frame extraction/selection: Python automation;
- alpha/alignment/pivot: Python automation;
- pixel-art reconstruction: FLUX.1 Kontext family, style quality still under validation;
- packing/preview/manifest: Python automation;
- eventual unified production UI: Gradio after the active gates stabilize.

## Canonical pipeline

`character source -> local master design/revision -> explicitly approved complete character master -> real action video + action metadata -> MiniMax H3 Base50 motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> pixel-art reconstruction preserving useful production resolution -> one horizontal spritesheet row for that action + frames/preview/JSON/manifest -> runtime scaling/playback`

The H3 video is an intermediate motion master, not final runtime art.

## Stage A — Character master design / revision

### A1. Existing reference image

Use an existing complete character reference as a working master.

For the Exilada, the current file is:

`assets/source/characters/exilada/reference/exilada_master.png`

However, on 2026-09-08 that master was **reopened for visual revision**. It remains identity evidence but is not final visual-design authority until the current local gate passes.

### A2. Exilada local visual editor — CURRENT GATE

Launcher:

`tools/structured-2d-character-pipeline/54_run_exilada_master_editor.ps1`

Application:

`tools/flux-kontext-spike/exilada_master_editor.py`

The editor exposes:

- current working master;
- optional approved nude anatomy turnaround;
- two optional visual-direction references;
- clothing/tear/exposure brief;
- body/identity brief;
- material/captivity brief;
- pictorial-direction brief;
- iteration-specific change;
- seed, steps, guidance and denoise;
- candidate versioning/provenance;
- candidate-as-next-input iteration;
- explicit approval before canonical master replacement.

For the Exilada, the active design objectives include:

- more severe and materially irregular captivity-cloth damage;
- substantially greater torso exposure than the current master;
- partial breast exposure as a valid/desirable candidate when caused by damage;
- near-nudity/full adult nudity as legitimate states when deliberately chosen;
- no mandatory censor garment;
- much stronger visible Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell sword-and-sorcery charge;
- rejection of generic contemporary fantasy/MMO/cosplay-clean character design.

The editor preserves native useful Kontext output and does not downscale candidates to 128/192/384px proxy sizes.

### A3. New character generation from text

The final system must also allow a new character to be described in text and locally generated before animation.

The exact text-to-image model is not yet locked. That is a later problem than the current Exilada master revision.

Any generated reference must be explicitly approved before H3 action generation.

## Stage B — Relative world scale

The UI must expose numeric relative scale independent of asset resolution.

Current contract:

- `1.0` = adult-human/Exilada world scale;
- no fixed gameplay pixel height is implied;
- larger/smaller creatures change intended world/render scale rather than being stretched arbitrarily.

The former `128px` Exilada baseline is retired.

Historical `192px` and `384px` renderer packaging sizes are also not production sprite-size locks.

Gameplay apparent size may be benchmarked at different viewport occupancies, but this is a runtime/composition question rather than a reason to destructively shrink production source assets.

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

### Canonical quality baseline

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

The current H0 remains valuable motion/model evidence. If the newly approved Exilada master changes materially, H3 must be revalidated against that master before production animation proceeds.

## Stage F — Automatic action distillation

The 124-frame H3 motion master is not the runtime animation.

Downstream automation must:

1. decode all frames;
2. locate the desired action interval/cycle;
3. select a compact ordered frame set;
4. reject obvious crop/structure failures where confidence permits;
5. derive runtime-appropriate timing/events rather than blindly preserving source-video holds;
6. preserve provenance separately from runtime timing.

### Spritesheet layout invariant — HARD LOCK

**One action = one spritesheet row.**

Frames inside the row read left-to-right in time.

Internal renderer chunks/tiles never define final semantic rows.

A later multi-action sheet may stack distinct actions vertically.

## Stage G — Automatic alpha, alignment and pivot

The system must automatically:

- isolate the complete visible character;
- preserve hair, cloth, weapons/accessories;
- produce RGBA frames;
- choose a stable action-appropriate pivot/root;
- preserve legitimate body bob/airborne motion;
- allocate sufficient frame bounds for the action envelope and relative world scale.

No routine manual masks or per-frame alignment.

## Stage H — Final pixel-art reconstruction

### Active renderer family

FLUX.1 Kontext [dev] remains the active technical family.

Runner52 proved enough structural preservation to continue but did not prove final high-level pixel-art quality.

### Runner53 — PAUSED

Runner53 tests the Modern Pixel Art LoRA while preserving Runner52 structure settings.

It is now paused because improving rendering language on the old Exilada master would preserve a character design that has been reopened.

Do not run Runner53 until Runner54 produces an explicitly approved master and any required H3 revalidation is complete.

### Approved adult-body invariant — HARD LOCK

The renderer changes rendering language, not approved body design.

For adult characters:

- preserve adult age/head-to-body ratio;
- preserve torso/limb length and major proportions;
- preserve adult bust/hips/pelvis/legs relationship;
- no shortened/thickened juvenile reinterpretation;
- no enlarged head, rounded childlike face, cute/chibi/adolescent drift.

### Art-direction invariant — HARD LOCK

Final art must preserve the approved master's sword-and-sorcery charge, including mature adult anatomy, danger, grime, sensuality, pulp-fantasy excess and tactile skin/cloth/metal.

A clean pixel-art result that loses this charge is not a pass.

## Stage I — Runtime packaging

Every completed action job should return at minimum:

- `<character>_<action>_motion_master.mp4`
- `<character>_<action>_frames/`
- `<character>_<action>_pixelart_master_row.png`
- `<character>_<action>_preview.gif`
- optional atlas PNG;
- JSON with rectangles, pivots, runtime durations/events;
- provenance manifest with source hashes/model/settings/relative scale/action preset.

Runtime-visible cells remain complete precomposed character images.

There is no arbitrary final 128/192/384px cell requirement. Preserve useful production resolution, then scale for presentation in the engine.

## Eventual unified local interface

The long-term UI must support:

### Character

- existing reference / local generation from text;
- character name/id;
- relative world scale;
- master revision/approval;
- optional anatomy and visual references.

### Motion

- reference-video upload;
- action-type dropdown;
- direction/facing metadata where relevant;
- optional custom action name;
- optional final-frame-count override.

### Generation/output

- locked quality defaults with advanced controlled experiments;
- job progress/stage status;
- motion-master preview;
- selected source-action strip;
- final one-row pixel-art master preview;
- frames/sheet/JSON/manifest access.

Gradio remains the intended V1 orchestration surface. Runner54 is the first focused local Gradio authoring tool because character-design iteration became the immediate bottleneck.

## Immediate implementation order

1. run Runner54;
2. iterate Exilada visual candidates locally;
3. explicitly approve a new master only after anatomy/identity, clothing damage/exposure and sword-and-sorcery charge all pass;
4. revalidate/regenerate H3 if the master revision is material;
5. resume Runner53/downstream pixel-art quality work only then;
6. solve action-specific frame distillation/runtime timing;
7. consolidate the focused tools into the unified Gradio authoring UI;
8. expand to new actions and creature-scale cases.

## License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is acceptable; commercial shipping later requires appropriate BFL licensing or a renderer with compatible terms.
