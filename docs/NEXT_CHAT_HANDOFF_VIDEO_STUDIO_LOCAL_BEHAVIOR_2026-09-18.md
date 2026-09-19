# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY PROFILE+FACIAL SIDECAR STRUCTURAL PASS / SECONDARY ROLE CURATION NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the canonical source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/behavior_source_annotations_secondary.json`;
6. `tools/video-studio/curate_secondary_behavior_source.py`;
7. `tools/video-studio/run_behavior_secondary_curation.ps1`.

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

## Primary source — CURATED PASS

```text
123 total units
118 eligible
5 hard excluded
24.1-37.5 s excluded for held object / hand occlusion / prop interaction
```

Role: torso/hands/posture/gesture.

## Secondary source — STRUCTURAL PASS THROUGH FACIAL SIDECAR

Source: `VID_20260819_124008056.mp4`  
Role: face/head/microexpression.

Full pose:

```text
1695 frames @ 6 fps
coded 1920x1080
display 1080x1920
rotation 90
analysis 540x960
1/1695 detector fallback
mean whole-body keypoint score 0.5453589803
CPUExecutionProvider
```

Base behavior profile:

```text
status complete
119 units
coverage 0.0 -> 282.574 s
119/119 valid pose snapshots
head activity 119
body activity 119
left hand activity 37
right hand activity 20
combined hands 38
speech mixed=84 pause=1 speech=34
```

Sparse hands are expected and do not fail this source.

## Facial sidecar — PASS

Architecture:

```text
behavior-profile/v1
+ facial-behavior-profile/v1
```

Face landmarks 23–90. Normalize by eye-line midpoint, remove in-plane roll, divide by inter-eye distance.

Frame-quality audit:

```text
1695 total
1677 normalized
18 normalization failures
101 static hard facial suspects
47 temporal review suspects
1576/1695 accepted facial geometry = 0.929794
```

Hard facial suspects are facial-layer-only exclusions. Temporal jumps are review-only.

Per-unit face weight:

```text
accepted_frame_ratio * mean_face_point_presence * mean_landmark_confidence
```

Built sidecar:

```text
119 units
116 usable with >=2 accepted facial frames
accepted ratio q10/median/q90 = 0.8318838 / 1.0 / 1.0
face weight q10/median/q90 = 0.7649534 / 0.913145 / 0.9241892
39 units contain hard facial suspects
4 units contain temporal-review signal
```

Zero-face units:

```text
u0003
u0006
u0007
```

Classification: **SECONDARY BASE PROFILE + FACIAL SIDECAR STRUCTURAL PASS**.

## Secondary source-role policy — LOCKED

Do not reuse primary whole-upper curation.

- face: enabled with >=2 accepted facial frames; weight = face quality;
- head: weight = coarse head pose quality × face quality;
- body support: auxiliary; weight = body pose quality × face quality;
- hands: retrieval disabled for this source;
- generic whole-upper: retrieval disabled.

Zero-face units stay in the base profile but are not face/head retrieval candidates. Do not globally hard-exclude them solely for facial failure.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_curation.ps1'
```

This does not run DWPose or Wan. It:

1. computes pose/group reliability per secondary motion unit;
2. joins the facial sidecar;
3. applies role-specific retrieval weights;
4. keeps hands diagnostic-only;
5. outputs curated secondary JSON/CSV and role-weight distributions.

Paste the complete terminal output.

## After secondary curation PASS

1. sample/choose a clean gate for `SIENA_BRUTO.mp4`;
2. run short DWPose gate before any full pass;
3. process/curate SIENA with semantic object/occlusion exclusions;
4. build unified source-preserving library;
5. synthesize a new 4–5 s multi-source behavioral driver;
6. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
