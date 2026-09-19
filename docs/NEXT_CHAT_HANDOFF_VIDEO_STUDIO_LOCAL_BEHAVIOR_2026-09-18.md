# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY BEHAVIOR PROFILE STRUCTURAL PASS / MOTION-UNIT INVENTORY REVIEW NEXT**

## Continue from canonical state

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. this file;
6. `tools/video-studio/analyze_behavior_inventory.py`;
7. `tools/video-studio/render_behavior_inventory_review.py`;
8. `tools/video-studio/run_behavior_inventory_review.ps1`.

GitHub living docs are source of truth. Do not reconstruct state from memory when docs differ.

## Hard constraints

- 100% local/self-hosted;
- zero service cost;
- never upload João's video/voice/identity to third parties;
- no SaaS/paid API/credits/subscriptions;
- do not download another large renderer;
- no new Python/DWPose/CUDA install while current local route works;
- Wan S2V, H3, Hunyuan and HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred.

## Goal

New text/audio must eventually produce a new performance that looks, sounds and chiefly **moves/reacts like João**. Generic presenter motion is failure.

## Multi-source requirement — LOCKED

Final behavior library must not use only one video.

Canonical sources:

- `VID_20260911_140124885.mp4` — torso/hands/posture/gesture primary;
- `VID_20260819_124008056.mp4` — head/face/microexpression source;
- `SIENA_BRUTO.mp4` — additional gesture/posture source with object/occlusion exclusions.

The first source is complete through structural profile validation only. The other two still must be processed before final library synthesis.

## Validated primary pose path

Primary video is coded 3840x2160, displayed 2160x3840 via 90° rotation.

Corrected DWPose analysis:

```text
540x960 @ 6 fps
1801 frames
0/1801 detector fallback
mean keypoint score: 0.7549247491487903
CPUExecutionProvider
```

Clean visual gate C3 = 88.7–93.7 s passed after orientation correction.

## Primary behavior profile — STRUCTURAL PASS

Profile builder completed:

```text
status: complete
units: 123
CSV rows: 123
coverage: 0.0 -> 300.352 s
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

Do not synthesize a driver yet. Structural completeness does not prove every unit is behaviorally usable.

## Next exact action — inventory quality review

Versioned:

- `tools/video-studio/analyze_behavior_inventory.py`;
- `tools/video-studio/render_behavior_inventory_review.py`;
- `tools/video-studio/run_behavior_inventory_review.ps1`.

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_inventory_review.ps1'
```

This does not rerun DWPose or Wan. It computes per-unit pose confidence/coverage and movement diagnostics, then selects up to 24 representative/suspicious units and creates a visual contact sheet with start/mid/end frames.

Outputs:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\inventory_analysis.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\inventory_units.csv
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\inventory_review_sheet.jpg
```

Paste the numeric terminal summary and upload `inventory_review_sheet.jpg`.

## After inventory review

1. classify/exclude/down-weight unusable primary motion units;
2. process `VID_20260819_124008056.mp4` through the validated pose/profile route;
3. process `SIENA_BRUTO.mp4` with explicit occlusion/object exclusions;
4. build unified multi-source João library preserving unit source/timestamps;
5. synthesize a new 4–5 s performance from multiple units/sources;
6. only then invoke installed Wan-Animate-2.

## Final human quality gate

> “isso não apenas parece João; isso se move e reage como João.”
