# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
4. `docs/G1_CAMERA_SCALE_LOG.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
7. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
8. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families.

True isometric multi-directional character production remains closed unless explicitly reopened.

## Runtime animation representation — LOCKED

`approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary runtime sprite playback`

Runtime does not require a 3D skeleton, MPFB, segmented puppet, diffusion model or per-frame generation.

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

The active SSD spike uses the complete master as appearance reference.

## Retained offline motion source

- G2 PASS/CLOSED;
- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- C1A skeleton walk PASS/CLOSED;
- approved cycle `1588,1598,1608,1618,1628,1638,1648,1658`.

This is the source of the first eight pose-control states for SSD. The user is not expected to supply eight new pose references.

## Historical/closed visible routes

- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp -> gait — CLOSED;
- MPFB skinned body as mandatory guide — CLOSED;
- Flux2 independent full-body redraw per frame — FAIL/CLOSED;
- segmented 2D puppet runner 23 — PAUSED/HISTORICAL.

## CURRENT — SPRITE SHEET DIFFUSION LOCAL VALIDATION

Canonical doc: `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Goal: determine whether Sprite Sheet Diffusion can generate a coherent Exilada action sequence strongly enough that accepted frames can be frozen into conventional spritesheets.

## Environment / dependencies / assets — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated state:

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- GPU `NVIDIA GeForce RTX 3060`;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD inference import graph PASS;
- core generation model gate PASS;
- authoring-support gate PASS.

Latest user-supplied support result:

- `SSD-SUPPORT: PASS`;
- DWPose available;
- FILM available, optional/not default;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_bootstrap.json`;
- probe `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_probe.json`.

The support runner requires the core-model PASS marker, so core generation models are structurally confirmed present before support PASS.

## PowerShell runner rule — LOCKED

Expected native failures must never be raw control flow under `$ErrorActionPreference='Stop'`. Use structured Python diagnostics, explicit exit-code handling and controlled project `FAIL` messages.

## CURRENT GATE — prepare canonical walk pose maps for first SSD inference

The phrase “8 poses” means the approved C1A eight-state walk cycle:

1. source 1588 — `left_contact`;
2. source 1598 — `left_down`;
3. source 1608 — `left_passing`;
4. source 1618 — `left_up`;
5. source 1628 — `right_contact`;
6. source 1638 — `right_down`;
7. source 1648 — `right_passing`;
8. source 1658 — `right_up`.

Canonical guide:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

Existing review PNGs in that workspace are **not** suitable SSD inputs because they include labels, a ground band, support-foot rings and review-specific rendering. Do not feed them directly to SSD.

Correct next work:

`C1A guide data -> clean OpenPose-compatible body pose maps -> SSD first 8-frame Exilada inference`

The user must not be asked to create or find an arbitrary `YOUR_8_POSE_IMAGES` folder.

## First real inference contract

- appearance reference: complete `exilada_master.png`;
- motion control: eight clean maps derived from the approved C1A guide;
- 8 frames;
- `512×512` first proof;
- FILM disabled;
- validate identity, anatomy/proportions, hair/clothing/equipment persistence, pose obedience, temporal coherence, VRAM fit and alpha/background cleanup viability.

Only after this PASS do we expand to multi-action spritesheets and automate packing/pivots/events.

## Explicit exclusions

- wav2vec2 / audio-driven AniPortrait models — unrelated;
- legacy CMU OpenPose body/hand/face weights — not a production dependency; DWPose is preferred;
- AnimateAnyone baseline denoising/reference UNets — must not replace SSD fine-tuned sprite UNets;
- xformers — optimization only if measured VRAM behavior requires it.

## No cleanup

SSD is ACTIVE. Do not delete `Z:\AI\SpriteSheetDiffusionSpike`.
