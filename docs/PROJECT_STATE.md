# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
7. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
8. `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`
9. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
10. `docs/CHARACTERS.md`
11. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active MiniMax H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Game/runtime presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- protagonist about `128px` tall at baseline scale;
- first locomotion family screen-left / mostly lateral-three-quarter;
- current facing baseline `72°`;
- runtime consumes complete precomposed character sprites only.

No visible runtime body/hair/clothing/equipment layer assembly.

## Final visible-art target — LOCKED

Final runtime character graphics are **deliberate high-quality pixel art**.

H3/Wan painterly/raster video is an intermediate **motion master**, not the final runtime art. Simple downscale/nearest-neighbor/palette reduction is not accepted as the final rendering method.

Canonical production chain:

`character reference -> real action driver -> H3 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> high-quality pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

The 1980s sword-and-sorcery lineage remains active: Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Adult sensuality/nudity remains legitimate.

## All-local authoring target — LOCKED 2026-09-08

The project now targets a **single local authoring workflow/interface** that can:

1. accept an existing character reference image **or** generate a local reference from a text description;
2. accept a numeric relative world scale for humans, creatures, monsters and bosses;
3. accept a real action reference video;
4. accept an action-type preset such as walk, jump, punch, kick, weapon attack, defense, hit, death, taunt/dance/gesture or custom;
5. run local motion generation, extraction, pixel-art reconstruction and packaging;
6. return the final spritesheet, preview, frames and metadata.

Canonical UI/workflow specification:

`docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`

Gradio is the current V1 UI scaffold choice unless integration evidence later replaces it.

## Relative character scale — CURRENT CONTRACT

`relative_scale=1.0` represents the baseline adult-human/Exilada scale, approximately `128px` visible height in the canonical gameplay composition.

Relative scale is explicit world/render metadata, not non-uniform image stretching. It influences target sprite height, cell/atlas dimensions and source-resolution policy for large creatures. Exact min/max range is still open.

## Motion model — MiniMax H3 Ref2VA ACTIVE

MiniMax H3 remains the selected motion-master family after H0.

H0 exact quality baseline:

- Base Ref2VA;
- Picture1 = canonical Exilada master;
- Video1 = raw comparison driver, timestamp-resampled only;
- `448×800`;
- `124f @24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed `0`;
- no Turbo/FL2VA/style embedding;
- schema-required audio VAE wired, with no audio reference/decode in the current job.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / preferred motion-master quality baseline.** Stable body topology, coherent hair/cloth motion and no destructive whole-body smear. Chain detail still drifts somewhat. Late right-foot crop follows the driver/source envelope.

`448×800` passes as the current motion-master generation size.

## Turbo4 / Runner49 — REJECTED FOR PRODUCTION QUALITY

The official Ref2V Turbo4 / 4-step experiment was run and visually rejected by the user.

The user explicitly prefers the original H0 Base50 result and requested returning to that configuration.

Therefore:

- Turbo4 is **not** the current gate;
- Turbo4 is **not** the default production path;
- Base50 is restored as canonical;
- do not invent Turbo4 elapsed time/prompt id/hash unless recovered from local evidence.

Record:

`docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`

The Turbo LoRA may be removed after local output/log/manifest evidence is preserved.

## Temporal rule

Do not assume normal H3 production should generate only 8–12 frames.

The current H3 path is proven at `124f@24fps`. The normal pipeline therefore remains:

`124-frame Base50 motion master -> automatic action/cycle distillation -> compact final action set -> pixel-art reconstruction`

Final frame count is action-dependent, typically in the 8–16 range for first tests.

## Current-video spritesheet proof

The existing H0 video is a dance/gesture-like action, **not a walk**.

It has already been used to prove basic local frame extraction and raster spritesheet packing. Those sheets are diagnostic intermediates only; they are not final pixel art.

This same existing H0 video is now the correct first input for the downstream pixel-art renderer proof because it avoids another ~75-minute H3 generation while testing the rest of the pipeline.

## Final pixel-art renderer — CURRENT PREFERRED CANDIDATE

**FLUX.1 Kontext [dev]** is the preferred first local model to validate for the final pixel-art reconstruction stage.

Why:

- the downstream task is image editing/style transformation;
- pose/silhouette/identity must survive while the rendering language changes;
- set-level/strip conditioning can be tested for cross-frame consistency.

Preferred first experiment:

`canonical character reference + selected action strip -> Kontext pixel-art reconstruction -> split cells -> deterministic pixel-grid/palette QA -> final sheet`

Kontext is not yet technically proven in this project.

### License caveat

The open-weight FLUX.1 Kontext [dev] release is non-commercial. It is acceptable for local technical validation, but commercial game shipping requires appropriate BFL commercial licensing or a renderer with compatible commercial terms.

SDXL/img2img remains a fallback if Kontext fails quality, hardware or licensing requirements.

## Character-reference generation from text — OPEN MODEL CHOICE

The interface must support local text-to-reference generation, but the exact model is **not yet locked**.

Current candidate families include SDXL-class and FLUX text-to-image models. Kontext [dev] is not being made the mandatory text-to-image generator because its intended open-weight role here is editing/reconstruction.

## Model-screening order

1. **MiniMax H3 Ref2VA — ACTIVE / Base50 quality baseline locked for motion masters.**
2. Wan-Animate-2 — paused after W1L, not exhausted.
3. SCAIL-2 — later only if H3 fails a future production gate.

## Immediate implementation order

1. stop treating Turbo4 as active; preserve its rejection history;
2. keep H3 Base50 as the canonical motion-master preset;
3. install/validate FLUX.1 Kontext [dev] locally in a separate workspace without disturbing H3;
4. use the existing H0 dance/gesture video as the first end-to-end downstream proof;
5. extract/select a sensible action frame set;
6. reconstruct the set as high-quality pixel art;
7. pack the first genuinely final-style spritesheet + preview + atlas/manifest;
8. build the local Gradio orchestration UI around the proven stages;
9. then expand action presets, text-reference generation and large-creature scale cases.

## Cleanup

- keep the minimal Base H3 Ref2VA set;
- Turbo4 LoRA is no longer an active dependency and may be deleted after preserving local evidence;
- do not accumulate H3 FL2VA/style/alternate quantizations without an explicit hypothesis;
- Wan large checkpoints may be removed while W1H/W1L evidence remains;
- keep SSD comparison evidence until explicit abandonment/final verdict.
