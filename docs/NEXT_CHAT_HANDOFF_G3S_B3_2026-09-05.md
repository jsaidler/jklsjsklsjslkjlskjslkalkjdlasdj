# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

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

Actions are stored as deterministic frame sequences in rows/blocks/atlas regions. Runtime does not require 3D, a segmented puppet or diffusion.

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

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Upstream clone: **SUCCESS**

Miniconda: **SUCCESS**

Resolved executable:

`C:\Users\jsaid\miniconda3\Scripts\conda.exe`

Environment `ssd`: **NOT CREATED YET**

Latest console result:

`conda create -n ssd python=3.10 pip -y` was blocked by `CondaToSNonInteractiveError` because Anaconda Terms of Service have not been accepted for:

- `https://repo.anaconda.com/pkgs/main`;
- `https://repo.anaconda.com/pkgs/r`;
- `https://repo.anaconda.com/pkgs/msys2`.

No package transaction/model download occurred. This is not an SSD inference/model failure.

## Superseded route

The segmented-puppet runner 23 is no longer the current production route. It remains historical and must not be continued unless explicitly reopened.

Flux2 per-frame full-body redraw remains FAIL/CLOSED.

## CURRENT RUNNER

`tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

Runner 24 now requires explicit user opt-in before accepting Anaconda channel terms. Switch:

`-AcceptAnacondaTos`

Without the switch, the runner will not accept terms on the user's behalf.

With the switch, it:

1. accepts Anaconda ToS for the three channels listed above;
2. creates `ssd` with Python 3.10 + pip;
3. verifies via `conda run`;
4. writes `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`;
5. downloads no model weights;
6. installs no large SSD dependency stack.

## Exact next operator action

Only if the user agrees to the Anaconda Terms of Service for those channels:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\24_bootstrap_ssd_environment.ps1" `
  -AcceptAnacondaTos
```

Supplying `-AcceptAnacondaTos` is explicit authorization to perform the ToS acceptance commands.

PASS requires:

- console `SSD-ENV: PASS`;
- Python 3.10.x inside env `ssd`;
- local bootstrap marker written.

After PASS, next work is a controlled Windows dependency bootstrap based on the Moore-AnimateAnyone pinned stack, followed later by model downloads in a documented order.

## Do not clean SSD workspace

SSD route is active. No cleanup applies now.
