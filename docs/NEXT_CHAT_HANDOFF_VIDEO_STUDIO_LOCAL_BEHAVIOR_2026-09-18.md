# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY INVENTORY REVIEW PASS WITH CURATION / PRIMARY CURATION NEXT**

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/behavior_source_annotations_primary.json`;
6. `tools/video-studio/curate_behavior_inventory.py`;
7. `tools/video-studio/run_behavior_primary_curation.ps1`.

## Hard constraints

- 100% local/self-hosted;
- zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred.

## Goal

New text/audio must yield a new performance that looks, sounds and chiefly **moves/reacts like João**. Generic presenter motion is failure.

## Multi-source requirement — LOCKED

Final behavior library must use all canonical sources, not only the first:

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture;
- `VID_20260819_124008056.mp4` — head/face/microexpression;
- `SIENA_BRUTO.mp4` — additional gesture/posture with exclusions.

## Primary pipeline — PASS

Primary corrected pose path:

```text
540x960 @ 6 fps
1801 frames
0/1801 detector fallback
mean keypoint score 0.7549247491487903
CPUExecutionProvider
```

Primary behavior profile:

```text
status complete
123 units
0.0 -> 300.352 s continuous coverage
123/123 valid pose snapshots
all 123 units have head/body/left-hand/right-hand activity
```

## Primary inventory review — PASS WITH CURATION

Inventory artifacts were uploaded and inspected.

Distribution:

```text
upper-pose coverage q10: 0.9352380952
median: 1.0
q90: 1.0
hand speed q10/median/q90: 0.049868 / 0.161759 / 0.3921014
body speed q10/median/q90: 0.0209724 / 0.05028 / 0.1128552
```

Important interpretation:

- `low_relative_pose_coverage` is a diagnostic tag, **not** an automatic reject condition;
- `u0038` is tagged low-relative-coverage but belongs to the already visually passed C3 interval, proving that vigorous/edge-of-frame gestures can legitimately reduce one-hand coverage;
- group coverage is therefore retained as a continuous retrieval reliability signal.

### Hard exclusion

Manual visual evidence establishes one nonportable object/prop interaction interval:

**24.1–37.5 s = `u0012`–`u0016`.**

Reasons: held object, hand occlusion, prop-specific motion. These five units are excluded from generic João behavior retrieval.

Canonical annotation:

`tools/video-studio/behavior_source_annotations_primary.json`

### Continuous quality weights

Eligible units keep continuous weights based on confident-keypoint ratio × frame presence for head, body, left hand and right hand. No arbitrary new binary cutoff is introduced.

Expected primary curation result:

```text
123 total
5 hard excluded
118 eligible
```

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_primary_curation.ps1'
```

Outputs:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_inventory.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_motion_units.csv
```

After confirming 118 eligible / 5 excluded, proceed to a short visual pose gate for `VID_20260819_124008056.mp4`; do not blindly launch its full extraction first.

## Downstream

1. curate primary inventory;
2. validate/process second canonical source;
3. validate/process `SIENA_BRUTO.mp4` with source-specific exclusions;
4. build unified source-preserving library;
5. synthesize a new 4–5 s multi-source behavioral driver;
6. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
