# Wan-Animate-2 validation spike — CLI only

Status: experimental offline character-animation tooling. It is not yet an accepted production animation pipeline.

ComfyUI runs locally as a background server and is controlled through command-line tooling / its local API. Manual graph editing is not part of the required operator workflow.

## Hardware target

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB RAM

## Current validated Base route

The originally planned public Base GGUF Q4_K_M route was superseded after that exact validated public file ceased to be available at the selected repository. No Distilled/TURBO model was silently substituted.

Current route:

- official Wan-Animate-2 **Base**;
- `wan_animate_2_int8_convrot.safetensors`;
- native ComfyUI `WanAnimate2ToVideo` support;
- FP8 UMT5 text encoder;
- CLIP Vision H;
- Wan 2.1 VAE;
- no LightX2V/distillation LoRA in Base validation;
- `D:\AI\WanAnimate2` isolated workspace by default.

`inspect.ps1` still recognizes a historical compatible Base Q4 GGUF installation when present, but runner 35 requires the official Base INT8 ConvRot route so the discriminant is not mixed with loader/quantization uncertainty.

## Original 17-frame spike inputs

Canonical character reference:

`ComfyUI/input/exilada_master.png`

Driving clip:

`ComfyUI/input/exilada_driver_17f.mp4`

Original driver contract:

- 17 frames;
- 384×576;
- 16 fps;
- H.264 / yuv420p;
- fixed camera;
- one full-body subject;
- first pose roughly matches the Exilada master;
- one small controlled step only.

## Runner 35 complete-motion use

Current Roguelite experiment:

`tools/structured-2d-character-pipeline/35_run_exilada_wan_animate2_complete_motion_proof.ps1`

Runner 35 replaces the generic test driver with:

`ComfyUI/input/exilada_complete_motion_driver_17f.mp4`

That driver is created deterministically from the current Exilada V2 gait and explicitly includes control motion for body, heavy hair, base cloth, subtle soft-body lag and wrist/ankle broken chains. It remains an offline motion-control proxy only; final runtime frames remain fully composed character sprites.

Runner 35 settings:

- 384×576;
- 17 driving/generated frames;
- seed 42;
- Euler;
- shift 5;
- 20 steps;
- no distillation LoRA;
- CPU model cache for the 12 GB VRAM target.

## Scripts

`bootstrap.ps1`

Creates/restores the isolated ComfyUI workspace and, only when explicitly run with `-UseOfficialBaseInt8`, downloads the official Base INT8 ConvRot model and required support models.

`make_driver.ps1`

Converts a user-supplied source motion clip into the original exact 17-frame validation driver.

`inspect.ps1`

Starts ComfyUI in the background, queries `/object_info`, validates required node classes/files and writes exact installed schemas to `object_info_spike.json`.

`build_workflow.py`

Patches the current official Wan Animate 2 template for the original simple Exilada 17-frame spike.

`build_workflow_complete_motion.py`

Patches the official template for runner 35 complete-motion transfer.

`run_spike.ps1`

Runs the original simple validation workflow. Runner 35 has its own top-level orchestrator and does not require manual invocation of `run_spike.ps1`.

## Rejection discipline

A strong visual failure rejects the candidate. Do not rescue it through seed fishing, reference redesign, cosmetic CFG/step tuning or manual frame-by-frame repair.

Infrastructure errors such as missing model files, wrong nodes, startup failures or OOM may be corrected because they are not visual evaluations of the model.
