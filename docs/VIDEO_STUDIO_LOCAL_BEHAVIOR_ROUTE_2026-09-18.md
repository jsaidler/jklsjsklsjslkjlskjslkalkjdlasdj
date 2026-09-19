# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / CORRECTED C3 VISUAL POSE GATE PASS / FULL PRIMARY POSE EXTRACTION NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`  
Preflight: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: posture, head movement, hands, gesture timing, expressions and delivery rhythm.

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
    -> NEW João driving performance

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later only if needed
```

The driving performance cannot be one fixed clip.

## Behavioral sources

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture source;
- `VID_20260819_124008056.mp4` — facial/microexpression source;
- `SIENA_BRUTO.mp4` — alternate gesture/look source with unusable occluded spans excluded later.

First target:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

## Renderer — downstream and already available

Installed Wan-Animate-2 is the priority renderer. No VACE, Motion Mirror or other large renderer is justified before the behavior profile is complete and inspected.

Wan-Animate-2 remains blocked for now.

## Behavior-profile v1 — implemented

Versioned:

- `tools/video-studio/behavior_profile_schema_v1.json`;
- `tools/video-studio/extract_behavior_profile.py`.

Every motion unit stores source/timing, RGB span, start/end pose, head/hand/body activity, motion energy, speech/pause evidence, available prosody and transition quality.

A pose-less run is `status=incomplete_pose` and never passes the gate.

## Pose representation

The adapter preserves original **COCO WholeBody 133** output from the lower-level WanGP DWPose functions instead of WanGP's later display/OpenPose remapping.

Behavior-profile v1 currently computes activity from:

- head: 0–4;
- body: 5–12;
- left hand: 91–111;
- right hand: 112–132.

`extract_behavior_profile.py` uses `CONF = 0.20`; lower-confidence points are ignored by centroid/activity calculations.

## Local DWPose stack — reuse PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

No DWPose download or Python install is justified.

Runtime inference on a real source frame passed. CUDA ONNX Runtime is not validated because provider loading reported missing CUDA dependencies; CPU is the current validated path.

## Critical orientation correction — PASS

The primary source is coded 3840x2160 but displayed as portrait through stream rotation metadata.

Earlier extraction used coded dimensions to choose 960x540 while FFmpeg autorotated to portrait, deforming João before DWPose.

`extract_dwpose_track.py` now:

- reads stream rotation metadata;
- records coded and display dimensions separately;
- derives analysis geometry from display dimensions;
- lets FFmpeg autorotate, then scales consistently.

Corrected primary analysis geometry is portrait, approximately **540x960** at long side 960.

## Visual upper-body gate — PASS

The first 30–35 s sample was rejected because a held object occluded hands/torso.

A clean gate was selected:

**C3 = 88.7–93.7 s**.

The corrected portrait C3 overlay was uploaded and inspected across all 30 frames.

Profile-relevant result:

- head/face stays aligned;
- shoulders/elbows/wrists/hips remain anatomically coherent;
- both hands track through active gestures, including convergence/clasp/separation;
- no subject switch;
- no gross left/right swap;
- no invalidating upper-body temporal jump.

White clutter near the bottom of the QA overlay comes from low-confidence/off-frame lower-body/foot points and visualization edges. The QA renderer showed points from score 0.05, while profile v1 ignores points below 0.20 and does not use those lower-body groups for current activity descriptors.

Classification: **CORRECTED C3 UPPER-BODY VISUAL POSE GATE PASS**.

## Full primary pose extraction — NEXT

Versioned runner:

`tools/video-studio/run_behavior_pose_full.ps1`

Defaults:

- full 300.352 s primary source;
- 6 fps;
- long side 960;
- portrait/display-rotation aware;
- `CPUExecutionProvider`;
- normalized COCO WholeBody 133 JSONL;
- summary with frame count, geometry, fallback ratio, confidence and throughput.

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`

Review the summary before profile build.

## Persistent profile build — after full-track review

1. run full 6 fps pose extraction;
2. validate full-track summary;
3. pass `pose_coco133.jsonl` to `extract_behavior_profile.py`;
4. require `status=complete`;
5. inspect `manifest.json` + `motion_units.csv`;
6. reject/down-weight object-occluded, low-confidence or otherwise unusable units.

## New speech -> new behavioral driver

After profile validation:

1. divide new local speech into prosodic windows;
2. retrieve units with compatible speech/energy profile;
3. score pose continuity between exit and entry;
4. penalize repetition/near-duplicates;
5. prefer pause/low-motion boundaries;
6. apply only conservative timing adjustment;
7. assemble a new 4–5 s driving performance from multiple real João units;
8. only then invoke installed Wan-Animate-2.

## Prosody v1

Implemented:

- speech/pause;
- RMS dBFS;
- normalized audio energy.

Pitch remains intentionally `null` until a validated local method is needed.

## Stop conditions

- no new large renderer download;
- no DWPose download;
- no blind Python/CUDA install;
- no `incomplete_pose` accepted as a valid profile;
- no Wan-Animate-2 render before complete profile inspection;
- no generic plausible motion accepted as João behavior.

## Immediate action — LOCKED

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_full.ps1'
```

Then review full-track summary before advancing.
