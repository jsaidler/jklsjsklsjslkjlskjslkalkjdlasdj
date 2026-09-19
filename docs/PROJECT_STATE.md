# Local Video Studio — Current Project State

Status date: **2026-09-19**

GitHub living documents are the canonical source of truth.

## Execution policy — LOCKED

The Video Studio remains **100% local/self-hosted and zero-service-cost**.

Hard constraints:

- no hosted avatar/generation/training service;
- no SaaS/cloud inference API, credits or subscriptions;
- never upload João's video, voice or identity to third parties;
- no new large renderer while the behavior route is active;
- Wan S2V, H3, Hunyuan and HeyGen remain historical/retired routes;
- MuseTalk/LatentSync/CosyVoice remain deferred;
- no new Python/DWPose/CUDA install while the validated local route works.

## Active objective — LOCKED

Generate new video from new text/audio that looks, sounds and chiefly **moves/reacts like João**. Generic plausible presenter motion is failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior profiles / motion units
    -> optional additive facial sidecar per source
    -> source-quality annotation/curation
    -> unified persistent João motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve compatible units across sources
    -> pose continuity + diversity + quality/source weighting
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A single source video is not the final library.

## Canonical behavior sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

- `VID_20260911_140124885.mp4` — 300.352 s — primary torso/hands/posture/gesture source;
- `VID_20260819_124008056.mp4` — 282.574 s — facial/head/microexpression source;
- `SIENA_BRUTO.mp4` — 113.3 s — additional gesture/posture source with object/occlusion exclusions.

## Local pose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

DWPose functional runtime: PASS. CPU is the validated route. CUDA ONNX remains unvalidated because the CUDA EP reported missing `cublasLt64_13.dll`; do not repair CUDA yet.

## Primary source — CURATED PASS

Primary curation completed:

```text
Units total: 123
Eligible: 118
Hard excluded: 5
Manual exclusion: 24.1-37.5 s / held_object,hand_occlusion,prop_interaction
```

Curated artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_inventory.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_motion_units.csv
```

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — FULL POSE PASS

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: **facial/head/microexpression source**.

Validated visual gate: **C3 = 83.6–88.6 s**.

Gate geometry:

```text
coded: 1920x1080
display: 1080x1920
rotation: 90
analysis: 540x960
frames: 30 @ 6 fps
fallback: 0/30
mean keypoint score: 0.5554170230711649
```

Full pose track:

```text
source_duration_s: 282.574
frames: 1695
last_timestamp_s: 282.333333
analysis: 540x960
rotation: 90
detector fallback: 1/1695 = 0.0005899705
mean keypoint score: 0.5453589803
provider: CPUExecutionProvider
```

Classification: **SECONDARY FULL POSE TRACK PASS**.

## Facial representation — ADDITIVE SIDECAR LOCKED

Do not mutate the already validated `behavior-profile/v1` schema.

Use:

```text
behavior-profile/v1
+ facial-behavior-profile/v1 sidecar
```

The sidecar aligns to the same motion-unit IDs/timestamps and uses COCO WholeBody face landmarks **23–90**.

Normalization:

1. center on eye-line midpoint;
2. remove in-plane roll;
3. divide by inter-eye-center distance.

This removes image translation/roll/scale before internal expression measurement. Perspective/yaw/pitch are not claimed to be removed.

Descriptor targets:

- overall internal facial deformation excluding jaw;
- brows;
- eyes;
- mouth;
- mouth opening;
- mouth width;
- eye opening;
- brow-eye distance;
- facial point presence/confidence.

Versioned core:

- `tools/video-studio/facial_descriptors.py`;
- `tools/video-studio/inspect_facial_track.py`;
- `tools/video-studio/run_behavior_secondary_facial_probe.ps1`.

## Secondary facial descriptor probe — COVERAGE PASS / OUTLIER CLEANUP REQUIRED

Observed full-track probe:

```text
Frames: 1695
normalized: 1677 = 0.989381
mean face-point presence: 0.988383
mean landmark confidence: 0.910192
expression deformation mean/peak/net: 0.294768 / 37.065123 / 0.031473
brows mean/peak/net: 0.1839 / 23.609748 / 0.019964
eyes mean/peak/net: 0.059626 / 4.657827 / 0.009234
mouth mean/peak/net: 0.420327 / 58.962267 / 0.046517
mouth_open mean/range: 0.031162 / 1.62261
mouth_width mean/range: 0.887221 / 2.053646
eye_open mean/range: 0.067165 / 4.18874
brow_eye_distance mean/range: 0.171277 / 3.146605
```

Validated C3 probe:

```text
Frames: 30
normalized: 30 = 1.0
mean face-point presence: 1.0
mean landmark confidence: 0.921025
expression deformation mean/peak/net: 0.122421 / 0.2463 / 0.054641
brows mean/peak/net: 0.085689 / 0.341491 / 0.048666
eyes mean/peak/net: 0.031661 / 0.040425 / 0.009874
mouth mean/peak/net: 0.169658 / 0.361598 / 0.077857
mouth_open mean/range: 0.016397 / 0.08113
mouth_width mean/range: 0.875241 / 0.106278
eye_open mean/range: 0.065198 / 0.01531
brow_eye_distance mean/range: 0.165608 / 0.080742
```

Interpretation:

- facial coverage/confidence are excellent overall;
- the C3 values are coherent and confirm that the descriptor design works on a visually validated interval;
- the huge full-track peaks/ranges are **not plausible expressions** and indicate a small number of pathological normalization/geometry frames;
- therefore the source is kept, but facial units must not be built until those outliers are quality-gated.

Classification: **FACIAL DESCRIPTOR COVERAGE PASS / FRAME-LEVEL QUALITY GATE REQUIRED**.

## Facial frame quality audit — NEXT

Versioned:

- `tools/video-studio/audit_facial_track_quality.py`;
- `tools/video-studio/render_facial_quality_review.py`;
- `tools/video-studio/run_behavior_secondary_facial_quality_audit.ps1`.

Policy:

- source-relative **Tukey outer fences (3×IQR)** on normalized facial geometry/signals;
- no arbitrary absolute facial threshold;
- normalization failures and static geometry outliers are hard suspects;
- temporal expression jumps are **review-only** and do not automatically reject frames;
- accepted-frame summary is recomputed after static-geometry suspects are removed;
- a contact sheet is generated for suspect timestamps so human-visible semantics can confirm whether the frames are genuinely bad tracking/geometry or legitimate movement.

No DWPose or Wan-Animate-2 runs during this audit.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_facial_quality_audit.ps1'
```

Then paste the complete terminal output and upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\facial_quality_review_sheet.jpg`

Only after this audit is visually confirmed should `facial-behavior-profile/v1` and the secondary behavior profile be materialized.

## Multi-video library requirement — LOCKED

After the second source passes facial-aware profile + curation:

1. process `SIENA_BRUTO.mp4` through the same route with source-specific exclusions;
2. preserve source ID and timestamps for every unit;
3. build a unified searchable library;
4. use source-role + body/hand/face quality weighting rather than treating all recordings/units as equivalent.

## Renderer — downstream

Installed Wan-Animate-2 remains the selected renderer. Do not invoke it until multi-source behavior inventory and driver synthesis are validated.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.
