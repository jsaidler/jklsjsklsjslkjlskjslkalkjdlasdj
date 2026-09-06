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
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- **canonical screen-facing: LEFT**.

Do not redraw or replace this asset during C0.

### Facing/travel rule — LOCKED

The canonical B3B source visibly faces screen-left. Therefore any travel preview using the exact unmirrored source must travel screen-left.

Earlier C0 code incorrectly increased x from `250 -> 390`, producing rightward travel. This is recorded as an implementation error:

`tools/structured-2d-character-pipeline/g3s_c0_travel_direction_correction.json`

Current V2 runner rebuilds travel as `390 -> 250`; it does not mirror the sprite and does not reverse gait phases.

## Hair — DEFERRED

B4 remains open and unapproved. Required eventual structure remains:

`rear_hair -> body -> front_hair`

The user explicitly instructed on 2026-09-06 to forget hair for now and show the doll moving. Do not resume B4 automatically.

## Motion backbone already validated

- G2 = PASS using CMU `105_34 NormalWalk`;
- hidden source rig = `G2_CANONICAL_RIG`;
- G3V-R = PASS;
- retarget/direction method = `DIRECTION_SPACE_FK`;
- validated phase frames = `1568, 1588, 1608, 1628`.

## CURRENT GATE — G3S-C0 BODY-ONLY MOTION PROOF

C0 is a diagnostic exception to the full layered order because the user wants to inspect the approved body in motion before more visual-layer work.

### C0 V1 — FAIL/CLOSED

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk\g3s_c0_body_walk_contact_sheet.png`

SHA256:

`730afda6a541db4524671931892685bee7317d8324efe6c9b3eb0c62fbdd5cc4`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`

V1's real-motion transfer worked, but the visible deformation did not. Hard upper/lower limb pieces visibly detach and create broken loop/arc silhouettes in later gait frames. Its travel presentation was also directionally wrong because the left-facing sprite was moved right.

Closed method:

`nearest-segment body partition + independent rigid per-part rotation`

Do not patch V1 with more overlap or more rigid pivot tuning.

### C0 V2 — CURRENT / RUNNER READY

V2 keeps the approved real-motion projection but replaces hard limb slabs with continuous chain deformation.

Visible regions:

- head;
- torso;
- left/right arm;
- left/right leg.

An arm/leg is warped as one complete chain, with adjacent-segment mapping blended around elbows/knees/ankles. Source pixel colors remain the visible art; hidden 3D contributes joints/depth only.

No diffusion, hidden-3D RGB, paid API, model download or manual user animation is used.

Travel is now explicitly leftward to match the canonical left-facing body.

Spec:

`tools/structured-2d-character-pipeline/g3s_c0_body_motion_spec_v2.json`

Builder:

`tools/structured-2d-character-pipeline/g3s_c0_continuous_warp_v2.py`

Travel builder:

`tools/structured-2d-character-pipeline/g3s_c0_build_left_facing_travel.py`

Runner:

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2`

Expected outputs:

- `g3s_c0_v2_body_walk_in_place.gif`
- `g3s_c0_v2_body_walk_travel.gif`
- `g3s_c0_v2_contact_sheet.png`
- `g3s_c0_v2_zoom_contact_sheet.png`
- `g3s_c0_v2_report.json`

If V2 still cannot keep the body visually continuous, move to an actual weighted 2D mesh/cage deformation representation. Do not return to rigid cutout parts.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\20_run_g3s_c0_body_walk_v2.ps1"
```

Then share:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_body_walk_in_place.gif`
- `Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_body_walk_travel.gif`
- `Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_zoom_contact_sheet.png`

If the runner fails, share the complete console output.

## Local requirements for C0

- `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend` must still exist from approved G2;
- Blender must remain installed/discoverable;
- embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- no AI model is required.
