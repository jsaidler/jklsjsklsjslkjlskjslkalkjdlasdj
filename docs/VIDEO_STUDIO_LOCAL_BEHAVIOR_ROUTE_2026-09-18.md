# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / THREE SOURCES REVIEWED / UNIFIED LIBRARY BUILD NEXT / FIRST MULTI-SOURCE POSE DRIVER IMPLEMENTED**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: posture, head movement, hands, gesture timing, expressions and delivery rhythm. Generic plausible motion is insufficient.

## Architecture — LOCKED

```text
real João behavior sources
    -> pose + motion + prosody
    -> source-specific behavior profiles
    -> semantic/quality curation
    -> joao-motion-library/v1

new local speech/audio
    -> target prosody windows
    -> role-specific retrieval
    -> composite COCO-133 behavioral pose driver
    -> visual QA
    -> Wan-Animate-2 only after PASS
```

## Source roles — LOCKED

### Primary — `VID_20260911_140124885.mp4`

Canonical source for torso, hands, gesture and primary posture.

```text
123 units
118 eligible
5 excluded
```

Excluded: `24.1–37.5 s / u0012-u0016` for prop-specific interaction and hand occlusion.

### Secondary — `VID_20260819_124008056.mp4`

Canonical source for face/head/microexpression; body support only.

```text
119 units
116 face eligible
116 head eligible
116 body-support eligible
hands disabled
generic whole-upper disabled
```

Facial representation is additive `facial-behavior-profile/v1`, using COCO WholeBody face points 23–90 normalized to the eye line.

### Tertiary — `SIENA_BRUTO.mp4`

Alternate posture/head/coarse-arm source.

```text
49 units
12 reviewed hard exclusions
37 semantically clean expected after curator run
hands disabled
generic whole-upper disabled
```

Reviewed exclusions:

```text
4.6–10.3 s    u0003-u0004   graphic/still overlay
18.7–24.7 s   u0009-u0010   held print/photo/book
43.7–55.7 s   u0021-u0025   lens/camera foreground interaction
67.9–74.0 s   u0031-u0033   held card / face-body occlusion
```

## Unified library — IMPLEMENTED

Schema: `joao-motion-library/v1`.

Builder: `tools/video-studio/build_unified_behavior_library.py`  
Runner: `tools/video-studio/run_behavior_finalize_library.ps1`

Source priority by role:

```text
face:       secondary only
head:       secondary -> primary -> SIENA
posture:    primary -> SIENA -> secondary support
coarse_arm: primary -> SIENA
hands:      primary only
generic whole-upper: primary only
```

Library entries preserve source provenance, timestamps, source video/pose paths, speech/prosody, transition quality, activity descriptors, pose boundaries and role-specific weights.

## First behavioral-driver synthesis — IMPLEMENTED

Synthesizer: `tools/video-studio/synthesize_behavioral_pose_driver.py`  
Runner: `tools/video-studio/run_behavior_first_pose_driver.ps1`

The first synthesis gate is 4–5 seconds in **pose space**, not RGB clip concatenation.

Composition:

```text
posture/coarse arm <- primary + SIENA
hands              <- primary
face/microexpression <- secondary
```

Key operations:

- role-aware retrieval with quality, target energy/speech class, transition and duration compatibility;
- explicit primary/SIENA body-source diversity in the first gate;
- shoulder-based similarity alignment across body-source changes;
- short boundary blending;
- primary hand retargeting through wrist/forearm geometry;
- secondary face/head retargeting through eye-line normalized geometry plus relative displacement/roll/scale;
- per-frame provenance;
- output COCO WholeBody 133 track plus an MP4 pose preview.

Target audio is optional for the neutral synthesis-QA spike and required for meaningful production retrieval.

## Immediate sequence

1. Build/validate the unified library:

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_finalize_library.ps1'
```

2. After PASS, synthesize the first pose driver:

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver.ps1'
```

Prefer real local target speech:

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver.ps1' -Audio '<LOCAL_AUDIO_PATH>'
```

3. Upload `behavioral_driver_pose_preview.mp4` and visually validate continuity, anatomy, hands and face/head behavior.

4. Only after that gate passes, inspect/bridge the installed Wan-Animate-2 input route and perform the first renderer test.

## Stop conditions

- no new renderer;
- no cloud/SaaS identity handling;
- no source role flattened into a universal score;
- no semantically excluded unit returned by retrieval;
- no SIENA/secondary hands promoted without evidence;
- no Wan-Animate-2 before composite pose-driver QA.

Quality criterion:

> this does not merely look like João; it moves and reacts like João.
