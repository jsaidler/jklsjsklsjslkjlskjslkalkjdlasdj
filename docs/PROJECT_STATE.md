# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/EXILADA_MASTER_REVISION_LOCAL_EDITOR_2026-09-08.md`
3. `docs/CHARACTERS.md`
4. `docs/VISUAL_DIRECTION.md`
5. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
6. `docs/GAMEPLAY_CHARACTER_SCALE_RECALIBRATION_2026-09-08.md`
7. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
8. `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`
9. `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`
10. `docs/ANIMATION_PIPELINE.md`
11. `docs/CHARACTER_PRODUCTION_PIPELINE.md`

Historical preflight/model-screening documents remain evidence but do not override the current gate.

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs and this file before completion is reported. Changed decisions replace stale locks rather than coexisting ambiguously.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext workspace: `Z:\AI\FluxKontext`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical and must not be used.

## Game/runtime presentation — LOCKED EXCEPT FINAL APPARENT CHARACTER SCALE

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- `relative_scale=1.0` means baseline adult-human/Exilada world scale, not a sprite pixel height;
- first locomotion family screen-left / mostly lateral-three-quarter;
- facing baseline `72°`;
- runtime consumes complete precomposed character sprites only;
- no visible runtime body/hair/clothing/equipment layer assembly.

## Sprite-resolution correction — HARD LOCK

The former `128px` Exilada asset baseline is retired.

There is no new mandatory `160/180/200px`, `192px` or `384px` production sprite resolution. Those values are historical diagnostics or optional viewport-composition comparisons only.

Production assets must preserve the useful resolution of the approved video/frame/render chain. Gameplay apparent size is controlled separately by runtime/world/camera scaling. Do not destructively shrink source/master sprites merely to match a viewport occupancy target.

## Final visible-art target — LOCKED

Runtime character graphics remain deliberate high-quality pixel art, but the character design itself must be correct before pixel-art reconstruction is optimized.

H3 painterly/raster video is an intermediate **motion master**, not final runtime art.

Canonical production chain after character approval:

`approved character master -> real action driver -> H3 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> high-quality pixel-art reconstruction at useful source resolution -> one horizontal row for that action + frames/metadata -> runtime scaling/playback`

Simple nearest-neighbor reduction or arbitrary small-cell packaging is not the final-art solution.

## Spritesheet layout contract — HARD LOCK

**One action = one spritesheet row.**

- frames read left-to-right in time;
- an action may contain a variable number of frames;
- internal renderer tiles/chunks never become semantic final rows;
- per-frame durations/events live in metadata;
- complete character remains visible in each frame;
- final asset resolution follows the approved production chain rather than a fixed legacy cell size.

## Exilada core identity — LOCKED

The protagonist is an unambiguously adult woman, approximately 162 cm tall, from the Ilhas do Sul.

Identity anchors:

- mature severe adult face and presence;
- lean, functional, resilient natural adult feminine anatomy;
- olive-to-brown skin;
- very long, heavy, voluminous, messy black hair as a primary silhouette anchor;
- alert, contained violence and survival rather than clean heroic presentation;
- weapon is not part of permanent identity.

The approved nude anatomy source remains legitimate offline authoring evidence. Adult partial or complete nudity is a normal supported character/world state.

## Exilada initial-state design — REOPENED FOR MASTER REVISION

The existing `assets/source/characters/exilada/reference/exilada_master.png` remains useful identity/anatomy evidence, but it is **no longer accepted as final visual-design authority**.

Reason:

- current clothing still reads too intact/generic;
- previously approved severe tearing and greater exposure are not yet visually resolved;
- the character still reads too generically relative to the locked sword-and-sorcery lineage.

The initial captivity state must be allowed to explore:

- severely torn asymmetrical cloth;
- irregular holes, edge loss, displaced remnants and incomplete coverage;
- substantially more torso exposure;
- partial breast exposure where materially caused by torn cloth;
- near-nudity or full nudity where deliberately appropriate to the state;
- equally degraded hip cloth;
- dirt, sweat, abrasions, scars/wounds and captivity evidence as causal material state;
- no mandatory censor garment;
- no neat fantasy bikini/bandeau/corset/MMO costume logic.

Exact tear geometry/exposure is open until visual approval.

## 1980s sword-and-sorcery direction — HARD LOCK / MASTER MUST NOW PROVE IT

Active inspiration lineage:

- Heavy Metal;
- Conan;
- Red Sonja;
- Frank Frazetta;
- Julie Bell.

The revised master must visibly carry adult physical weight, danger, grime, sensuality/erotic charge, tactile skin/hair/cloth/metal and pulp-fantasy excess. Merely mentioning these references in a prompt is insufficient.

Reject generic modern fantasy heroine, cosplay-clean/MMO polish, cute/chibi drift and sanitized adult anatomy.

## CURRENT GATE — Runner54 local Exilada master editor

**Runner53 is paused. Do not continue downstream pixel-art style validation against the stale master.**

Current launcher:

`tools/structured-2d-character-pipeline/54_run_exilada_master_editor.ps1`

Application:

`tools/flux-kontext-spike/exilada_master_editor.py`

Detailed record:

`docs/EXILADA_MASTER_REVISION_LOCAL_EDITOR_2026-09-08.md`

Purpose:

- work on character visual details locally rather than through the chat image-generation surface;
- edit clothing damage/exposure, body/identity locks, material state and pictorial direction interactively;
- optionally use the approved nude anatomy turnaround and two arbitrary visual-direction references;
- preserve native useful Kontext output with no forced 128/192/384px reduction;
- version every candidate with prompt/settings/hashes;
- never overwrite `exilada_master.png` automatically;
- only explicit local **APPROVE** promotes a candidate and backs up the previous master.

The master-revision gate passes only on explicit user approval of a candidate.

## Motion model — MiniMax H3 Ref2VA ACTIVE / BASE50 QUALITY BASELINE

Current proven motion-master configuration:

- MiniMax H3 Base Ref2VA;
- `448×800` video generation;
- `124 frames @24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed `0`;
- no Turbo LoRA;
- no FL2VA;
- no style embedding.

Current H0 evidence:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

H0 is dance/gesture-like and remains valid motion/model evidence, but a materially revised Exilada master may require H3 revalidation before production animation proceeds.

## FLUX.1 Kontext local tooling — ACTIVE

Workspace: `Z:\AI\FluxKontext`

Installed/proven set:

- ComfyUI v0.34.0 on port `8191`;
- `flux1-dev-kontext_fp8_scaled.safetensors`;
- `clip_l.safetensors`;
- `t5xxl_fp16.safetensors`;
- `ae.safetensors`.

Reuse this installation. Do not redownload it for each test.

### Renderer history

- Runner50: inference worked but task/denoise caused body drift and wrong formulation — rejected.
- Runner51: rejected pre-inference because a 4×3 layout incorrectly split one action into semantic rows.
- Runner52: one-action/one-row structure and adult-body preservation passed provisionally; high-level pixel-art construction did not yet pass.
- Runner53: dedicated Modern Pixel Art LoRA probe prepared but now **PAUSED** until the Exilada master is revised and approved.

Runner52's `192×192` packaging and Runner53's planned `384×384` review cells are not production sprite-resolution mandates.

## Runtime character representation — LOCKED

The game does not assemble body/hair/clothing/equipment layers visibly at runtime.

Runtime representation:

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

Every exported frame already contains any body/jiggle, hair, cloth, bindings, chains/accessories and final occlusion for that state.

Variation is solved offline.

## Current immediate implementation order

1. pull the current repository state;
2. run Runner54;
3. revise the Exilada locally, including the already-approved severe tear/exposure direction and stronger sword-and-sorcery pictorial charge;
4. iterate candidates without promoting them automatically;
5. explicitly approve one new canonical master only when identity, anatomy, exposure/material logic and art direction pass;
6. if the visual revision is material, revalidate/regenerate H3 motion using the new master;
7. resume downstream pixel-art reconstruction/style-adapter validation only after that;
8. derive sprites at the useful production resolution of the approved video/frame chain and leave gameplay apparent scale to runtime.

## License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Current use is technical/art-direction R&D. Commercial shipping requires appropriate BFL commercial licensing or a renderer with compatible terms.

## Cleanup

- keep Base H3 Ref2VA minimal set;
- keep current Kontext model set;
- keep the Modern Pixel Art LoRA while the downstream style hypothesis remains open;
- Wan large checkpoints may remain removed/paused while evidence is retained;
- SSD comparison evidence remains until explicit abandonment/final verdict.
