# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA C6 VISUAL GATE PASS / FULL SIENA POSE NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_pose_full_tertiary.ps1`.

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

`VID_20260911_140124885.mp4`  
Role: torso/hands/posture/gesture.

```text
123 total units
118 eligible
5 hard excluded
24.1–37.5 s excluded for held object / hand occlusion / prop interaction
```

## Secondary source — CURATED PASS

`VID_20260819_124008056.mp4`  
Role: face/head/microexpression; body support only.

```text
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands retrieval disabled
generic whole-upper retrieval disabled
face/head median weight = 0.913145
body-support median weight = 0.519182
```

## Third source — SIENA_BRUTO

Canonical source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4`

Verified duration: **113.313 s**.

Selected gate: **C6 = 75.2–80.2 s**.

Uploaded overlay was visually inspected across the 30 frames:

- face/head stable;
- shoulders/elbows/torso coherent;
- coarse arm/posture motion tracked smoothly;
- hands are near the lower frame boundary and finger landmarks are unstable/spread.

Classification: **SIENA C6 VISUAL GATE PASS FOR TORSO / POSTURE / HEAD / COARSE ARM MOTION**.

Do not treat SIENA as a hand source yet. Hand retrieval remains pending full-inventory per-unit quality evidence. The primary source remains canonical for hands/gesture.

Provisional semantic-suspect spans from the SIENA contact sheet, review-only:

```text
~5–10 s   inserted image/graphic overlays
~19–24 s  held print/book/photo interaction
~47–52 s  lens/camera foreground interaction/occlusion
```

Exact boundaries must be determined after full profile/inventory generation.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_full_tertiary.ps1'
```

This runs DWPose only, 6 fps / long side 960 / CPU, and retains all 133 keypoints. It does not run Wan-Animate-2.

Expected outputs:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\pose_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\pose_coco133.jsonl.summary.json
```

Paste the final summary before building the SIENA behavior profile.

## After full SIENA pose PASS

1. build/inspect SIENA `behavior-profile/v1`;
2. analyze inventory/group reliability;
3. determine exact semantic exclusion intervals for overlays/objects/occlusions;
4. role-aware SIENA curation; enable hands only where evidence supports them;
5. build unified source-preserving multi-source library;
6. synthesize a new 4–5 s behavioral driver;
7. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
