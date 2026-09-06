# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
5. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
6. `docs/G3S_C0_BODY_MOTION_PROOF.md`
7. `docs/G3S_B4_HAIR_LOG.md`

## Canonical animation architecture — LOCKED

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root control -> complete visible 2D pose assets -> sprite playback -> QA`

The hidden 3D is the skeleton/armature. Do not reintroduce a skinned human mesh as a prerequisite for animation guidance.

## Canonical body — LOCKED

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- faces screen-left;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- identity/body-style reference only; never warp it into full gait.

## Hair — DEFERRED

Do not resume B4 automatically.

## Closed routes

- visible 3D -> final pixel art;
- single-still cutout/warp/cage -> full gait;
- skinned MPFB body as mandatory hidden animation guide.

## C1A skeleton-only walk — PASS/CLOSED

Approved cycle:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

Reviewed evidence:

- contact sheet SHA256 `672c8f9cb419cb8aa317447801931ce76da07b101b766c3f616bb2c25a39c2cd`;
- zoom GIF SHA256 `9a61ae7414be04ef4a89d8f83127e73d58e46da2075f37e23b7b048864286970`;
- projected root travel approximately `-43.77 px` screen-left.

PASS criteria met: coherent gait, left/right progression, intact chains, support-foot progression, readable pelvis/trunk/legs, laterality/near-far and screen-left direction.

Earlier camera-selection failure is closed/resolved. C1A itself used no model/API/download; no cleanup applies.

## CURRENT — C1B VISIBLE EXILADA WALK PROOF

Goal: finally show the bald Exilada body visibly walking through the complete eight-state cycle.

Current bounded route:

`approved C1A skeleton -> exact B3B identity/style conditioning + per-state skeleton pose control -> already-retained local FLUX.2 Klein -> complete visible body redraw for each state -> GIF/contact-sheet review`

This is a visual proof gate, not automatic production promotion.

Existing local stack only:

`Z:\AI\Flux2RefControlSpike`

Expected retained files:

- `flux-2-klein-base-4b-fp8.safetensors`;
- `qwen_3_4b.safetensors`;
- `flux2-vae.safetensors`.

No download and no paid API are allowed.

Current files:

- `tools/structured-2d-character-pipeline/g3s_c1b_flux2_walk_spec.json`;
- `tools/structured-2d-character-pipeline/g3s_c1b_prepare_flux2_walk_inputs.py`;
- `tools/structured-2d-character-pipeline/g3s_c1b_build_flux2_walk_review.py`;
- `tools/structured-2d-character-pipeline/22_run_g3s_c1b_flux2_walk_visual_proof.ps1`.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof`

Primary outputs:

- `g3s_c1b_exilada_walk_visual_proof.gif`;
- `g3s_c1b_exilada_walk_contact_sheet.png`;
- `g3s_c1b_review.json`.

Hard locks:

- no static-body warp/cutout/cage;
- no hidden-3D visible pixels;
- no hair/clothing/restraints/accessories/weapons;
- no manual frame repair required from user;
- generated frames are review candidates only;
- review `96×160` reductions are not production sprites.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\22_run_g3s_c1b_flux2_walk_visual_proof.ps1"
```

If successful, share:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof\g3s_c1b_exilada_walk_visual_proof.gif`;
- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof\g3s_c1b_exilada_walk_contact_sheet.png`.

If it fails, share the complete console output.

## After C1B review

If the eight visible frames read as one coherent woman walking, freeze/author the accepted native persistent 2D walk family under production-art rules. Hair and other layers return only after body locomotion is viable.
