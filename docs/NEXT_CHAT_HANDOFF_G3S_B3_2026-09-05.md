# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
4. `docs/G1_CAMERA_SCALE_LOG.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G3S_C1B_SEGMENTED_PUPPET.md`

## Locked production direction

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed `640×360` orthographic camera, pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- no north/south/isometric sprite-family multiplication;
- final runtime = conventional deterministic spritesheet playback.

Runtime does not require 3D, a segmented puppet or diffusion.

## Current source-authoring route

**Sprite Sheet Diffusion (SSD)** validation spike.

Canonical doc: `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Purpose: generate a coherent Exilada action sequence from the complete master plus pose/motion guidance, then freeze approved frames into ordinary spritesheets.

## Local SSD state — ALL INSTALLATION/SUPPORT GATES PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated environment/dependencies:

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- GPU `NVIDIA GeForce RTX 3060`;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- real SSD inference import graph PASS.

Core generation models: PASS.

Authoring support actual user result:

- `SSD-SUPPORT: PASS`;
- DWPose available;
- FILM available, optional/not default;
- marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_bootstrap.json`;
- probe `Z:\AI\SpriteSheetDiffusionSpike\ssd_authoring_support_probe.json`.

DWPose is the preferred future driving-video/action pose extractor. FILM is not enabled for the first proof.

## IMPORTANT CLARIFICATION — WHAT “8 POSES” MEANS

The user does **not** need to find or provide eight new pose images.

The eight states already exist canonically in C1A, derived from real `CMU 105_34 NormalWalk` motion:

1. 1588 — `left_contact`;
2. 1598 — `left_down`;
3. 1608 — `left_passing`;
4. 1618 — `left_up`;
5. 1628 — `right_contact`;
6. 1638 — `right_down`;
7. 1648 — `right_passing`;
8. 1658 — `right_up`.

Canonical data:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

The C1A review builder also created eight review PNGs in that workspace, but those contain labels, a ground band, support-foot rings and review colors. **Do not feed those review PNGs directly to SSD.**

The previous manual instruction containing a placeholder `YOUR_8_POSE_IMAGES` was wrong. Do not ask the user for that folder again.

## CURRENT NEXT WORK

Prepare clean SSD/OpenPose-compatible body pose maps from the existing C1A guide data:

`C1A guide -> clean 8 pose-control PNGs -> Exilada master -> first real SSD inference`

The clean pose maps must contain only the pose-control drawing expected by the SSD family, without review annotations.

## First real SSD proof contract

- reference: complete `assets/source/characters/exilada/reference/exilada_master.png`;
- 8 clean C1A-derived pose maps;
- `512×512` first proof;
- 8 frames;
- FILM disabled;
- evaluate identity persistence, anatomy/proportions, hair/clothing/equipment persistence, pose obedience, temporal coherence, RTX 3060 12 GB fit, and background/alpha cleanup viability.

Only after PASS expand to multi-action sheet production and automate packing/alpha/pivots/events.

## PowerShell rule

Do not repeat raw expected-failure native probes under `$ErrorActionPreference='Stop'`. Use controlled process execution, explicit exit codes and structured Python diagnostics.

## Historical routes

- segmented-puppet runner 23: historical/paused;
- Flux2 independent full-body frame redraw: FAIL/CLOSED;
- isometric multi-directional character production: CLOSED unless explicitly reopened.

SSD route is ACTIVE. No cleanup applies.
