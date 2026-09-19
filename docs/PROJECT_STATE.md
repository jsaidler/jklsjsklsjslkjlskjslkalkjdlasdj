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
- no Wan-Animate-2 until a multi-source behavioral pose driver passes numeric + visual QA.

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
    -> numeric + visual QA
    -> only then installed Wan-Animate-2
```

## Curated source state — PASS

### Primary — `VID_20260911_140124885.mp4`

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

### Secondary — `VID_20260819_124008056.mp4`

Role: face / head / microexpression; body support only.

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
accepted facial geometry 1576/1695 = 0.929794
face/head median quality 0.913145
body-support median quality 0.519182
```

Facial sidecar uses landmarks 23–90, eye-line normalization, roll removal, inter-eye scale and source-relative 3×IQR geometry QA.

### SIENA — `SIENA_BRUTO.mp4`

Role: alternate posture / head / coarse-arm vocabulary.

```text
113.313208 s
680 pose frames @ 6 fps
0 fallback
mean keypoint score 0.6698323212
49 behavior units
12 hard excluded
37 semantically clean
hands disabled
generic whole-upper disabled
```

Locked exclusions:

```text
4.6–10.3 s    u0003-u0004   graphic/still overlay + subject occlusion
18.7–24.7 s   u0009-u0010   held print/photo/book + prop/hand occlusion
43.7–55.7 s   u0021-u0025   lens/camera foreground interaction + occlusion
67.9–74.0 s   u0031-u0033   held purple card + face/body occlusion
```

SIENA `head/posture/coarse_arm` reliability weights are saturated at `1.0 / 1.0 / 1.0` q10/median/q90 and therefore do not rank its 37 clean units meaningfully. Retrieval within SIENA is differentiated by motion/prosody/transition/duration.

## Unified source-preserving library — PASS

Artifact:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

```text
271 total units
primary   118
secondary 116
tertiary   37

face                116 secondary only
head                271
posture             271
coarse_arm          155 primary + tertiary
left/right/both_hands 118 each, primary only
generic_whole_upper 118 primary only
body_support        271
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## First multi-source behavioral pose driver v1 — NUMERIC FAIL / VISUAL DIAGNOSTIC PENDING

Neutral QA synthesis only, no target audio:

```text
duration 4.5 s
fps 24
frames 108
base order primary -> tertiary
planner boundary continuity 0.528554
```

Selected provenance:

```text
window 0
  base  primary:VID_20260911_140124885_u0114
  hands primary:VID_20260911_140124885_u0114
  face  secondary:VID_20260819_124008056_u0026

window 1
  base  tertiary:SIENA_BRUTO_u0037
  hands primary:VID_20260911_140124885_u0075
  face  secondary:VID_20260819_124008056_u0105
```

Artifacts:

```text
...\unified\first_driver\driver_plan.json
...\unified\first_driver\behavioral_driver_coco133.jsonl
...\unified\first_driver\behavioral_driver_pose_preview.mp4
...\unified\first_driver\driver_qa.json
```

### Numeric QA v2 — observed

```text
OOB all finite:               2568/14364 = 0.178780
OOB confidence-qualified:     2185/13490 = 0.161972

confidence-qualified OOB:
  coarse_head        0/540   = 0.000000
  upper_body       153/864   = 0.177083
  lower_body/foot   86/206   = 0.417476
  face               0/7344  = 0.000000
  left_hand         946/2268 = 0.417108
  right_hand       1000/2268 = 0.440917

transition-window q90 / non-transition q90:
  body_head   6.1729x
  face        3.1519x
  left_hand   3.0979x
  right_hand  1.5199x

transition-window max / non-transition q90:
  body_head   6.2012x
  face        3.2443x
  left_hand   3.1861x
  right_hand  1.6191x

hand-root/body-wrist distance:
  left  q10/median/q90/max = 0/0/0/0
  right q10/median/q90/max = 0/0/0/0
```

### Interpretation — LOCKED

The first pose compositor v1 **does not pass numeric QA**.

This is a compositor/retrieval-continuity failure, **not** a failure of the curated source videos or unified library.

Evidence:

1. the `primary -> SIENA` transition window is anomalously faster than the driver's own non-transition movement distribution, especially body/head (`6.17x q90`), face (`3.15x`) and left hand (`3.10x`);
2. the exact boundary pair being `0.0` is an artifact of the compositor beginning its 0.25 s blend by copying the previous pose and is not evidence of good continuity;
3. confidence-qualified hand coordinates are out of frame for about `42–44%` of samples, which is unacceptable for a driver whose target behavior explicitly includes hand gesticulation;
4. face and coarse-head OOB are zero, so the OOB pathology is localized rather than a global coordinate-system error;
5. zero hand-root/wrist distance confirms hand attachment is exact at the root, but does not rescue hand framing or transition dynamics.

Wan-Animate-2 remains blocked.

## Immediate next action

Upload the existing visual diagnostic:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_pose_preview.mp4`

The preview is now diagnostic rather than a possible PASS gate: numeric QA has already failed v1. Inspect it to determine the exact visible failure mode before patching the compositor.

Expected compositor-v2 work after visual diagnosis:

- continuity-aware retrieval for base, face and hand channels rather than independent per-window selection;
- transition smoothing evaluated across the full transition interval, not just the exact boundary pair;
- hand/base candidate selection that accounts for in-frame wrist/hand room;
- preserve source-role architecture and unified library; do **not** change renderer or retrain/re-extract DWPose.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. Do not leave long-running terminal tasks silent.

## Final quality criterion

> this does not merely look like João; this moves and reacts like João.
