# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA CURATED PASS / UNIFIED LIBRARY PASS / FIRST DRIVER GENERATED / QA NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_first_pose_driver_qa.ps1`;
6. `tools/video-studio/inspect_behavioral_pose_driver.py`.

## Hard constraints

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current CPU route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred;
- no Wan-Animate-2 until first multi-source pose driver passes numeric + visual QA.

## Curated sources

### Primary

`VID_20260911_140124885.mp4` — torso/hands/gesture/posture.

```text
123 total
118 eligible
5 excluded
24.1–37.5 s / u0012-u0016 excluded
```

### Secondary

`VID_20260819_124008056.mp4` — face/head/microexpression; body support only.

```text
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands disabled
face/head median weight 0.913145
```

### SIENA

`SIENA_BRUTO.mp4` — alternate posture/head/coarse arm.

```text
49 total
12 hard excluded
37 clean
hands disabled
generic whole-upper disabled
```

Locked SIENA exclusions:

```text
4.6–10.3 s    u0003-u0004
18.7–24.7 s   u0009-u0010
43.7–55.7 s   u0021-u0025
67.9–74.0 s   u0031-u0033
```

SIENA head/posture/coarse-arm reliability weights all saturated at 1.0, so they are currently non-discriminative. Do not claim these weights rank clean SIENA units; retrieval within SIENA is differentiated by motion/prosody/transition/duration.

## Unified library — PASS

Artifact:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

Observed:

```text
271 units total
primary 118
secondary 116
tertiary 37
```

Role counts:

```text
face 116
head 271
posture 271
coarse_arm 155
left/right/both_hands 118 each
generic_whole_upper 118
body_support 271
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## First pose driver — GENERATED / QA PENDING

Neutral QA target only: no target audio.

```text
duration 4.5 s
24 fps
108 frames
base order primary -> tertiary
planner boundary continuity = 0.528554
```

Selected provenance:

```text
window 0
base  primary:VID_20260911_140124885_u0114
hands primary:VID_20260911_140124885_u0114
face  secondary:VID_20260819_124008056_u0026

window 1
base  tertiary:SIENA_BRUTO_u0037
hands primary:VID_20260911_140124885_u0075
face  secondary:VID_20260819_124008056_u0105
```

Artifacts:

```text
...\unified\first_driver\driver_plan.json
...\unified\first_driver\behavioral_driver_coco133.jsonl
...\unified\first_driver\behavioral_driver_pose_preview.mp4
```

The planner continuity score has no canonical cutoff. Do not call the driver PASS from that number alone.

## Next exact action

Run numeric QA:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_qa.ps1'
```

It runs no DWPose and no Wan. It reports:

- out-of-bounds coordinates;
- frame-step jumps by body/head, face, left hand, right hand;
- boundary jump relative to the driver's own non-boundary q90;
- normalized arm-length distributions;
- inter-eye/shoulder ratio;
- hand-root/body-wrist attachment distances.

Then paste the complete terminal output and upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_pose_preview.mp4`

Visual preview + numeric diagnostics decide PASS/FAIL. If PASS, only then determine the exact installed Wan-Animate-2 conditioning interface and prepare the first render spike. If FAIL, patch pose synthesis rather than changing renderer.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
