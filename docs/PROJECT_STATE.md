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
    -> source-specific semantic/quality curation
    -> unified source-preserving João motion library

new local speech/audio
    -> prosodic windows
    -> retrieve compatible units across sources
    -> body/hand/head/face quality weighting + continuity + diversity
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A single source video is never the final library.

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

Corrected portrait geometry and 6 fps DWPose route passed.

```text
full pose frames: 1801
fallback: 0/1801
mean keypoint score: 0.7549247491
behavior-profile/v1 status: complete
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

Artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_inventory.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_motion_units.csv
```

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — FULL POSE PASS

Role: face/head/microexpression.

Validated C3 facial gate: **83.6–88.6 s**.

Geometry is the same encoded-landscape + rotation-metadata condition as the primary source, and the orientation fix is working:

```text
coded: 1920x1080
display: 1080x1920
rotation: 90
analysis: 540x960
```

Full pose result:

```text
duration: 282.574 s
frames: 1695 @ 6 fps
fallback: 1/1695 = 0.0005899705
mean keypoint score: 0.5453589803
provider: CPUExecutionProvider
```

All 133 keypoints are retained. Classification: **SECONDARY FULL POSE TRACK PASS**.

## Facial representation — ADDITIVE SIDECAR LOCKED

Do not mutate the validated `behavior-profile/v1` schema.

Use an aligned sidecar:

```text
behavior-profile/v1
+ facial-behavior-profile/v1
```

Face landmarks: COCO WholeBody **23–90**.

Normalization before expression measurement:

1. center on eye-line midpoint;
2. remove in-plane roll;
3. divide by inter-eye-center distance.

This removes image translation, in-plane rotation and scale. It does not claim to remove yaw/pitch perspective effects.

Descriptors:

- internal expression deformation, jaw excluded;
- brows;
- eyes;
- mouth;
- mouth opening / width;
- eye opening;
- brow-eye distance;
- face point presence/confidence.

## Secondary facial probe — COVERAGE PASS

Full source:

```text
1695 frames
1677 normalized = 0.989381
mean face-point presence = 0.988383
mean landmark confidence = 0.910192
```

The validated C3 interval produced coherent facial dynamics, but raw full-track peaks were pathological (`expression peak 37.065`, `mouth peak 58.962`), proving that a small number of off-frame/degenerate frames must be removed from the facial layer.

## Secondary facial frame-quality audit — PASS / POLICY LOCKED

Audit policy:

- source-relative Tukey outer fences, **3×IQR**;
- normalization failures + static normalized-geometry outliers = facial hard suspects;
- temporal expression jumps = review-only, never automatic hard exclusion;
- no absolute hand-tuned facial threshold.

Observed:

```text
frames total: 1695
normalized: 1677
normalization failed: 18
static hard suspects: 101
temporal review suspects: 47
accepted facial static geometry: 1576/1695 = 0.929794
```

Filtered dynamics become plausible:

```text
expression mean/peak: 0.135848 / 0.712936
mouth mean/peak: 0.188157 / 0.921541
mouth_open mean/range: 0.023286 / 0.118971
mouth_width mean/range: 0.886436 / 0.192813
eye_open mean/range: 0.063497 / 0.038902
brow_eye_distance mean/range: 0.162553 / 0.119461
```

The uploaded review sheet visually confirms that the highest-severity hard suspects are primarily moments with the face partially outside the frame, severe lateral/cropped geometry, or degenerate normalization. They are unsuitable for facial microexpression descriptors but do **not** imply global rejection of the underlying body/head motion.

### Facial exclusion semantics — LOCKED

Hard facial suspects are excluded **only from the facial sidecar**. They do not automatically remove the corresponding motion unit from `behavior-profile/v1`.

Per-unit facial reliability is continuous:

```text
face_quality_weight =
accepted_frame_ratio
× mean_face_point_presence
× mean_landmark_confidence
```

No new binary per-unit face threshold is introduced at this stage.

Versioned tooling:

- `tools/video-studio/facial_descriptors.py`;
- `tools/video-studio/audit_facial_track_quality.py`;
- `tools/video-studio/render_facial_quality_review.py`;
- `tools/video-studio/facial_behavior_profile_schema_v1.json`;
- `tools/video-studio/build_facial_behavior_sidecar.py`;
- `tools/video-studio/inspect_facial_behavior_sidecar.py`;
- `tools/video-studio/run_behavior_secondary_profile_and_facial_sidecar.ps1`.

## Immediate next action

Build the secondary base behavior profile and its aligned facial sidecar from existing local artifacts:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_profile_and_facial_sidecar.ps1'
```

This runs no DWPose and no Wan-Animate-2.

Expected outputs include:

```text
...\VID_20260819_124008056\manifest.json
...\VID_20260819_124008056\motion_units.csv
...\VID_20260819_124008056\profile_inspection.json
...\VID_20260819_124008056\facial_behavior_profile.json
...\VID_20260819_124008056\facial_sidecar_inspection.json
```

Paste the complete terminal output before secondary curation.

## Downstream

1. inspect/curate secondary units with source role strongly favoring face/head;
2. optionally derive a facial sidecar for primary from its existing 133-point track without rerunning DWPose;
3. process `SIENA_BRUTO.mp4` with source-specific exclusions;
4. build unified source-preserving library;
5. synthesize a new 4–5 s multi-source behavioral driver;
6. only then invoke installed Wan-Animate-2.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.
