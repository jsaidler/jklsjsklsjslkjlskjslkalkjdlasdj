# Local Video Studio — resolution / detail diagnosis

Date: **2026-09-15**  
Status: **ACTIVE BLOCKER / NOT PRODUCTION-APPROVED**

Canonical quality gate: `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`.

## User-visible problem

The generated talking-video clips look noticeably softer / lower-detail than the desired publication standard even when the generation is run on the current 768-class vertical canvas.

This is now a separate quality blocker from anatomy, hand motion, gesture naturalness, face stability and scene compliance.

## Measured benchmark outputs

The two uploaded quality-gate files were inspected directly.

### `production_00001_.mp4` — legacy Turbo4 baseline

- encoded frame size: **768 × 1344**;
- frame rate: **24 fps**;
- duration: **8.0 s**;
- codec: H.264 / yuv420p;
- measured video bitrate: approximately **1.70 Mbit/s**;
- measured total file bitrate: approximately **1.84 Mbit/s**.

### `quality_00001_.mp4` — Base20 candidate

- encoded frame size: **768 × 1344**;
- frame rate: **24 fps**;
- duration: **8.0 s**;
- codec: H.264 / yuv420p;
- measured video bitrate: approximately **1.06 Mbit/s**;
- measured total file bitrate: approximately **1.20 Mbit/s**.

Therefore the files are not accidentally being written at 480p or another smaller canvas. The perceived low resolution comes from **effective detail**, not merely the MP4 width/height metadata.

## Root-cause layers

### 1. H3-Base local ceiling

The open/local MiniMax H3 Base pipeline is a **768p-class generator**. The official H3 architecture describes the complete system as:

`H3-Context-IR -> H3-Base 768p -> H3-Regenerate-2K`

The official 2K stage is an in-context regeneration pass that uses the low-resolution result together with the original multimodal context. As of this date, MiniMax states that **H3-Regenerate-2K is not yet open-sourced**; official 2K validation is provided through the MiniMax API.

Consequences:

- increasing the local H3 Base canvas beyond its normal 768-short-edge regime is not equivalent to the official 2K path;
- Base20/Base50 can improve denoising / temporal structure but cannot by themselves remove the native 768p detail ceiling;
- a local publication pipeline needs either a high-quality post-generation video restoration/upscale stage or a different video engine that natively produces more detail.

Official references:

- `https://github.com/MiniMax-AI/MiniMax-H3`
- `https://www.minimax.io/news/minimax-h3-open-source`

## 2. Effective detail is lower than nominal pixels

Frame inspection shows that the face, beard/hair, skin, hands and background surfaces have less stable high-frequency detail than a real 768×1344 camera recording would have. This is a generation/VAE issue rather than a metadata issue.

The output can therefore be 768×1344 while still *looking* substantially lower-resolution.

## 3. Output encoding is also too weak for a quality benchmark

The current Video Studio graph writes the generated video through `SaveVideo` using H.264 without an explicit low-CRF quality target.

Measured benchmark bitrates are low for 768×1344 / 24 fps material, especially the Base20 result (~1.06 Mbit/s video). Compression is therefore a confounding variable on top of the H3 Base softness.

Before judging an upscaler or another model, the benchmark must remove this avoidable loss.

## Correct next experiment — VIDEO-STUDIO-RESOLUTION-01

One H3 inference must feed **two SaveVideo outputs from the exact same decoded frames**:

1. current/automatic H.264 path;
2. H.264 re-encode at **CRF 14**.

Because both files come from the same decoded frame tensor, any visible difference is codec-only. No second diffusion generation is needed.

If CRF14 materially improves the image, the Studio encoder becomes an immediate quality fix.

If CRF14 looks essentially the same, the softness is upstream (H3 Base / VAE / generated detail), which is the expected primary outcome.

## Local super-resolution candidates after codec isolation

Do not confuse ordinary resize with restoration. `ffmpeg scale=1080:1920` only creates more pixels and cannot reconstruct missing detail.

Candidates for a controlled local video-restoration test include:

- **SeedVR2** — preferred first high-quality open local candidate because it is designed for temporally coherent video upscaling and has a consumer-GPU / low-VRAM path;
- **RTX Video Super Resolution** — fast NVIDIA path if the ComfyUI RTX node is already available and stable on this Windows installation; useful as a speed baseline, but not assumed to be the best quality;
- **FlashVSR** — possible faster local alternative if SeedVR2 proves too slow or too heavy.

The RTX 3060 12 GB must be tested on a short clip before any tool is promoted. No upscaler is considered production-safe until temporal consistency, face identity, beard/hair, glasses, hands and background geometry are reviewed frame-to-frame.

## Decision rule

1. finish the codec-isolation test;
2. keep Base20/Base50 evaluation focused on structural/temporal quality, not on solving the native resolution ceiling;
3. test one local video-restoration/upscale candidate on the best H3 clip;
4. compare the restored result against the untouched decoded H3 result at 100% and normal viewing size;
5. if local restoration cannot reach publication quality, compare another base video engine rather than stacking more sharpening/upscaling stages.

Current classification remains:

**FUNCTIONAL / ARCHITECTURAL PASS — PRODUCTION QUALITY FAIL.**
