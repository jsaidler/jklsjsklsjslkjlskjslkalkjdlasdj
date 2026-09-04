# Wan-Animate-2 validation spike — CLI only

Status: experimental validation tooling. This is not an accepted production animation pipeline.

The spike is intentionally operated without manual ComfyUI graph editing. ComfyUI runs locally as a background server and is controlled through command-line tooling / its local API.

## Hardware target

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB RAM

## Model path

- Wan-Animate-2 Base
- GGUF Q4_K_M
- `model_type=animate2` must be injected by `RebelsGGUFUnetLoaderMeta`
- `model class=WAN_Animate2` in the ComfyUI log is mandatory proof that the correct architecture was loaded
- no LightX2V/distillation LoRA in the Base validation spike

## Inputs

Canonical character reference:

`ComfyUI/input/exilada_master.png`

Driving clip:

`ComfyUI/input/exilada_driver_17f.mp4`

Driver contract:

- 17 frames
- 384×576
- 16 fps
- H.264 / yuv420p
- fixed camera
- one full-body subject
- first pose roughly matches the Exilada master
- one small controlled step only

## Scripts

`bootstrap.ps1`

Creates an isolated ComfyUI workspace (default `D:\AI\WanAnimate2`), installs the two required custom-node repositories, installs dependencies and downloads only the Base Q4_K_M model plus required FP8 text encoder, CLIP Vision and VAE.

`make_driver.ps1`

Converts a user-supplied source motion clip into the exact 17-frame validation driver with ffmpeg.

`inspect.ps1`

Starts ComfyUI in the background, queries `/object_info`, validates the required node classes and files, and writes the exact installed schemas to `object_info_spike.json`.

The headless API workflow must be generated against these actual installed schemas rather than guessed from a UI screenshot.

## Rejection discipline

A strong visual failure rejects the candidate. Do not rescue it through seed fishing, reference redesign, cosmetic CFG/step tuning or manual frame-by-frame repair.

Infrastructure errors (wrong model class, missing node, OOM) may be corrected because they do not constitute a visual evaluation of the model.
