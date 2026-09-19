# Local Video Studio

Active local tooling for the Video Studio project.

Canonical state: `../../docs/PROJECT_STATE.md`  
Canonical route: `../../docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`  
Policy: `../../docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Current engineering problem

Behavioral identity: new speech must yield a new performance built from João's real gesture/posture/head/hand vocabulary, not generic presenter motion.

```text
multiple João behavioral videos
    -> local pose + motion + prosody
    -> per-source motion-unit profiles
    -> unified motion-unit library

new local speech
    -> prosody windows
    -> retrieve/sequence units across sources
    -> pose continuity + diversity + quality filters
    -> new João behavioral driver

behavioral driver
    -> installed Wan-Animate-2
    -> lip-sync later if required
```

A single source video is not the final library.

## Canonical behavior sources

```text
Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4
Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4
Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4
```

The first source is the current pipeline-validation source.

## Local pose stack — VALIDATED REUSE

Do not download DWPose.

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

CPU ONNX inference is validated. CUDA EP is not currently validated and should not be repaired unless CPU becomes a real blocker.

## `extract_dwpose_track.py`

Video -> normalized COCO WholeBody 133 JSONL adapter using the existing WanGP stack.

Current behavior:

- 6 fps full-source default;
- 960 px analysis long side;
- display-rotation aware;
- original COCO WholeBody 133 ordering;
- normalized coordinates `[0,1]`;
- detector fallback marker;
- summary JSON with geometry/provider/confidence/fallback/throughput.

Primary full pose result already passed:

```text
frames: 1801
analysis: 540x960
detector fallback: 0/1801
mean keypoint score: 0.7549247491487903
provider: CPUExecutionProvider
```

Primary full track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`

## `behavior_profile_schema_v1.json`

Persistent `behavior-profile/v1` schema. Each motion unit stores source/timing/RGB span, pose endpoints, head/hand/body activity, motion energy, speech/pause, available prosody and transition descriptors.

## `extract_behavior_profile.py`

Renderer-independent profile builder.

Current analysis:

- full external COCO WholeBody 133 pose track;
- pose confidence floor `0.20`;
- display-orientation-aware grayscale frame-difference motion energy at 6 fps;
- motion analysis preserves aspect ratio with 128 px long side;
- primary portrait source therefore uses 72x128, not distorted 128x72;
- mono 16 kHz audio RMS/dBFS + normalized energy;
- speech/pause evidence;
- unit segmentation prioritizing pause + low motion around a 2.2 s target.

Outputs:

```text
manifest.json
motion_units.csv
```

Required status:

```text
complete
```

`incomplete_pose` is diagnostic only.

## `inspect_behavior_profile.py`

Dependency-free post-build structural/inventory inspection.

Checks:

- schema + `status=complete`;
- manifest/CSV unit-count agreement;
- continuous source coverage;
- unique unit IDs;
- valid start/end `coco_wholebody_133` snapshots;
- availability of head/body/left-hand/right-hand/combined-hand activity;
- unit-duration, speech-class and boundary-reason distributions.

Writes `profile_inspection.json`.

## Current exact command

Build and inspect the first complete source profile:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_profile_primary.ps1'
```

The runner does not invoke Wan-Animate-2.

## After the primary profile passes

1. inspect motion-unit inventory and quality distributions;
2. annotate/exclude object-occluded or unusable spans;
3. process `VID_20260819_124008056.mp4`;
4. process `SIENA_BRUTO.mp4` with exclusions;
5. unify motion units while preserving source/timestamps;
6. compose a new 4–5 s multi-source behavioral performance;
7. only then run installed Wan-Animate-2;
8. lip-sync and final voice stage later.

## Stop conditions

Do not:

- install another Python merely because Windows `py -3.11` is unresolved;
- download another DWPose/ControlNet pose stack;
- download another large renderer;
- repair CUDA before evidence that it is needed;
- accept a single-source library as final João behavior;
- install MuseTalk/LatentSync yet;
- run Wan-Animate-2 before behavior inventory/synthesis validation.

The quality criterion remains:

> this does not merely look like João; it moves and reacts like João.
