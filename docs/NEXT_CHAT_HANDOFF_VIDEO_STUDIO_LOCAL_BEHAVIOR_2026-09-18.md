# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY FULL POSE PASS / FACIAL QA PASS / SECONDARY PROFILE+FACIAL SIDECAR NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the canonical source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/build_facial_behavior_sidecar.py`;
6. `tools/video-studio/inspect_facial_behavior_sidecar.py`;
7. `tools/video-studio/run_behavior_secondary_profile_and_facial_sidecar.ps1`.

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

## Secondary source — FULL POSE PASS

`VID_20260819_124008056.mp4`

Role: head/face/microexpression.

Validated facial gate: C3 = **83.6–88.6 s**.

Full pose:

```text
1695 frames @ 6 fps
coded 1920x1080
display 1080x1920
rotation 90
analysis 540x960
1/1695 detector fallback
mean keypoint score 0.5453589803
CPUExecutionProvider
```

## Facial sidecar architecture — LOCKED

Keep `behavior-profile/v1` unchanged. Add aligned `facial-behavior-profile/v1` using face landmarks 23–90.

Normalization:

- eye-line midpoint center;
- remove in-plane roll;
- divide by inter-eye-center distance.

Facial hard suspects are excluded only from the facial layer, never automatically from the underlying motion unit.

Continuous per-unit face weight:

```text
face_quality_weight = accepted_frame_ratio * mean_face_point_presence * mean_landmark_confidence
```

## Facial quality audit — PASS

Observed:

```text
frames total: 1695
normalized: 1677
normalization failed: 18
static hard suspects: 101
temporal review suspects: 47
accepted facial static geometry: 1576/1695 = 0.929794
```

Filtered descriptor ranges:

```text
expression mean/peak: 0.135848 / 0.712936
mouth mean/peak: 0.188157 / 0.921541
mouth_open mean/range: 0.023286 / 0.118971
mouth_width mean/range: 0.886436 / 0.192813
eye_open mean/range: 0.063497 / 0.038902
brow_eye_distance mean/range: 0.162553 / 0.119461
```

The review JPG confirms that top hard suspects are predominantly face-off-frame / severe crop / lateral degenerate-normalization frames. The source remains valid.

Classification: **SECONDARY FACIAL FRAME QA PASS**.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_profile_and_facial_sidecar.ps1'
```

This does **not** run DWPose and does not run Wan-Animate-2. It:

1. builds secondary `behavior-profile/v1` from the already existing pose track;
2. structurally inspects it;
3. builds aligned `facial-behavior-profile/v1` from accepted facial frames;
4. inspects sidecar alignment and face-quality distributions.

Expected outputs:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\manifest.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\motion_units.csv
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\profile_inspection.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\facial_behavior_profile.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\facial_sidecar_inspection.json
```

Paste the complete terminal output before any secondary curation.

## After structural pass

1. curate secondary units with strong source-role emphasis on face/head and continuous face quality;
2. optionally derive facial sidecar for primary from existing 133-point track without rerunning DWPose;
3. process `SIENA_BRUTO.mp4` with source-specific exclusions;
4. build unified source-preserving library;
5. synthesize a new 4–5 s multi-source behavioral driver;
6. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
