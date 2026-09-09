# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
3. `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`
4. `docs/GAMEPLAY_CHARACTER_SCALE_RECALIBRATION_2026-09-08.md`
5. `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`
6. `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`
7. `docs/RUNNER51_LAYOUT_CONCEPT_REJECT_2026-09-08.md`
8. `docs/VISUAL_DIRECTION.md`
9. `docs/ANIMATION_PIPELINE.md`
10. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
11. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
12. `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`
13. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
14. `docs/CHARACTERS.md`
15. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

Historical preflight incidents remain documented separately.

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext renderer workspace: `Z:\AI\FluxKontext`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` stale/historical and must not be used.

## Game/runtime presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- `relative_scale=1.0` means baseline adult-human/Exilada world scale, **not** a fixed pixel height;
- protagonist gameplay visible height is **OPEN pending comparative viewport benchmarking**;
- first locomotion family screen-left / mostly lateral-three-quarter;
- facing baseline `72°`;
- runtime consumes complete precomposed character sprites only;
- no visible runtime body/hair/clothing/equipment layer assembly.

The former `128px` Exilada hard baseline is retired. See `docs/GAMEPLAY_CHARACTER_SCALE_RECALIBRATION_2026-09-08.md`.

## Final visible-art target — LOCKED

Runtime character graphics are deliberate high-quality pixel art.

H3/Wan painterly/raster video is an intermediate **motion master**, not final runtime art.

Canonical production chain:

`character reference -> real action driver -> H3 Base50 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> high-quality pixel-art reconstruction -> one horizontal row for that action + frames/metadata -> runtime`

Simple downscale/nearest-neighbor/palette reduction is not accepted as the final renderer.

## Spritesheet layout contract — HARD LOCK

**One action = one spritesheet row.**

For every action asset:

- frames read left-to-right in time;
- one action may contain a variable number of frames/columns;
- internal renderer tiles/chunks never become final semantic rows;
- per-frame durations/events live in JSON metadata;
- complete character remains visible in every cell.

Current H0 `dance_or_gesture` proof uses 12 frames. Runner52 used `192×192` diagnostic cells; that size is historical test packaging, **not** a production-scale recommendation.

A later combined character sheet may stack distinct actions vertically.

## 1980s sword-and-sorcery direction — HARD LOCK

Active inspiration lineage:

- Heavy Metal;
- Conan;
- Red Sonja;
- Frank Frazetta;
- Julie Bell.

Final art must preserve mature adult anatomy, danger, grime, sensuality, tactile materials and pulp-fantasy physicality. Approved adult characters may not be sanitized or infantilized.

## Adult body/identity preservation — HARD LOCK

Renderer changes rendering language, not physical identity.

For approved adult characters including the Exilada:

- preserve mature adult age and head-to-body ratio;
- preserve torso/limb length and major proportions;
- preserve adult bust/hips/pelvis/legs relationship;
- no enlarged head, shortened/thickened juvenile body, rounded childlike face, cute/chibi/adolescent drift.

## All-local authoring target — LOCKED

One local interface must eventually support:

1. existing character reference image **or** local text-to-reference generation;
2. relative world scale for humans/creatures/monsters/bosses;
3. real action driver video;
4. action preset such as idle/walk/run/jump/punch/kick/weapon attack/defense/hit/death/taunt/dance/custom;
5. local H3 motion generation;
6. local action-frame extraction;
7. local pixel-art reconstruction;
8. local action-row/preview/atlas/JSON/manifest output.

Gradio remains the V1 UI choice **after renderer behavior passes**.

## Relative scale — CURRENT CONTRACT

`relative_scale=1.0` = baseline adult-human/Exilada **world scale only**.

It does not imply a fixed visible pixel height.

First gameplay-composition benchmark at native `640×360` will compare approximately:

- `160px` visible standing height (~44% of viewport height);
- `180px` (~50%);
- `200px` (~56%).

These are comparison candidates, not locks. Final scale must be chosen in a real gameplay composition with multiple enemies, depth movement, attack envelopes, HUD-safe area, hair/cloth/chain extents and at least one larger creature/boss case.

Authoring/render masters remain materially larger than eventual gameplay display; current target is roughly `256–320px` visible subject height where practical, with `384×384` or larger cells when required by the action envelope.

## Motion model — MiniMax H3 Ref2VA ACTIVE / BASE50 LOCKED

Canonical H0 quality baseline:

- Base Ref2VA;
- Picture1 = canonical Exilada master;
- Video1 = raw comparison driver, timestamp-resampled only;
- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no Turbo/FL2VA/style embedding;
- schema-required audio VAE wired, no audio reference/decode for current job.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / preferred motion-master quality baseline**.

Turbo4 was visually rejected. Base50 remains the production default.

The current H0 is a **dance/gesture-like action**, not a walk. Do not generate a new walk merely to debug downstream rendering.

## FLUX.1 Kontext local renderer — ACTIVE FAMILY

Workspace: `Z:\AI\FluxKontext`

Installed/proven runtime:

- ComfyUI v0.34.0 on port `8191`;
- `flux1-dev-kontext_fp8_scaled.safetensors`;
- `clip_l.safetensors`;
- `t5xxl_fp16.safetensors`;
- `ae.safetensors`.

Reuse this installation; do not redownload it for each renderer test.

## Renderer history

### Runner50 — MODEL/TASK FAIL

Technical inference worked, but denoise1.0 caused adult body drift/infantilization and the task/layout formulation was wrong. Pixel-art language was only partial.

### Runner51 — REJECTED PRE-INFERENCE

Its `4×3` final layout incorrectly split one action into three rows. Classification: **CONFIGURATION / TASK-FORMULATION FAIL — PRE-INFERENCE**. No model-quality evidence.

### Runner52 — COMPLETED / PARTIAL PASS

Runner:

`tools/structured-2d-character-pipeline/52_run_flux_kontext_h0_dance12_single_action_row.ps1`

Evidence from submitted manifest/log:

- selected source frames one-based: `1,12,23,35,46,57,68,79,90,102,113,124`;
- three internal four-frame `2×2` Kontext chunks;
- prompt ids:
  - `0cb61aec-f6f9-4073-9941-970186ff7d15`;
  - `10bff98b-7453-4064-9e30-95b76dfd38b5`;
  - `65b26095-ccf5-4874-80d0-ca624b9cdb4b`;
- elapsed: `288.49s + 280.52s + 280.34s = 849.35s` (~14m09s);
- 20 steps, guidance2.5, CFG1, Euler/simple, seed0, denoise0.45;
- final local layout `12×1`, `192×192` diagnostic cells.

Verdict:

- final one-action layout: **PASS**;
- adult body/identity preservation: **PASS_CANDIDATE**;
- pose fidelity: **PASS_CANDIDATE**;
- cross-chunk consistency: **PASS_CANDIDATE**;
- automatic alpha: **PASS_CANDIDATE**;
- final high-level deliberate pixel art: **NOT YET PASS**.

The result still reads too much like reduced/filtered raster with residual painterly microtexture/noisy miniature detail rather than authored pixel clusters. The premature small review scale may contribute to that reading and is no longer treated as a production assumption.

Record:

`docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`

Runner52 also does **not** prove final runtime action timing/cycle distillation; its `250–479ms` durations preserve broad source coverage only.

## CURRENT GATE — Runner53 / dedicated pixel-art LoRA probe at larger master scale

Do not raise denoise yet: `0.45` is the current structure-preserving value.

Runner53 tests whether a dedicated style adapter can strengthen pixel-art construction without sacrificing the Runner52 body/pose gains.

Runner:

`tools/structured-2d-character-pipeline/53_run_flux_kontext_h0_dance_chunk2_modern_pixelart_lora_probe.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance_chunk2_modern_pixelart_lora_probe.py`

Controlled model test:

- only Runner52 chunk2 / source frames `46,57,68,79`;
- same Kontext FP8;
- same canonical Exilada reference;
- same 20 steps / guidance2.5 / CFG1 / Euler-simple / seed0 / denoise0.45;
- only model/style change: `UmeAiRT/FLUX.1-dev-LoRA-Modern_Pixel_art`, `ume_modern_pixelart.safetensors`, strength1.0;
- LoRA SHA256 `ed226c149dca6286ae345b6900d807f791a52b1746ed8f524af41efdfda6f0a4`;
- ~344MB, MIT license for the adapter itself;
- underlying Kontext non-commercial license caveat remains.

Packaging/master correction after scale review:

- Runner53 no longer downpacks to `192×192` cells;
- output review/master cells are `384×384`;
- gameplay apparent height remains explicitly `UNLOCKED_PENDING_VIEWPORT_BENCHMARK`;
- this packaging change does not alter Kontext inference conditioning/settings.

This is deliberately one chunk (~one Kontext inference) before spending another full 12-frame pass.

Runner53 PASS requires materially stronger intentional pixel-art construction while preserving mature adult anatomy, exact poses and the locked sword-and-sorcery charge.

## Character-reference generation from text — OPEN MODEL CHOICE

The final interface must support local text-to-reference generation, but the exact model remains open. SDXL-class and FLUX T2I families remain candidates.

## Model-screening order

1. MiniMax H3 Ref2VA — ACTIVE / Base50 locked for motion masters.
2. FLUX.1 Kontext [dev] — ACTIVE renderer family / Runner53 current gate.
3. Wan-Animate-2 — paused, not exhausted.
4. SCAIL-2 — later only if H3 fails a future motion-production contract.

## License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is acceptable; commercial shipping requires appropriate BFL licensing or another renderer with compatible terms.

## Immediate implementation order

1. run Runner53 only after pulling the scale-corrected runner;
2. compare its four frames against Runner52 chunk2 at master/review scale;
3. judge pixel-cluster quality separately from anatomy/pose fidelity;
4. if the style adapter passes, apply it to the full 12-frame action at master scale;
5. if it fails, reject the adapter specifically before changing denoise/precision/model family;
6. once pixel-art renderer quality passes, run comparative `160/180/200px` viewport composition tests rather than assuming a fixed gameplay height;
7. then implement action-specific distillation/timing and build the Gradio authoring UI.

## Cleanup

- keep Base H3 Ref2VA minimal set;
- Turbo4 LoRA may be removed after evidence preservation;
- keep current Kontext model set;
- keep the Modern Pixel Art LoRA only while its hypothesis is active;
- Wan large checkpoints may be removed while W1H/W1L evidence remains;
- SSD comparison evidence remains until explicit abandonment/final verdict.
