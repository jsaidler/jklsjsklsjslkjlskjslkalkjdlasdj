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
    -> optional additive facial sidecar per source
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

## Secondary source — FACIAL/HEAD GATE PASS

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

Whole-body/hand lines crossing the face are QA-overlay clutter from off-frame groups, not facial-landmark failure.

### Secondary gate geometry — PASS

```text
coded: 1920x1080
display: 1080x1920
rotation_degrees: 90
analysis: 540x960
frames: 30
fallback: 0/30
mean_keypoint_score: 0.5554170230711649
CPUExecutionProvider
```

The old portrait-squashing bug is not present.

## Secondary full pose extraction — PASS

Completed full-track result:

```text
source_duration_s: 282.574
coded_width: 1920
coded_height: 1080
display_width: 1080
display_height: 1920
rotation_degrees: 90
sample_fps: 6.0
analysis_width: 540
analysis_height: 960
frames: 1695
last_timestamp_s: 282.333333
detector_fallback_frames: 1
detector_fallback_ratio: 0.0005899705014749262
mean_keypoint_score: 0.5453589802956859
onnx_provider: CPUExecutionProvider
```

Interpretation:

- geometry is correct;
- all 133 points, including facial 23–90, are retained;
- 1 fallback in 1695 frames (~0.059%) does not invalidate the source;
- the lower whole-body mean score is expected for this tighter face/head framing and is not used alone as a rejection criterion because the facial visual gate passed.

Track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl`

Classification: **SECONDARY FULL POSE TRACK PASS**.

## Facial representation — ADDITIVE SIDECAR LOCKED

The existing `behavior-profile/v1` remains unchanged and valid. It continues to represent segmentation, body/hands, coarse head motion, motion energy and prosody.

Facial/microexpression information is added as a separate, source-aligned sidecar instead of mutating the already validated v1 schema:

```text
behavior-profile/v1
    + facial-behavior-profile/v1 sidecar
```

Rationale:

- backward-compatible with the curated primary source;
- avoids invalidating existing motion-unit manifests;
- allows facial descriptors to be recomputed from any existing 133-point pose track without rerunning DWPose;
- keeps face-specific retrieval quality separate from body/hand quality.

Canonical face landmarks: **23–90** (68-point face layout).

Normalization before expression measurement:

1. center on eye-line midpoint;
2. remove in-plane roll using the eye line;
3. divide by inter-eye-center distance.

This removes image translation, in-plane rotation and scale before measuring internal facial deformation. It does **not** claim to remove perspective effects from yaw/pitch.

Planned descriptor groups:

- overall internal facial deformation (excluding jaw);
- brows;
- eyes;
- mouth;
- normalized mouth opening;
- normalized mouth width;
- normalized eye opening;
- normalized brow-to-eye distance;
- face-point presence and mean landmark confidence.

Versioned tooling now present:

- `tools/video-studio/facial_descriptors.py`;
- `tools/video-studio/inspect_facial_track.py`;
- `tools/video-studio/run_behavior_secondary_facial_probe.ps1`.

The probe is read-only with respect to models: it reads the already generated full pose JSONL and compares facial descriptors on the complete source and the visually validated C3 interval. It does not run DWPose or Wan-Animate-2.

## Immediate next action — FACIAL DESCRIPTOR PROBE

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_secondary_facial_probe.ps1'
```

Paste the complete terminal output. Validate descriptor coverage and C3/full-track ranges before generating the secondary behavior profile and facial sidecar.

## Multi-video library requirement — LOCKED

After the second source passes facial-aware profile + curation:

1. process `SIENA_BRUTO.mp4` through the same route with source-specific exclusions;
2. preserve source ID and timestamps for every unit;
3. build a unified searchable library;
4. use source-role + body/hand/face quality weighting rather than treating all recordings/units as equivalent.

## Renderer — downstream

Installed Wan-Animate-2 remains the selected renderer. Do not invoke it until multi-source behavior inventory and driver synthesis are validated.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.
