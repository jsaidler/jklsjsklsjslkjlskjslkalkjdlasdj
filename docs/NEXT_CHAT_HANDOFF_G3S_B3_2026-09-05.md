# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G1_CAMERA_SCALE_LOG.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
7. `docs/G3S_C1B_SEGMENTED_PUPPET.md`
8. `docs/G3S_C0_BODY_MOTION_PROOF.md`
9. `docs/G3S_B4_HAIR_LOG.md`

## Presentation simplification — LOCKED

The project is not pursuing true isometric multi-directional character production.

Locked presentation:

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic `640×360` camera;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite sets.

## Runtime animation representation — LOCKED

Use conventional sprite animation:

`approved 2D frames -> spritesheet PNG(s) + metadata -> ordinary runtime sprite playback`

Actions are stored as deterministic frame sequences in rows/blocks/atlas regions. The runtime does not require 3D, a segmented puppet or diffusion.

## Current source-authoring route — SSD SPIKE

Current active validation:

**Sprite Sheet Diffusion (SSD)**

Canonical doc:

`docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

Purpose:

Test whether SSD can generate a coherent Exilada action sequence from the complete master plus pose/motion guidance, so approved frames can be frozen into conventional spritesheets.

## Upstream repository facts — VERIFIED

Repo:

`chenganhsieh/Sprite-Sheet-Diffusion`

Actual code layout:

- inference: `ModelTraining/inference.py`;
- config: `ModelTraining/configs/prompts/inference.yaml`.

Upstream README says to use a Python 3.10 conda environment and `pip install -r requirements.txt`, but the repository does **not** contain the referenced root `requirements.txt`.

The actual config additionally requires:

- Stable Diffusion v1.5 base model;
- SD VAE;
- CLIP image encoder;
- SSD denoising UNet;
- SSD reference UNet;
- AnimateAnyone pose guider;
- AnimateAnyone motion module.

## Actual local state

Workspace intended:

`Z:\AI\SpriteSheetDiffusionSpike`

Upstream clone: **SUCCESS**

Observed user console:

- 887/887 objects received;
- ~289.63 MiB transferred;
- `conda` command unavailable;
- env `ssd` not created yet;
- `cd /d` failed because it is CMD syntax, not PowerShell;
- `pip install -r requirements.txt` failed from the wrong directory and the upstream file is absent anyway.

These are bootstrap/procedure failures, not an SSD inference failure.

## Superseded current route

The segmented-puppet runner 23 is no longer the current production route. It remains historical and must not be continued unless explicitly reopened.

Flux2 per-frame full-body redraw remains FAIL/CLOSED.

## Exact next operator action

Only bootstrap Miniconda + Python 3.10 env. Do not download weights yet.

Use the PowerShell block provided in the current chat, which:

1. installs Miniconda through WinGet if `conda.exe` is absent;
2. locates `conda.exe` without relying on shell PATH refresh;
3. creates env `ssd` with Python 3.10;
4. verifies `conda run -n ssd python --version`.

PASS requires Python 3.10.x inside env `ssd`.

After PASS, next work is a controlled Windows dependency bootstrap based on the Moore-AnimateAnyone pinned stack, then model download in a documented order.

## Do not clean SSD workspace

SSD route is active. No cleanup applies now.
