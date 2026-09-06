# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
5. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
6. `docs/G3S_C0_BODY_MOTION_PROOF.md`
7. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
8. `docs/G3S_B4_HAIR_LOG.md`
9. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

- systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and causal living world;
- elevated 2D belt-scroller / false 3D;
- true modern pixel art at native gameplay raster;
- `640×360`, orthographic, pitch `26°`, protagonist standing body height approximately `128 px`.

## Final animation architecture — LOCKED

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root control -> complete visible 2D pose assets -> deterministic sprite playback -> QA`

Hidden 3D is the skeleton/armature. It owns motion, bone/joint transforms, anatomical side identity, near/far/depth order, contact/root travel and sockets. It does not require a skinned human body mesh and does not own final visible RGB, alpha, anatomy or silhouette.

## Canonical Exilada body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- screen-left front-three-quarter family.

B3B is identity/body-style reference only. It is never warped into arbitrary gait poses.

## Closed routes

- direct visible 3D -> final pixel art — CLOSED;
- single B3B still -> projected joints -> cutout/warp/cage -> full walk — CLOSED;
- MPFB skinned body as mandatory hidden animation guide — CLOSED.

## Hair — DEFERRED

B4 remains paused by user. Do not resume automatically.

## Motion infrastructure — RETAINED

- G2 = PASS/CLOSED;
- source motion = CMU `105_34 NormalWalk`;
- source armature = `G2_CANONICAL_RIG`;
- local blend = `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`.

## G3S-C1A skeleton walk — PASS/CLOSED

Approved cycle:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

Reviewed user-supplied artifacts:

- contact sheet SHA256 `672c8f9cb419cb8aa317447801931ce76da07b101b766c3f616bb2c25a39c2cd`;
- zoom GIF SHA256 `9a61ae7414be04ef4a89d8f83127e73d58e46da2075f37e23b7b048864286970`;
- projected root travel approximately `-43.77 px` screen-left.

Visual review PASS:

- coherent eight-state gait;
- correct left/right progression;
- intact limb chains;
- support-foot progression;
- readable pelvis/trunk/leg relationship;
- laterality/near-far readability;
- canonical screen-left direction.

Earlier C1A camera-selection failure is `CLOSED_RESOLVED_AFTER_SUCCESSFUL_RERUN` in:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_camera_selection_failure.json`

No model/API/download was used by C1A; no cleanup applies.

## CURRENT — G3S-C1B visible Exilada walk proof

The current goal is no longer another hidden guide. It is to show the bald Exilada body visibly walking through all eight approved gait states.

Current bounded path:

`C1A approved skeleton -> exact B3B identity/style reference + per-state skeleton pose control -> existing retained local FLUX.2 Klein -> 8 complete visible body redraws -> GIF/contact sheet review`

This is a **visual proof gate**, not automatic production promotion.

Existing local stack only:

`Z:\AI\Flux2RefControlSpike`

Required retained files:

- `flux-2-klein-base-4b-fp8.safetensors`;
- `qwen_3_4b.safetensors`;
- `flux2-vae.safetensors`.

No download and no paid API are allowed by the runner.

Current files:

- `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`;
- `tools/structured-2d-character-pipeline/g3s_c1b_flux2_walk_spec.json`;
- `tools/structured-2d-character-pipeline/g3s_c1b_prepare_flux2_walk_inputs.py`;
- `tools/structured-2d-character-pipeline/g3s_c1b_build_flux2_walk_review.py`;
- `tools/structured-2d-character-pipeline/22_run_g3s_c1b_flux2_walk_visual_proof.ps1`.

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof`

Expected outputs:

- `g3s_c1b_exilada_walk_visual_proof.gif`;
- `g3s_c1b_exilada_walk_contact_sheet.png`;
- `g3s_c1b_review.json`;
- eight full-resolution generated candidate frames.

Hard locks:

- no static-body warp/cutout/cage;
- no hidden-3D visible pixels;
- no hair/clothing/restraints/accessories/weapons;
- no manual frame repair demanded from the user;
- no automatic production promotion;
- `96×160` reductions are review-only inspection images.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\22_run_g3s_c1b_flux2_walk_visual_proof.ps1"
```

If successful, inspect/share:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof\g3s_c1b_exilada_walk_visual_proof.gif`;
- `Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof\g3s_c1b_exilada_walk_contact_sheet.png`.

If it fails, share the complete console output.

## After C1B review

If the eight visible frames read as the same coherent woman walking, freeze/author the accepted native persistent 2D walk family under the production-art rules. Hair and other layers return only after body locomotion is viable.
