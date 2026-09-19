# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / PRIMARY PROFILE STRUCTURAL PASS / INVENTORY QUALITY REVIEW NEXT**

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
    -> source-preserving quality annotations
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

The final library cannot be one clip or one source video.

## Canonical sources

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture source;
- `VID_20260819_124008056.mp4` — facial/head/microexpression source;
- `SIENA_BRUTO.mp4` — alternate gesture/posture source with unusable object/occlusion spans excluded/down-weighted.

## Primary source validated path

- DWPose local reuse: PASS;
- portrait orientation preprocessing: FIXED;
- clean C3 visual upper-body pose gate: PASS;
- full pose track: PASS — 1801 frames, 0 fallback, mean keypoint score 0.7549247491487903;
- behavior-profile motion analysis orientation: FIXED — 72x128 for the portrait primary source.

## Primary behavior-profile — STRUCTURAL PASS

Observed profile inventory:

```text
status: complete
units: 123
source coverage: 0.0 -> 300.352 s
motion analysis: 72x128
pose snapshots valid: 123/123
activity present: head/body/left hand/right hand/combined hands = 123/123
speech classes: mixed=89, pause=4, speech=30
unit duration min/median/max: 0.800/2.500/3.800 s
```

This proves the per-source extraction/segmentation/profile path is structurally viable. It does not certify all 123 units as retrieval candidates.

## Motion-unit inventory quality review — ACTIVE NEXT GATE

Versioned tooling:

- `tools/video-studio/analyze_behavior_inventory.py`;
- `tools/video-studio/render_behavior_inventory_review.py`;
- `tools/video-studio/run_behavior_inventory_review.ps1`.

The analyzer reads the complete manifest plus full COCO WholeBody track and derives per-unit diagnostics using the same profile confidence floor (`CONF = 0.20`). It records group confidence/coverage for head, body and both hands, plus movement and transition descriptors.

Thresholds used for review selection are **source-relative quantiles**, not arbitrary pass/fail constants. The selected visual-review set intentionally mixes low-relative-coverage units with high-hand-motion, high-body-motion, high-RGB-motion and pause units.

The visual review sheet shows start/mid/end of up to 24 units so held objects, occlusion, off-frame hands and other human-visible problems can be identified before retrieval/synthesis.

Outputs:

```text
inventory_analysis.json
inventory_units.csv
inventory_review_sheet.jpg
```

No DWPose, Wan-Animate-2 or remote service is invoked.

## Multi-source expansion — after primary inventory review

1. classify/exclude/down-weight unusable primary units;
2. process `VID_20260819_124008056.mp4` through the validated pose/profile route;
3. process `SIENA_BRUTO.mp4` with explicit object/occlusion quality handling;
4. preserve source IDs and timestamps;
5. build unified library with source-role weighting;
6. only then synthesize a new 4–5 s multi-source behavioral driver.

## Prosody v1

Implemented:

- speech/pause;
- RMS dBFS;
- normalized audio energy.

Pitch remains intentionally `null` until a validated local method is needed.

The distribution `mixed=89, pause=4, speech=30` is recorded. It is not automatically a failure, but retrieval design must account for it rather than treating labels as perfect semantic speech segmentation.

## Stop conditions

- no new large renderer download;
- no DWPose download;
- no blind Python/CUDA install;
- no `incomplete_pose` accepted as valid;
- no structurally complete profile mistaken for a quality-approved inventory;
- no single-source library accepted as final João behavior;
- no Wan-Animate-2 render before inventory/multi-source/synthesis validation;
- no generic plausible motion accepted as João behavior.

## Immediate action

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_inventory_review.ps1'
```

Then inspect the numeric inventory summary and `inventory_review_sheet.jpg` before processing the next source.
