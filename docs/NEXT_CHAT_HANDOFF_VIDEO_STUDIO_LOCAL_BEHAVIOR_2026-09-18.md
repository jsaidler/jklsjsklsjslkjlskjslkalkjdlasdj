# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **FULL PRIMARY POSE TRACK PASS / PRIMARY BEHAVIOR PROFILE BUILD NEXT**

## Continue from canonical state

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. this file;
6. `tools/video-studio/extract_behavior_profile.py`;
7. `tools/video-studio/inspect_behavior_profile.py`;
8. `tools/video-studio/run_behavior_profile_primary.ps1`.

GitHub living docs are source of truth. Do not reconstruct state from memory when docs differ.

## Hard constraints

- 100% local/self-hosted;
- zero service cost;
- never upload João's video/voice/identity to third parties;
- no SaaS/paid API/credits/subscriptions;
- do not download another large renderer;
- do not reopen Wan S2V, H3, Hunyuan or HeyGen as next route;
- no new Python/DWPose/CUDA install while current local route works;
- MuseTalk/LatentSync/TTS remain deferred.

## Goal

New text/audio must eventually produce a new performance that looks, sounds and chiefly **moves/reacts like João**. Generic presenter motion is failure.

## Multi-source requirement — LOCKED

The final behavior library must **not** use only one video.

Canonical sources:

- `VID_20260911_140124885.mp4` — torso/hands/posture/gesture primary;
- `VID_20260819_124008056.mp4` — head/face/microexpression source;
- `SIENA_BRUTO.mp4` — additional gesture/posture source with object/occlusion exclusions.

The first source is being completed first only to validate the full pipeline. After its profile passes, process the other two and unify all motion units while preserving source/timestamps.

## Validated local pose stack

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

DWPose functional runtime: PASS.

CUDA ONNX Runtime remains unvalidated because `cublasLt64_13.dll` is absent. CPU is the validated path; do not install CUDA dependencies yet.

## Orientation corrections

Primary video is coded 3840x2160 but displayed portrait with 90° stream rotation.

Pose extraction is now display-orientation aware:

- display: 2160x3840;
- DWPose analysis: 540x960.

Behavior-profile motion analysis is also now display-orientation aware. It preserves aspect ratio at 128 px long side, so the primary portrait source uses **72x128**, not 128x72.

## Visual pose gate — PASS

Clean gate C3 = 88.7–93.7 s passed after orientation correction:

- face aligned;
- upper-body anatomy aligned;
- both hands tracked through gestures;
- no subject switch;
- no gross left/right swap or upper-body temporal jump.

Behavior metrics ignore points below confidence 0.20.

## Full primary pose track — PASS

Completed result:

```text
source_duration_s: 300.352
coded: 3840x2160
display: 2160x3840
rotation_degrees: 90
sample_fps: 6.0
analysis: 540x960
frames: 1801
last_timestamp_s: 300.0
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.7549247491487903
provider: CPUExecutionProvider
elapsed_s: 2780.1648166179657
frames_per_second_wall: 0.6478033205926593
```

Track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`

Classification: **FULL PRIMARY POSE TRACK PASS.**

## Next exact action

Run the versioned primary profile builder:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_profile_primary.ps1'
```

It:

1. uses the existing full `pose_coco133.jsonl`;
2. computes display-orientation-aware motion energy;
3. computes local RMS/prosody descriptors;
4. segments motion units;
5. writes `manifest.json` + `motion_units.csv`;
6. runs `inspect_behavior_profile.py` immediately;
7. writes `profile_inspection.json`.

Required profile status: **`complete`**.

Do not synthesize a driving performance if structural inspection fails.

## After primary-profile PASS

1. inspect the actual motion-unit inventory and quality distributions;
2. mark/exclude/down-weight object-occluded or unusable spans;
3. process `VID_20260819_124008056.mp4` through the same pipeline;
4. process `SIENA_BRUTO.mp4` through the same pipeline with exclusions;
5. build unified multi-source João motion-unit library;
6. synthesize a new 4–5 s performance from multiple units/sources;
7. only then invoke installed Wan-Animate-2.

## Final human quality gate

> “isso não apenas parece João; isso se move e reage como João.”
