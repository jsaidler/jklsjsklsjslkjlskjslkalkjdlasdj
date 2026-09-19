# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA CURATED PASS / UNIFIED LIBRARY PASS / DRIVER v1 FAIL / DRIVER v2 IMPROVED BUT NOT PASS / DRIVER v3 QA NEXT**

Continue in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/synthesize_behavioral_pose_driver_v3.py`;
6. `tools/video-studio/run_behavior_first_pose_driver_v3_and_qa.ps1`.

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

Locked exclusions:

```text
4.6–10.3 s    u0003-u0004
18.7–24.7 s   u0009-u0010
43.7–55.7 s   u0021-u0025
67.9–74.0 s   u0031-u0033
```

SIENA pose-reliability weights are saturated at 1.0 and do not rank clean units meaningfully.

## Unified library — PASS

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

```text
271 total units
primary 118
secondary 116
tertiary 37
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## Driver v1 — FAIL

4.5 s / 24 fps / neutral QA.

Key failure:

```text
transition q90 / normal q90
body_head  6.1729x
face       3.1519x
left_hand  3.0979x
right_hand 1.5199x

hand OOB
left  41.71%
right 44.09%
```

Visual preview confirmed body reconfiguration and hands lost below frame. Library remained valid.

## Driver v2 — major improvement / not full PASS

```text
base primary -> tertiary
overlap 1.875–2.625 s / 0.75 s
base continuity 0.615637
face continuity 0.937309
hand continuity 0.783131
predicted hand in-frame 0.707143
```

QA:

```text
OOB
coarse_head 0.00%
upper_body  6.37%
lower_body  3.42%
face        0.00%
left_hand  21.87%
right_hand 27.73%

transition q90 / normal q90
body_head  0.7920x
face       2.4043x
left_hand  0.2085x
right_hand 0.8727x
```

Visual review of `first_driver_v2\behavioral_driver_pose_preview.mp4`:

- body transition is substantially fixed and no longer reads as a skeleton swap;
- hands still scrape/leave the lower frame too frequently, especially second segment;
- face remains stable spatially but accelerates through the overlap, matching the 2.40× numeric signal.

Classification: **v2 improved but NOT PASS**. Wan remains blocked.

## Architectural clarification — LOCKED

Source-camera translation/scale is not behavioral identity. A single constant similarity transform may normalize the synthesized performance into a canonical target canvas because it preserves relative pose/motion and adds no dynamic camera motion.

## Driver v3 — IMPLEMENTED

Versioned:

- `synthesize_behavioral_pose_driver_v3.py`
- `run_behavior_first_pose_driver_v3_and_qa.ps1`

Changes from v2:

1. base and hands selected jointly;
2. retargeted hand framing is a constraint, attempted at floors `0.90 -> 0.86 -> 0.82 -> 0.78 -> 0.74`;
3. base pair can change if a high-scoring body pair cannot support in-frame hands;
4. hand pair also scores forward source-time adjacency;
5. face pair favors forward/adjacent secondary units and scores both shape and velocity continuity;
6. one constant robust global similarity transform normalizes the complete driver to the portrait frame;
7. transform scale is not allowed below `0.82`, preventing framing failures from being hidden by excessive shrinking.

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3`

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_v3_and_qa.ps1'
```

This runs no DWPose and no Wan. Paste the complete terminal output and upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3\behavioral_driver_pose_preview.mp4`

Review goals:

- hand OOB materially below v2 (`21.9% / 27.7%`);
- face transition ratio materially below v2 (`2.40x`);
- body transition remains as stable as v2 (`0.79x` transition q90 / normal q90);
- visual preview reads as one continuous performance.

Only after a true v3 PASS should we inspect the installed Wan-Animate-2 conditioning interface and prepare the first render spike.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
