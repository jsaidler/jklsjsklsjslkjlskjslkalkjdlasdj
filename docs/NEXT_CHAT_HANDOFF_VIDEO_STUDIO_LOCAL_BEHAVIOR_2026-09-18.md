# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY SOURCE CURATED PASS / SECONDARY GATE CANDIDATE SELECTION NEXT**

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_secondary_gate_candidates.ps1`;
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

## Multi-source requirement — LOCKED

Final behavior library must use all canonical sources:

- `VID_20260911_140124885.mp4` — torso/hands/posture/gesture primary;
- `VID_20260819_124008056.mp4` — head/face/microexpression;
- `SIENA_BRUTO.mp4` — additional gesture/posture with exclusions.

## Primary source — CURATED PASS

Primary corrected pose/profile path passed.

Full pose:

```text
540x960 @ 6 fps
1801 frames
0/1801 detector fallback
mean keypoint score 0.7549247491487903
CPUExecutionProvider
```

Behavior profile:

```text
status complete
123 units
0.0 -> 300.352 s continuous coverage
123/123 valid pose snapshots
all 123 units have head/body/left-hand/right-hand activity
```

Inventory review established strong overall upper-body coverage and continuous group-quality weighting rather than binary rejection by relative coverage.

Manual hard exclusion:

**24.1–37.5 s = `u0012`–`u0016`** due held-object/prop interaction and hand occlusion.

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

## Secondary source — NEXT

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: **facial/head/microexpression source**.

Do not launch full pose extraction yet.

First select a clean 5-second candidate with visible face, useful head/expression variation, minimal occlusion and stable framing.

Versioned sampler:

`tools/video-studio/run_behavior_secondary_gate_candidates.ps1`

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_gate_candidates.ps1'
```

Expected contact sheet:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\gate_candidates\candidate_contact_sheet.jpg`

Upload that JPG. Choose the best face/head interval before running DWPose on only those 5 seconds.

## After secondary visual gate selection

1. run DWPose on the selected 5 seconds only;
2. render/inspect the COCO WholeBody overlay, paying special attention to face/head landmarks and upper-body continuity;
3. only if visual gate passes, run full 6 fps secondary pose extraction;
4. build/inspect/curate its behavior profile;
5. then process `SIENA_BRUTO.mp4` with source-specific exclusions;
6. build unified multi-source João library;
7. synthesize a new 4–5 s multi-source behavioral driver;
8. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
