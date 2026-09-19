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

A single source video is never the final library, and different sources do **not** have interchangeable roles.

## Canonical sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

1. `VID_20260911_140124885.mp4` — 300.352 s — torso/hands/posture/gesture primary;
2. `VID_20260819_124008056.mp4` — 282.574 s — head/face/microexpression;
3. `SIENA_BRUTO.mp4` — 113.313 s — alternate gesture/posture with object/occlusion exclusions.

## Local pose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

Validated provider: `CPUExecutionProvider`. CUDA ORT remains intentionally unrepaired because its EP reported missing `cublasLt64_13.dll` while CPU is functional.

## Primary source — CURATED PASS

```text
full pose frames: 1801
fallback: 0/1801
mean keypoint score: 0.7549247491
behavior-profile/v1: complete
motion units: 123
```

Manual generic-behavior exclusion:

**24.1–37.5 s = `u0012`–`u0016`** due held object / hand occlusion / prop-specific interaction.

Final primary curation:

```text
123 total
118 eligible
5 hard excluded
```

Role: torso/hands/posture/gesture. Group quality remains continuous rather than using one global rejection threshold.

Artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_inventory.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\curated_motion_units.csv
```

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — CURATED PASS

Source: `VID_20260819_124008056.mp4`  
Role: **face/head/microexpression**, with body only as auxiliary support.

### Pose / profile / facial sidecar

```text
full pose: 1695 frames @ 6 fps
geometry: 1080x1920 display / rotation 90 / analysis 540x960
fallback: 1/1695
mean whole-body keypoint score: 0.5453589803
behavior-profile/v1: complete
base motion units: 119
facial-behavior-profile/v1 units: 119
facial units usable with >=2 accepted frames: 116
```

Facial frame QA remains locked:

- face landmarks 23–90;
- eye-line midpoint normalization;
- remove in-plane roll;
- divide by inter-eye distance;
- source-relative Tukey outer fences, 3×IQR;
- normalization failures + static geometry outliers are facial-layer-only hard suspects;
- temporal jumps are review-only.

Observed facial quality:

```text
accepted facial geometry: 1576/1695 = 0.929794
face weight q10/median/q90: 0.7649534 / 0.913145 / 0.9241892
```

### Secondary role-aware curation — PASS

Observed:

```text
units total: 119
global hard excluded: 0
face eligible: 116
head eligible: 116
body-support eligible: 116
hands retrieval: disabled
generic whole-upper retrieval: disabled
```

Role weights:

```text
face q10/median/q90: 0.7649534 / 0.913145 / 0.9241892
head q10/median/q90: 0.7649534 / 0.913145 / 0.9241892
body_support q10/median/q90: 0.4351354 / 0.519182 / 0.5724356
```

Lowest face-quality units:

```text
u0003 weight=0.0 accepted=0.0 frames=0
u0006 weight=0.0 accepted=0.0 frames=0
u0007 weight=0.0 accepted=0.0 frames=0
u0005 weight=0.276583 accepted=0.3125
u0094 weight=0.432046 accepted=0.466667
u0004 weight=0.440393 accepted=0.5
```

Interpretation:

- sparse hands are expected and not a source failure;
- zero-face units remain in the base profile but are ineligible for face/head retrieval;
- no unit is globally deleted solely because the face is unavailable;
- head quality equals face quality in the current curated result because coarse head pose is effectively saturated across the face-usable units; the discriminating factor is facial usability, so no artificial extra penalty is added.

Artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\curated_secondary_inventory.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\curated_secondary_motion_units.csv
```

Classification: **SECONDARY SOURCE CURATED PASS**.

## Third source — SIENA_BRUTO GATE SELECTED

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4`

Verified contact sheet:

```text
SOURCE: SIENA_BRUTO.mp4
duration: 113.313 s
window: 5 s
candidates: 8
```

Role: alternate gesture/posture vocabulary with explicit prop/object/occlusion handling.

### Selected clean gate — C6

**75.2–80.2 s**.

Why C6:

- no held object;
- torso is visible and stable;
- useful free arm/hand movement is present;
- no graphic overlay crossing the subject;
- stronger gesture/posture test than the more static C3/C5 windows.

Versioned runner:

`tools/video-studio/run_behavior_tertiary_pose_gate.ps1`

It runs DWPose only on C6 at 6 fps with the validated CPU provider and renders an overlay. It does not run Wan-Animate-2.

### Provisional semantic-suspect spans from the sampled sheet

These are **review markers only**, not final hard-exclusion boundaries:

- C1 / approximately 5–10 s: inserted still-image/graphic overlays obscure the subject;
- C2 / approximately 19–24 s: held print/book/photo interaction and hand occlusion;
- C4 / approximately 47–52 s: lens/camera prop interaction with major foreground occlusion.

Do not lock exact exclusion boundaries from the coarse contact sheet. Exact intervals must be derived from the full SIENA source/inventory after pose/profile generation.

Classification: **SIENA CLEAN GATE SELECTED / SHORT POSE GATE NEXT**.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_tertiary_pose_gate.ps1'
```

Expected artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\selected_gate\pose_gate_c6_75p2_80p2_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\selected_gate\pose_gate_c6_75p2_80p2_coco133.jsonl.summary.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\selected_gate\pose_gate_c6_75p2_80p2_overlay.mp4
```

Upload the overlay and paste the summary. Evaluate body/arms/hands/posture and geometry before any full SIENA extraction.

## Downstream

1. validate SIENA C6 short pose gate;
2. if gate passes, run full SIENA pose track;
3. build behavior profile and inventory;
4. define exact semantic exclusion intervals for overlays/objects/occlusions from the full source/inventory;
5. curate SIENA as alternate gesture/posture source;
6. preserve source IDs/timestamps/roles for every eligible unit;
7. build unified source-preserving library;
8. synthesize a new 4–5 s multi-source behavioral driver;
9. only then invoke installed Wan-Animate-2.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.
