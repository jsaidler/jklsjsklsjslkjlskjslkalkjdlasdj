# Wan-Animate-2 PRIMARY baseline result — 2026-09-20

## Runtime result

The isolated PRIMARY Wan-Animate-2 baseline inference completed successfully on the local RTX 3060 12 GB runtime.

Observed runtime:

```text
ComfyUI 0.34.0
Python 3.13.14
PyTorch 2.13.0+cu130
RTX 3060 12 GB
LOW_VRAM
DynamicVRAM enabled
wan_animate_2_bf16.safetensors
65 frames / 512x912 / 24 fps
30 sampling steps
sampling 01:17:19
prompt total 01:19:25
```

No OOM or execution error occurred. This establishes local runtime viability for the installed Wan-Animate-2 BF16 model under the current protected ComfyUI runtime.

## Output-selection bug

The first baseline runner copied every video reported in ComfyUI history into the run output directory. That list contained both:

1. the input driving-video passthrough `pose_video_primary_baseline65.mp4`;
2. the actual generated Wan output `wan_animate2_bf16_...mp4`.

The helper `assemble_if_frames()` then selected `videos[0]`, so the canonical file `wan_animate2_primary_baseline65.mp4` could become a copy of the driving input rather than the generated render. The uploaded baseline file therefore cannot be used for visual Wan QA.

This is a packaging/output-selection defect only. The server log proves that the Wan inference itself completed.

## Recovery

Versioned recovery runner:

`tools/video-studio/recover_wan_animate2_primary_baseline_output.ps1`

It finds the latest `primary-baseline-*` run, reads `run_manifest.json`, excludes the driver passthrough by exact filename/prefix, selects the actual generated Wan video, copies it as:

`wan_animate2_primary_baseline65_GENERATED.mp4`

and creates:

`wan_animate2_primary_baseline65_GENERATED_contact.jpg`

No inference is rerun.

## Classification

- local Wan-Animate-2 BF16 runtime: **PASS**;
- first prompt execution: **PASS**;
- uploaded canonical baseline MP4: **INVALID FOR VISUAL QA — driver passthrough selected by runner bug**;
- actual generated Wan output: **EXISTS / VISUAL QA PENDING RECOVERY**.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\recover_wan_animate2_primary_baseline_output.ps1'
```

Upload the recovered generated MP4 and generated contact sheet. Do not rerun inference.
