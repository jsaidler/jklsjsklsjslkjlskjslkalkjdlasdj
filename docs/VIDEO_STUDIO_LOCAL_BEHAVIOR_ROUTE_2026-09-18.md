# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / PRIMARY INVENTORY REVIEW PASS WITH CURATION / PRIMARY CURATION NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: posture, head movement, hands, gesture timing, expressions and delivery rhythm. Generic plausible motion is insufficient.

## Selected architecture — LOCKED

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source profiles
    -> semantic/manual exclusions + continuous group-quality weights
    -> unified source-preserving motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve units across sources
    -> pose continuity + diversity + quality/source weighting
    -> NEW João driving performance

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

## Canonical sources

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture;
- `VID_20260819_124008056.mp4` — facial/head/microexpression;
- `SIENA_BRUTO.mp4` — alternate gesture/posture with explicit object/occlusion handling.

A single source is never the final João library.

## Primary source — validated through inventory review

Pose/profile path:

- local WanGP DWPose reuse: PASS;
- portrait orientation correction: PASS;
- C3 88.7–93.7 s visual upper-body gate: PASS;
- full pose track: 1801 frames, 0 fallback, mean keypoint score 0.7549247491;
- behavior profile: `status=complete`, 123 units, complete 0–300.352 s coverage;
- all 123 units have valid pose snapshots and head/body/both-hand activity.

Inventory diagnostics:

```text
upper pose coverage q10: 0.9352380952
median: 1.0
q90: 1.0
hand speed q10/median/q90: 0.049868 / 0.161759 / 0.3921014
body speed q10/median/q90: 0.0209724 / 0.05028 / 0.1128552
```

Classification: **PRIMARY INVENTORY QUALITY IS SUFFICIENT TO CURATE AND KEEP**.

## Curation policy — LOCKED

### Manual semantic/visual hard exclusions

Human-visible source semantics outrank pure tracking metrics when motion is nonportable.

Confirmed hard exclusion:

**24.1–37.5 s (`u0012`–`u0016`)** because this span contains reaching for, holding and presenting physical objects. The behavior is prop-specific and includes hand occlusion.

Canonical source annotation:

`tools/video-studio/behavior_source_annotations_primary.json`

### Pose coverage is continuous reliability, not binary rejection

`low_relative_pose_coverage` is not itself a failure condition. The already visually validated `u0038` carries that tag, proving that a vigorous/edge-of-frame gesture can remain valid while one hand's confidence temporarily drops.

Eligible units therefore retain group-specific quality weights based on:

`confident keypoint ratio × group frame presence`

for head, body, left hand and right hand. Both-hands reliability is the minimum of hand reliabilities; whole-upper reliability is the minimum across active groups.

No arbitrary new global pass/fail threshold is added.

Versioned tools:

- `tools/video-studio/behavior_source_annotations_primary.json`;
- `tools/video-studio/curate_behavior_inventory.py`;
- `tools/video-studio/run_behavior_primary_curation.ps1`.

Expected current curation:

```text
123 total
5 hard excluded
118 eligible
```

## Next source

After primary curation is materialized locally, do not blindly process the full second video. First run a short visual pose gate for:

`VID_20260819_124008056.mp4`

If that gate passes, run its full pose/profile/inventory route. Its source role is primarily head/face/microexpression, and v1 head descriptors may later need expansion beyond keypoints 0–4 based on evidence from this source.

## Downstream

1. curate primary;
2. validate/process second source;
3. validate/process `SIENA_BRUTO.mp4` with source-specific exclusions;
4. unify all eligible source-preserving units;
5. retrieve with source-role + group-quality weighting;
6. synthesize a new 4–5 s multi-source performance;
7. only then invoke installed Wan-Animate-2.

## Stop conditions

- no new large renderer;
- no DWPose/Python/CUDA reinstall while current route works;
- no low-relative-coverage tag treated blindly as rejection;
- no prop/object-specific motion accepted as generic behavior;
- no single-source final library;
- no Wan-Animate-2 before multi-source library/synthesis validation.

Quality criterion:

> this does not merely look like João; it moves and reacts like João.
