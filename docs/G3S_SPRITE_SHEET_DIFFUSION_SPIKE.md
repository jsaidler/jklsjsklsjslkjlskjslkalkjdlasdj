# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — ENVIRONMENT PASS / DEPENDENCIES PASS / MODEL DOWNLOAD RUNNER READY**

## Decision

The character-production target is a conventional **2D spritesheet**: approved persistent frames arranged by action in rows/blocks or equivalent atlas regions, with metadata for timing, pivots, hitboxes and events as needed.

The active offline source-authoring spike is **Sprite Sheet Diffusion (SSD)**, using the complete Exilada master as appearance reference plus pose/motion guidance. SSD is a production tool under validation, not a runtime dependency.

## Presentation/runtime lock retained

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime is ordinary spritesheet playback, not 3D, puppet assembly or diffusion.

## Verified upstream layout

Upstream: `https://github.com/chenganhsieh/Sprite-Sheet-Diffusion`

- inference entry point: `ModelTraining/inference.py`;
- prompt config: `ModelTraining/configs/prompts/inference.yaml`;
- actual dependency file: `ModelTraining/requirements.txt`;
- no root `requirements.txt` despite the README command;
- upstream `pretrained_model/download.sh` confirms the SD1.5 UNet, SD VAE and CLIP vision image encoder layout used by inference;
- SSD config also requires `denoising_unet.pth`, `reference_unet.pth`, `pose_guider.pth` and `motion_module.pth`.

## Environment bootstrap — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Runner: `tools/structured-2d-character-pipeline/24_bootstrap_ssd_environment.ps1`

Actual validated state:

- clone: PASS;
- Miniconda: PASS;
- `conda.exe`: `C:\Users\jsaid\miniconda3\Scripts\conda.exe`;
- env `ssd`: PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_environment_bootstrap.json`.

## Windows inference dependencies — PASS

Runner: `tools/structured-2d-character-pipeline/25_bootstrap_ssd_dependencies.ps1`

The first version of runner 25 had a PowerShell native-process control-flow bug. That bug was fixed and the rerun supplied by the user is now **PASS**.

Validated console result:

- `SSD-DEPS: PASS`;
- GPU: `NVIDIA GeForce RTX 3060`;
- Torch: `2.0.1+cu118`;
- CUDA build: `11.8`;
- real SSD inference import graph: PASS;
- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependencies_bootstrap.json`;
- freeze: `Z:\AI\SpriteSheetDiffusionSpike\ssd_dependency_freeze.txt`.

No model/checkpoint was downloaded by the dependency gate.

## Native-process scripting rule — LOCKED

For subsequent project PowerShell runners:

1. do not use an expected native-process failure as raw control flow under `$ErrorActionPreference='Stop'`;
2. do not depend on native STDERR/`2>&1` to decide expected states;
3. Python probes must catch expected exceptions and emit structured diagnostics;
4. native calls must have explicitly inspected exit codes;
5. project failure must end as a controlled `FAIL`, not an unhandled `NativeCommandError`.

Runner 26 therefore keeps the large network/download logic inside a Python helper and invokes it as one controlled process.

## Model download decision — MINIMAL INFERENCE SET

Manifest:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Runner:

`tools/structured-2d-character-pipeline/26_download_ssd_models.ps1`

Destination root matching the upstream default config:

`Z:\AI\SpriteSheetDiffusionSpike\repo\ModelTraining\pretrained_model`

Estimated download: **~13.7 GB**. The runner checks remaining free space before starting, resumes `.part` files and verifies known SHA256 values.

### Files

1. Stable Diffusion v1.5 UNet
   - `stable-diffusion-v1-5/unet/config.json`
   - `stable-diffusion-v1-5/unet/diffusion_pytorch_model.bin`
   - expected UNet SHA256: `c7da0e21ba7ea50637bee26e81c220844defdf01aafca02b2c42ecdadb813de4`

2. Stability AI MSE VAE
   - `sd-vae-ft-mse/config.json`
   - `sd-vae-ft-mse/diffusion_pytorch_model.safetensors`
   - expected weights SHA256: `a1d993488569e928462932c8c38a0760b874d166399b14414135bd9c42df5815`

3. Lambda CLIP vision image encoder
   - `image_encoder/config.json`
   - `image_encoder/pytorch_model.bin`
   - expected weights SHA256: `89d2aa29b5fdf64f3ad4f45fb4227ea98bc45156bbae673b85be1af7783dbabb`

4. SSD fine-tuned weights, community re-host preserving the recovered upstream release
   - `denoising_unet.pth`
   - expected SHA256: `341cca53cfaa4e0c05098e511b8a3dc1a0db90c6ec68f345ba14115e0d3e43ac`
   - `reference_unet.pth`
   - expected SHA256: `84194364a42b5ae8b2a93a60b02a36ed0f989c230bb4c3ee33d7956bba5d0dcc`

5. AnimateAnyone baseline components
   - `pose_guider.pth`
   - expected SHA256: `1a8b7c1b4db92980fd977b4fd003c1396bbae9a9cdea00c35d452136d5e4f488`
   - `motion_module.pth`
   - expected SHA256: `0d11e01a281b39880da2efeea892215c1313e5713fca3d100a7fbb72ee312ef9`

## Intentionally not downloaded in this gate

- `wav2vec2-base-960h` — not used by the selected `ModelTraining/inference.py` path;
- DWPose models — the first smoke test will provide pose images directly rather than detecting poses from a raw driving video;
- `film_net_fp16.pt` — frame interpolation is loaded only with `--accelerate`; first smoke test will not use it;
- AnimateAnyone baseline denoising/reference UNets — they must not replace the SSD fine-tuned UNets.

## Runner 26 behavior

- requires environment and dependency PASS markers;
- uses the environment's `python.exe` directly;
- downloads directly over resumable HTTP rather than creating a second Hugging Face cache copy;
- uses `.part` files and resumes when the server supports byte ranges;
- verifies size and known SHA256 after every large file;
- removes a downloaded file if its enforced hash is wrong;
- writes `Z:\AI\SpriteSheetDiffusionSpike\ssd_models_bootstrap.json`;
- loads no checkpoint into Torch and performs no inference.

## Current exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\26_download_ssd_models.ps1"
```

## Model gate PASS

PASS requires:

- `SSD-MODELS: PASS`;
- all ten manifest entries present;
- known large-file hashes verified;
- local marker `Z:\AI\SpriteSheetDiffusionSpike\ssd_models_bootstrap.json` written.

After model PASS, the next gate is **input/config preparation + first 8-frame Exilada inference** using the complete master and an 8-state walk pose sequence.

## Cleanup if SSD is explicitly discarded

```powershell
Remove-Item -LiteralPath "Z:\AI\SpriteSheetDiffusionSpike" -Recurse -Force -ErrorAction SilentlyContinue
& "C:\Users\jsaid\miniconda3\Scripts\conda.exe" env remove -n ssd -y
```

SSD is ACTIVE, so no cleanup applies now.
