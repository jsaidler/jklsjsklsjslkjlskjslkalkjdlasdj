# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / PRIMARY CURATED PASS / SECONDARY PROFILE+FACIAL SIDECAR STRUCTURAL PASS / ROLE CURATION NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: posture, head movement, hands, gesture timing, expressions and delivery rhythm. Generic plausible motion is insufficient.

## Selected architecture — LOCKED

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior-profile/v1
    -> optional facial-behavior-profile/v1 sidecar
    -> semantic exclusions + role-specific continuous quality weights
    -> unified source-preserving motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve by role + quality + continuity + diversity
    -> NEW João driving performance

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

## Canonical sources and roles

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture;
- `VID_20260819_124008056.mp4` — primary face/head/microexpression;
- `SIENA_BRUTO.mp4` — alternate gesture/posture with object/occlusion handling.

A single source is never the final João library, and sources must not be forced into one universal quality policy.

## Primary source — CURATED PASS

```text
123 total units
118 eligible
5 hard excluded
24.1–37.5 s excluded for held-object/prop interaction + hand occlusion
```

Primary policy:

- whole-upper gesture source;
- continuous group quality by head/body/left/right hand;
- semantic prop-specific spans can be globally excluded from generic retrieval.

## Secondary source — STRUCTURAL PASS THROUGH FACIAL SIDECAR

Validated face/head gate C3: **83.6–88.6 s**.

Full pose:

```text
1695 frames @ 6 fps
1080x1920 display after 90-degree metadata rotation
540x960 analysis
1/1695 detector fallback
mean whole-body keypoint score 0.5453589803
```

Base behavior profile:

```text
119 units
complete 0.0 -> 282.574 s coverage
119/119 head activity
119/119 body activity
37 left-hand units
20 right-hand units
38 combined-hand units
```

This source is not rejected for sparse hands because its role is face/head.

## Facial representation — LOCKED ADDITIVE SIDECAR

Do not mutate `behavior-profile/v1`.

Use `facial-behavior-profile/v1` aligned to the same unit IDs/timestamps.

Face landmarks: COCO WholeBody 23–90.

Normalize by:

1. eye-line midpoint;
2. remove in-plane roll;
3. inter-eye scale.

Descriptor groups:

- internal expression deformation;
- brows;
- eyes;
- mouth;
- mouth open/width;
- eye open;
- brow-eye distance;
- face presence/confidence.

## Facial quality policy — LOCKED

Source-relative Tukey outer fences (3×IQR) are used to identify gross normalized-geometry failures.

- normalization failures + static geometry outliers = facial hard suspects;
- temporal expression jumps = review-only;
- no hard facial suspect automatically removes the underlying base motion unit;
- no arbitrary absolute facial-expression threshold.

Observed full secondary QA:

```text
1695 total frames
1677 normalized
18 normalization failures
101 static hard facial suspects
47 temporal review suspects
1576 accepted facial geometry frames = 0.929794
```

Filtered facial dynamics returned to plausible ranges, and visual review showed top suspects are mainly face-off-frame/crop/lateral-degenerate frames.

Per-unit face quality:

```text
face_quality_weight =
accepted_frame_ratio
× mean_face_point_presence
× mean_landmark_confidence
```

Facial sidecar result:

```text
119 units
116 with >=2 accepted facial frames
accepted ratio q10/median/q90 = 0.8318838 / 1.0 / 1.0
face weight q10/median/q90 = 0.7649534 / 0.913145 / 0.9241892
```

## Role-aware secondary retrieval — LOCKED

Do not use the primary source's `whole_upper=min(head,body,left,right)` policy here.

For the second source:

- **face/microexpression**: eligible with >=2 accepted facial frames; weight = `face_quality_weight`;
- **head**: weight = `head_pose_quality × face_quality_weight`;
- **body_support**: auxiliary anchor only; weight = `body_pose_quality × face_quality_weight`;
- **left/right/both hands**: retrieval disabled;
- **generic whole-upper**: retrieval disabled.

This prevents camera/scenery spans or face-off-frame spans from being misread as reusable head behavior while avoiding unnecessary global deletion of otherwise valid base units.

Versioned:

- `tools/video-studio/behavior_source_annotations_secondary.json`;
- `tools/video-studio/curate_secondary_behavior_source.py`;
- `tools/video-studio/run_behavior_secondary_curation.ps1`.

## Next

1. run secondary role-aware curation;
2. validate/process `SIENA_BRUTO.mp4` with a short gate first;
3. curate SIENA with source-specific object/occlusion exclusions;
4. build unified source-preserving library;
5. synthesize a new 4–5 s multi-source performance;
6. only then invoke installed Wan-Animate-2.

## Stop conditions

- no new large renderer;
- no DWPose/Python/CUDA reinstall while current route works;
- no source role forced into an inappropriate universal quality metric;
- no prop/object-specific motion accepted as generic behavior;
- no face-off-frame pathology accepted as microexpression data;
- no single-source final library;
- no Wan-Animate-2 before multi-source library/synthesis validation.

Quality criterion:

> this does not merely look like João; it moves and reacts like João.
