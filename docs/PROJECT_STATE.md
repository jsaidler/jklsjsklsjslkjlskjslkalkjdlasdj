# Local Video Studio — Current Project State

Status date: **2026-09-19**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Execution policy — LOCKED

The Video Studio remains **100% local/self-hosted and zero-service-cost**.

Hard constraints:

- no hosted avatar/generation/training service;
- no SaaS/cloud inference API, credits or subscriptions;
- never upload João's video, voice or identity to third parties;
- do not download another large renderer while the behavior route is active;
- Wan S2V, H3, Hunyuan and HeyGen remain historical/retired branches;
- MuseTalk/LatentSync/CosyVoice remain deferred;
- no new Python/DWPose/CUDA install while the validated local route works.

## Active objective — LOCKED

Generate new video from new text/audio in which the result:

1. looks like João;
2. sounds like João;
3. chiefly **moves and reacts like João**.

Generic plausible presenter motion is a failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior profiles / motion units
    -> unified persistent João motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve/sequence compatible units across sources
    -> pose continuity + diversity + source-quality constraints
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A single source video is not the final library.

## Canonical behavior sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

- `VID_20260911_140124885.mp4` — 300.352 s — primary torso/hands/posture/gesture source;
- `VID_20260819_124008056.mp4` — 282.6 s — facial/head/microexpression source;
- `SIENA_BRUTO.mp4` — 113.3 s — additional gesture/posture source with object/occlusion exclusions.

The first source is complete through the structural behavior-profile gate. The other two remain required before the final multi-source library is complete.

## Installed Wan-Animate-2 — REUSE PASS

Present locally and reserved for downstream rendering. Do **not** invoke it before behavior inventory review, multi-source expansion and driver synthesis are validated.

## Local DWPose reuse — PASS

Validated local stack:

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

DWPose functional runtime: PASS. CUDA ONNX acceleration remains unvalidated; CPU is the validated route.

## Orientation/preprocessing defects — FIXED

The primary video is coded 3840x2160 but displayed portrait via 90° rotation metadata.

Corrected pose extraction:

- coded: 3840x2160;
- display: 2160x3840;
- DWPose analysis: 540x960.

Corrected behavior-profile motion analysis preserves display aspect ratio at 128 px long side:

- primary motion analysis: **72x128**, not 128x72.

## Visual pose gate — PASS

Clean interval C3 = 88.7–93.7 s passed after orientation correction. Head/face, upper-body joints and both hands were visually coherent with no subject switch, gross left/right swap or invalidating temporal jump.

Behavior-profile v1 uses `CONF = 0.20`; low-confidence QA clutter below this threshold is ignored.

## Full primary pose extraction — PASS

Completed result:

```text
source_duration_s: 300.352
sample_fps: 6.0
analysis: 540x960
frames: 1801
last_timestamp_s: 300.0
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.7549247491487903
onnx_provider: CPUExecutionProvider
```

Track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`

Classification: **FULL PRIMARY POSE TRACK PASS**.

## Primary behavior profile — STRUCTURAL PASS

`run_behavior_profile_primary.ps1` completed successfully using the full pose track.

Observed:

```text
status: complete
units: 123
CSV rows: 123
coverage: 0.0 -> 300.352 s / source=300.352 s
motion analysis: 72x128
pose snapshots valid: 123/123
activity units: head=123, body=123, left_hand=123, right_hand=123, combined_hands=123
speech classes: mixed=89, pause=4, speech=30
unit duration min/median/max: 0.800/2.500/3.800 s
```

Files:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\manifest.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\motion_units.csv
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\profile_inspection.json
```

Classification: **PRIMARY BEHAVIOR PROFILE STRUCTURAL PASS**.

This proves completeness and consistency of the first per-source profile. It does **not** yet prove that all 123 units are good retrieval candidates.

## Motion-unit inventory quality gate — NEXT

Versioned tools:

- `tools/video-studio/analyze_behavior_inventory.py`;
- `tools/video-studio/render_behavior_inventory_review.py`;
- `tools/video-studio/run_behavior_inventory_review.ps1`.

The analyzer uses the profile + full pose track to compute per-unit source-relative diagnostics, including:

- head/body/left-hand/right-hand mean pose score;
- confident keypoint ratio using the same `CONF = 0.20` threshold as profile v1;
- per-group frame presence;
- hand/body/head movement metrics;
- transition and RGB-motion metrics;
- source-relative q10/q50/q90 distributions.

It selects up to 24 units for human review, deliberately mixing:

- lowest relative upper-body pose coverage;
- highest hand motion;
- highest body motion;
- highest RGB motion;
- pause units;
- representative units if needed.

The renderer creates one contact sheet showing **start / midpoint / end** for every selected unit. This is the next gate for detecting object-held spans, occlusion, off-frame hands or otherwise unsuitable units that pure metrics cannot identify reliably.

Expected outputs:

```text
inventory_analysis.json
inventory_units.csv
inventory_review_sheet.jpg
```

No DWPose, diffusion, training or remote service runs during this review.

## Multi-video library requirement — LOCKED

After the primary inventory review passes:

1. process `VID_20260819_124008056.mp4` through the same validated pose/profile route;
2. process `SIENA_BRUTO.mp4`, explicitly excluding/down-weighting occluded/object spans;
3. preserve source ID and timestamps for every unit;
4. build a unified searchable multi-source library;
5. allow source-role weighting rather than treating the recordings as equivalent.

## Known quality work

- object-held/occluded spans need explicit quality annotation or exclusion;
- the 89 `mixed` speech units are not automatically a problem, but speech/prosody distribution must be considered during retrieval design;
- facial descriptors may later need expansion beyond head points 0–4 if the second source proves that v1 is too coarse;
- repair CUDA ORT only if CPU throughput becomes a meaningful blocker.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

1. pull `main`;
2. run `tools/video-studio/run_behavior_inventory_review.ps1`;
3. paste the numeric inventory analysis and upload `inventory_review_sheet.jpg`;
4. classify/exclude/down-weight unusable primary units;
5. then process the other two canonical behavior videos;
6. unify the multi-source motion-unit library;
7. synthesize a new 4–5 s multi-source behavioral driver;
8. only then invoke installed Wan-Animate-2.
