# G3S — Animation Architecture Lock

Status date: **2026-09-08**

Status: **CANONICAL / COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME / H3 BASE50 MOTION MASTER / FINAL PIXEL-ART RECONSTRUCTION / ALL-LOCAL AUTHORING / NO MANUAL ANIMATION OR PER-FRAME CLEANUP**

Canonical local workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Presentation lock

The game uses an elevated arcade beat'em-up / belt-scroller false-3D presentation:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- Exilada about `128px` tall at baseline relative scale `1.0`;
- first locomotion family screen-left and mostly lateral/three-quarter;
- intended first gameplay facing `72°`.

## Final runtime representation — LOCKED

Runtime consumes **complete, already-composed character frames**:

`complete pixel-art frames -> spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment layer assembly.

## End-to-end authoring architecture — LOCKED

`existing or locally generated character reference + relative world scale + real action driver + action preset -> MiniMax H3 Base50 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> high-quality pixel-art reconstruction -> complete transparent spritesheet/atlas + metadata -> runtime`

Normal asset authoring is intended to run locally after model installation.

## Complete-frame motion requirement — LOCKED

Every valid exported animation must bake together, where present:

- body locomotion/action and weight transfer;
- soft-tissue/jiggle;
- hair inertia/follow-through;
- clothing/binding motion;
- material/wind response;
- weapons;
- shackles/chains/restraints/accessories;
- final occlusion changes.

## Character-source contract — UPDATED

The local UI supports two sources:

1. upload an approved complete reference image;
2. generate a local complete reference from text, then approve/select it before motion generation.

The exact text-to-reference model is not yet locked.

For the Exilada, canonical appearance remains:

`assets/source/characters/exilada/reference/exilada_master.png`

## Dual-reference motion-authoring contract — LOCKED

Motion authoring uses:

1. **appearance:** approved complete target-character reference;
2. **movement:** arbitrary real driving video.

The driving performer does not need matching costume, hair, body or identity.

The motion model must consume richer evidence than skeleton pose so it can infer non-rigid temporal behavior for hair, cloth, soft tissue, wind and accessories.

## Relative world scale — LOCKED IN PRINCIPLE

The pipeline carries explicit `relative_scale` metadata.

- `1.0` = baseline adult-human/Exilada scale;
- scale changes intended world/render occupancy and cell/atlas policy;
- it does not non-uniformly stretch character anatomy;
- exact allowed min/max remains open.

Very large monsters may require larger runtime sprite occupancy and higher source-render resolution than baseline humans.

## Action preset contract

The driver video owns actual motion. Action-type presets supply metadata/defaults for extraction, looping, pivots and events.

Initial presets include locomotion, jumps, punches, kicks, defenses, hit/death states, common weapon attacks, spell/special attacks, taunt/dance/gesture and `custom`.

## No-manual-production rule — LOCKED

Disallowed as required production steps:

- manual rigging/weight painting;
- manual keyframing;
- manual hair animation;
- manual cloth/chain setup or repair;
- manual pose alignment;
- manual mask repair;
- per-frame repainting/retouching;
- hand compositing or cleanup.

Allowed: fully automatic preprocessing, segmentation, crop/resize, background removal, cycle/action detection, frame extraction, alignment, pixel-art reconstruction, packing, QA and metadata.

## Motion-model state

1. **MiniMax H3 Ref2VA — ACTIVE / H0 Base50 PASS_CANDIDATE and preferred motion-master quality baseline.**
2. Wan-Animate-2 — paused after W1L, not exhausted.
3. SCAIL-2 — later only if H3 fails a future motion-production gate.

Pose-only Moore/SSD routes remain research evidence and do not satisfy the richer raw-video motion contract.

## H3 Base50 quality lock

Canonical motion-master settings:

- `448×800`;
- `124f @24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- no Turbo LoRA.

Completed H0:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- visual verdict **PASS_CANDIDATE**.

The ~75-minute cost is accepted temporarily rather than knowingly degrading quality.

## Turbo4 — CLOSED AS DEFAULT

The official 4-step Turbo experiment was executed and visually rejected by the user.

Base50 is restored. Turbo4 is a failed setting-quality branch, not a failure of H3.

Record: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

## Temporal production rule

Do not assume the production route should ask H3 for only 8–12 generated frames.

The current proven H3 regime is `124f@24fps`.

Production baseline:

`124-frame Base50 motion master -> automatic action distillation -> compact selected game frames -> final pixel-art reconstruction`

Final frame count is action-dependent; early tests generally target 8–16 selected frames.

## Existing H0 downstream proof source

The H0 video is a **dance/gesture-like action**, not a walk.

It is the immediate proof source for the downstream final renderer because no additional H3 generation is needed to validate extraction/reconstruction/packing.

## Final pixel-art renderer — CURRENT PREFERRED CANDIDATE

Preferred first local model: **FLUX.1 Kontext [dev]**.

The first test should use the approved character reference plus the selected action frames as a shared-context set/strip when practical, reconstruct deliberate pixel art, split cells, then run deterministic pixel-grid/palette QA.

Kontext is not yet proven.

The open-weight Kontext [dev] license is non-commercial; commercial shipping later requires appropriate BFL licensing or a compatible replacement renderer. SDXL/img2img remains fallback.

## Local UI — REQUIRED

One local interface must orchestrate:

- existing reference vs text-generated reference;
- character id/category;
- relative world scale;
- driver-video upload;
- action preset/custom action;
- locked Base50 H3 preset by default;
- progress/previews;
- final spritesheet/frames/preview/atlas/manifest outputs.

Gradio is the current V1 scaffold choice.

## Cleanup discipline — LOCKED

- keep Base H3 Ref2VA files;
- Turbo4 LoRA may be removed after preserving local evidence;
- do not accumulate FL2VA/style/alternate quantizations without evidence;
- Wan large weights may be removed while W1H/W1L proof/results remain;
- keep SSD comparison evidence until explicit abandonment/final verdict.

## Closed routes / assumptions

- runtime visible-character layer assembly — CLOSED;
- body-pose-only animation as final motion foundation — CLOSED;
- manual hidden secondary animation as required production method — CLOSED;
- independent unconstrained full-body redraw per frame — CLOSED;
- tiny H0 gameplay proxy as final production art — CLOSED;
- H3 painterly video itself as final runtime art — CLOSED;
- Turbo4 as current production-quality default — CLOSED.

## Current validation question

> Can the existing H3 Base50 motion master be automatically distilled and reconstructed locally through FLUX.1 Kontext [dev] into a coherent high-quality pixel-art spritesheet, then generalized through one local UI to arbitrary characters, creature scales and action presets?
