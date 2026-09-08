# Visual Direction — Living Document

Status date: **2026-09-08**

Status: **FINAL RUNTIME ART = HIGH-QUALITY PIXEL ART / H3 BASE50 = MOTION MASTER / KONTEXT STRUCTURE PASS / PIXEL-ART QUALITY STILL OPEN / RUNNER53 STYLE-ADAPTER GATE / 1980s SWORD-AND-SORCERY LOCKED**

Canonical project state: `docs/PROJECT_STATE.md`.

Local workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Runner52 result: `docs/RUNNER52_KONTEXT_STRUCTURE_PASS_PIXELART_QUALITY_PARTIAL_2026-09-08.md`.

## Core production constraint

The project must remain producible end-to-end through local tooling without routine bespoke manual art/animation work from the user or a hired art team.

A visual direction is invalid if it can make one attractive frame but cannot be animated, varied, maintained and expanded through the same automatic production system.

## Final runtime visible-art language — LOCKED

Runtime character art is deliberate high-quality pixel art:

- coherent intentional pixel clusters rather than blurred miniature illustration;
- exact pixel-grid rendering;
- strong silhouette and readable large masses;
- controlled palette/material separation;
- enough detail to feel contemporary at gameplay scale;
- final art should exceed the current canonical Exilada reference in pixel construction and consistency.

Simple nearest-neighbor reduction, palette quantization or the old tiny H0 proxy is not the final-art solution.

## Adult identity/body preservation — HARD LOCK

Renderer may change **rendering language**, not approved physical design.

For the Exilada and equivalent adults:

- mature adult age remains unambiguous;
- adult head-to-body ratio remains materially consistent;
- torso/limb length, shoulder/hip relationship, bust, pelvis, legs and adult sexual dimorphism are preserved;
- no shortened/thickened juvenile reinterpretation;
- no enlarged head, rounded childlike face, cute/chibi/adolescent drift.

Runner50 violated this. Runner52 materially corrected it at denoise0.45.

## H3 painterly/raster output — INTERMEDIATE MOTION MASTER

MiniMax H3 Base50 remains the motion-master quality baseline.

Its useful qualities should survive downstream conversion:

- physical body mass;
- coherent anatomy through motion;
- rich hair volume/inertia;
- cloth/material response;
- mature dark-fantasy severity;
- complete-character continuity.

Canonical chain:

`character reference + real action video -> H3 Base50 motion master -> automatic action-frame distillation -> high-quality pixel-art reconstruction -> one horizontal action row + transparent frames/metadata -> runtime`

## Spritesheet organization — HARD LOCK

**One action = one spritesheet row.**

Frames read left-to-right in time. Internal high-resolution renderer tiles/chunks never define final semantic rows.

Current H0 `dance_or_gesture` proof:

- 12 frames;
- final `12×1` row;
- `192×192` cells locally.

A later combined character sheet may stack different actions vertically.

## 1980s sword-and-sorcery charge — HARD LOCK

Canonical inspiration lineage:

- **Heavy Metal**;
- **Conan**;
- **Red Sonja**;
- **Frank Frazetta**;
- **Julie Bell**.

Interpretation:

- adult sensuality, heroic anatomy, danger, grime, erotic charge and pulp-fantasy excess may coexist;
- mature body language must not be sanitized or infantilized;
- materials should feel tactile, physical and illustrated even after pixel-art reconstruction;
- the 1980s influence is tonal/art-directional, not VHS/CRT gimmicks.

A technically clean sprite that loses this charge is not a visual PASS.

## Exilada appearance reference

Canonical identity/state reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It remains the initial-state authority. The current reference is usable pixel art, but it is not the final ceiling of runtime-art quality.

## Exilada body/clothing direction — LOCKED IN PRINCIPLE

The Exilada does not need to be visually desexualized to be treated seriously.

Her captivity/deprivation state may include:

- more severely torn cloth;
- irregular holes/edge loss;
- more exposed skin and possible partial breast exposure where consistent with damage;
- asymmetrical coverage rather than a neat fantasy costume;
- simultaneous vulnerability, danger, sensuality and physical presence.

Exact tear geometry/exposure remains subject to visual approval.

## Character scale variation — LOCKED DIRECTION

`relative_scale=1.0` = adult-human/Exilada baseline, about `128px` visible height in canonical gameplay composition.

Relative scale is world/render metadata, not arbitrary stretching. Larger monsters may require larger visible runtime height, cells/atlases and source-resolution policy.

## Gameplay-scale principles

At baseline protagonist scale:

- hair mass, body proportions, clothing asymmetry and equipment shapes remain readable;
- facial microdetail cannot be the only identity carrier;
- anatomy remains adult and materially grounded;
- exposed skin, partial nudity and full adult nudity are valid states;
- final pixel clusters remain deliberate and stable across animation frames;
- motion-local impression may exist, destructive blur/ghosting may not.

## Runtime / production architecture

Visible runtime characters are complete precomposed frames. There is no visible runtime body/hair/clothing/equipment layer assembly.

Routine manual rigging, keyframing, mask repair, per-frame repainting/retouching and hand compositing remain disallowed.

## Gameplay projection — LOCKED BASELINE

- native raster `640×360`;
- camera pitch `26°`;
- Exilada baseline about `128px` tall at `relative_scale=1.0`;
- first locomotion family screen-left, mostly lateral/slight 3/4;
- current facing baseline `72°`;
- combat readability over geometric purity.

## H3 quality configuration — LOCKED

- `448×800`;
- `124f@24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- no Turbo LoRA.

Do not trade this quality away for speed until a faster path is proven visually equivalent.

## Runner52 visual result — PARTIAL PASS

Runner52 materially fixed structure/layout:

- one action correctly packs into one horizontal row;
- adult Exilada proportions materially survive;
- source poses remain recognizable;
- three independently rendered chunks remain acceptably compatible;
- automatic alpha is usable enough to continue.

But final art is **not yet high-level pixel art**. It still reads too much like reduced/filtered raster with residual painterly microtexture/noisy miniature detail rather than confident authored pixel clusters and controlled palette/material grouping.

Therefore do not build the final UI around Runner52 as though renderer quality were solved.

## Current visual gate — Runner53

Runner53 keeps all Runner52 structure-preserving settings and changes only the style signal:

- source frames `46,57,68,79`;
- Kontext FP8;
- 20 steps;
- guidance2.5;
- CFG1;
- Euler/simple;
- seed0;
- denoise0.45;
- canonical Exilada reference;
- add `ume_modern_pixelart.safetensors` strength1.0.

Runner:

`tools/structured-2d-character-pipeline/53_run_flux_kontext_h0_dance_chunk2_modern_pixelart_lora_probe.ps1`

PASS requires a visible increase in authored pixel-cluster quality **without** losing adult anatomy, exact source pose, severe identity or sword-and-sorcery charge.

If the adapter fails, reject that adapter specifically before increasing denoise, switching precision or changing renderer family.

## Current decisions

**LOCKED:** final runtime character graphics are deliberate high-quality pixel art.

**LOCKED:** H3 Base50 painterly/raster output is an intermediate motion master.

**LOCKED:** one action = one horizontal spritesheet row.

**LOCKED:** internal renderer chunks never define semantic action rows.

**LOCKED:** approved adult body/age/proportions may not be infantilized or redesigned.

**ACTIVE RENDERER FAMILY:** FLUX.1 Kontext [dev], structure-preserving path proven enough to continue; style quality still under validation.

**CURRENT STYLE GATE:** Runner53 Modern Pixel Art LoRA probe.

**LOCKED:** Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell remain active.

**LOCKED:** mature erotic charge, nudity and partial nudity remain legitimate.

**LOCKED:** runtime remains complete-character 2D sprite playback and production must scale without routine manual art labor.
