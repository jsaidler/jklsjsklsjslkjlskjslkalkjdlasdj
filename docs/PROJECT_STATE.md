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
- `VID_20260819_124008056.mp4` — 282.574 s — facial/head/microexpression source;
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

## Secondary source — C3 FACIAL/HEAD VISUAL GATE PASS

Source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4`

Role: **facial/head/microexpression source**.

Canonical clean gate:

**C3 = 83.6–88.6 s.**

The uploaded 30-frame / 6 fps overlay was inspected frame-by-frame.

Observed facial result:

- facial landmarks 23–90 remain attached to brows, eyes, nose and mouth;
- mouth-shape changes are followed coherently;
- brow/eye landmarks remain stable through expression changes;
- head landmarks move smoothly with the face;
- no gross facial topology jump;
- no subject switch;
- shoulders/upper torso remain coherent enough to anchor the facial sequence.

The large white whole-body/hand skeleton lines crossing the face are QA-overlay clutter from partially off-frame body/hand points. They do **not** invalidate the facial landmarks themselves.

### Secondary gate geometry — CONFIRMED CORRECT

The second source has the **same encoded-landscape + rotation-metadata condition** as the primary source, but the orientation fix is active and correct.

Observed gate summary:

```text
source_duration_s: 282.574
coded_width: 1920
coded_height: 1080
display_width: 1080
display_height: 1920
rotation_degrees: 90
analysis_width: 540
analysis_height: 960
frames: 30
sample_fps: 6.0
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.5554170230711649
onnx_provider: CPUExecutionProvider
```

Interpretation:

- no portrait-to-landscape squashing is present;
- the old 960x540 deformation bug is not active;
- the lower global mean keypoint score versus the primary source does not invalidate this source because the intended role is face/head, the visual facial gate passed, and partially off-frame hands/body depress the whole-body average;
- geometry is safe for a full secondary pose pass.

Classification: **SECONDARY C3 FACIAL/HEAD VISUAL GATE PASS / ORIENTATION CONFIRMED**.

## Important profile-design finding — FACIAL DESCRIPTORS REQUIRED

Current behavior-profile v1 computes `head_motion` only from keypoints **0–4**. That is adequate for coarse head translation/orientation but does not capture the principal value of the secondary source: microexpression.

The secondary gate proves that COCO WholeBody facial landmarks **23–90** are usable. Therefore:

- full secondary pose extraction is authorized now, because the JSONL preserves all 133 keypoints;
- do **not** build the secondary behavior profile with the old head-only descriptor path;
- before secondary profile construction, extend the behavior representation with facial descriptors derived from 23–90;
- facial descriptors should separate expression deformation from gross head translation/scale as far as practical, rather than merely averaging all face points as another head centroid.

This extension should be additive/backward-compatible so the already-curated primary source does not become invalid. The primary full pose track can be re-derived into facial features later without rerunning DWPose.

## Secondary full pose extraction — NEXT

Versioned runner:

`tools/video-studio/run_behavior_pose_full_secondary.ps1`

Defaults:

- source: `VID_20260819_124008056.mp4`;
- full duration;
- 6 fps;
- 960 px long side;
- CPU provider;
- normalized COCO WholeBody 133 JSONL;
- all facial landmarks 23–90 retained;
- no Wan-Animate-2.

Output:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl.summary.json
```

Review the full-track summary before implementing/building the secondary facial-aware behavior profile.

## Multi-video library requirement — LOCKED

After the second source passes full pose + facial-aware profile + curation:

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
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_full_secondary.ps1'
```

Then paste the full secondary pose summary. Do not build the secondary behavior profile yet; facial descriptors 23–90 are the next representation change after the full pose track is validated.
