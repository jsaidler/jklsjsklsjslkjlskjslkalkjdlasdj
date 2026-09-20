# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-20**  
Status: **PRIMARY/SECONDARY/SIENA CURATED PASS / UNIFIED LIBRARY PASS / DRIVER v3 POSE PASS / WAN RAW-RGB CONTRACT VERIFIED / PRIMARY WAN BASELINE PASS / CROSS-SOURCE SIENA WAN GATE NEXT**

Continue in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. this file
3. `tools/video-studio/run_wan_animate2_cross_source_siena_render.py`
4. `tools/video-studio/run_wan_animate2_cross_source_siena_render.ps1`

## Hard constraints

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions/cloud generation;
- no new large renderer;
- no new Python/DWPose/CUDA install while current route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/CosyVoice remain deferred;
- do not invalidate the curated source/library/pose system because of downstream RGB/render failures;
- use only the installed Wan-Animate-2 BF16 path;
- long local passes must emit heartbeat/progress.

## Canonical source/library state

```text
PRIMARY   VID_20260911_140124885.mp4   118 eligible   torso/hands/gesture/posture
SECONDARY VID_20260819_124008056.mp4   116 face/head/body-support eligible
SIENA     SIENA_BRUTO.mp4               37 clean      posture/head/coarse-arm
UNIFIED   271 units total
```

SIENA exclusions remain locked:

```text
4.6–10.3 s    u0003-u0004
18.7–24.7 s   u0009-u0010
43.7–55.7 s   u0021-u0025
67.9–74.0 s   u0031-u0033
```

## Behavioral pose driver v3 — PASS

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3`

Selected:

```text
window 0
base  primary:VID_20260911_140124885_u0041
hands primary:VID_20260911_140124885_u0117
face  secondary:VID_20260819_124008056_u0046

window 1
base  tertiary:SIENA_BRUTO_u0035
hands primary:VID_20260911_140124885_u0118
face  secondary:VID_20260819_124008056_u0047
```

Key QA:

```text
transition-only OOB 0% all groups
body transition q90 ratio 0.792506x
face 1.411900x
left hand 0.682394x
right hand 0.944349x
```

Classification: **FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 PASS**.

## Wan contract — VERIFIED

Installed node: `WanAnimate2ToVideo`.

Important facts:

```text
pose_video type = IMAGE
pose_video is RGB video frames, resized and VAE-encoded directly
no COCO/OpenPose/DWPose conversion inside node
no separate face_video input
```

Therefore COCO-133 remains canonical behavior representation, but Animate2 needs RGB driving frames.

## Failed RGB adapter routes — DO NOT RESUME

- Delaunay still-frame warp: stalled before frame 1;
- IDW still-frame remap: completed but severe anatomical melting;
- PRIMARY+SIENA raw RGB xfade: double-exposed source/acquisition transition.

These failures do not invalidate v3 pose composition.

## First actual Wan render — PASS

Run:

`Z:\AI\VideoStudioRuns\wan-animate2-behavior\primary-baseline-20260920_113651`

Actual generated output:

`wan_animate2_bf16_exilada_aspectmatched_ref10_pose080_steps30_00001_.mp4`

Runtime:

```text
RTX 3060 12GB / LOW_VRAM
65 frames / 512x912 / 24 fps
30 steps
sampling 01:17:19
prompt total 01:19:25
no OOM / no execution_error
```

Visual QA: stable identity/background, recognizable transferred motion, no material anatomy collapse.

Classification: **WAN-ANIMATE-2 PRIMARY BASELINE RENDER PASS**.

Known bug in the old baseline runner: it labeled the first returned MP4 as final, but that file was the driving input. The real generated MP4 was the second returned video. Do not rerun the baseline just to fix naming.

## Current next gate — CROSS-SOURCE SIENA

Purpose: isolate whether Wan can take motion from a different acquisition domain while PRIMARY reference controls identity/appearance.

Inputs:

```text
reference: PRIMARY u0041 midpoint
driver:    SIENA u0035 real RGB span
65 frames / 512x912 / 24 fps
same BF16 Animate2 runtime
```

Versioned:

- `tools/video-studio/run_wan_animate2_cross_source_siena_render.py`
- `tools/video-studio/run_wan_animate2_cross_source_siena_render.ps1`

The new runner selects the generated output deterministically and will not confuse the driving input with the Wan result.

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_wan_animate2_cross_source_siena_render.ps1'
```

Expected runtime: roughly the prior ~80 minutes.

Upload:

`wan_animate2_cross_source_siena65_GENERATED.mp4`

If this passes, investigate and implement Animate2 `continue_motion`/chunking to join source-specific generated spans under one stable reference identity instead of raw RGB xfade.

Final quality criterion:

> isso não apenas parece João; isso se move e reage como João.
