# Local Video Studio — local behavior route preflight

Date: **2026-09-18**  
Strict follow-up/current state: **2026-09-19**  
Status: **WAN-ANIMATE-2 REUSE PASS / LOCAL DWPOSE REUSE PASS / CORRECTED C3 VISUAL PASS / FULL PRIMARY POSE PASS / PRIMARY PROFILE NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Technical route: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Locked constraints

Fully local/self-hosted and zero-service-cost. João identity media stays local. No new large renderer, DWPose package, Python environment or CUDA repair is justified at this gate.

## Behavioral sources

Primary source currently validated end-to-end through pose:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

- duration: 300.352 s;
- coded geometry: 3840x2160;
- display geometry: 2160x3840;
- rotation: 90°.

Final behavior library remains multi-source and must later include:

- `VID_20260819_124008056.mp4`;
- `SIENA_BRUTO.mp4` with quality exclusions.

## Wan-Animate-2 reuse — PASS

Installed locally and reserved for after behavior-profile/library validation. No new renderer is justified.

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

Detector + whole-body inference returned `coco_wholebody_133` on a real source frame.

CUDA ONNX Runtime remains **not validated** because provider loading reported missing `cublasLt64_13.dll` / CUDA-cuDNN dependencies. CPU is the validated path.

## Orientation preprocessing — FIXED

Pose extraction now derives geometry from display dimensions rather than coded dimensions. Correct primary DWPose analysis: **540x960**.

Behavior-profile motion energy was also corrected to preserve display aspect ratio. Primary portrait motion analysis will use **72x128** at 128 px long side instead of the old distorted 128x72.

## Corrected visual validation — PASS

Canonical clean interval: **C3 = 88.7–93.7 s**.

After orientation correction:

- face/head stable;
- shoulders/elbows/wrists/hips aligned;
- both hands track active gestures;
- no subject switch;
- no gross left/right swap;
- no invalidating upper-body temporal jump.

Behavior-profile v1 ignores pose points below confidence 0.20.

## Full primary pose extraction — PASS

Completed result:

```text
frames: 1801
last_timestamp_s: 300.0
sample_fps: 6.0
analysis: 540x960
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.7549247491487903
provider: CPUExecutionProvider
```

Combined with the clean visual gate, this authorizes primary behavior-profile construction.

## Primary behavior profile — NEXT

Versioned runner:

`tools/video-studio/run_behavior_profile_primary.ps1`

It builds:

- `manifest.json`;
- `motion_units.csv`;
- `profile_inspection.json`.

`inspect_behavior_profile.py` checks structural completeness, continuous source coverage, CSV/manifest unit agreement, valid 133-point pose snapshots and availability of head/body/hand activity.

Required status: **`complete`**.

## Deferred components

- CUDA ONNX repair: deferred unless CPU becomes a real blocker;
- MuseTalk / LatentSync: deferred;
- final TTS / voice clone: deferred;
- Wan-Animate-2: blocked until multi-source behavior inventory/synthesis is validated.

## Current exact gate

```text
local WanGP + DWPose reuse PASS
    -> runtime PASS
    -> orientation fix PASS
    -> corrected C3 visual pose gate PASS
    -> full primary pose track PASS
    -> PRIMARY behavior profile status=complete NEXT
    -> quality/occlusion annotation
    -> process remaining two behavior sources
    -> unified multi-source João motion library
    -> new multi-unit behavioral driver
    -> installed Wan-Animate-2
```
