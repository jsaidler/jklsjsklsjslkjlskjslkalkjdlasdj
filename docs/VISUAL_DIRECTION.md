# Visual Direction — Living Document

Status date: **2026-09-08**

Status: **FINAL RUNTIME ART = HIGH-QUALITY PIXEL ART / H3 BASE50 = MOTION MASTER / FLUX.1 KONTEXT [DEV] = PREFERRED FIRST PIXEL-ART RECONSTRUCTION CANDIDATE / 1980s SWORD-AND-SORCERY LOCKED**

Canonical project state: `docs/PROJECT_STATE.md`.

Local authoring workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Core production constraint

The project must remain producible end-to-end through local tooling without routine bespoke manual art/animation work from the user or a hired art team.

A visual direction is invalid if it can make one attractive frame but cannot be animated, varied, maintained and expanded through the same automatic production system.

## Final runtime visible-art language — LOCKED

Runtime character art is deliberate high-quality pixel art:

- coherent pixel clusters rather than blurred miniature illustration;
- exact pixel-grid rendering;
- strong silhouette and readable large masses;
- controlled palette/material separation;
- enough detail to feel contemporary at the target gameplay scale;
- no dependence on facial microdetail as the sole identity carrier;
- final art should exceed the current canonical Exilada reference in pixel construction and consistency.

Simple nearest-neighbor reduction, palette quantization or the old tiny H0 proxy is not the final-art solution.

## H3 painterly/raster output — INTERMEDIATE MOTION MASTER

MiniMax H3 Base50 has been visually approved as the current motion-master quality baseline.

Its strengths should inform the final pixel art:

- physical body mass;
- coherent anatomy through motion;
- rich hair volume and inertia;
- cloth/material response;
- mature dark-fantasy severity;
- useful localized motion impression;
- complete-character continuity.

But H3 output is not the final runtime raster style.

Canonical chain:

`character reference + real action video -> H3 Base50 complete-character motion master -> automatic action-frame extraction/alignment -> high-quality pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

## Final pixel-art reconstruction — CURRENT PREFERRED CANDIDATE

**FLUX.1 Kontext [dev] is the preferred first local renderer to validate for this stage.**

This choice is based on the actual task boundary: the system already has pose/motion frames and needs image editing/style transformation while preserving identity, silhouette and attachment relationships.

Preferred validation method:

- give the renderer the canonical character reference;
- give it the selected action frames as one shared-context strip/contact sheet when practical;
- request high-quality deliberate pixel art while preserving frame order, pose and silhouette;
- split the reconstructed set back into cells;
- apply deterministic pixel-grid/palette QA afterward.

Processing every frame independently with no shared context is not the preferred first strategy because temporal design/palette consistency matters.

Kontext is **not yet proven** in this project; it is the next renderer gate.

### License caveat

The open-weight FLUX.1 Kontext [dev] release is non-commercial. It may be used for local technical validation, but commercial game shipping requires appropriate commercial licensing from Black Forest Labs or a renderer with compatible commercial terms.

SDXL/img2img remains a fallback candidate if Kontext fails quality, hardware or licensing requirements.

## 1980s sword-and-sorcery charge — LOCKED

Canonical inspiration lineage remains:

- **Heavy Metal**;
- **Conan**;
- **Red Sonja**;
- **Frank Frazetta**;
- **Julie Bell**.

Interpretation:

- adult sensuality, heroic anatomy, danger, grime, erotic charge and pulp-fantasy excess may coexist;
- mature body language should not be sanitized by default;
- materials should feel tactile, physical and illustrated even after pixel-art reconstruction;
- the 1980s influence is tonal/art-directional, not VHS/CRT gimmicks;
- the objective is the imagery of that period made playable with contemporary systemic and animation quality.

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

## Character scale variation — UPDATED

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
- first locomotion family screen-left, mostly lateral/slight3/4;
- current facing baseline `72°`;
- strong lateral travel plus continuous walkable depth;
- combat readability over geometric purity.

## H3 quality configuration — RESTORED

The official Turbo4 / 4-step experiment was visually rejected by the user.

The preferred H3 motion-master quality configuration is restored to the original H0 Base50 settings:

- `448×800`;
- `124f@24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- no Turbo LoRA.

Do not trade this quality away for speed until a faster path is proven visually equivalent.

## Current visual gates

1. install/validate FLUX.1 Kontext [dev] locally in a separate workspace;
2. use the existing H0 dance/gesture motion master — not a new walk — to test the entire downstream render path without another H3 wait;
3. distill a sensible action-frame set;
4. reconstruct that set as coherent high-quality pixel art;
5. pack the first genuinely final-style spritesheet;
6. validate at actual gameplay scale and against backgrounds;
7. then expand to new actions and creature-scale cases.

## Superseded decisions

- painterly H3/Wan video as final runtime art — superseded;
- tiny whole-frame proxy as production asset — closed;
- Turbo4 as production-quality H3 default — rejected;
- mandatory pixel-preservation through the video model itself — unnecessary; final pixel reconstruction is downstream.

## Current decision

**LOCKED:** final runtime character graphics are deliberate high-quality pixel art.

**LOCKED:** H3 Base50 painterly/raster output is a motion-master intermediate.

**CURRENT PREFERRED RENDERER CANDIDATE:** FLUX.1 Kontext [dev], pending local quality/hardware/license validation.

**LOCKED:** Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell and the 1980s sword-and-sorcery charge remain active.

**LOCKED:** mature erotic charge, nudity and partial nudity remain legitimate.

**LOCKED:** runtime remains complete-character 2D sprite playback and production must scale without routine manual art labor.
