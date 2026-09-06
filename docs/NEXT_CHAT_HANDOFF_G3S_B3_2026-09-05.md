# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_C0_BODY_MOTION_PROOF.md`
3. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
4. `docs/G3S_B4_HAIR_LOG.md`
5. `docs/ANIMATION_PIPELINE.md`

Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant

Every state-changing project action updates thematic docs, `PROJECT_STATE`, this handoff and commits before reporting completion.

## Canonical body — LOCKED

B3B V4 is PASS/CLOSED / PROMOTED:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical screen-facing: **LEFT**.

This is a front-three-quarter authored still, not an animation-ready full body source by itself.

## Facing/laterality — LOCKED

- left-facing source travels screen-left unless a separately authored right-facing family is selected;
- do not mirror silently;
- screen-x position is not anatomical left/right or near/far ownership in a 3/4 sprite.

## Hair — DEFERRED

B4 remains open and unapproved. Eventual minimum structure remains:

`rear_hair -> body -> front_hair`

Do not resume B4 automatically.

## Motion backbone — RETAINED

- G2 = PASS using CMU `105_34 NormalWalk`;
- source rig = `G2_CANONICAL_RIG`;
- G3V-R = PASS using `DIRECTION_SPACE_FK`;
- validated phase frames = `1568, 1588, 1608, 1628`.

Use this infrastructure for pose guides, timing, foot contacts, root travel, sockets and depth. It does not own final visible RGB/silhouette.

## C0 V1 — FAIL/CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`

Closed method:

`single monolithic still -> hard body-part cutout -> independent rigid rotations`

Reason: detached joints and broken/loop-like leg-foot silhouettes.

## C0 V2 — FAIL/CLOSED VISUAL + METHOD

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_contact_sheet.png`

SHA256:

`6d6199aa7bc159cad344c8dbc31b52577f2c70bb70f674ab5216ea40db67fba3`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v2_visual_failure.json`

V2 used continuous arm/leg chain warping and still produced anatomically impossible stride shapes.

Root causes are architectural:

- facing/laterality/near-far ownership of the authored 3/4 sprite was not registered correctly;
- sprite rest/camera basis and G2 screen-space motion basis were not validated as the same coordinate system;
- real gait depth/foreshortening cannot be represented by 2D chain-angle warp alone;
- one 3/4 still lacks hidden visible surfaces that appear when occlusion changes;
- alpha-bbox-bottom placement is not true contact-foot/root grounding.

Closed route:

`single B3B still -> any cutout/chain/cage warp intended to manufacture the full walk`

Do not create another pivot/anchor/overlap/mesh tuning revision using the same single still as the only visible source. A smoother mesh does not solve missing anatomy.

The V2 runner is intentionally disabled:

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1`

## CURRENT architectural task

Create an **animation-ready persistent native-2D source family** rather than trying to extract a whole gait from the one rest sprite.

For the first left-facing walk proof, use real gait events to define a small pose family (e.g. contact/down/passing/up across both sides). Each key state must contain complete visible anatomy with correct:

- anatomical left/right and near/far ownership;
- foreshortening;
- pelvis/torso relationship;
- hip/knee/ankle geometry;
- foot contact and roll;
- silhouette and occlusion.

G2 supplies pose/timing/contact/root/depth guides. Persistent 2D art owns final visible pixels.

No new runner is approved yet. First prove a method that can author **one non-rest gait pose** at production quality without asking the user to manually redraw it. Do not resume hair while solving this.

## Local state

- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- G2 blend remains required for motion guides;
- retained FLUX.2 workspace exists historically but is not automatically selected as the next animation source-authoring method;
- no broad model search is open;
- PixelLab remains historical paid spike only and is not authorized.
