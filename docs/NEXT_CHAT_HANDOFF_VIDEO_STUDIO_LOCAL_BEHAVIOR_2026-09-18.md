# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **CORRECTED C3 VISUAL POSE GATE PASS / FULL PRIMARY POSE EXTRACTION NEXT**

## Continue from canonical state

Continue the **Local Video Studio** in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. this file;
6. `tools/video-studio/extract_dwpose_track.py`;
7. `tools/video-studio/extract_behavior_profile.py`;
8. `tools/video-studio/run_behavior_pose_full.ps1`.

GitHub living docs are source of truth. Do not reconstruct state from memory when docs differ.

## Hard constraints

- 100% local/self-hosted;
- zero service cost;
- never upload João's video/voice/identity to third parties;
- no SaaS/paid API/credits/subscriptions;
- do not download another large renderer;
- do not reopen Wan S2V, H3, Hunyuan or HeyGen as next route;
- no new Python/DWPose/CUDA install while current local route works;
- MuseTalk/LatentSync/TTS remain deferred.

## Goal

New text/audio must eventually produce a new performance that looks, sounds and chiefly **moves/reacts like João**. Generic presenter motion is failure.

## Validated local pose stack

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

DWPose functional runtime: PASS.

CUDA ONNX Runtime: not validated; missing `cublasLt64_13.dll` was reported. CPU is the validated path. Do not install CUDA components yet.

## Critical preprocessing correction

The primary source is coded `3840x2160` but displayed as portrait via stream rotation metadata. Earlier extraction calculated analysis geometry from coded dimensions while FFmpeg autorotated, distorting portrait content to `960x540` before DWPose.

`extract_dwpose_track.py` now reads rotation metadata and derives analysis size from **display dimensions**. The corrected primary-source pose analysis is portrait, approximately `540x960`.

## Visual pose gate result

Clean gate interval: **C3 = 88.7–93.7 s**.

Corrected portrait overlay was uploaded and inspected frame-by-frame.

PASS evidence:

- face landmarks remain on face;
- shoulders/elbows/wrists/hips remain anatomically aligned;
- both hands follow the moving hands through the gesture sequence;
- no subject switch;
- no gross left/right swap or upper-body temporal jump.

Distracting lines toward the lower frame are low-confidence/off-frame lower-body/foot landmarks shown by the QA renderer. They do not invalidate behavior-profile v1.

Important: QA overlay displayed points at score >= 0.05; `extract_behavior_profile.py` uses `CONF = 0.20`. v1 activity groups are head 0–4, body 5–12, left hand 91–111, right hand 112–132. Low-confidence points are ignored.

Classification:

**C3 corrected upper-body visual pose gate: PASS.**

## Next exact action

Run full primary pose extraction only:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_full.ps1'
```

Expected output track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`

Summary:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl.summary.json`

After completion, inspect/paste:

- frames;
- display + analysis dimensions;
- ONNX provider;
- detector fallback count/ratio;
- mean keypoint score.

Do not build the profile automatically if full extraction reports anomalies.

## After full-track review

1. run `extract_behavior_profile.py` with the full pose track;
2. require `status=complete`;
3. inspect `manifest.json` + `motion_units.csv`;
4. reject/down-weight object-occluded or low-quality spans;
5. synthesize a new 4–5 s behavioral driver from multiple João motion units;
6. only then invoke installed Wan-Animate-2.

## Final human quality gate

> “isso não apenas parece João; isso se move e reage como João.”
