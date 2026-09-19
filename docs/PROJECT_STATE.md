# Local Video Studio — Current Project State

Status date: **2026-09-19**

GitHub living documents are the canonical source of truth.

## Execution policy — LOCKED

- 100% local/self-hosted;
- zero service cost;
- no SaaS/cloud generation/training/inference;
- never upload João's video/voice/identity to third parties;
- no new large renderer while this route is active;
- no new Python/DWPose/CUDA install while the validated local route works;
- Wan S2V, H3, Hunyuan and HeyGen remain historical/retired;
- MuseTalk/LatentSync/CosyVoice remain deferred.

## Objective — LOCKED

Generate new video from new text/audio that looks, sounds and chiefly **moves/reacts like João**. Generic plausible presenter motion is failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior-profile/v1 motion units
    -> optional aligned facial-behavior-profile/v1 sidecar
    -> source-specific semantic + role-aware quality curation
    -> unified source-preserving João motion library

new local speech/audio
    -> prosodic windows
    -> retrieve by source role + quality + continuity + diversity
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A single source video is never the final library, and different sources do **not** have interchangeable roles.

## Canonical sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

1. `VID_20260911_140124885.mp4` — 300.352 s — torso/hands/posture/gesture primary;
2. `VID_20260819_124008056.mp4` — 282.574 s — head/face/microexpression;
3. `SIENA_BRUTO.mp4` — 113.3 s — alternate gesture/posture with object/occlusion exclusions.

## Local pose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

Validated provider: `CPUExecutionProvider`. CUDA ORT remains intentionally unrepaired because its EP reported missing `cublasLt64_13.dll` while CPU is functional.

## Primary source — CURATED PASS

```text
full pose frames: 1801
fallback: 0/1801
mean keypoint score: 0.7549247491
behavior-profile/v1: complete
motion units: 123
```

Manual generic-behavior exclusion:

**24.1–37.5 s = `u0012`–`u0016`** due held object / hand occlusion / prop-specific interaction.

Final primary curation:

```text
123 total
118 eligible
5 hard excluded
```

Role: torso/hands/posture/gesture. Group quality remains continuous rather than using one global rejection threshold.

Artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_inventory.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_motion_units.csv
```

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — BASE PROFILE + FACIAL SIDECAR STRUCTURAL PASS

Source: `VID_20260819_124008056.mp4`  
Role: **face/head/microexpression**.

### Pose / geometry

Validated C3 facial gate: **83.6–88.6 s**.

```text
coded: 1920x1080
display: 1080x1920
rotation: 90
analysis: 540x960
C3: 30 frames @ 6 fps, 0 fallback
```

Full pose:

```text
1695 frames @ 6 fps
1/1695 detector fallback
mean whole-body keypoint score: 0.5453589803
CPUExecutionProvider
```

Classification: **SECONDARY FULL POSE TRACK PASS**.

### Base behavior-profile/v1

```text
status: complete
units: 119
coverage: 0.0 -> 282.574 s
pose snapshots valid: 119/119
head activity: 119/119
body activity: 119/119
left-hand activity: 37/119
right-hand activity: 20/119
combined-hand activity: 38/119
speech: mixed=84, pause=1, speech=34
unit duration min/median/max: 0.800/2.500/3.800 s
```

Sparse hands are **not a source failure** because this source is not a hand/gesture source.

### Facial sidecar architecture — LOCKED

Keep `behavior-profile/v1` unchanged. Add:

```text
facial-behavior-profile/v1
```

Face landmarks: COCO WholeBody **23–90**.

Normalization:

1. eye-line midpoint center;
2. remove in-plane roll;
3. divide by inter-eye-center distance.

Descriptors:

- internal expression deformation, jaw excluded;
- brows;
- eyes;
- mouth;
- mouth open/width;
- eye open;
- brow-eye distance;
- face-point presence/confidence.

### Facial quality audit — PASS / POLICY LOCKED

```text
frames total: 1695
normalized: 1677
normalization failed: 18
static hard suspects: 101
temporal review suspects: 47
accepted facial static geometry: 1576/1695 = 0.929794
```

Filtered dynamics:

```text
expression mean/peak: 0.135848 / 0.712936
mouth mean/peak: 0.188157 / 0.921541
mouth_open range: 0.118971
mouth_width range: 0.192813
eye_open range: 0.038902
brow_eye_distance range: 0.119461
```

The reviewed suspect sheet confirms hard facial suspects are mainly face-off-frame / severe crop / strong lateral geometry / degenerate normalization.

Locked semantics:

- hard facial suspects are excluded **only from facial descriptors**;
- they do not automatically remove the underlying base motion unit;
- temporal jumps remain review-only;
- facial quality stays continuous.

Per-unit facial reliability:

```text
face_quality_weight =
accepted_frame_ratio
× mean_face_point_presence
× mean_landmark_confidence
```

### Facial sidecar build — STRUCTURAL PASS

```text
units: 119
usable with >=2 accepted facial frames: 116
accepted-frame ratio q10/median/q90: 0.8318838 / 1.0 / 1.0
face-quality weight q10/median/q90: 0.7649534 / 0.913145 / 0.9241892
units with hard facial suspects: 39
hard-suspect frame references across units: 120
units with temporal-review signal: 4
```

Lowest facial-quality units:

```text
u0003 weight=0.0 accepted=0.0
u0006 weight=0.0 accepted=0.0
u0007 weight=0.0 accepted=0.0
u0005 weight=0.276583 accepted=0.3125
u0094 weight=0.432046 accepted=0.466667
u0004 weight=0.440393 accepted=0.5
```

Classification: **SECONDARY BASE PROFILE + FACIAL SIDECAR STRUCTURAL PASS**.

## Secondary role-aware curation — NEXT

Do **not** apply the primary source's whole-upper policy to this video.

Locked retrieval roles:

- **face/microexpression**: enabled when a unit has at least 2 accepted facial frames; weight = `face_quality_weight`;
- **head**: enabled only when face is structurally usable; weight = `head_pose_quality × face_quality_weight`;
- **body_support**: auxiliary anchor only; weight = `body_pose_quality × face_quality_weight`;
- **left/right/both hands**: diagnostic only; retrieval disabled for this source;
- **generic whole-upper**: disabled for this source.

The three zero-face units remain in the base profile but are not eligible for face/head retrieval. They are **not globally hard-excluded** simply because the facial layer is unusable.

Versioned:

- `tools/video-studio/behavior_source_annotations_secondary.json`;
- `tools/video-studio/curate_secondary_behavior_source.py`;
- `tools/video-studio/run_behavior_secondary_curation.ps1`.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_curation.ps1'
```

This runs no DWPose and no Wan-Animate-2. Paste the complete terminal output before processing `SIENA_BRUTO.mp4`.

## Downstream

1. complete secondary role-aware curation;
2. validate/process `SIENA_BRUTO.mp4` with a short gate first and source-specific exclusions;
3. preserve source IDs/timestamps and source roles for every unit;
4. build unified source-preserving library;
5. synthesize a new 4–5 s multi-source behavioral driver;
6. only then invoke installed Wan-Animate-2.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.
