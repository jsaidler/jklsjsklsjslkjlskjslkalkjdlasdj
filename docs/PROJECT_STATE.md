# Local Video Studio — Current Project State

Status date: **2026-09-19**

GitHub living documents are the canonical source of truth.

## Execution policy — LOCKED

- 100% local/self-hosted;
- zero service cost;
- no SaaS/cloud generation/training/inference;
- never upload João's video/voice/identity to third parties;
- no new large renderer while this route is active;
- no new Python/DWPose/CUDA install while the validated local route works;
- Wan S2V, H3, Hunyuan and HeyGen remain historical/retired;
- MuseTalk/LatentSync/CosyVoice remain deferred.

## Objective — LOCKED

Generate new video from new text/audio that looks, sounds and chiefly **moves/reacts like João**. Generic plausible presenter motion is failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior-profile/v1 motion units
    -> optional aligned facial-behavior-profile/v1 sidecar
    -> source-specific semantic + role-aware quality curation
    -> unified source-preserving João motion library

new local speech/audio
    -> prosodic windows
    -> retrieve by source role + quality + continuity + diversity
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A single source video is never the final library, and different sources do not have interchangeable roles.

## Canonical sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

1. `VID_20260911_140124885.mp4` — 300.352 s — torso/hands/posture/gesture primary;
2. `VID_20260819_124008056.mp4` — 282.574 s — head/face/microexpression;
3. `SIENA_BRUTO.mp4` — 113.313208 s — alternate posture/arm/head vocabulary with explicit prop/occlusion handling.

## Local pose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

Validated provider: `CPUExecutionProvider`. CUDA ORT remains intentionally unrepaired because its EP reported missing `cublasLt64_13.dll` while CPU is functional.

## Primary source — CURATED PASS

`VID_20260911_140124885.mp4`

```text
full pose frames: 1801
fallback: 0/1801
mean keypoint score: 0.7549247491
behavior-profile/v1: complete
motion units: 123
curated eligible: 118
hard excluded: 5
```

Manual generic-behavior exclusion: **24.1–37.5 s = `u0012`–`u0016`** for held object / hand occlusion / prop interaction.

Role: primary torso/hands/posture/gesture source.

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — CURATED PASS

`VID_20260819_124008056.mp4`

Role: **face/head/microexpression**, body support only.

```text
full pose: 1695 frames @ 6 fps
fallback: 1/1695
base units: 119
facial units usable with >=2 accepted frames: 116
face eligible: 116
head eligible: 116
body-support eligible: 116
hands retrieval: disabled
generic whole-upper retrieval: disabled
```

Facial quality policy remains locked: landmarks 23–90, eye-line normalization, roll removal, inter-eye scale, source-relative 3×IQR static-geometry audit, temporal jumps review-only.

```text
accepted facial geometry: 1576/1695 = 0.929794
face/head median weight: 0.913145
body-support median weight: 0.519182
```

Classification: **SECONDARY SOURCE CURATED PASS**.

## Third source — SIENA_BRUTO FULL POSE PASS

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4`

Selected/validated short gate: **C6 = 75.2–80.2 s**.

Short-gate visual classification remains:

**PASS for torso / posture / head / coarse arm motion. Hands remain pending per-unit full-inventory evidence because finger landmarks are unstable near the lower frame boundary.**

Full pose result:

```text
duration: 113.313208 s
coded: 1080x1920
display: 1080x1920
rotation: 0
analysis: 540x960
frames: 680 @ 6 fps
last timestamp: 113.166667 s
detector fallback: 0/680 = 0.0
mean keypoint score: 0.6698323212
provider: CPUExecutionProvider
elapsed: 1047.040972 s
wall throughput: 0.649449 fps
```

Classification: **SIENA FULL POSE TRACK PASS**.

All 133 keypoints are preserved. This result does **not** promote SIENA to a hand source; that decision remains per-unit and evidence-based.

Provisional semantic-suspect spans from the verified SIENA candidate sheet remain review-only:

- ~5–10 s: inserted still-image/graphic overlays;
- ~19–24 s: held print/book/photo interaction and hand occlusion;
- ~47–52 s: lens/camera foreground interaction/occlusion.

Exact exclusion boundaries must be derived from the generated SIENA behavior profile/inventory, not from the coarse sampler alone.

### Progress-output policy — LOCKED

Long DWPose passes must emit visible progress. `extract_dwpose_track.py` now reports initialization and frequent heartbeat/progress instead of leaving the terminal silent for long intervals.

## Immediate next action

Build and inspect the SIENA profile/inventory from the already-complete pose track:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_tertiary_profile_inventory.ps1'
```

This runs **no DWPose and no Wan-Animate-2**. It:

1. builds `behavior-profile/v1`;
2. validates structure;
3. analyzes per-unit/group reliability;
4. renders `inventory_review_sheet.jpg` for semantic/quality review.

Expected artifacts include:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\manifest.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\motion_units.csv
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\profile_inspection.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\inventory_analysis.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\inventory_units.csv
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\inventory_review_sheet.jpg
```

Paste the complete terminal output and upload the inventory review sheet before SIENA semantic exclusions/curation.

## Downstream

1. inspect SIENA profile/inventory;
2. determine exact overlay/object/occlusion exclusion intervals;
3. role-aware SIENA curation; enable hands only where per-unit evidence supports them;
4. build unified source-preserving multi-source library;
5. synthesize a new 4–5 s multi-source behavioral driver;
6. only then invoke installed Wan-Animate-2.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.
