# Local Spritesheet Authoring Workflow — Living Specification

Status date: **2026-09-08**

Status: **CANONICAL TARGET WORKFLOW / ALL-LOCAL AUTHORING / H3 BASE50 MOTION MASTER LOCKED / FLUX.1 KONTEXT [DEV] PREFERRED PIXEL-ART RECONSTRUCTION CANDIDATE / UI IMPLEMENTATION NEXT**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Define the local authoring application that takes a character concept plus a real action video and returns a complete runtime-ready pixel-art animation asset.

Target operator experience:

1. provide an existing character reference **or** describe a new character in text;
2. provide the character/creature's relative world scale;
3. provide a real reference video containing the desired action;
4. choose the action type from a preset list or `custom`;
5. run one local job;
6. receive a finished transparent pixel-art spritesheet, preview and metadata.

The workflow must remain usable for humanoids, animals, monsters, fantastic creatures and bosses with materially different sizes.

## All-local requirement — LOCKED

The intended production workflow runs locally after model installation. Normal asset production must not require a hosted generation API.

The current H3 implementation already runs locally. Frame extraction, segmentation/alignment, pixel-art reconstruction and packing are also intended to run locally.

The official MiniMax hosted `H3-Context-IR` and `H3-Regenerate-2K` services are **not** required by the currently validated Roguelite Base Ref2VA pipeline.

## Pipeline — LOCKED

`character source -> complete reference image -> real action video + action metadata -> MiniMax H3 Base50 motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> FLUX.1 Kontext [dev] pixel-art reconstruction -> transparent spritesheet/atlas + metadata`

The H3 video is an **intermediate motion master**, not the final runtime art.

## Stage A — Character source

The interface must expose two mutually exclusive modes.

### A1. Existing reference image

Upload a complete character reference image. This is the preferred mode when the character already has an approved visual identity.

For the Exilada, the canonical current source remains:

`assets/source/characters/exilada/reference/exilada_master.png`

### A2. Text-described character generation

Enter a text description and generate a complete reference image locally before action generation.

The exact local text-to-image model for this stage is **not yet locked**. It is a separate selection gate. Current candidates include SDXL-class or FLUX text-to-image models.

Do not misuse FLUX.1 Kontext [dev] as the mandatory text-to-image generator: its local open-weight role in this workflow is downstream image editing/reconstruction.

The generated reference must be approved/selected before the H3 action job starts.

## Stage B — Relative world scale

The UI must include a numeric **relative scale** independent of image resolution.

Baseline semantics:

- `1.0` = baseline adult-human/Exilada scale;
- Exilada remains approximately `128px` tall in the canonical gameplay composition at scale `1.0`;
- smaller/larger creatures multiply the intended world/render scale rather than stretching the character non-uniformly.

The exact allowed numeric range is not yet locked.

Relative scale influences:

- target visible runtime sprite height;
- required cell/atlas dimensions;
- camera/composition QA for very large creatures;
- source-render resolution policy when a larger runtime sprite needs more detail;
- metadata consumed by the game/content pipeline.

It may also be supplied semantically to character-reference generation (`tiny`, `human-sized`, `giant`, etc.), but deterministic runtime scale remains explicit metadata.

## Stage C — Action input

Upload a real reference video containing the desired action.

The **video is authoritative for the actual motion**. The action-type selector does not replace the driver and must not synthesize unrelated motion by name alone.

Driver preferences:

- fixed camera when practical;
- complete action visible;
- body/extremities remain inside the source frame;
- sufficient margin for generated hair, cloth, weapons and accessories;
- performer identity/costume/body may differ completely from the target character.

## Stage D — Action type presets

The UI must provide at least these initial presets plus `custom`:

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
- default loop/non-loop policy;
- suggested final frame count;
- action-segment/cycle detection heuristic;
- pivot/alignment policy;
- optional gameplay-event metadata such as foot contacts, hit frames, release frames or guard windows.

The driver video still owns the detailed performance.

## Stage E — Motion master: MiniMax H3 Base Ref2VA

### Canonical quality configuration — LOCKED

The H0 Base50 result is the quality baseline and is restored as the production motion-master configuration:

- MiniMax H3 Base Ref2VA;
- `448×800`;
- `124 frames @ 24fps`;
- `ref_image_size=match`;
- `50 steps`;
- sampler `res_multistep`;
- scheduler `beta`;
- seed `0` as current deterministic baseline;
- no Turbo LoRA;
- no FL2VA;
- no style embedding;
- schema-required audio VAE remains wired, with no audio reference/decode requirement for the current job.

The completed H0 output remains the quality proof:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H0 required about `4504.8s` on the current machine. This cost is accepted as the current quality-first baseline until a faster setting is proven to match it.

### Turbo4 — REJECTED FOR PRODUCTION QUALITY

The 4-step Ref2V Turbo experiment was executed and visually rejected by the user. It does not replace Base50.

Do not use Turbo4 as the default path merely because it is faster. Preserve the test as failure history; exact local timing/hash evidence must not be invented if not captured in repository documentation.

## Stage F — Automatic action-frame distillation

The H3 124-frame video is not the runtime animation.

Downstream automation must:

1. extract all video frames;
2. locate the useful action interval or one stable loop/cycle when applicable;
3. select a compact final frame set appropriate to the action;
4. reject obvious structural/crop failures where automatic confidence permits;
5. preserve action timing in metadata.

Default frame count is action-dependent rather than globally fixed. Typical initial targets may be 8–16 frames, with 12 as a useful general review target.

The previously produced H0 dance/gesture sheets proved that ordinary video frames can be extracted and packed; they were only raster/proxy proof and not final pixel art.

## Stage G — Automatic alpha, alignment and pivot

The system must automatically:

- isolate the complete visible character;
- preserve hair, cloth, weapon and accessory extents;
- produce RGBA frames;
- choose a stable pivot/root appropriate to the action;
- preserve legitimate body bob and airborne motion rather than forcibly freezing the character;
- allocate cells large enough for the action envelope and relative character scale.

No routine manual masks or per-frame alignment.

## Stage H — Final pixel-art reconstruction

### Preferred model — CURRENT DECISION

**FLUX.1 Kontext [dev] is the preferred first local model to validate for the final pixel-art reconstruction stage.**

Reason for the choice:

- the task is image editing/transformation, not motion generation;
- character identity and pose should survive while the visible rendering language changes;
- Kontext is designed for context-aware image editing, character consistency and style transformation;
- it is a better conceptual fit than asking H3 to preserve literal pixel clusters through video generation.

### Set-level consistency strategy

Do not default to independently re-generating each frame with no shared context.

Preferred first validation:

- provide the canonical/reference character image;
- provide the selected action frames as a coherent strip/contact sheet or otherwise shared-context set;
- request deliberate high-quality pixel art while preserving frame order, silhouette, pose and attachments;
- split the reconstructed set back into exact runtime cells;
- apply deterministic palette/grid QA after reconstruction.

The goal is **authored-looking pixel art**, not nearest-neighbor reduction, blurred miniature illustration or simple palette quantization.

### License caveat — MUST REMAIN VISIBLE

The open-weight FLUX.1 Kontext [dev] release uses the FLUX non-commercial license. It is suitable for local technical validation, but a commercial game release requires either appropriate Black Forest Labs commercial licensing or a production renderer whose license permits the intended commercial use.

Therefore Kontext is the preferred technical renderer candidate, **not yet a commercial-license lock**.

SDXL/img2img remains a fallback candidate if Kontext fails quality, hardware or licensing requirements.

## Stage I — Runtime packaging

Every completed job should return at minimum:

- `<character>_<action>_motion_master.mp4`
- `<character>_<action>_frames/` — selected transparent frames
- `<character>_<action>_pixelart_sheet.png` — final review/runtime sheet
- `<character>_<action>_preview.gif` or equivalent loop/preview
- `<character>_<action>_atlas.png` — optional trimmed atlas
- `<character>_<action>_atlas.json` — rectangles, pivots, durations and events
- `<character>_<action>_manifest.json` — source hashes, model/settings, scale, action preset and provenance

Runtime-visible cells remain complete precomposed character images.

## Local interface — REQUIRED

The production workflow must be exposed through one local UI rather than requiring the operator to run individual scripts manually.

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

Default H3 controls should remain hidden/locked to the approved Base50 preset. An advanced panel may expose settings for controlled experiments, but production defaults must not silently drift.

### Output

- job progress/stage status;
- motion-master preview;
- selected-frame/contact-sheet preview;
- final pixel-art spritesheet preview;
- direct access to output files and manifest.

## UI implementation

**Gradio is the current V1 implementation choice** because it supports local image/video upload, galleries, progress reporting and file outputs with low integration cost.

This is an engineering implementation choice, not a permanent game architecture dependency. Replace it if integration evidence shows a better local UI framework is needed.

## Failure classification

Keep the project-wide failure vocabulary:

- `INFRASTRUCTURE FAIL`
- `INTEGRATION FAIL`
- `CONFIGURATION FAIL`
- `BLOCKED`
- `MODEL/TASK FAIL`
- `EXHAUSTED_FAIL`

Each stage records its own failure. A failure in pixel-art reconstruction does not retroactively invalidate a good H3 motion master, and a good final render does not excuse bad motion topology.

## Immediate implementation order

1. freeze H3 motion generation back to the proven Base50 configuration;
2. preserve Turbo4 as rejected quality history and stop treating it as the current gate;
3. install/validate FLUX.1 Kontext [dev] locally in a separate workspace without disturbing H3;
4. use the **existing H0 dance/gesture video** as the first end-to-end input — no new H3 generation is required for this proof;
5. extract a sensible action frame set from that video;
6. run the Kontext pixel-art reconstruction experiment on the set;
7. pack and inspect the first genuinely final-style pixel-art spritesheet;
8. then build the Gradio orchestration UI around the proven stages;
9. only after that expand to new action types and creature scales.

## Current validation question

> Can a fully local pipeline preserve the H3 Base50 motion/anatomy/secondary dynamics while converting an automatically distilled action set into coherent, high-quality, temporally consistent pixel art through FLUX.1 Kontext [dev], then package it automatically as a runtime-ready spritesheet?
