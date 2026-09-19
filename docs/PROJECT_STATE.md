# Local Video Studio — Current Project State

Status date: **2026-09-19**

GitHub living documents are the canonical source of truth.

## Policy — LOCKED

- 100% local/self-hosted, zero service cost;
- never upload João's video/voice/identity to third parties;
- no new large renderer while this route is active;
- no new Python/DWPose/CUDA install while the validated CPU route works;
- Wan S2V, H3, Hunyuan and HeyGen remain retired/historical;
- MuseTalk/LatentSync/CosyVoice remain deferred;
- no Wan-Animate-2 until the multi-source behavioral driver passes local QA.

## Objective

New text/audio must yield a new performance that looks, sounds and chiefly **moves/reacts like João**. Generic presenter motion is failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> pose + motion + prosody
    -> per-source behavior-profile/v1
    -> optional facial-behavior-profile/v1
    -> semantic + role-aware curation
    -> joao-motion-library/v1

new speech/audio
    -> prosodic target windows
    -> role-specific retrieval + continuity + diversity
    -> multi-source behavioral pose driver
    -> visual QA
    -> only then installed Wan-Animate-2
```

## Local pose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

Validated provider: `CPUExecutionProvider`. CUDA ORT is not repaired because CPU is functional.

## Source 1 — PRIMARY CURATED PASS

`VID_20260911_140124885.mp4`

Role: torso / hands / gesture / primary posture.

```text
300.352 s
1801 pose frames
0 fallback
123 motion units
118 eligible
5 hard excluded
```

Locked exclusion: **24.1–37.5 s / u0012–u0016** for held object, hand occlusion and prop interaction.

## Source 2 — SECONDARY CURATED PASS

`VID_20260819_124008056.mp4`

Role: face / head / microexpression; body only as support.

```text
282.574 s
1695 pose frames
1 fallback
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands retrieval disabled
generic whole-upper disabled
```

Facial sidecar uses landmarks 23–90, eye-line normalization, roll removal, inter-eye scale and source-relative 3×IQR geometry QA.

```text
accepted facial geometry: 1576/1695 = 0.929794
face/head median quality: 0.913145
body-support median quality: 0.519182
```

## Source 3 — SIENA CURATION POLICY LOCKED

`SIENA_BRUTO.mp4`

Role: alternate posture / head / coarse-arm vocabulary.

Full pose/profile:

```text
113.313208 s
680 pose frames @ 6 fps
0 fallback
mean keypoint score 0.6698323212
49 behavior units
49/49 valid pose snapshots
```

Reviewed hard exclusions from the full inventory sheet:

```text
4.6–10.3 s    u0003-u0004   graphic/still overlay + subject occlusion
18.7–24.7 s   u0009-u0010   held print/photo/book + prop/hand occlusion
43.7–55.7 s   u0021-u0025   lens/camera foreground interaction + occlusion
67.9–74.0 s   u0031-u0033   held purple card + face/body occlusion
```

Expected curated state:

```text
49 total
12 hard excluded
37 semantically clean
```

Retrieval roles:

- `head`: enabled on clean units with continuous head pose quality;
- `posture`: enabled on clean units with continuous body pose quality;
- `coarse_arm`: enabled on clean units with continuous body pose quality;
- hands: disabled;
- generic whole-upper: disabled.

Versioned:

- `behavior_source_annotations_tertiary.json`
- `curate_tertiary_behavior_source.py`
- `run_behavior_tertiary_curation.ps1`

## Unified source-preserving library — IMPLEMENTED

Builder: `tools/video-studio/build_unified_behavior_library.py`  
Runner: `tools/video-studio/run_behavior_finalize_library.ps1`

Schema: `joao-motion-library/v1`.

Each unit preserves source identity, source timestamps, source video and pose-track paths, speech/prosody, transitions, motion/activity descriptors, pose boundary snapshots and role-specific quality/priority.

Locked role/source priorities:

```text
face:       secondary only / tier 0
head:       secondary tier 0 -> primary tier 1 -> SIENA tier 2
posture:    primary tier 0 -> SIENA tier 1 -> secondary support tier 2
coarse_arm: primary tier 0 -> SIENA tier 1
hands:      primary only
generic whole-upper: primary only
```

The library never collapses the three sources into one generic score.

Expected artifact:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

## First multi-source behavioral driver — IMPLEMENTED / QA PENDING

Synthesizer: `tools/video-studio/synthesize_behavioral_pose_driver.py`  
Runner: `tools/video-studio/run_behavior_first_pose_driver.ps1`

The first gate is **pose-domain synthesis**, not RGB clip concatenation and not Wan inference.

For a 4–5 s target it creates two synchronized windows and deliberately exercises multiple sources:

```text
base posture/coarse arm: primary + SIENA, order chosen by retrieval score + boundary continuity
hands:                   primary
face/microexpression:    secondary
```

Retrieval uses source role eligibility, continuous quality, target prosodic energy, speech class, transition quality and duration fit. Source IDs/timestamps remain in the plan and per-frame provenance.

Pose composition v1:

- base units are similarity-aligned through shoulder geometry;
- source changes receive a short boundary blend;
- primary hands are retargeted to the current target wrists using forearm scale/rotation;
- secondary face landmarks are eye-line normalized and retargeted onto the current head geometry;
- secondary relative face/head displacement, roll and bounded scale variation contribute to the composite head/face track;
- output remains COCO WholeBody 133.

Outputs:

```text
first_driver\driver_plan.json
first_driver\behavioral_driver_coco133.jsonl
first_driver\behavioral_driver_pose_preview.mp4
```

If `-Audio` is supplied, the first 4–5 s are analyzed locally for target prosodic energy/speech class. Without `-Audio`, the runner produces only a neutral synthesis-QA target and must not be treated as production retrieval.

Wan-Animate-2 remains blocked until the pose preview passes visual QA.

## Immediate next action

First finalize and validate the library:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_finalize_library.ps1'
```

Paste the complete terminal output. Do **not** run the driver yet if this library build fails.

After library PASS, the next command is:

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver.ps1'
```

or, preferably with a real 4–5 s target speech/audio file:

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver.ps1' -Audio '<PATH_TO_LOCAL_AUDIO>'
```

Upload `behavioral_driver_pose_preview.mp4` for QA before any Wan-Animate-2 call.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. Do not leave long-running terminal tasks silent.

## Final quality criterion

> this does not merely look like João; it moves and reacts like João.
