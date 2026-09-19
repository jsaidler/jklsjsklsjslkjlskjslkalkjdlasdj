# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA CURATED PASS / UNIFIED LIBRARY PASS / FIRST DRIVER GENERATED / QA v2 NEXT**

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

SIENA head/posture/coarse-arm reliability weights all saturated at 1.0 and are non-discriminative. Retrieval within SIENA is differentiated by motion/prosody/transition/duration.

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

## Numeric QA v1 — COMPLETE / NOT SUFFICIENT FOR VERDICT

Observed:

```text
all-finite OOB 2568/14364 = 0.178780
exact boundary jump = 0.0 in all groups
left/right hand-root to body-wrist = 0.0
```

Do not interpret these raw numbers as PASS/FAIL:

- OOB v1 counted finite low-confidence landmarks together with reliable landmarks;
- exact boundary jump is zero by construction because the current compositor starts the 0.25 s blend from the previous pose;
- continuity must be judged across the whole transition window, not one pair of frames.

## Numeric QA v2 — NEXT

`inspect_behavioral_pose_driver.py` now emits `behavioral-pose-driver-qa/v2` with:

- all-finite OOB and confidence-qualified OOB separated;
- confidence-qualified OOB by coarse head / upper body / lower body-foot / face / left hand / right hand;
- exact boundary retained only as explanatory diagnostic;
- complete 0.25 s transition-window q90/max for body/head, face and each hand;
- transition q90/max divided by the driver's own non-transition q90.

## Next exact action

Run the revised QA against the already-generated driver; do not regenerate it:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_qa.ps1'
```

Then paste the complete v2 terminal output and upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_pose_preview.mp4`

Visual preview + v2 numeric diagnostics decide PASS/FAIL. If PASS, inspect the exact installed Wan-Animate-2 conditioning interface and prepare the first render spike. If FAIL, patch pose synthesis rather than changing renderer.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
