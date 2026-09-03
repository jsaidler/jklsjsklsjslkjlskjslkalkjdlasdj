# Local sprite-animation pipeline

Status: **experimental production spike**. This tool does not prove the final art pipeline yet; it exists to test whether the approved Exilada reference can be converted into coherent animation without manually drawing every frame.

## Why this implementation

The original **Sprite Sheet Diffusion (SSD)** paper/repository fine-tuned AnimateAnyone for game sprites, but the trained custom SSD pose-guider checkpoint was never released. Therefore the upstream Python inference cannot reproduce the exact paper stack from publicly available weights.

This tool uses the currently runnable hybrid documented by the `fszontagh/stable-diffusion.cpp` Sprite-Sheet-Diffusion port:

- SSD fine-tuned **denoising UNet**;
- SSD fine-tuned **ReferenceNet**;
- Moore/patrolli AnimateAnyone baseline **pose guider**;
- Moore/patrolli AnimateAnyone baseline **motion module**;
- SD image-variations CLIP vision encoder;
- `sd-vae-ft-mse` VAE.

This is deliberate and documented. It must not be described as the exact unreleased SSD checkpoint stack.

## Target machine

Primary target for this project:

- Windows 11
- NVIDIA RTX 3060 12 GB
- 48 GB system RAM
- Intel i7-12700

The C++ port documents a measured RTX 3060 recipe using FP16, CPU offload and flash attention. At 512x640 / 25 steps it reports about **7.4 GB peak VRAM for 8 video frames**. For our taller 512x768 quality profile the script additionally enables VAE tiling.

## One-time prerequisites

Install these before running `install.ps1`:

1. Current NVIDIA driver.
2. **Visual Studio 2022 Build Tools**, workload **Desktop development with C++**.
3. A current **CUDA Toolkit 12.x** (must provide `nvcc.exe`).
4. Git for Windows.
5. CMake.
6. Python 3.10 or newer.

Convenient commands for the small prerequisites:

```powershell
winget install --id Git.Git -e
winget install --id Kitware.CMake -e
winget install --id Python.Python.3.10 -e
```

Visual Studio Build Tools and CUDA Toolkit should be installed with their normal installers so their C++/CUDA components are actually present.

## Install

From the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
cd tools\sprite-animation
.\install.ps1
```

`install.ps1` will:

1. clone `fszontagh/stable-diffusion.cpp` branch `feat/sprite-sheet-diffusion`;
2. build `sd-cli.exe` with CUDA;
3. create the small Python utility environment;
4. download the required model files;
5. verify pinned SHA256 hashes where known;
6. generate the canonical 24 driving-pose frames for the walk experiment.

Large model files, the C++ checkout/build, generated poses, and generated animation outputs are ignored by git.

## First Exilada test

Use the approved **Frame 1 canonical Exilada PNG** as `-Reference`.

Fast smoke test:

```powershell
.\run_walk.ps1 -Reference "C:\path\to\exilada_frame1.png" -Profile smoke
```

Quality test:

```powershell
.\run_walk.ps1 -Reference "C:\path\to\exilada_frame1.png" -Profile quality
```

Quality profile:

- 512x768
- 25 denoising steps
- CFG 3.5
- seed 42 by default
- FP16
- CPU offload
- flash attention
- VAE tiling
- 24 pose frames (8-frame walk cycle repeated three times)

The repetition is intentional. The AnimateAnyone motion module was trained around a 24-frame context; the C++ port reports visible late-window drift at only 8 frames. `build_spritesheet.py` keeps the **middle 8 frames** from the generated 24-frame window.

Outputs are written under `tools/sprite-animation/output/`:

- animated WebP;
- horizontal 8-frame PNG sprite sheet;
- JSON manifest with frame dimensions, FPS and anchor.

## Pose policy

`prepare_walk_poses.py` generates BODY_18/OpenPose-style RGB skeletons rather than asking a generative model to invent each frame independently.

For the Exilada test the poses deliberately:

- preserve adult human proportions;
- keep framing stable;
- omit face and hand landmarks;
- use the same 8 biomechanical walk phases each run;
- repeat the cycle to fill the 24-frame motion context.

The pose images are deterministic and can be regenerated at any target resolution.

## Pass/fail gate

This experiment passes only if the generated middle walk cycle:

1. unmistakably remains the approved Exilada;
2. preserves her adult proportions, face, hair, clothing and curved blade;
3. has no extra limbs/props or major costume drift;
4. cycles without obvious temporal popping;
5. is good enough that cleanup is mechanical/post-process work rather than frame-by-frame redrawing.

If those conditions fail, this pipeline is rejected. We do not rescue it by manually repainting dozens of frames.
