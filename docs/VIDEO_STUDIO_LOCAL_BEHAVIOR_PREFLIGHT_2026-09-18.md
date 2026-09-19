# Local Video Studio — local behavior route preflight

Date: **2026-09-18**  
Strict follow-up/current state: **2026-09-19**  
Status: **WAN-ANIMATE-2 REUSE PASS / LOCAL DWPOSE REUSE PASS / CORRECTED C3 VISUAL POSE GATE PASS / FULL PRIMARY POSE EXTRACTION NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Technical route: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Locked constraints

Fully local/self-hosted and zero-service-cost. João identity media stays local. No new large renderer, DWPose package, Python environment or CUDA repair is justified at this gate.

## Behavioral sources — PASS

Primary source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

- duration: 300.352 s;
- coded geometry: 3840x2160;
- portrait display orientation comes from stream rotation metadata.

Other canonical sources remain available for later facial/alternate behavior enrichment.

## Wan-Animate-2 reuse — PASS

Installed locally and reserved for after behavior-profile validation. No new renderer is justified.

## WanGP / DWPose reuse — PASS

Validated local components:

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

No alternate pose stack download is required.

## Runtime probe — FUNCTIONAL PASS

Detector + whole-body inference returned `coco_wholebody_133` on a real source frame with no detector fallback.

CUDA ONNX Runtime remains **not validated** because provider loading reported missing `cublasLt64_13.dll` / CUDA-cuDNN dependencies. CPU is the validated path. Do not install CUDA dependencies yet.

## Preprocessing defect discovered and fixed

Early pose runs used coded 3840x2160 dimensions to choose analysis geometry while FFmpeg autorotated the video to portrait. That distorted the displayed portrait frame into 960x540 before DWPose.

`extract_dwpose_track.py` now reads rotation metadata, separates coded and display dimensions, and computes the analysis size from display geometry. The primary source now analyzes at portrait geometry (approximately 540x960 for long side 960).

Classification: **display-orientation preprocessing FIXED**.

## Visual validation — PASS after correction

The first 30–35 s sample was rejected because a held object occluded hands/torso. A clean interval was then selected:

**C3 = 88.7–93.7 s.**

After the orientation correction, the uploaded 30-frame / 6 fps / 540x960 C3 overlay was inspected.

Profile-relevant upper-body result:

- face/head alignment stable;
- shoulders/elbows/wrists/hips aligned;
- both moving hands followed plausibly;
- no subject switch;
- no gross left/right swap;
- no upper-body temporal jump that invalidates behavior descriptors.

The QA overlay used a display threshold of 0.05 and therefore shows distracting low-confidence/off-frame lower-body and foot lines. `extract_behavior_profile.py` uses `CONF = 0.20` and only behaviorally relevant upper-body groups for v1 activity:

- head 0–4;
- body 5–12;
- left hand 91–111;
- right hand 112–132.

Classification: **CORRECTED C3 UPPER-BODY VISUAL POSE GATE PASS**.

## Full extraction — NEXT

Versioned runner:

`tools/video-studio/run_behavior_pose_full.ps1`

It runs only DWPose on the full primary source using:

- 6 fps;
- long side 960;
- portrait-aware analysis geometry;
- CPU provider;
- output `pose_coco133.jsonl` + `.summary.json` in the primary profile directory.

Review full-track summary before building the behavior profile.

## Deferred components

- CUDA ONNX repair: deferred unless CPU becomes a real blocker;
- MuseTalk / LatentSync: deferred;
- final TTS / voice clone: deferred;
- Wan-Animate-2: blocked until complete behavior profile is inspected.

## Current exact gate

```text
local WanGP + DWPose reuse PASS
    -> runtime PASS
    -> orientation fix PASS
    -> corrected C3 upper-body visual pose gate PASS
    -> FULL 6 fps primary pose track NEXT
    -> behavior profile status=complete
    -> motion-unit quality/occlusion filtering
    -> new multi-unit behavioral driver
    -> installed Wan-Animate-2
```
