# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY SOURCE CURATED PASS / SECONDARY FACIAL GATE PASS / SECONDARY FULL POSE NEXT**

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_pose_full_secondary.ps1`;
6. `tools/video-studio/extract_dwpose_track.py`;
7. `tools/video-studio/extract_behavior_profile.py`;
8. `tools/video-studio/behavior_profile_schema_v1.json`.

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

```text
Units total: 123
Eligible: 118
Hard excluded: 5
Manual exclusion: 24.1-37.5 s / held_object,hand_occlusion,prop_interaction
```

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — FACIAL/HEAD GATE PASS

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: **facial/head/microexpression source**.

Canonical gate:

**C3 = 83.6–88.6 s.**

Uploaded 30-frame / 6 fps overlay was visually inspected.

Result:

- facial landmarks 23–90 stay attached to brows, eyes, nose and mouth;
- mouth-shape changes track coherently;
- brow/eye landmarks remain stable;
- head landmark motion is smooth;
- no gross face-topology jump or subject switch;
- upper torso is coherent enough to anchor the sequence.

Whole-body/hand lines crossing the face in the QA overlay are clutter from off-frame groups, not failure of the facial landmarks.

Classification: **SECONDARY C3 FACIAL/HEAD VISUAL GATE PASS**.

## Important representation finding

Current behavior-profile v1 uses keypoints 0–4 for `head_motion`. That is too coarse to exploit this source's validated facial detail.

COCO WholeBody face landmarks **23–90** are now proven usable in the secondary gate.

Therefore:

- full secondary pose extraction is allowed immediately, because the JSONL preserves all 133 keypoints;
- do **not** build the secondary profile using only the existing head descriptor;
- after full-track validation, extend the profile representation additively with facial/microexpression descriptors from 23–90;
- keep the extension backward-compatible with the already-curated primary profile;
- primary facial features can later be recomputed from its existing full 133-point track without rerunning DWPose.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_full_secondary.ps1'
```

This runs only DWPose on the full second source at 6 fps / long side 960 / CPU and retains all 133 points. It does not invoke Wan-Animate-2.

Expected outputs:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl.summary.json
```

Paste the final summary/output.

## After secondary full pose PASS

1. implement additive facial/microexpression descriptors using landmarks 23–90;
2. validate those descriptors against the secondary gate/full-track distributions;
3. build/inspect/curate the secondary behavior profile with strong face/head weighting;
4. process `SIENA_BRUTO.mp4` with source-specific exclusions;
5. build unified source-preserving library;
6. synthesize a new 4–5 s multi-source behavioral driver;
7. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
