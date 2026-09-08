# H1-S — MiniMax H3 spritesheet production pass

Status date: **2026-09-08**

Status: **HISTORICAL WALK-SPECIFIC PLAN / SUPERSEDED AS CURRENT GATE BY ACTION-AGNOSTIC LOCAL AUTHORING WORKFLOW**

Canonical state: `docs/PROJECT_STATE.md`.

Current workflow specification: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Historical purpose

This document separated three concepts that remain valid:

1. **motion master:** H3-generated complete-character video;
2. **action distillation:** automatic reduction of the motion master to a compact game-frame set;
3. **runtime render:** reconstruction of those selected frames as final high-quality pixel art.

The old tiny H0 proxy remains historical legibility evidence only.

## Decisions that still survive

- final runtime art is deliberate high-quality pixel art;
- H3 painterly/raster output is an intermediate motion master;
- runtime uses complete precomposed frames;
- no routine manual masks, repainting, rigging or per-frame cleanup;
- H3 is currently proven at `124f@24fps`, so compact runtime frame counts are downstream distillation, not the default H3 generation length;
- action frames should be processed as a coherent set when possible to improve final design/palette consistency.

## H0 quality baseline — STILL CANONICAL

The preferred H3 motion-master configuration remains the original H0 Base50 result:

- MiniMax H3 Base Ref2VA;
- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no Turbo LoRA.

Completed evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`.

## Turbo4 result — SUPERSEDES THIS DOCUMENT'S OLD THROUGHPUT GATE

The 4-step Turbo experiment was executed and visually rejected by the user.

Therefore the earlier H0T/Runner49 assumption in this document is closed:

- Turbo4 is not the production default;
- Base50 is restored;
- speed optimization is deferred until a faster configuration can actually match Base50 quality.

Detailed record:

`docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

## Why H1-S walk is no longer the immediate next gate

The user clarified that the existing H0 video itself should be treated as a valid sample action for downstream pipeline development. That video is a **dance/gesture-like action**, not a walk.

Therefore there is no reason to spend another ~75-minute Base50 generation merely to test frame extraction and final rendering.

The immediate proof now reuses the existing H0 motion master:

`existing H0 dance/gesture video -> action-frame selection -> alpha/alignment -> final pixel-art reconstruction -> spritesheet`

## Final pixel-art renderer direction — UPDATED

The preferred first local renderer candidate is now **FLUX.1 Kontext [dev]** because the downstream problem is image editing/style transformation while preserving character identity, pose and silhouette.

Preferred first test:

- approved character reference;
- selected H0 action frames as a shared-context strip/set;
- Kontext reconstruction to high-quality pixel art;
- split cells and run deterministic pixel-grid/palette QA;
- pack final spritesheet.

Kontext is not yet proven. Its open-weight release is non-commercial, so commercial shipping later requires BFL commercial licensing or a compatible replacement renderer.

SDXL/img2img remains a fallback.

## Action-agnostic architecture

The new local workflow is broader than locomotion and supports presets for idle, walk, run, jump, punch, kick, defenses, hit/death, weapon attacks, taunt/dance/gesture and custom actions.

The real reference video owns the detailed motion; the action preset owns metadata/extraction/loop/pivot defaults.

It also carries explicit `relative_scale` so small creatures and very large monsters can share the same pipeline without assuming one human-sized sprite envelope.

## Current gate

**Do not execute a new H1-S walk solely to prove the pipeline. Install/validate the local pixel-art renderer and use the existing H0 dance/gesture video as the first end-to-end spritesheet proof.**
