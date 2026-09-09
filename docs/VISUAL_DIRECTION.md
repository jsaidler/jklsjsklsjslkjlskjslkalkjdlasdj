# Visual Direction — Living Document

Status date: **2026-09-08**

Status: **FINAL RUNTIME ART = HIGH-QUALITY PIXEL ART / H3 = MOTION MASTER / EXILADA MASTER REOPENED / RUNNER54 LOCAL CHARACTER-DESIGN GATE / 128PX ASSET BASELINE RETIRED / 1980s SWORD-AND-SORCERY LOCKED**

Canonical project state: `docs/PROJECT_STATE.md`.

Active character-design gate: `docs/EXILADA_MASTER_REVISION_LOCAL_EDITOR_2026-09-08.md`.

Local workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Core production constraint

The project must remain producible end-to-end through local tooling without routine bespoke manual art/animation labor from the user or a hired art team.

A visual direction is invalid if it can make one attractive frame but cannot be animated, varied, maintained and expanded through the same automatic production system.

## Final runtime visible-art language — LOCKED

Runtime character art remains deliberate high-quality pixel art:

- coherent intentional pixel clusters rather than blurred miniature illustration;
- exact pixel-grid rendering;
- strong silhouette and readable large masses;
- controlled palette/material separation;
- enough detail to feel contemporary at gameplay scale;
- final art should exceed the current Exilada reference in pixel construction and consistency.

The pixel-art renderer is a downstream stage. It must not be optimized around a character design that is still visually unresolved.

## Exilada visual master — REOPENED

Current file:

`assets/source/characters/exilada/reference/exilada_master.png`

It remains useful for identity/anatomy continuity but is no longer final visual-design authority.

Two failures must be corrected before more animation/style work:

1. initial captivity cloth is still too intact/generic relative to the approved severe-damage/exposure direction;
2. the image still reads too much like generic contemporary dark fantasy rather than unmistakably carrying the locked sword-and-sorcery lineage.

The master-revision gate passes only when the user explicitly approves a local candidate.

## Adult identity/body preservation — HARD LOCK

Renderer/editor may change rendering language, clothing damage and intentionally open design details, but must not accidentally redesign approved physical identity.

For the Exilada and equivalent adults:

- mature adult age remains unambiguous;
- adult head-to-body ratio remains materially consistent;
- torso/limb length, shoulder/hip relationship, bust, pelvis, legs and adult sexual dimorphism are preserved unless a deliberate character-design change is explicitly chosen;
- no shortened/thickened juvenile reinterpretation;
- no enlarged head, rounded childlike face, cute/chibi/adolescent drift.

## Nudity / exposure direction — HARD PERMISSION, EXACT DESIGN OPEN

The Exilada does not need to be visually desexualized to be treated seriously.

Her initial captivity/deprivation state may include:

- severely torn cloth;
- irregular holes and missing edges;
- displaced remnants rather than neat coverage;
- substantially more exposed skin than the current master;
- partial breast exposure when physically consistent with damage;
- near-nudity or full adult nudity when deliberately appropriate to state;
- asymmetrical hip coverage;
- simultaneous vulnerability, danger, sensuality and physical presence.

No censor garment is mandatory. Exact tear geometry/exposure remains subject to visual approval.

## 1980s sword-and-sorcery charge — HARD LOCK / MUST BE VISIBLE

Canonical inspiration lineage:

- **Heavy Metal**;
- **Conan**;
- **Red Sonja**;
- **Frank Frazetta**;
- **Julie Bell**.

Interpretation:

- adult sensuality, heroic/natural anatomy, danger, grime, erotic charge and pulp-fantasy excess may coexist;
- mature body language must not be sanitized or infantilized;
- materials should feel tactile, physical and illustrated even after pixel-art reconstruction;
- long hair should feel like heavy physical mass, not decorative strands;
- the influence is tonal/pictorial, not VHS/CRT gimmicks;
- merely naming references in a prompt is not enough.

Reject generic modern fantasy heroine, glossy MMO/cosplay polish, clean leather-bikini logic, cute/chibi drift and sanitized adult anatomy.

## Runner54 — CURRENT VISUAL GATE

Launcher:

`tools/structured-2d-character-pipeline/54_run_exilada_master_editor.ps1`

Application:

`tools/flux-kontext-spike/exilada_master_editor.py`

Purpose:

- revise the Exilada master locally;
- work directly on torn cloth/exposure, anatomy, material state, hair/face severity and pictorial charge;
- use the approved nude anatomy turnaround and optional user-supplied visual references;
- preserve candidate provenance and full useful output resolution;
- iterate without automatically overwriting the canonical master;
- promote a result only through explicit local approval.

Runner53 is paused until this gate passes.

## H3 painterly/raster output — INTERMEDIATE MOTION MASTER

MiniMax H3 Base50 remains the motion-master quality baseline.

Canonical proven configuration:

- `448×800`;
- `124f@24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- no Turbo LoRA.

Its useful qualities should survive downstream conversion:

- physical body mass;
- coherent anatomy through motion;
- rich hair volume/inertia;
- cloth/material response;
- mature dark-fantasy severity;
- complete-character continuity.

A materially revised Exilada master may require a new H3 validation before production animation resumes.

## Spritesheet organization — HARD LOCK

**One action = one spritesheet row.**

Frames read left-to-right in time. Internal high-resolution renderer tiles/chunks never define final semantic rows.

A later combined character sheet may stack different actions vertically.

## Resolution architecture — HARD LOCK

`128px` is retired as an Exilada production-asset baseline.

Likewise, historical `192×192` Runner52 cells and `384×384` Runner53 review cells are not final production-resolution mandates.

The sprite/frame asset should preserve the useful resolution of the approved video/frame/render chain. Gameplay apparent size is controlled separately by runtime/world/camera scaling.

Do not destructively reduce the production master merely because a viewport composition test may display the character at a smaller apparent height.

## Gameplay projection — LOCKED EXCEPT FINAL APPARENT CHARACTER SIZE

- native raster `640×360`;
- camera pitch `26°`;
- `relative_scale=1.0` = adult-human/Exilada world scale, not pixel height;
- first locomotion family screen-left, mostly lateral/slight 3/4;
- current facing baseline `72°`;
- combat readability over geometric purity.

Viewport comparisons may still test different apparent heights, but these do not redefine asset resolution.

## Runtime / production architecture

Visible runtime characters are complete precomposed frames. There is no visible runtime body/hair/clothing/equipment layer assembly.

Routine manual rigging, keyframing, mask repair, per-frame repainting/retouching and hand compositing remain disallowed.

## Renderer history

Runner52 materially fixed structure/layout and adult-body preservation but did not prove final high-level pixel art.

Runner53 remains a useful downstream style-adapter experiment, but it is **PAUSED** because the source character master must be corrected first.

## Current decisions

**LOCKED:** final runtime character graphics are deliberate high-quality pixel art.

**LOCKED:** H3 Base50 painterly/raster output is an intermediate motion master.

**LOCKED:** one action = one horizontal spritesheet row.

**LOCKED:** approved adult body/age/proportions may not be accidentally infantilized or redesigned.

**LOCKED:** adult partial/complete nudity is legitimate and no censor garment is mandatory.

**REOPENED:** exact Exilada initial clothing damage/exposure and final master pictorial treatment.

**CURRENT GATE:** Runner54 local Exilada master editor.

**PAUSED:** Runner53 Modern Pixel Art LoRA probe until the new master is approved.

**RETIRED:** `128px`, `192px` or `384px` as mandatory Exilada production sprite-size assumptions.

**LOCKED:** Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell remain active and must be visibly expressed rather than merely named.

**LOCKED:** runtime remains complete-character 2D sprite playback and production must scale without routine manual art labor.
