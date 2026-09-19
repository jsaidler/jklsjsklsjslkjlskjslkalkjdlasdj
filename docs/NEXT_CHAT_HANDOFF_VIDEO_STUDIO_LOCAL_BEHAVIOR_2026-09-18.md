# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA GATE SAMPLING NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the canonical source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_tertiary_gate_candidates.ps1`;
6. `tools/video-studio/sample_behavior_gate_candidates.py`.

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

Base/facial state:

```text
119 base units
116 facial units usable with >=2 accepted frames
accepted facial geometry = 1576/1695 = 0.929794
```

Role-aware curation result:

```text
units total: 119
global hard excluded: 0
face eligible: 116
head eligible: 116
body-support eligible: 116
hands retrieval: disabled
generic whole-upper retrieval: disabled
```

Weights:

```text
face q10/median/q90 = 0.7649534 / 0.913145 / 0.9241892
head q10/median/q90 = 0.7649534 / 0.913145 / 0.9241892
body_support q10/median/q90 = 0.4351354 / 0.519182 / 0.5724356
```

Zero-face units `u0003`, `u0006`, `u0007` remain in the base profile but are not face/head retrieval candidates. Do not globally delete them solely for facial unavailability.

Artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\curated_secondary_inventory.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\curated_secondary_motion_units.csv
```

Classification: **SECONDARY SOURCE CURATED PASS**.

## Third source — SIENA_BRUTO

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4`

Role: alternate gesture/posture vocabulary, with explicit held-object/prop/occlusion handling.

Do not run full DWPose yet.

First generate an 8-candidate contact sheet of 5-second windows. Select a clean gate with useful gesture/posture and free body/hands, while separately noting visible object/occlusion spans for later semantic exclusions.

Versioned runner:

`tools/video-studio/run_behavior_tertiary_gate_candidates.ps1`

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_tertiary_gate_candidates.ps1'
```

This samples frames only. No DWPose and no Wan.

Upload:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\gate_candidates\candidate_contact_sheet.jpg
```

## After contact-sheet review

1. choose clean SIENA 5 s gate;
2. identify visible prop/object/occlusion intervals from the sampled material and later full inventory;
3. run short DWPose gate only;
4. if visual gate passes, run full SIENA pose track;
5. build/inspect/curate SIENA with source-specific semantic exclusions;
6. build unified source-preserving multi-source library;
7. synthesize a new 4–5 s behavioral driver;
8. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
