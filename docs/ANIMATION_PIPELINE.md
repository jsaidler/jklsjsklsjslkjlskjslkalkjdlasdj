# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **H3 BASE50 LOCKED AS MOTION-MASTER QUALITY BASELINE / TURBO4 REJECTED / FINAL PIXEL-ART RENDERER GATE = FLUX.1 KONTEXT [DEV] / ALL-LOCAL UI WORKFLOW NEXT**

Canonical state: `docs/PROJECT_STATE.md`.

Local workflow specification: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Hard production constraints

- complete target-character appearance reference + separate real driving video;
- driver identity/clothing/hair may differ completely;
- infer locomotion/action, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging, keyframing, simulation repair, mask repair, per-frame repainting or hand compositing;
- runtime consumes complete precomposed sprite frames;
- normal production should be runnable locally after installation.

## Production chain — LOCKED

`character reference -> real driver + action metadata -> H3 Base50 complete-character motion master -> automatic action/cycle distillation -> automatic alpha/pivot/alignment -> FLUX.1 Kontext [dev] pixel-art reconstruction -> transparent spritesheet/atlas + metadata -> runtime playback`

H3 solves motion. The downstream renderer solves final pixel-art appearance.

## H3 quality baseline — RESTORED

Canonical motion-master configuration:

- MiniMax H3 Base Ref2VA;
- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no Turbo/FL2VA/style embedding.

Completed H0 evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Human/visual verdict: **PASS_CANDIDATE and preferred motion-master quality baseline.**

## Turbo4 — REJECTED

Runner49/4-step Turbo was executed and visually rejected by the user.

Do not use it as the default production route. Do not keep the earlier assumption that speed optimization precedes downstream pipeline proof.

Record: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

A future speed optimization must independently prove H0/Base50-equivalent visual quality before replacing the baseline.

## Temporal production rule

The current proven H3 regime remains `124 frames @24fps`.

Do not default to requesting only 8–12 generated H3 frames.

Normal flow:

`124-frame motion master -> select/distill useful action frames -> final renderer`

The compact final frame count is action-dependent. First tests will normally fall in the 8–16 range.

## Existing H0 video — CURRENT DOWNSTREAM TEST SOURCE

The completed H0 video is a **dance/gesture-like action**, not a walk.

It has already proven basic frame extraction and raster sheet packing. The correct next use is to reuse this existing motion master for the pixel-art stage rather than spend another Base50 hour just to test downstream tooling.

## Action metadata/presets

The authoring UI must support presets including at least:

- idle, walk, run, jump, land, dodge, roll;
- punch, kick, block, parry, hit reaction, knockdown, get-up, death;
- taunt, dance/gesture;
- sword slash/overhead/thrust, axe swing, spear thrust, bow shot, staff attack, spell cast, special attack;
- custom.

The **driver video owns the actual performance**. The action preset defines extraction/loop policy, naming, default frame count, pivot policy and optional event metadata.

## Relative character scale

The animation pipeline must not assume every asset is human-sized.

`relative_scale=1.0` = baseline adult-human/Exilada scale, approximately 128px visible height in the canonical gameplay composition.

Scale influences output occupancy, cell/atlas size and source-resolution policy. It does not non-uniformly stretch character anatomy.

## Action distillation

Automatic stage responsibilities:

1. decode/extract the H3 motion master;
2. identify the useful action interval or stable loop/cycle where applicable;
3. choose an action-appropriate compact frame set;
4. preserve timing/event information;
5. reject obvious structural/crop failures where confidence allows;
6. produce high-resolution frames for segmentation/rendering.

No manual per-frame selection is a required production step.

## Alpha / alignment / pivot

Automatic stage must:

- isolate the complete visible character;
- preserve hair, cloth, weapon and accessory extents;
- output RGBA;
- derive an action-appropriate stable pivot/root;
- preserve legitimate bob, jump arcs and knockback instead of artificially freezing every frame;
- allocate a cell/action envelope consistent with relative character scale.

## Final pixel-art reconstruction — CURRENT RENDERER GATE

Preferred first local model: **FLUX.1 Kontext [dev]**.

The first validation should operate on the selected action as a shared-context set/strip when practical, using the canonical character reference as identity/style anchor.

Goals:

- preserve pose, silhouette and attachment relationships;
- reconstruct deliberate high-quality pixel art;
- keep palette/design coherent across frames;
- avoid blurred miniature illustration and arbitrary per-frame redesign;
- split back into exact cells after reconstruction;
- run deterministic pixel-grid/palette QA afterward.

Kontext is not yet proven in this project.

### License note

The open-weight Kontext [dev] release is non-commercial. Technical validation is allowed under that license; commercial shipping later requires appropriate BFL licensing or replacement with a compatible renderer.

SDXL/img2img remains a fallback renderer candidate.

## Runtime outputs

Each completed action job should produce:

- motion-master MP4;
- selected transparent PNG frames;
- final pixel-art spritesheet PNG;
- preview GIF or equivalent;
- optional trimmed atlas PNG;
- atlas/action JSON with rectangles, pivots, durations and events;
- provenance manifest with source hashes/model/settings/relative scale/action preset.

## Local authoring interface

One local UI is required.

V1 implementation choice: **Gradio**, with:

- existing-reference vs generate-from-text mode;
- image/text input;
- character name/category;
- relative world scale;
- driver-video upload;
- action-type dropdown/custom action;
- optional facing/frame-count override;
- locked H3 Base50 production preset with advanced settings hidden;
- progress and previews at each stage;
- downloadable/directly accessible final artifacts.

The exact text-to-reference generation model is still open; SDXL-class and FLUX text-to-image models are candidates.

## Current order

1. keep H3 Base50 fixed;
2. stop Turbo4 production use;
3. install/validate FLUX.1 Kontext [dev] separately;
4. use the existing H0 dance/gesture video for the first end-to-end pixel-art sheet proof;
5. only after that build the UI around proven stages and expand to new action/scale families.

## Cleanup

- keep minimal Base H3 files;
- Turbo4 LoRA may be removed after its local evidence is preserved;
- do not add H3 FL2VA/style/alternate quantizations without explicit evidence;
- paused Wan large checkpoints may be removed while W1H/W1L proof remains;
- keep SSD comparison evidence until explicit abandonment/final verdict.
