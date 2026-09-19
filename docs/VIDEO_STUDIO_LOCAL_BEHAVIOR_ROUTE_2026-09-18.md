# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / BEHAVIOR PROFILE IMPLEMENTATION / LOCAL DWPOSE REUSE FOUND**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`  
Preflight/follow-up: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: characteristic posture, head movement, hands, gesture timing, expressions and delivery rhythm.

Generic plausible motion is not sufficient.

## Selected architecture — LOCKED

```text
João behavioral videos
    -> local pose + prosody analysis
    -> persistent motion-unit library from João's own footage

new local speech/audio
    -> prosody windows
    -> retrieve/sequence compatible João motion units
    -> pose continuity + diversity scoring
    -> assemble a NEW João driving performance

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later only if needed
```

The driving performance cannot be one fixed source clip.

Semantic transcript matching may be added later. The first implementation gate uses pose continuity + prosody + diversity.

## Behavioral sources

- `VID_20260911_140124885.mp4` — primary upper-body/hands/posture/gesture source;
- `VID_20260819_124008056.mp4` — facial/microexpression source;
- `SIENA_BRUTO.mp4` — alternate gesture/look source; exclude problematic object/occlusion spans when needed.

First target:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

## Renderer — already solved for this gate

Installed Wan-Animate-2 is the priority renderer and passed local reuse preflight. No VACE, Motion Mirror or other large renderer should be downloaded before the behavior profile is built and validated.

Wan-Animate-2 remains downstream. It must not be run yet.

## Behavior-profile schema and base extractor — IMPLEMENTED

Versioned files:

- `tools/video-studio/behavior_profile_schema_v1.json`;
- `tools/video-studio/extract_behavior_profile.py`.

`behavior-profile/v1` stores for every unit:

- source file;
- start/end/duration;
- original RGB span;
- start/end pose;
- head movement;
- left/right/combined hand activity;
- body activity;
- motion energy;
- speech/pause evidence;
- available prosody;
- transition/boundary quality.

Base extractor behavior:

- FFmpeg/ffprobe media analysis;
- low-resolution grayscale frame-difference motion energy;
- RMS/dBFS + normalized audio energy + speech/pause evidence;
- segmentation prioritizing pauses + low motion;
- target motion units around 2.2 s within a bounded short-unit range;
- inspectable `manifest.json` + `motion_units.csv`.

A run without pose is `status=incomplete_pose` and is diagnostic only. It never passes the behavior-profile gate.

## Local tooling discovery — COMPLETED 2026-09-19

### System Python launcher

Strict result:

```text
py -3.11: NOT RESOLVED
```

The old `Python 3.11 PASS / C:\Python314\python.exe / 3.14.3` line is invalid and superseded.

No new Python installation is justified by this result because the project already has an isolated WanGP environment from earlier validated work:

`Z:\AI\WanGP\env_uv\Scripts\python.exe`

Historical project evidence records that environment as Python 3.11.14 with Torch 2.10.0+cu130 and CUDA 13.0. Existing WanGP runners use it directly.

### DWPose payload — REUSE FOUND

The targeted no-download scan found:

- code: `Z:\AI\WanGP\preprocessing\dwpose`;
- person detector: `Z:\AI\WanGP\ckpts\pose\yolox_l.onnx` — ~206.7 MB;
- whole-body model: `Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx` — ~128.2 MB.

Classification:

**LOCAL POSE PAYLOAD REUSE: PASS.**

Do not download DWPose-L or another pose stack.

## Pose representation

The project adapter uses the lower-level WanGP detector + pose functions and preserves the original **COCO WholeBody 133** layout rather than WanGP's later display/OpenPose remapping.

Standard index groups used by `extract_behavior_profile.py`:

- body: 0–16;
- feet: 17–22;
- face: 23–90;
- left hand: 91–111;
- right hand: 112–132.

Coordinates written to the project pose track are normalized to `[0,1]` and stored as JSONL.

## New pose adapter tooling — IMPLEMENTED

### `probe_wangp_dwpose_runtime.ps1`

One-frame, no-download runtime gate. It verifies:

- existing WanGP `env_uv` Python;
- OpenCV/NumPy/ONNX Runtime imports;
- ONNX execution providers;
- YOLOX + DWPose session creation;
- real person detection;
- real 133-keypoint inference on a frame from the primary source.

It does not install or mutate models.

### `extract_dwpose_track.py`

Local video -> normalized COCO WholeBody 133 JSONL adapter.

Defaults:

- source: primary João video;
- sample rate: 6 fps for the eventual full pass;
- analysis long side: 960 px;
- provider: auto, preferring CUDA and falling back to CPU;
- detector continuity: largest initial person, then center/area continuity;
- detector miss: full-frame pose fallback is recorded explicitly;
- summary records fallback ratio, mean keypoint confidence, provider and wall throughput.

### `run_behavior_pose_smoke.ps1`

Short pose-only validation before spending time on the full 300 s source.

Default smoke:

- start ~30 s;
- duration 5 s;
- 4 fps;
- provider auto.

It does not run Wan-Animate-2.

## Persistent profile build

For the primary source:

1. validate existing WanGP DWPose runtime on one frame;
2. run a short pose smoke and inspect provider/detection/fallback/confidence;
3. generate a full normalized 6 fps pose track;
4. combine that pose track with local motion/prosody analysis in `extract_behavior_profile.py`;
5. require `status=complete`;
6. inspect the motion-unit inventory before any diffusion render.

## New speech -> new behavioral driver

After the profile passes:

1. divide new local speech into prosodic windows;
2. retrieve units with compatible speech/energy profile;
3. score pose continuity between exit and entry poses;
4. penalize repeated units and near-duplicate sequences;
5. prefer boundaries with pause/low-motion transition quality;
6. apply only conservative time adjustment;
7. assemble a new 4–5 s driving performance from multiple real João units;
8. only then test the installed Wan-Animate-2 renderer.

## Prosody v1

Reliable descriptors currently implemented:

- speech/pause;
- RMS dBFS;
- normalized audio energy.

Pitch remains intentionally `null` until a local validated method is needed. This does not block the first behavior-profile gate.

## Deferred stages

MuseTalk/LatentSync and final local voice-clone/TTS remain deferred until body/head behavior passes.

## Stop conditions

- no another large renderer download;
- no DWPose download while the local WanGP payload exists;
- no blind Python reinstall;
- no Wan S2V prompt acting as substitute for behavior;
- no `incomplete_pose` accepted as a valid profile;
- no Wan-Animate-2 render before the complete profile inventory is inspected;
- no generic plausible motion accepted as João behavior.

## Immediate action — LOCKED

1. run `tools/video-studio/probe_wangp_dwpose_runtime.ps1`;
2. if PASS, run `tools/video-studio/run_behavior_pose_smoke.ps1`;
3. inspect smoke evidence;
4. generate the full 6 fps pose track;
5. build the complete profile for `VID_20260911_140124885.mp4`;
6. inspect `manifest.json` and `motion_units.csv`;
7. synthesize a new 4–5 s multi-unit behavior driver;
8. only then run installed Wan-Animate-2.
