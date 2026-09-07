# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G1_CAMERA_SCALE_LOG.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
5. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
6. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
7. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
8. `docs/G3S_C0_BODY_MOTION_PROOF.md`
9. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
10. `docs/G3S_B4_HAIR_LOG.md`
11. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED FOR FEASIBILITY

The project originally considered true isometric 2D presentation. That direction was deliberately abandoned because it multiplied view families, pose coverage, occlusion cases and animation production cost.

The locked gameplay presentation is an **elevated 2D arcade beat'em-up / belt-scroller / false 3D**:

- fixed orthographic camera;
- `640×360` native raster;
- pitch `26 deg`;
- protagonist standing body height about `128 px`;
- walkable gameplay depth band retained;
- first visible character family is screen-left front-three-quarter;
- movement through gameplay depth does not require north/south/isometric sprite families;
- screen-right is deferred until the left family is proven.

Any route that silently recreates isometric/multi-directional complexity is architecture drift.

## Canonical Exilada body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- screen-left front-three-quarter family.

## Hair — DEFERRED

B4 remains paused by user. Do not resume automatically.

## Motion backbone — PASS/RETAINED

- G2 = PASS/CLOSED;
- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- C1A skeleton walk = PASS/CLOSED;
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`;
- projected root travel approximately `-43.77 px` screen-left.

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

## Closed visible routes

- direct visible 3D -> final pixel art — CLOSED;
- C0 V1 nearest-segment exclusive hard partition + exposed independent rigid parts — CLOSED;
- single-still continuous full-body chain/cage warp -> gait — CLOSED;
- MPFB skinned body as mandatory hidden animation guide — CLOSED;
- independent full-body generative redraw for each walk frame — CLOSED after C1B Flux2 review;
- implicit return to isometric/multi-directional character coverage — CLOSED unless presentation is explicitly reopened.

## C1B Flux2 per-frame redraw — FAIL/CLOSED

Reviewed artifacts:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Failure: face, skin tone, anatomy, proportions, silhouette/view and pixel treatment drifted across frames. Runner 22 is intentionally disabled. No new model/runtime was installed by that gate; no cleanup applies.

## CURRENT — C1B MINIMAL SEGMENTED 2D PUPPET — RUNNER READY

Architecture:

`real mocap -> approved hidden skeleton -> persistent B3B-derived 2D part set -> bind landmarks + deliberate overlap -> projected bone transforms -> camera-space depth sort -> composited sprite -> QA`

The hidden skeleton owns motion/spatial control only. Final visible pixels remain persistent 2D assets.

Current implementation:

- doc: `docs/G3S_C1B_SEGMENTED_PUPPET.md`;
- spec: `tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json` revision `MINIMAL_BEATEMUP_SEGMENTED_PUPPET_V2`;
- builder: `tools/structured-2d-character-pipeline/g3s_c1b_build_segmented_puppet.py`;
- runner: `tools/structured-2d-character-pipeline/23_run_g3s_c1b_segmented_puppet_walk.ps1`.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1b_segmented_puppet`

### Minimal persistent part set

- `head_neck`;
- one continuous `core` for torso + pelvis;
- bilateral upper arms, forearms and hands;
- bilateral thighs, shins and feet.

Torso and pelvis intentionally remain one core in this first proof to avoid an unnecessary waist seam.

### Difference from C0 V1

The builder does not use an exclusive nearest-segment ownership partition. It fits bind landmarks to the actual B3B alpha silhouette, builds overlapping capsule regions for neighboring limb pieces, restores shoulder/hip/neck cap pixels into the core, preserves elbow/knee/wrist/ankle overlap and draws parts by C1A camera-space depth.

### Simplification locks

- one screen-left front-three-quarter visible family only;
- same persistent B3B-derived part assets in all eight states;
- no isometric/north/south sprite families;
- no per-frame generation;
- no MPFB body;
- no preemptive part variants;
- no model/API/download;
- no manual user frame repair;
- hair deferred.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\23_run_g3s_c1b_segmented_puppet_walk.ps1"
```

Primary review outputs:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_segmented_puppet\g3s_c1b_puppet_walk_zoom.gif`;
- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_segmented_puppet\g3s_c1b_puppet_contact_sheet.png`;
- debug if needed: `g3s_c1b_puppet_contact_sheet_skeleton_overlay.png`;
- part inspection: `g3s_c1b_segmented_part_atlas.png`.

## Review decision

Judge only whether this reads as **the same B3B doll moving**. If a concrete joint/projection defect appears, fix that specific part/binding. Do not change the presentation or add directional/variant complexity preemptively.
