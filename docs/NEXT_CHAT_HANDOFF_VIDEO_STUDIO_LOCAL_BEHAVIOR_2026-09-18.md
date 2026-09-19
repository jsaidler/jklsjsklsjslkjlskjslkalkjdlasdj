# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY SOURCE CURATED PASS / SECONDARY C3 FACIAL GATE SELECTED**

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_secondary_pose_gate.ps1`;
6. `tools/video-studio/extract_dwpose_track.py`;
7. `tools/video-studio/render_pose_overlay.py`.

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

Final behavior library must use all canonical sources:

- `VID_20260911_140124885.mp4` — torso/hands/posture/gesture primary;
- `VID_20260819_124008056.mp4` — head/face/microexpression;
- `SIENA_BRUTO.mp4` — additional gesture/posture with exclusions.

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

## Secondary source — SELECTED GATE

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: **facial/head/microexpression source**.

Eight 5-second candidate windows were sampled without DWPose and visually reviewed.

Selected first validation gate:

**C3 = 83.6–88.6 s.**

Why C3:

- frontal, clearly visible face;
- stable framing;
- useful mouth/brow/expression variation;
- no hand/object face occlusion;
- no strong head rotation.

C6 remains a possible later stress case because it contains stronger tilt/blink variation.

Versioned runner:

`tools/video-studio/run_behavior_secondary_pose_gate.ps1`

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_pose_gate.ps1'
```

This runs DWPose only on C3 at 6 fps with CPU and renders the overlay. It does not invoke Wan-Animate-2.

Expected overlay:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\selected_gate\pose_gate_c3_83p6_88p6_overlay.mp4`

Upload that MP4 and paste the short summary if useful.

## Secondary gate review criteria

Inspect especially:

- facial landmarks remain attached to the face through mouth/brow changes;
- head landmarks move smoothly with head motion;
- no gross facial topology jump or subject switch;
- shoulders/upper torso remain coherent enough to anchor the face/head sequence;
- do not reject merely because hands/lower body are weak if they are outside this source's intended role.

Only after this visual gate passes:

1. run full 6 fps secondary pose extraction;
2. build its complete profile;
3. review/curate units with greater weight on head/face quality;
4. then process `SIENA_BRUTO.mp4`;
5. build unified source-preserving library;
6. synthesize a new 4–5 s multi-source behavioral driver;
7. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
