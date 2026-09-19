# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA CURATED PASS / UNIFIED LIBRARY PASS / DRIVER v1 FAIL / DRIVER v2 IMPLEMENTED / LOCAL v2 QA NEXT**

Continue in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/synthesize_behavioral_pose_driver_v2.py`;
6. `tools/video-studio/inspect_behavioral_pose_driver_overlap.py`;
7. `tools/video-studio/run_behavior_first_pose_driver_v2_and_qa.ps1`.

## Hard constraints

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current CPU route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred;
- no Wan-Animate-2 until a multi-source pose driver passes numeric + visual QA.

## Curated sources

### Primary
`VID_20260911_140124885.mp4` — torso/hands/gesture/posture.

```text
123 total
118 eligible
5 excluded
24.1–37.5 s / u0012-u0016 excluded
```

### Secondary
`VID_20260819_124008056.mp4` — face/head/microexpression; body support only.

```text
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands disabled
face/head median quality 0.913145
```

### SIENA
`SIENA_BRUTO.mp4` — alternate posture/head/coarse arm.

```text
49 total
12 hard excluded
37 clean
hands disabled
generic whole-upper disabled
```

Locked SIENA exclusions:

```text
4.6–10.3 s    u0003-u0004
18.7–24.7 s   u0009-u0010
43.7–55.7 s   u0021-u0025
67.9–74.0 s   u0031-u0033
```

SIENA pose reliability is saturated at 1.0 and does not rank its clean units meaningfully.

## Unified library — PASS

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

```text
271 total units
primary 118
secondary 116
tertiary 37
```

## Driver v1 — FAIL

Neutral 4.5 s / 24 fps / 108-frame multi-source QA synthesis.

Numeric evidence:

```text
confidence-qualified OOB:
upper_body  0.177083
left_hand   0.417108
right_hand  0.440917
face        0.000000
coarse_head 0.000000

transition q90 / normal q90:
body_head  6.1729x
face       3.1519x
left_hand  3.0979x
right_hand 1.5199x
```

Visual preview confirmed the same failure: around the `primary -> SIENA` transition the skeleton drops/reconfigures too quickly, and afterward hands/arms disappear through the lower frame boundary. Face/head remain comparatively stable.

Interpretation: source library remains valid; compositor v1 fails. Wan stays blocked.

## Driver v2 — IMPLEMENTED

Files:

- `synthesize_behavioral_pose_driver_v2.py`
- `inspect_behavioral_pose_driver_overlap.py`
- `run_behavior_first_pose_driver_v2_and_qa.ps1`

Evidence-driven changes:

- stronger base-pair continuity in retrieval;
- base candidate framing includes body coverage + wrist room;
- hand donors are selected jointly with the chosen base using predicted post-retarget in-frame coverage;
- face pair selection includes normalized face-shape continuity;
- hand pair selection includes normalized hand-shape continuity;
- symmetric **0.75 s** overlap/crossfade with quintic easing replaces the v1 0.25 s incremental blend;
- v1 output is preserved; v2 writes to `...\first_driver_v2`.

Default 4.5 s geometry:

```text
segment duration 2.625 s
overlap 1.875 -> 2.625 s
blend 0.75 s
```

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_v2_and_qa.ps1'
```

This runs no DWPose and no Wan. It synthesizes v2 and immediately runs overlap-aware numeric QA.

Expected artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\driver_plan.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\behavioral_driver_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\behavioral_driver_pose_preview.mp4
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\driver_qa.json
```

Paste complete terminal output and upload the v2 preview. Only a numeric + visual PASS can unblock Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
