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

## Orientation/preprocessing — FIXED

Primary source is coded 3840x2160 but displayed portrait through 90° rotation metadata.

Validated corrected geometry:

- display: 2160x3840;
- DWPose analysis: 540x960;
- behavior-profile motion analysis: 72x128.

## Primary pose/profile pipeline — PASS

Corrected visual C3 gate (88.7–93.7 s): PASS.

Full primary pose extraction:

```text
frames: 1801
sample_fps: 6.0
detector fallback: 0/1801
mean keypoint score: 0.7549247491487903
provider: CPUExecutionProvider
```

Primary behavior profile:

```text
status: complete
units: 123
coverage: 0.0 -> 300.352 s
pose snapshots valid: 123/123
activity units: head=123, body=123, left_hand=123, right_hand=123, combined_hands=123
speech classes: mixed=89, pause=4, speech=30
unit duration min/median/max: 0.800/2.500/3.800 s
```

Classification: **PRIMARY PIPELINE STRUCTURAL PASS**.

## Primary motion-unit inventory review — PASS WITH CURATION REQUIRED

Uploaded inventory analysis + review sheet were inspected on 2026-09-19.

Source-relative diagnostics:

```text
units: 123
confidence threshold: 0.20
upper-pose coverage q10: 0.9352380952
upper-pose coverage median: 1.0
upper-pose coverage q90: 1.0
hand speed q10/median/q90: 0.049868 / 0.161759 / 0.3921014
body speed q10/median/q90: 0.0209724 / 0.05028 / 0.1128552
```

Interpretation:

- overall upper-body pose coverage is strong; median coverage is 1.0;
- 13/123 units fall below the source-relative q10 coverage threshold;
- **`low_relative_pose_coverage` is not an automatic rejection condition**: for example `u0038` (90.5–93.8 s) carries that tag yet belongs to the already visually validated C3 gesture interval;
- low relative coverage frequently reflects a hand leaving/approaching the frame during a legitimate gesture, so reliability must remain continuous and group-specific rather than binary.

### Manual hard exclusion — LOCKED

The visual sheet plus the earlier failed 30–35 s gate confirm a nonportable prop/object interaction spanning:

**24.1–37.5 s = units `u0012` through `u0016`.**

This interval includes reaching for, holding and presenting physical objects, causing hand occlusion and object-specific movement. These five units are not eligible as generic João behavior.

Canonical annotation file:

`tools/video-studio/behavior_source_annotations_primary.json`

### Continuous quality weighting — LOCKED

Do not invent a binary confidence cutoff beyond the established per-keypoint `CONF=0.20`.

For eligible units, retrieval quality is represented continuously per group using confident-keypoint ratio × frame presence for:

- head;
- body;
- left hand;
- right hand;
- both hands (minimum of left/right);
- whole upper body (minimum across groups).

Thus units such as early 7.1–20 s spans can remain usable for head/body behavior even when one hand has weaker visibility.

Versioned curation tooling:

- `tools/video-studio/behavior_source_annotations_primary.json`;
- `tools/video-studio/curate_behavior_inventory.py`;
- `tools/video-studio/run_behavior_primary_curation.ps1`.

Expected result for the current annotations:

- 123 total units;
- 5 hard-excluded object/prop units;
- 118 eligible units with continuous group-quality weights.

## Multi-video library requirement — LOCKED

After primary curation is materialized locally:

1. process `VID_20260819_124008056.mp4` through the same pose/profile/quality route, emphasizing facial/head behavior;
2. process `SIENA_BRUTO.mp4` through the same route with source-specific object/occlusion annotations;
3. preserve source ID and timestamps for every unit;
4. build a unified searchable library;
5. use source-role + group-quality weighting rather than treating all recordings/units as equivalent.

## Renderer — downstream

Installed Wan-Animate-2 remains the selected renderer. Do not invoke it until multi-source behavior inventory and driver synthesis are validated.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_primary_curation.ps1'
```

Then confirm the curation summary. After that, move to a short visual pose gate for `VID_20260819_124008056.mp4` before its full-source extraction.
