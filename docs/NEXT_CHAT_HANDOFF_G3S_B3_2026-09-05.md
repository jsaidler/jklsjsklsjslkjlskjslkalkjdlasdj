# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Mandatory source of truth

Read first:

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
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

Do not redraw or replace this asset during C0.

## Hair — DEFERRED

B4 remains open and unapproved. Required eventual structure remains:

`rear_hair -> body -> front_hair`

The user explicitly instructed on 2026-09-06 to forget hair for now and show the doll moving.

B4C produced a review contact sheet but no hair was promoted:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter\g3s_b4c_flux2_contact_sheet.png`

User-provided SHA256:

`ac95bf9e3fae2df1e25cc91bcbda69be061526c163ce61cbe0d065cfc7be1c1c`

Do not resume B4 automatically.

## Motion backbone already validated

- G2 = PASS using CMU `105_34 NormalWalk`;
- hidden source rig = `G2_CANONICAL_RIG`;
- G3V-R = PASS;
- retarget/direction method = `DIRECTION_SPACE_FK`;
- validated phase frames = `1568, 1588, 1608, 1628`.

## CURRENT GATE — G3S-C0 BODY-ONLY MOTION PROOF

C0 is a diagnostic exception to the full layered order. It is allowed now because the user wants to inspect the approved body in motion before more visual-layer work.

C0 uses:

`real G2 walk -> projected joints/depth -> direction deltas -> persistent B3B pixel-part transforms -> depth-aware native 2D composition`

It does not use diffusion, hidden-3D RGB, paid APIs, new model downloads or user keyframing.

Runner:

`tools/structured-2d-character-pipeline/19_run_g3s_c0_body_walk_proof.ps1`

Support:

- `g3s_c0_body_motion_spec.json`
- `g3s_c0_extract_g2_motion.py`
- `g3s_c0_body_puppet_walk.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk`

Expected outputs:

- `g3s_c0_body_walk_in_place.gif`
- `g3s_c0_body_walk_travel.gif`
- `g3s_c0_body_walk_contact_sheet.png`
- `g3s_c0_motion_projection.json`
- `g3s_c0_body_walk_report.json`

The first C0 revision is a diagnostic cutout/deformation proof. Visible seams or rigid-joint artifacts should be analyzed and fixed in the deformation method; they are not final accepted animation quality.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\19_run_g3s_c0_body_walk_proof.ps1"
```

Then share the in-place GIF first:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk\g3s_c0_body_walk_in_place.gif`

If the runner fails, share the complete console output.

## Local requirements for C0

- `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend` must still exist from approved G2;
- Blender must remain installed/discoverable;
- embedded Python used for deterministic raster work: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- no AI model is required.
