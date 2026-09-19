# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / FULL PRIMARY POSE PASS / PRIMARY BEHAVIOR PROFILE BUILD NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`  
Preflight: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: posture, head movement, hands, gesture timing, expressions and delivery rhythm.

Generic plausible motion is not sufficient.

## Selected architecture — LOCKED

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source motion-unit profiles
    -> unified João motion-unit library

new local speech/audio
    -> prosodic windows
    -> multi-source motion-unit retrieval
    -> pose continuity + diversity + quality constraints
    -> NEW João driving performance

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later only if needed
```

The final behavior library cannot be one fixed clip or one source video.

## Behavioral sources

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture source;
- `VID_20260819_124008056.mp4` — facial/head/microexpression source;
- `SIENA_BRUTO.mp4` — alternate gesture/posture source with unusable object/occlusion spans excluded or down-weighted.

The first video is processed first only to validate the complete pipeline.

## Renderer — downstream and already available

Installed Wan-Animate-2 is the priority renderer. No new large renderer is justified before the behavior library and synthesis path are validated.

## Behavior-profile v1

Versioned:

- `tools/video-studio/behavior_profile_schema_v1.json`;
- `tools/video-studio/extract_behavior_profile.py`;
- `tools/video-studio/inspect_behavior_profile.py`;
- `tools/video-studio/run_behavior_profile_primary.ps1`.

Every motion unit stores source/timing, RGB span, start/end pose, head/hand/body activity, motion energy, speech/pause evidence, available prosody and transition quality.

A pose-less run is `status=incomplete_pose` and never passes.

## Pose representation

The adapter preserves original **COCO WholeBody 133** output from lower-level WanGP DWPose.

Behavior-profile v1 activity groups:

- head: 0–4;
- body: 5–12;
- left hand: 91–111;
- right hand: 112–132.

`CONF = 0.20`; lower-confidence points are ignored.

## Local DWPose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

Runtime inference: PASS. CUDA ONNX Runtime remains unvalidated; CPU is the validated path.

## Orientation handling — FIXED

Primary source is coded 3840x2160 but displayed portrait at 2160x3840 via 90° stream rotation.

Pose extraction now derives geometry from display dimensions and uses **540x960** analysis.

Behavior-profile motion analysis was also corrected to preserve display aspect ratio with a 128 px long side. Primary portrait motion analysis is **72x128**, not 128x72.

## Visual upper-body gate — PASS

Canonical clean gate: **C3 = 88.7–93.7 s**.

Corrected portrait overlay passed for face, upper body, hands, subject continuity, left/right consistency and temporal stability.

## Full primary pose extraction — PASS

Result:

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
```

Full track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`

Classification: **PASS**.

## Primary behavior-profile build — NEXT

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_profile_primary.ps1'
```

The runner builds and then structurally inspects:

- `manifest.json`;
- `motion_units.csv`;
- `profile_inspection.json`.

Required status: `complete`.

Structural inspection checks schema/status, source coverage, timeline continuity, CSV/manifest unit count, valid 133-point pose snapshots and availability of head/body/hand activity. Inventory distributions are reported without pretending that one numeric threshold proves behavioral quality.

## After primary-profile PASS

1. inspect actual motion-unit inventory and distributions;
2. annotate/exclude object-occluded or unusable spans;
3. process `VID_20260819_124008056.mp4`;
4. process `SIENA_BRUTO.mp4` with exclusions;
5. unify all source-preserving motion units;
6. synthesize a new 4–5 s performance from multiple units/sources;
7. only then invoke installed Wan-Animate-2.

## Prosody v1

Implemented:

- speech/pause;
- RMS dBFS;
- normalized audio energy.

Pitch remains intentionally `null` until a validated local method is needed.

## Stop conditions

- no new large renderer download;
- no DWPose download;
- no blind Python/CUDA install;
- no `incomplete_pose` accepted as valid;
- no single-source library accepted as final João behavior;
- no Wan-Animate-2 render before behavior inventory/synthesis validation;
- no generic plausible motion accepted as João behavior.
