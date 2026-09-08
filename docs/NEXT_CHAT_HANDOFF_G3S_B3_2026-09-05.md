# Next-chat handoff — local complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- active H3: `Z:\AI\MiniMaxH3`
- paused Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Read first

- `docs/PROJECT_STATE.md`
- `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
- `docs/VISUAL_DIRECTION.md`
- `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
- `docs/ANIMATION_PIPELINE.md`
- `docs/CHARACTER_PRODUCTION_PIPELINE.md`
- `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
- `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`

## Current production contract

Final local pipeline:

`existing or locally generated character reference + relative world scale + real action driver + action preset -> H3 Base50 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> FLUX.1 Kontext [dev] pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

No routine manual rigging/keyframing/mask repair/per-frame repainting/hand compositing.

## Final visible art

Runtime characters are deliberate high-quality pixel art.

H3/Wan painterly/raster outputs are intermediate motion/pictorial masters only. The tiny H0 proxy is historical QA, not a production asset.

Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell and mature 1980s sword-and-sorcery direction remain active.

## H3 H0 / Runner48 — COMPLETE / PREFERRED QUALITY BASELINE

Canonical Base50 configuration:

- Picture1 = canonical Exilada;
- Video1 = raw comparison driver, timestamp-resampled only;
- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- video `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / preferred motion-master quality baseline.** Stable body topology, coherent hair/cloth response, no destructive global smear. Chain detail still drifts somewhat. Late foot crop follows driver/source envelope.

## Turbo4 / Runner49 — REJECTED

The 4-step Ref2V Turbo experiment was run and visually rejected by the user.

The user wants the original H0 Base50 quality back.

Therefore:

- Turbo4 is closed as default production setting;
- Base50 is restored;
- do not invent Turbo4 timing/hash/prompt evidence if not recovered locally;
- preserve local output/log/manifest if available, then the Turbo LoRA may be removed.

Record: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

## Important H0 action clarification

The existing H0 result is a **dance/gesture-like action**, not a walk.

This is now useful: it is the immediate downstream proof source. Do not generate a new walk merely to test spritesheet conversion.

It has already proved basic frame extraction/raster packing. The next proof must turn selected H0 action frames into genuinely final-style pixel art.

## Temporal rule

Keep the proven `124f@24fps` H3 motion-master regime for now.

Do not default to 8–12 generated H3 frames. Distill the long motion master downstream into an action-appropriate compact set, typically 8–16 frames for early tests.

## Final pixel-art renderer — NEXT GATE

Preferred first local candidate: **FLUX.1 Kontext [dev]**.

First test:

1. approved Exilada reference;
2. selected action frames from the existing H0 dance/gesture video as a shared-context strip/set;
3. Kontext reconstruction into deliberate high-quality pixel art;
4. split cells;
5. deterministic pixel-grid/palette QA;
6. final transparent spritesheet + preview + atlas/manifest.

Kontext is not yet proven.

### License caveat

The open-weight Kontext [dev] release is non-commercial. Technical validation is fine; commercial game shipping later requires BFL commercial licensing or a renderer with compatible terms.

SDXL/img2img remains fallback.

## Local authoring UI — REQUIRED

The finished tool must expose one local interface with:

- reference image **or** text-described local reference generation;
- character name/category;
- numeric relative world scale;
- action reference video upload;
- action preset dropdown including common locomotion/combat/weapon/defense/taunt/dance/custom actions;
- locked H3 Base50 production preset by default;
- progress/previews;
- final sheet/frames/preview/JSON/manifest file access.

Gradio is the current V1 UI scaffold choice.

The exact local text-to-reference model is not yet locked. SDXL-class and FLUX text-to-image families are candidates.

## Relative scale

`relative_scale=1.0` = baseline adult-human/Exilada size, about 128px visible height in the canonical gameplay composition.

Scale affects target sprite occupancy, cell/atlas dimensions and source-resolution policy. It is not arbitrary image stretching. Exact min/max remains open.

## Wan

Wan remains paused after W1L, not exhausted. Preserve W1H/W1L evidence. Large Wan checkpoints may be removed if proof remains.

## Immediate next actions

1. install/validate FLUX.1 Kontext [dev] locally in a separate workspace without touching H3;
2. reuse the existing H0 dance/gesture motion master;
3. extract/select a coherent action set;
4. produce the first final-style pixel-art spritesheet;
5. then wrap the proven stages in the local Gradio UI;
6. only afterward expand to new actions and creature scales.
