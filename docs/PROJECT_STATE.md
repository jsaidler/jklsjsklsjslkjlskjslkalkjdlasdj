# Local Video Studio — Current Project State

Status date: **2026-09-19**

GitHub living documents are the canonical source of truth.

## Execution policy — LOCKED

The Video Studio remains **100% local/self-hosted and zero-service-cost**.

Hard constraints:

- no hosted avatar/generation/training service;
- no SaaS/cloud inference API, credits or subscriptions;
- never upload João's video, voice or identity to third parties;
- no new large renderer while the behavior route is active;
- Wan S2V, H3, Hunyuan and HeyGen remain historical/retired routes;
- MuseTalk/LatentSync/CosyVoice remain deferred;
- no new Python/DWPose/CUDA install while the validated local route works.

## Active objective — LOCKED

Generate new video from new text/audio that looks, sounds and chiefly **moves/reacts like João**. Generic plausible presenter motion is failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior profiles / motion units
    -> source-quality annotation/curation
    -> unified persistent João motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve compatible units across sources
    -> pose continuity + diversity + quality/source weighting
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A single source video is not the final library.

## Canonical behavior sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

- `VID_20260911_140124885.mp4` — 300.352 s — primary torso/hands/posture/gesture source;
- `VID_20260819_124008056.mp4` — 282.6 s — facial/head/microexpression source;
- `SIENA_BRUTO.mp4` — 113.3 s — additional gesture/posture source with object/occlusion exclusions.

## Local pose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

DWPose functional runtime: PASS. CPU is the validated route. CUDA ONNX remains unvalidated because the CUDA EP reported missing `cublasLt64_13.dll`; do not repair CUDA yet.

## Primary source — CURATED PASS

The primary source is fully validated through pose, profile, inventory review and curation.

### Pose/profile path

Corrected display geometry:

- coded: 3840x2160;
- display: 2160x3840 via 90° stream rotation;
- DWPose analysis: 540x960;
- behavior-profile motion analysis: 72x128.

Clean C3 visual gate (88.7–93.7 s): PASS.

Full pose extraction:

```text
frames: 1801
sample_fps: 6.0
detector fallback: 0/1801
mean keypoint score: 0.7549247491487903
provider: CPUExecutionProvider
```

Behavior profile:

```text
status: complete
units: 123
coverage: 0.0 -> 300.352 s
pose snapshots valid: 123/123
activity units: head=123, body=123, left_hand=123, right_hand=123, combined_hands=123
speech classes: mixed=89, pause=4, speech=30
unit duration min/median/max: 0.800/2.500/3.800 s
```

### Inventory review and curation

`low_relative_pose_coverage` is a reliability diagnostic, not an automatic rejection condition. Group visibility remains a continuous weighting signal.

Manual hard exclusion:

**24.1–37.5 s = units `u0012` through `u0016`** because the sequence contains held-object/prop interaction and hand occlusion.

Canonical annotation:

`tools/video-studio/behavior_source_annotations_primary.json`

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

## Secondary source — C3 FACIAL/HEAD GATE SELECTED

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: **facial/head/microexpression source**.

Eight no-pose candidate windows were sampled across the video and visually reviewed. Selected canonical gate:

**C3 = 83.6–88.6 s.**

Selection rationale:

- face remains frontal and clearly visible;
- stable framing;
- useful variation in mouth, brows and expression across the window;
- no hand/object crosses the face;
- no strong head rotation that would make the first facial gate unnecessarily ambiguous.

C6 is a useful later stress-case candidate because it includes stronger head tilt/blink variation, but C3 is the clean first validation gate.

Versioned runner:

`tools/video-studio/run_behavior_secondary_pose_gate.ps1`

Defaults:

- C3 start 83.6 s;
- duration 5.0 s;
- 6 fps;
- CPU provider;
- same local WanGP DWPose stack;
- output under `profile_v1\VID_20260819_124008056\selected_gate`;
- produces normalized COCO WholeBody 133 JSONL + visual overlay;
- does not run Wan-Animate-2.

Next gate: inspect the resulting overlay with emphasis on face/head landmark continuity and upper-body coherence. Do **not** launch the full 282.6 s extraction until this passes.

## Multi-video library requirement — LOCKED

After the second source passes and is curated:

1. process `SIENA_BRUTO.mp4` through the same route with source-specific exclusions;
2. preserve source ID and timestamps for every unit;
3. build a unified searchable library;
4. use source-role + group-quality weighting rather than treating all recordings/units as equivalent.

## Renderer — downstream

Installed Wan-Animate-2 remains the selected renderer. Do not invoke it until multi-source behavior inventory and driver synthesis are validated.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_pose_gate.ps1'
```

Then upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\selected_gate\pose_gate_c3_83p6_88p6_overlay.mp4`

Inspect that 5-second result before any secondary full pass.
