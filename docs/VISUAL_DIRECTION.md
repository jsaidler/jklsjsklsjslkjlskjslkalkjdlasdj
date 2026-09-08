# Visual Direction — Living Document

Status date: **2026-09-08**

Status: **FINAL RUNTIME ART = HIGH-QUALITY PIXEL ART / H3 BASE50 = MOTION MASTER / FLUX.1 KONTEXT [DEV] = ACTIVE RENDERER CANDIDATE / RUNNER50 VISUAL FAIL RECORDED / RUNNER51 STRUCTURE-LOCK PREPARED / 1980s SWORD-AND-SORCERY LOCKED**

Canonical project state: `docs/PROJECT_STATE.md`.

Local authoring workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Runner50 visual-failure record: `docs/RUNNER50_KONTEXT_VISUAL_FAIL_2026-09-08.md`.

## Core production constraint

The project must remain producible end-to-end through local tooling without routine bespoke manual art/animation work from the user or a hired art team.

A visual direction is invalid if it can make one attractive frame but cannot be animated, varied, maintained and expanded through the same automatic production system.

## Final runtime visible-art language — LOCKED

Runtime character art is deliberate high-quality pixel art:

- coherent pixel clusters rather than blurred miniature illustration;
- exact pixel-grid rendering;
- strong silhouette and readable large masses;
- controlled palette/material separation;
- enough detail to feel contemporary at gameplay scale;
- final art should exceed the current canonical Exilada reference in pixel construction and consistency.

Simple nearest-neighbor reduction, palette quantization or the old tiny H0 proxy is not the final-art solution.

## Adult identity/body preservation — HARD LOCK

The renderer is allowed to change **rendering language**, not the physical design of an approved character.

For the Exilada and equivalent adult characters:

- mature adult age must remain visually unambiguous;
- adult head-to-body ratio must remain materially consistent;
- torso/limb length, shoulder/hip relationship, bust, pelvis, legs and overall adult sexual dimorphism must not be arbitrarily redesigned;
- do not shorten torso/limbs, enlarge the head, widen/round the face, thicken/soften the anatomy into a juvenile shape or otherwise infantilize the character;
- no cute/chibi/adolescent drift;
- body mass may move dynamically, but the underlying mature physical structure remains the same character across frames.

Runner50 violated this rule by making the Exilada physically shorter/thicker and more juvenile-looking. That result is rejected.

## H3 painterly/raster output — INTERMEDIATE MOTION MASTER

MiniMax H3 Base50 remains the current motion-master quality baseline.

Its strengths should inform the final pixel art:

- physical body mass;
- coherent anatomy through motion;
- rich hair volume and inertia;
- cloth/material response;
- mature dark-fantasy severity;
- complete-character continuity.

H3 output is not the final runtime raster style.

Canonical chain:

`character reference + real action video -> H3 Base50 complete-character motion master -> automatic coherent action-frame extraction -> high-quality pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

## Spritesheet temporal organization — HARD LOCK

A spritesheet is not an arbitrary contact sheet.

For the current `4×N` authoring convention:

- **one row = one temporally coherent animation sequence**;
- frames inside a row read left-to-right in time;
- do not scatter unrelated timestamps across one sheet and call it an animation;
- if a selected action needs more than one row, each row must be an explicitly meaningful sequence/chunk according to the action preset and metadata;
- final packing must preserve exact frame order and timing metadata.

Runner50 violated this by evenly sampling the whole 124-frame H0 and placing unrelated stages of the gesture across a global `4×3` grid.

## Final pixel-art reconstruction — ACTIVE CANDIDATE

**FLUX.1 Kontext [dev] remains the active first local renderer family, but Runner50 did not pass the task contract.**

Runner50 proved:

- local inference works on the current RTX 3060 12GB stack;
- FP8-scaled Kontext can produce a useful pixel-art-like language;
- automatic alpha extraction is viable enough to keep testing.

Runner50 failed:

- adult identity/body-proportion preservation;
- correct spritesheet temporal semantics;
- part of the locked mature art-direction charge.

Therefore the next controlled test is Runner51 rather than a model-family jump.

### Runner51 controlled repair

Runner51 changes the task formulation while keeping the same model/runtime:

- each final row is one short coherent temporal sequence;
- one high-motion 16-frame window is selected inside each third of the existing H0;
- four ordered frames are taken from each window;
- each four-frame row is reconstructed separately as a `2×2` `1024×1024` input so each character is much larger during the edit;
- Kontext denoise is reduced from `1.0` to `0.45` to preserve source structure;
- the prompt explicitly forbids infantilization/body redesign;
- the mature 1980s sword-and-sorcery inspiration lineage is a hard requirement.

Runner51:

`tools/structured-2d-character-pipeline/51_run_flux_kontext_h0_dance3x4_temporal_rows_structure_lock.ps1`

## 1980s sword-and-sorcery charge — LOCKED

Canonical inspiration lineage remains:

- **Heavy Metal**;
- **Conan**;
- **Red Sonja**;
- **Frank Frazetta**;
- **Julie Bell**.

Interpretation:

- adult sensuality, heroic anatomy, danger, grime, erotic charge and pulp-fantasy excess may coexist;
- mature body language must not be sanitized or infantilized by default;
- materials should feel tactile, physical and illustrated even after pixel-art reconstruction;
- the 1980s influence is tonal/art-directional, not VHS/CRT gimmicks;
- the objective is the imagery of that period made playable with contemporary systemic and animation quality.

This inspiration set remains active in every renderer prompt and review gate. A technically clean sprite that loses this charge is not a visual PASS.

## Exilada appearance reference

Canonical Exilada identity/state reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It remains the complete initial-state source for current work.

The current reference is a usable pixel-art source, but it is not the final ceiling of runtime-art quality.

## Exilada initial-state erotic/body direction — LOCKED IN PRINCIPLE

The Exilada does not need to be visually desexualized to be treated seriously.

Her initial deprivation/captivity state may include:

- much more severely torn cloth;
- irregular holes and edge loss exposing additional skin;
- partial breast exposure where consistent with torn-garment state;
- asymmetrical coverage rather than a neat fantasy bandeau;
- simultaneous vulnerability, danger, sensuality and physical presence.

Exact tear geometry and exposure remain subject to visual-state approval rather than temporary prompt wording.

## Character scale variation — LOCKED DIRECTION

The same visual system must work for very different creature sizes.

`relative_scale=1.0` is the baseline adult-human/Exilada scale, approximately `128px` visible height in the canonical gameplay composition.

Relative scale is world/render metadata, not arbitrary image stretching. Larger monsters may require:

- larger visible runtime height;
- larger cells/atlases;
- different source-resolution policy to preserve detail;
- different scene-scale QA.

Exact min/max scale is not yet locked.

## Systemic visual rule

Whenever feasible, visually relevant state follows simulation/history rather than arbitrary decoration.

Examples: scars, equipment wear, blood, dirt, wetness, burns, frost, fatigue, hunger, injury posture and clothing damage.

Procedural variation must be causal and constrained rather than random noise.

## Character visual principles at gameplay scale

At baseline protagonist scale:

- hair mass, body proportions, clothing asymmetry and equipment shapes remain readable;
- facial microdetail cannot be the only identity carrier;
- clothing/equipment may evolve without erasing body/hair/posture identity;
- anatomy remains adult and materially grounded;
- exposed skin, partial nudity and full adult nudity are valid states;
- final pixel clusters remain deliberate and stable across animation frames;
- motion-local impression is allowed, destructive blur/ghosting is not.

## Runtime / production architecture

Visible runtime characters are complete precomposed frames. There is no visible runtime body/hair/clothing/equipment layer assembly.

Routine manual rigging, keyframing, mask repair, per-frame repainting/retouching and hand compositing remain disallowed.

## Gameplay projection — LOCKED BASELINE

The game remains an elevated 2D belt-scroller / false-3D action presentation:

- native raster `640×360`;
- camera pitch `26°`;
- Exilada baseline about `128px` tall at `relative_scale=1.0`;
- first locomotion family screen-left, mostly lateral/slight 3/4;
- current facing baseline `72°`;
- strong lateral travel plus continuous walkable depth;
- combat readability over geometric purity.

## H3 quality configuration — LOCKED

The preferred H3 motion-master quality configuration remains the original H0 Base50 settings:

- `448×800`;
- `124f@24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- no Turbo LoRA.

Do not trade this quality away for speed until a faster path is proven visually equivalent.

## Current visual gate

1. Runner50 is closed as **MODEL/TASK FAIL** for adult body preservation and spritesheet semantics;
2. run Runner51 on the same H0 motion master;
3. first inspect the automatically selected source temporal rows;
4. inspect each row GIF independently for temporal coherence;
5. inspect the final sheet for mature body preservation, pose fidelity, pixel-art quality and 1980s sword-and-sorcery charge;
6. only after renderer behavior passes, build the Gradio orchestration UI;
7. then expand to new actions and creature-scale cases.

## Current decision

**LOCKED:** final runtime character graphics are deliberate high-quality pixel art.

**LOCKED:** H3 Base50 painterly/raster output is a motion-master intermediate.

**LOCKED:** one temporally coherent animation sequence per spritesheet row.

**LOCKED:** approved adult character body/age/proportions may not be infantilized or redesigned by the renderer.

**ACTIVE RENDERER CANDIDATE:** FLUX.1 Kontext [dev], now under Runner51 structure-lock validation.

**LOCKED:** Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell and the mature 1980s sword-and-sorcery charge remain active.

**LOCKED:** mature erotic charge, nudity and partial nudity remain legitimate.

**LOCKED:** runtime remains complete-character 2D sprite playback and production must scale without routine manual art labor.
