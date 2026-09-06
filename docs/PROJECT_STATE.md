# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
5. `docs/G3S_C0_BODY_MOTION_PROOF.md`
6. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
7. `docs/G3S_B4_HAIR_LOG.md`
8. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates its thematic docs, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

- systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and causal living world;
- elevated 2D belt-scroller / false 3D;
- true modern pixel art at native gameplay raster;
- `640×360`, orthographic, pitch `26°`, protagonist standing body height approximately `128 px`.

## Final animation architecture — LOCKED

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root guide data -> persistent native-2D pose assets -> deterministic sprite playback -> QA`

The hidden 3D is the skeleton/armature. It owns motion, bone/joint transforms, anatomical side identity, near/far chain depth, foreshortening, contact/root travel and sockets. It does **not** require a skinned human body mesh and does not own final RGB, alpha, anatomy or sprite silhouette.

## Canonical Exilada body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical facing screen-left.

B3B is the visible identity/body-style anchor only. It is not warped into arbitrary gait poses.

## Motion infrastructure — RETAINED / ACTIVE

- G2 = PASS/CLOSED;
- source motion = CMU `105_34 NormalWalk`;
- source armature = `G2_CANONICAL_RIG`;
- local blend = `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`;
- G2 already validated topology, left/right alternation, captured-motion basis and sequence continuity.

G3V-R `DIRECTION_SPACE_FK` remains historical validated infrastructure but **current C1A no longer needs MPFB/G3V at all**; it reads G2 directly.

## Closed routes

- direct visible 3D -> final pixel art — CLOSED;
- single B3B still -> projected joints -> cutout/warp/cage -> full walk — CLOSED;
- MPFB skinned body as mandatory hidden animation guide — CLOSED.

C1A V1–V5 are historical skinned-body failure evidence. V6 was superseded pre-run after the user clarified that the hidden guide should simply be a skeleton.

## Hair — DEFERRED

B4 remains paused by user. Do not resume automatically.

## CURRENT gate — G3S-C1A SKELETON-ONLY WALK CYCLE

The current runner now exports the complete first eight-state walk cycle instead of stopping on another isolated pose:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

C1A uses only `G2_CANONICAL_RIG`. No skinned mesh or hidden human render is involved.

Current files:

- spec: `tools/structured-2d-character-pipeline/g3s_c1_skeleton_walk_spec.json`;
- exporter: `tools/structured-2d-character-pipeline/g3s_c1_export_skeleton_walk.py`;
- review builder: `tools/structured-2d-character-pipeline/g3s_c1_build_skeleton_walk_review.py`;
- runner: `tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`.

C1A records full bone matrices, joint world/screen/depth data, chain lengths/depths, anatomical left/right, near/far side, support foot, ground distance and real projected root travel.

Camera: `640×360`, orthographic, pitch `26°`, front-three-quarter `45°` relative to measured root heading, camera side selected so real forward travel projects screen-left. Maximum skeleton height calibrated to about `128 px`. The rig is not transformed for facing.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk`

Expected outputs:

- `g3s_c1_skeleton_walk_guide.json`;
- `g3s_c1_skeleton_walk_in_place.gif`;
- `g3s_c1_skeleton_walk_travel.gif`;
- `g3s_c1_skeleton_walk_zoom.gif`;
- `g3s_c1_skeleton_walk_contact_sheet.png`;
- eight frame PNGs.

No model/API/download is used by C1A. No cleanup applies.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

If it completes, inspect/share first:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_zoom.gif`;
- `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_contact_sheet.png`.

If it fails, share the complete console output.

## Next — C1B visible body walk

After the skeleton cycle passes, C1B goes directly to the **eight persistent native-2D body poses** for the first left-facing walk animation. C1A supplies spatial/motion control; B3B V4 supplies visible body identity/style.

The user is not expected to redraw or repair frames manually. C1B may not revive the static-still warp route or promote hidden-3D pixels. Any offline visual source-authoring tool must be explicitly approved for that gate.
