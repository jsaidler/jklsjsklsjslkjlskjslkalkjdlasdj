# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
5. `docs/G3S_C0_BODY_MOTION_PROOF.md`
6. `docs/G3S_B4_HAIR_LOG.md`

## Canonical animation architecture — LOCKED

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root control -> persistent native-2D pose assets -> sprite playback -> QA`

The hidden 3D is the **skeleton/armature**. Do not reintroduce a skinned human mesh as a prerequisite for animation guidance.

Hidden rig owns joint/bone transforms, anatomical side, chain depth/near-far, foreshortening, contacts, root travel and sockets. Visible anatomy/RGB/alpha/silhouette belong to persistent native-2D assets.

## Canonical body — LOCKED

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- 37×128 RGBA;
- faces screen-left;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- identity/body-style anchor only; never warp it into the full gait.

## Hair — DEFERRED

Do not resume B4 automatically.

## Motion source — ACTIVE

- G2 PASS;
- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- local blend `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`.

Current C1A reads G2 directly. MPFB/G3V body is no longer involved.

## Closed routes

- visible 3D -> final pixel art;
- single-still cutout/warp/cage -> full gait;
- skinned MPFB body as mandatory hidden pose/anatomy/silhouette/depth guide.

V1–V5 remain historical C1A failure evidence. V6 is superseded pre-run and should not be repaired.

## CURRENT — C1A SKELETON-ONLY EIGHT-STATE WALK

The runner now exports an entire motion cycle in one pass:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

Current files:

- `tools/structured-2d-character-pipeline/g3s_c1_skeleton_walk_spec.json`;
- `tools/structured-2d-character-pipeline/g3s_c1_export_skeleton_walk.py`;
- `tools/structured-2d-character-pipeline/g3s_c1_build_skeleton_walk_review.py`;
- `tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`.

Camera is `640×360`, orthographic, pitch `26°`, front-three-quarter `45°` from actual root travel. Camera side is selected so real forward travel projects screen-left. Rig is not rotated for facing. Maximum projected skeleton height is approximately `128 px`.

The guide records complete bone matrices, projected joints, chain lengths/depths, laterality, near/far, support foot, ground distance and projected root travel. Review drawing orders chains by depth and computes the zoom crop from actual joint bounds, not labels/background graphics.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk`

Primary outputs:

- `g3s_c1_skeleton_walk_zoom.gif`;
- `g3s_c1_skeleton_walk_travel.gif`;
- `g3s_c1_skeleton_walk_contact_sheet.png`;
- `g3s_c1_skeleton_walk_guide.json`.

No model/API/download. No cleanup applies.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

If successful, share `g3s_c1_skeleton_walk_zoom.gif` and `g3s_c1_skeleton_walk_contact_sheet.png`. If it fails, share the complete console output.

## Immediately after C1A PASS

C1B authors the **eight complete persistent native-2D body poses** for the first left-facing walk family, using the skeleton guide as motion/spatial control and B3B V4 as visible identity/body-style anchor.

Do not make the user draw/repair frames manually. Do not revive static-body warp. Do not promote hidden-3D pixels. Any offline visual authoring tool must be explicitly approved for C1B before use.
