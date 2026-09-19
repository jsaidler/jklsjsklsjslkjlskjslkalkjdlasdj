# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA FULL POSE PASS / SIENA PROFILE+INVENTORY NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_tertiary_profile_inventory.ps1`.

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

`VID_20260911_140124885.mp4` — torso/hands/posture/gesture.

```text
123 total units
118 eligible
5 hard excluded
24.1–37.5 s excluded for held object / hand occlusion / prop interaction
```

## Secondary source — CURATED PASS

`VID_20260819_124008056.mp4` — face/head/microexpression; body support only.

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

## Third source — SIENA_BRUTO FULL POSE PASS

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4`

Short visual gate C6 = **75.2–80.2 s** passed for torso/posture/head/coarse arms. Hands remained visibly unstable near the lower frame boundary, so SIENA is **not** yet a hand source.

Full pose result:

```text
duration 113.313208 s
coded/display 1080x1920
rotation 0
analysis 540x960
680 frames @ 6 fps
0/680 detector fallback
mean keypoint score 0.6698323212
CPUExecutionProvider
```

Classification: **SIENA FULL POSE TRACK PASS**.

Provisional semantic review markers only:

```text
~5–10 s   inserted still-image/graphic overlays
~19–24 s  held print/book/photo interaction + hand occlusion
~47–52 s  lens/camera foreground interaction/occlusion
```

Do not lock exact exclusions from these coarse sampler windows. Use the full profile/inventory to establish exact unit/span boundaries.

Progress policy: long DWPose extraction now emits frequent live progress; do not revert to silent long-running execution.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_tertiary_profile_inventory.ps1'
```

This does not run DWPose or Wan. It:

1. builds SIENA `behavior-profile/v1` from the existing 680-frame pose track;
2. structurally inspects the profile;
3. analyzes pose/group reliability by motion unit;
4. renders `inventory_review_sheet.jpg`.

Expected outputs:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\manifest.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\motion_units.csv
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\profile_inspection.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\inventory_analysis.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\inventory_units.csv
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\inventory_review_sheet.jpg
```

Paste the complete terminal output and upload the review sheet.

## After SIENA inventory review

1. define exact semantic exclusions for overlays/objects/occlusions;
2. role-aware SIENA curation;
3. keep posture/head/coarse-arm retrieval enabled where quality supports it;
4. enable hand retrieval only for units with actual per-unit evidence;
5. build unified source-preserving multi-source library;
6. synthesize a new 4–5 s behavioral driver;
7. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
