# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G1_CAMERA_SCALE_LOG.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
5. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
6. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
7. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
8. `docs/G3S_C0_BODY_MOTION_PROOF.md`
9. `docs/G3S_B4_HAIR_LOG.md`

## Presentation simplification — LOCKED

True isometric character production was abandoned for feasibility.

Locked presentation:

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic `640×360` camera;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left front-three-quarter;
- gameplay depth movement uses world position/depth sorting, not north/south/isometric character sprite families.

Do not silently recreate multi-directional/isometric art complexity.

## Canonical body

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- screen-left front-three-quarter family;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`.

Hair remains DEFERRED.

## Motion backbone — PASS

- G2 PASS;
- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- C1A skeleton walk PASS/CLOSED;
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`;
- projected root travel approximately `-43.77 px` screen-left.

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

## Closed methods

- visible 3D -> final pixel art;
- C0 V1 nearest-segment exclusive hard partition + exposed independent rigid parts;
- single-still full-body chain/cage warp -> gait;
- skinned MPFB body as mandatory hidden guide;
- independent full-body generative redraw per walk frame;
- implicit return to isometric/multi-directional character coverage.

## C1B Flux2 — FAIL/CLOSED

Reviewed output failed persistent identity:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Runner 22 is disabled and must not be tuned/rerun for locomotion. No new model/runtime was installed; no cleanup applies.

## CURRENT — C1B MINIMAL SEGMENTED PERSISTENT 2D PUPPET — RUNNER READY

Architecture:

`approved hidden skeleton -> persistent B3B-derived part set -> bind landmarks + overlap -> projected skeleton transforms -> camera-space depth sort -> composited sprite`

Current files:

- doc: `docs/G3S_C1B_SEGMENTED_PUPPET.md`;
- spec: `tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json` revision `MINIMAL_BEATEMUP_SEGMENTED_PUPPET_V2`;
- builder: `tools/structured-2d-character-pipeline/g3s_c1b_build_segmented_puppet.py`;
- runner: `tools/structured-2d-character-pipeline/23_run_g3s_c1b_segmented_puppet_walk.ps1`.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1b_segmented_puppet`

### Minimal persistent part set

- `head_neck`;
- one continuous torso+pelvis `core`;
- bilateral upper arms, forearms, hands;
- bilateral thighs, shins, feet.

The builder fits bind landmarks to the actual B3B alpha silhouette, uses overlapping limb masks and shoulder/hip/neck cap pixels, then reuses those same parts through all eight approved skeleton states. No per-frame generation is involved.

### First-proof locks

- screen-left family only;
- no north/south/isometric directions;
- no pre-emptive orientation/foreshortening variants;
- no MPFB body;
- no image model/API/download;
- no manual frame repair required from the user;
- hair deferred.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\23_run_g3s_c1b_segmented_puppet_walk.ps1"
```

Primary review outputs:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_segmented_puppet\g3s_c1b_puppet_walk_zoom.gif`;
- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_segmented_puppet\g3s_c1b_puppet_contact_sheet.png`.

Debug only if needed:

- `g3s_c1b_puppet_contact_sheet_skeleton_overlay.png`;
- `g3s_c1b_segmented_part_atlas.png`;
- `g3s_c1b_puppet_bind_manifest.json`.

If the result fails, diagnose the specific joint/part/projection defect. Do not change presentation or add art families unless the visible failure requires it.
