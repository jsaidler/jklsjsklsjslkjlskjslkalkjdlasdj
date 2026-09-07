# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G1_CAMERA_SCALE_LOG.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
7. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
8. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
9. `docs/G3S_C0_BODY_MOTION_PROOF.md`
10. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
11. `docs/G3S_B4_HAIR_LOG.md`
12. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED FOR FEASIBILITY

True isometric character production was deliberately abandoned because it multiplies view families, pose coverage, occlusion cases and animation cost.

The locked gameplay presentation is an **elevated 2D arcade beat'em-up / belt-scroller / false 3D**:

- fixed orthographic camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist standing body about `128 px`;
- walkable gameplay-depth band retained;
- first visible family screen-left/front-three-quarter;
- movement through gameplay depth does not require north/south/isometric sprite families.

Any route that silently recreates isometric/multi-directional character complexity is architecture drift.

## Final runtime animation representation — LOCKED

The game uses conventional 2D sprite animation:

`approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary runtime playback`

Actions are deterministic frame sequences arranged in rows/blocks or equivalent atlas regions. One huge PNG is not required; grouped sheets are acceptable.

Runtime does not require a 3D skeleton, segmented-body puppet, diffusion model or per-frame generation.

## Canonical Exilada references

Design/master reference:

`assets/source/characters/exilada/reference/exilada_master.png`

Approved earlier body-base artifact remains retained for provenance:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- screen-left/front-three-quarter family.

For the active SSD spike, the **complete Exilada master** is the intended appearance reference; the old body-only/hair-deferred staging is not a prerequisite for this direct spritesheet-source test.

## Motion backbone — PASS/RETAINED AS OFFLINE SOURCE

- G2 = PASS/CLOSED;
- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- C1A skeleton walk = PASS/CLOSED;
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`;
- projected root travel approximately `-43.77 px` screen-left.

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

This work may be reused as offline pose/motion control. It is not a runtime dependency.

## Closed / superseded visible routes

- direct visible 3D -> final pixel art — CLOSED;
- C0 V1 nearest-segment hard partition / exposed rigid pieces — CLOSED;
- single-still continuous chain/cage warp -> gait — CLOSED;
- MPFB skinned body as mandatory hidden guide — CLOSED;
- independent full-body Flux2 redraw for each walk frame — FAIL/CLOSED;
- segmented 2D skeletal puppet — **PAUSED/HISTORICAL, NOT CURRENT**;
- implicit return to isometric/multi-directional character coverage — CLOSED unless presentation is explicitly reopened.

## CURRENT — SPRITE SHEET DIFFUSION LOCAL VALIDATION SPIKE

Canonical doc:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Goal:

Determine whether **Sprite Sheet Diffusion (SSD)** can locally generate a coherent Exilada action sequence from the master plus pose/motion guidance strongly enough that the accepted frames can be frozen into conventional spritesheets.

### Upstream verified facts

Upstream repo:

`chenganhsieh/Sprite-Sheet-Diffusion`

Actual implementation facts:

- README requests Python 3.10 conda environment;
- README references `requirements.txt`, but the repository does **not** contain that root file;
- actual inference entry point: `ModelTraining/inference.py`;
- actual config: `ModelTraining/configs/prompts/inference.yaml`;
- config requires SD1.5 base model in addition to SSD/AnimateAnyone/VAE/CLIP components.

### Actual local result so far

Workspace intended:

`Z:\AI\SpriteSheetDiffusionSpike`

Clone result:

- upstream clone completed successfully;
- 887/887 objects received;
- approximately 289.63 MiB transferred.

Environment bootstrap failures:

- `conda` is not installed / not on PATH;
- `conda create -n ssd python=3.10 -y` failed because command was not found;
- `conda activate ssd` failed for the same reason;
- prior instruction `cd /d ...` was wrong for PowerShell (`/d` is CMD syntax);
- `pip install -r requirements.txt` failed from `C:\Users\jsaid` and the upstream repo independently lacks the referenced root requirements file.

These are installation-procedure defects, not an SSD model-quality failure.

## Current exact next gate

**Install Miniconda and create only the isolated Python 3.10 environment.**

Do not install the large Python stack or download model weights until this passes.

PASS requires:

- `conda.exe` located;
- env `ssd` created;
- `conda run -n ssd python --version` reports Python 3.10.x.

## No cleanup yet

SSD is ACTIVE, not discarded. Do not delete `Z:\AI\SpriteSheetDiffusionSpike`.

If the route is later explicitly closed, cleanup is documented in `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`.
