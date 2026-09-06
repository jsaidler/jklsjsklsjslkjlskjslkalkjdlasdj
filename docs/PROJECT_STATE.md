# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
7. `docs/PIXEL_ART_PRODUCTION.md`
8. `docs/ANIMATION_PIPELINE.md`
9. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
10. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
11. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
12. `docs/G3S_B4_HAIR_LOG.md`
13. `docs/G3S_C0_BODY_MOTION_PROOF.md`
14. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic doc, this file and the active handoff before completion is reported.

Normal operator loop only after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

Native gameplay baseline:

- `640×360`;
- orthographic camera;
- pitch `26°`;
- protagonist standing body height approximately `128 px`.

## Visible-ownership invariant — CRITICAL

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides but **not** final visible RGB/alpha/silhouette. Final visible art is owned by persistent native 2D pixel assets.

No recurring Blender/Aseprite/rigging/manual frame repainting burden is placed on the user.

## Canonical Exilada body — PASS/CLOSED / LOCKED

Production body:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- dimensions `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical screen-facing for this asset: **LEFT**.

The body remains byte/pixel unchanged as source art.

## Facing/laterality invariant — LOCKED

The current body is an authored **front-three-quarter, screen-left-facing** sprite. Screen-left/screen-right positions in this raster are not automatically anatomical left/right or near/far limb ownership.

Any travel preview using this exact source family must move screen-left unless a separately authored right-facing family is selected. Do not mirror silently and do not infer anatomical laterality from x-position alone.

## Motion infrastructure — RETAINED

- G2 real motion/topology — **PASS/CLOSED**;
- motion source: CMU `105_34 NormalWalk`;
- source rig: `G2_CANONICAL_RIG`;
- G3V-R retarget preflight — **PASS/CLOSED**;
- method: `DIRECTION_SPACE_FK`;
- validated phase frames: `1568, 1588, 1608, 1628`.

This infrastructure remains useful for pose guides, contacts, timing, root travel, sockets and depth. It does not by itself create valid visible 2D anatomy.

## Hair — DEFERRED BY USER

B4 remains open and unapproved. Eventual minimum structure remains:

`rear_hair -> body -> front_hair`

No hair pixels were promoted. Hair does not resume automatically.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3/G3R/G3V direct visible 3D translation routes — CLOSED/REJECTED
- G3S-B3 production body — **PASS/CLOSED**
- G3S-B4 hair — **DEFERRED / OPEN**
- **G3S-C0 body-only motion proof**
  - V1 rigid cutout — **FAIL/CLOSED**
  - V2 continuous chain warp — **FAIL/CLOSED**
  - **single-still puppet/warp route — CLOSED**
- **CURRENT architectural task: animation-ready native-2D pose source**
- G3S-B5 clothing/restraints/accessories — DEFERRED
- full layered G3S-C — later, after visible layer families exist

## G3S-C0 V1 — FAIL/CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`

The single body still was partitioned into rigid limb pieces. Real motion reached the sprite, but joints detached and later stride poses produced broken loop/arc silhouettes.

Closed method:

`one monolithic still -> hard body-part cutout -> independent rigid rotations`

## G3S-C0 V2 — FAIL/CLOSED VISUAL + METHOD

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_contact_sheet.png`

Reviewed SHA256:

`6d6199aa7bc159cad344c8dbc31b52577f2c70bb70f674ab5216ea40db67fba3`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v2_visual_failure.json`

V2 used continuous arm/leg chain warping. It still produced anatomically impossible legs and stride silhouettes.

Root cause is architectural, not cosmetic:

- sprite facing/laterality/near-far ownership was not registered against the authored 3/4 view;
- G2 screen-space deltas and sprite rest/camera basis were not validated as a common coordinate system;
- real gait depth/foreshortening cannot be reduced to 2D angle warp;
- a single 3/4 raster lacks hidden body surfaces needed when occlusion changes;
- bbox-bottom grounding is not true foot-contact/root grounding.

Therefore all of the following are closed when the only visible source is the single B3B still:

- rigid cutout animation;
- continuous chain warp;
- more pivot/anchor/overlap tuning;
- weighted cage/mesh as a supposed fix for missing visible anatomy.

The V2 runner is intentionally disabled:

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1`

## Current architectural requirement

A production walk needs **pose-specific native-2D visible information**.

Preferred first source family: a small left-facing gait set tied to actual motion events, e.g. contact/down/passing/up for both sides. Each key state must be a complete native-2D body pose with correct:

- anatomical left/right and near/far ownership;
- foreshortening;
- hip/knee/ankle geometry;
- foot contact/roll;
- pelvis/torso counter-motion;
- silhouette and occlusion.

G2 supplies pose guides/timing/contacts/root/depth; persistent 2D art owns the visible result.

**No runner is currently approved.** The next implementation must first prove a source-authoring method for at least one non-rest gait pose without asking the user to manually redraw frames.

## Local state relevant to next step

- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- retained embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- retained FLUX.2 workspace exists historically at `Z:\AI\Flux2RefControlSpike` but is not automatically authorized as the next animation-source method;
- no new model search is open;
- PixelLab remains historical paid spike only and is not authorized.
