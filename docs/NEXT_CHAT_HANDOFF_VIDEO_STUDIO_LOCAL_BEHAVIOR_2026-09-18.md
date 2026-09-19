# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY FULL POSE PASS / FACIAL DESCRIPTOR PROBE NEXT**

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/facial_descriptors.py`;
6. `tools/video-studio/inspect_facial_track.py`;
7. `tools/video-studio/run_behavior_secondary_facial_probe.ps1`.

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
Units total: 123
Eligible: 118
Hard excluded: 5
Manual exclusion: 24.1-37.5 s / held_object,hand_occlusion,prop_interaction
```

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — FULL POSE PASS

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: face/head/microexpression.

Validated C3 gate: **83.6–88.6 s**.

Gate geometry:

```text
coded 1920x1080
display 1080x1920
rotation 90
analysis 540x960
30 frames @ 6 fps
0 fallback
```

Full pose track:

```text
source_duration_s: 282.574
frames: 1695
last_timestamp_s: 282.333333
analysis: 540x960
rotation: 90
detector fallback: 1/1695 = 0.0005899705
mean keypoint score: 0.5453589803
provider: CPUExecutionProvider
```

Classification: **SECONDARY FULL POSE TRACK PASS**.

## Facial representation — ADDITIVE SIDECAR

Do not mutate the already validated `behavior-profile/v1` schema.

Use:

```text
behavior-profile/v1
+ facial-behavior-profile/v1 sidecar
```

The sidecar aligns to the same motion-unit IDs/timestamps and uses COCO WholeBody face landmarks 23–90.

Normalization:

- eye-line midpoint centering;
- remove in-plane roll;
- divide by inter-eye-center distance.

This removes image translation/roll/scale before expression-deformation measurement. Perspective/yaw/pitch are not claimed to be removed.

Descriptor targets:

- overall internal expression deformation (jaw excluded);
- brows;
- eyes;
- mouth;
- mouth opening;
- mouth width;
- eye opening;
- brow-eye distance;
- facial point presence/confidence.

Versioned:

- `tools/video-studio/facial_descriptors.py`;
- `tools/video-studio/inspect_facial_track.py`;
- `tools/video-studio/run_behavior_secondary_facial_probe.ps1`.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_facial_probe.ps1'
```

This does not run DWPose or Wan. It reads the existing full pose track and prints facial descriptor diagnostics for:

1. full second source;
2. visually validated C3 = 83.6–88.6 s.

Paste the complete terminal output.

## After facial descriptor probe PASS

1. materialize `facial-behavior-profile/v1` aligned to secondary motion units;
2. build/inspect/curate secondary behavior profile with strong face/head weighting;
3. optionally derive facial sidecar for primary from its existing 133-point track without rerunning DWPose;
4. process `SIENA_BRUTO.mp4` with source-specific exclusions;
5. build unified source-preserving library;
6. synthesize a new 4–5 s multi-source behavioral driver;
7. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
