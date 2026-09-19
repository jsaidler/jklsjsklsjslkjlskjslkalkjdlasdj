# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY FULL POSE PASS / FACIAL PROBE COVERAGE PASS / FACIAL QUALITY AUDIT NEXT**

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/facial_descriptors.py`;
6. `tools/video-studio/audit_facial_track_quality.py`;
7. `tools/video-studio/render_facial_quality_review.py`;
8. `tools/video-studio/run_behavior_secondary_facial_quality_audit.ps1`.

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

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: face/head/microexpression.

Validated C3 gate: **83.6–88.6 s**.

Full pose:

```text
source_duration_s: 282.574
1695 frames @ 6 fps
coded 1920x1080
display 1080x1920
rotation 90
analysis 540x960
1/1695 detector fallback
mean keypoint score 0.5453589803
CPUExecutionProvider
```

Classification: **SECONDARY FULL POSE TRACK PASS**.

## Facial representation — ADDITIVE SIDECAR

Keep `behavior-profile/v1` unchanged.

Use a separate aligned `facial-behavior-profile/v1` sidecar derived from face landmarks 23–90.

Normalization:

- eye-line midpoint center;
- remove in-plane roll;
- divide by inter-eye-center distance.

Descriptor groups:

- internal expression deformation;
- brows;
- eyes;
- mouth;
- mouth open/width;
- eye open;
- brow-eye distance;
- face presence/confidence.

## Facial probe result

Full-track coverage is excellent:

```text
1695 frames
1677 normalized = 0.989381
mean face-point presence = 0.988383
mean landmark confidence = 0.910192
```

Validated C3 is coherent:

```text
expression mean/peak = 0.122421 / 0.2463
brows mean/peak = 0.085689 / 0.341491
eyes mean/peak = 0.031661 / 0.040425
mouth mean/peak = 0.169658 / 0.361598
mouth_open range = 0.08113
mouth_width range = 0.106278
eye_open range = 0.01531
brow_eye_distance range = 0.080742
```

Full-track raw maxima contain pathological outliers:

```text
expression peak 37.065123
mouth peak 58.962267
mouth_open range 1.62261
eye_open range 4.18874
brow_eye_distance range 3.146605
```

These are not plausible expression values. Do not reject the source: coverage/confidence are high and C3 passed visually. Instead quality-gate the small number of pathological frames before materializing facial units.

## Next exact action — facial quality audit

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_facial_quality_audit.ps1'
```

Audit policy:

- source-relative Tukey outer fences, 3×IQR;
- normalization failures + static geometry outliers = hard suspects;
- temporal expression jumps = review-only;
- recompute filtered descriptor summary after hard suspects are removed;
- render up to 24 suspect timestamps in one JPG.

Expected outputs:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\facial_quality_audit.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\facial_quality_review_sheet.jpg
```

Paste the complete terminal output and upload the JPG.

## After audit confirmation

1. lock the facial frame-quality policy;
2. build base secondary `behavior-profile/v1` using the full pose track;
3. materialize aligned `facial-behavior-profile/v1` using only accepted facial frames plus reliability weights;
4. inspect/curate secondary units with source role strongly favoring face/head;
5. process `SIENA_BRUTO.mp4`;
6. build unified source-preserving library;
7. synthesize a new 4–5 s multi-source behavioral driver;
8. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
