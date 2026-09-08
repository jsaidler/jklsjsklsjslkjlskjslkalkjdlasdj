# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
3. `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`
4. `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`
5. `docs/VISUAL_DIRECTION.md`
6. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
7. `docs/ANIMATION_PIPELINE.md`
8. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
9. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
10. `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`
11. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
12. `docs/CHARACTERS.md`
13. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`
14. historical Runner50 preflight incidents:
   - `docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`
   - `docs/RUNNER50_CLIP_L_SHA256_PREFLIGHT_FAIL_2026-09-08.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active H3 workspace: `Z:\AI\MiniMaxH3`
- active Kontext renderer workspace: `Z:\AI\FluxKontext`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` stale/historical.

## Game/runtime presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- Exilada baseline about `128px` tall at `relative_scale=1.0`;
- first locomotion family screen-left / mostly lateral-three-quarter;
- facing baseline `72°`;
- runtime consumes complete precomposed character sprites only;
- no visible runtime body/hair/clothing/equipment layer assembly.

## Final visible-art target — LOCKED

Runtime character graphics are deliberate high-quality pixel art.

H3/Wan painterly/raster video is an intermediate **motion master**, not final runtime art.

Canonical production chain:

`character reference -> real action driver -> H3 complete-character motion master -> automatic coherent action-sequence extraction -> automatic alpha/pivot/alignment -> high-quality pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

Simple downscale/nearest-neighbor/palette reduction is not accepted as the final renderer.

## 1980s sword-and-sorcery direction — HARD LOCK

Active inspiration lineage:

- Heavy Metal;
- Conan;
- Red Sonja;
- Frank Frazetta;
- Julie Bell.

Final art must preserve mature adult anatomy, danger, grime, sensuality, tactile materials and pulp-fantasy physicality. The renderer may not sanitize or infantilize approved adult characters.

## Adult body/identity preservation — HARD LOCK

For approved adult characters, including the Exilada:

- preserve mature adult age;
- preserve adult head-to-body ratio;
- preserve torso/limb length and major body proportions;
- preserve adult bust/hips/pelvis/legs relationship;
- do not enlarge the head, shorten/thicken the body, round/widen the face into a juvenile read, make the character cute/chibi/adolescent-looking or otherwise infantilize the design;
- renderer changes rendering language, not physical identity.

## Spritesheet row semantics — HARD LOCK

A spritesheet is not an arbitrary contact sheet.

Current authoring rule:

- **one row = one temporally coherent animation sequence**;
- frames read left-to-right in time;
- unrelated timestamps may not be scattered across a row;
- if one action uses several rows, their temporal/semantic relationship must be explicit in metadata.

## All-local authoring target — LOCKED

One local interface must eventually support:

1. existing character reference image **or** local text-to-reference generation;
2. relative world scale for humans/creatures/monsters/bosses;
3. real action driver video;
4. action preset such as idle/walk/run/jump/punch/kick/weapon attack/defense/hit/death/taunt/dance/custom;
5. local H3 motion generation;
6. local sequence extraction;
7. local pixel-art reconstruction;
8. local sheet/preview/atlas/JSON/manifest output.

Canonical specification:

`docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`

Gradio remains the V1 UI choice **after renderer behavior passes**.

## Relative scale — CURRENT CONTRACT

`relative_scale=1.0` = baseline adult-human/Exilada size, about `128px` visible height in canonical gameplay composition.

Scale is explicit world/render metadata, not non-uniform image stretching. It influences sprite occupancy, cell/atlas dimensions and source-resolution policy.

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

Visual verdict: **PASS_CANDIDATE / preferred motion-master quality baseline.**

Turbo4 / Runner49 was visually rejected. Base50 remains production default.

## Current H0 action

The existing H0 is a **dance/gesture-like action**, not a walk.

It remains the renderer proof source. Do not generate a new walk merely to debug downstream conversion.

## FLUX.1 Kontext local renderer — ACTIVE FAMILY

Workspace:

`Z:\AI\FluxKontext`

Pinned renderer runtime:

- ComfyUI v0.34.0;
- port `8191`;
- native/core Kontext nodes;
- no custom-node requirement for current tests.

Installed/verified model payload:

- `flux1-dev-kontext_fp8_scaled.safetensors` ~11.9GB, SHA256 `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`;
- `clip_l.safetensors` ~246MB, SHA256 `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`;
- `t5xxl_fp16.safetensors` ~9.79GB, SHA256 `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`;
- `ae.safetensors` ~335MB, SHA256 `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`.

Local installation/inference is proven and should be reused.

## Runner50 — INFERENCE COMPLETE / MODEL-TASK FAIL

Runner50 completed technically:

- prompt id `56576cf4-165a-4ad2-8a96-ec28bf75da1e`;
- elapsed `296.63s`;
- 20 steps;
- guidance2.5;
- CFG1.0;
- Euler/simple;
- seed0;
- denoise1.0;
- final review sheet `768×576` with `192×192` cells.

Useful evidence:

- Kontext local inference works;
- pixel-art-like rendering is promising;
- automatic alpha remains viable enough to continue testing.

Visual failures:

1. adult Exilada proportions drifted shorter/thicker and more juvenile/infantilized;
2. evenly spaced 12-frame selection across the whole H0 created a contact sheet, not correct animation rows;
3. mature 1980s sword-and-sorcery charge weakened;
4. denoise1.0 + 12 small characters in one square gave excessive redraw freedom.

Classification: **MODEL/TASK FAIL**, not infrastructure/integration fail.

Record:

`docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`

## CURRENT GATE — Runner51 / temporal rows + structure lock

Runner:

`tools/structured-2d-character-pipeline/51_run_flux_kontext_h0_dance3x4_temporal_rows_structure_lock.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance3x4_temporal_rows_structure_lock.py`

Runner51 keeps the same model/runtime and changes only the task formulation.

### Temporal selection

- divide H0 timeline into three thirds;
- inside each third find the highest-motion 16-frame window using simple grayscale frame-difference energy;
- choose four ordered frames at offsets `0,5,10,15`;
- each four-frame sequence becomes one final sheet row.

This enforces **one animation per row** for the proof.

### Renderer formulation

Each row is rendered separately:

- input `1024×1024`;
- four ordered frames arranged `2×2`;
- much larger character representation than Runner50;
- canonical Exilada as second identity/art-direction reference;
- same FP8-scaled Kontext model;
- 20 steps;
- guidance2.5;
- CFG1.0;
- Euler/simple;
- seed0;
- **denoise0.45**.

Hard prompt locks:

- preserve mature adult body proportions;
- no infantilization/cute/chibi/adolescent drift;
- preserve pose/silhouette/hair/cloth/restraints;
- preserve Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell mature sword-and-sorcery charge;
- change rendering language only.

### Expected Runner51 outputs

Under `Z:\AI\FluxKontext`:

- `h0_dance3x4_source_temporal_rows.png`
- `h0_dance3x4_temporal_selection_manifest.json`
- row-specific `2×2` inputs and Kontext full outputs;
- `h0_dance_row01_preview.gif`
- `h0_dance_row02_preview.gif`
- `h0_dance_row03_preview.gif`
- `h0_dance3x4_pixelart_sheet_opaque.png`
- `h0_dance3x4_pixelart_sheet_rgba.png`
- `h0_dance3x4_kontext_manifest.json`
- `h0_dance3x4_kontext_executor.log`.

### Runner51 pass boundary

PASS requires:

- each row = coherent temporal four-frame animation;
- adult Exilada age/body proportions materially preserved;
- no infantilization;
- H0 poses/silhouettes recognizably preserved;
- deliberate high-quality pixel art;
- locked 1980s sword-and-sorcery charge visible;
- hair/cloth/restraints readable;
- usable automatic alpha.

If Runner51 still changes body structure at denoise0.45, classify that exact failure before changing model precision/family.

## Character-reference generation from text — OPEN MODEL CHOICE

The final interface must support local text-to-reference generation, but the exact model remains open. SDXL-class and FLUX T2I families remain candidates.

## Model-screening order

1. MiniMax H3 Ref2VA — ACTIVE / Base50 locked for motion masters.
2. FLUX.1 Kontext [dev] — ACTIVE renderer family / Runner51 current gate.
3. Wan-Animate-2 — paused, not exhausted.
4. SCAIL-2 — later only if H3 fails future motion-production contract.

## License caveat

FLUX.1 Kontext [dev] open weights are non-commercial. Technical validation is acceptable; commercial shipping requires appropriate BFL licensing or another renderer with compatible terms.

## Immediate implementation order

1. run Runner51;
2. inspect source temporal rows first;
3. inspect each row GIF;
4. inspect opaque final sheet for body maturity/proportions, pose fidelity, pixel-art quality and art direction;
5. inspect RGBA/alpha;
6. if renderer passes, build Gradio orchestration UI;
7. then implement action-specific cycle detection, text-reference generation and creature-scale cases;
8. do not spend another Base50 H3 hour solely to debug the renderer.

## Cleanup

- keep Base H3 Ref2VA minimal set;
- Turbo4 LoRA may be removed after preserving evidence;
- keep current Kontext model set; no new precision/model variant before Runner51 evidence;
- Wan large checkpoints may be removed while W1H/W1L evidence remains;
- SSD comparison evidence remains until explicit abandonment/final verdict.
