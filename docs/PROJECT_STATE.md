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

face                   116 secondary only
head                   271
posture                271
coarse_arm             155 primary + tertiary
left/right/both_hands  118 each, primary only
generic_whole_upper    118 primary only
body_support           271
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## First pose driver v1 — FAIL

Neutral 4.5 s / 24 fps / 108 frames.

Numeric v2 QA of the v1 compositor established:

```text
confidence-qualified OOB:
  coarse_head  0.0000
  face         0.0000
  upper_body   0.1771
  left_hand    0.4171
  right_hand   0.4409

transition q90 / normal q90:
  body_head    6.1729x
  face         3.1519x
  left_hand    3.0979x
  right_hand   1.5199x
```

Visual preview confirmed the failure: around the source change the body reconfigured too quickly and hands were repeatedly lost below frame. Root hand-to-wrist attachment itself remained exact.

Classification: **COMPOSITOR v1 FAIL / library remains valid**.

## Pose driver v2 — MAJOR IMPROVEMENT / STILL NOT PASS

Observed neutral synthesis:

```text
duration 4.5 s
24 fps
108 frames
base source order primary -> tertiary
overlap 1.875–2.625 s = 0.750 s
base continuity 0.615637
face pair continuity 0.937309
hand pair continuity 0.783131
predicted hand in-frame ratio 0.707143
```

Selected windows:

```text
window 0
  base  primary:VID_20260911_140124885_u0027
  hands primary:VID_20260911_140124885_u0107
  face  secondary:VID_20260819_124008056_u0026

window 1
  base  tertiary:SIENA_BRUTO_u0035
  hands primary:VID_20260911_140124885_u0108
  face  secondary:VID_20260819_124008056_u0009
```

Numeric QA:

```text
OOB confidence-qualified:
  coarse_head 0.000000
  upper_body  0.063657
  lower body  0.034221
  face        0.000000
  left hand   0.218695
  right hand  0.277337

transition q90 / normal q90:
  body_head   0.7920x
  face        2.4043x
  left_hand   0.2085x
  right_hand  0.8727x
```

Visual QA of `first_driver_v2\behavioral_driver_pose_preview.mp4` confirms:

- the body transition is now smooth enough to eliminate the v1 “skeleton swap” failure;
- face/coarse head remain in frame;
- hands still scrape/leave the lower frame too often in the second segment;
- face motion still accelerates across the overlap, matching the 2.40× transition ratio.

Therefore **v2 is not a full PASS**. Wan-Animate-2 remains blocked.

## Camera framing is not behavioral identity — LOCKED

Absolute source-camera translation/scale must not be treated as João behavior. Relative pose, gesture, head motion, hand shape/motion and facial deformation are behavioral; source framing is acquisition geometry.

A behavioral driver may therefore apply one global similarity transform to the whole synthesized performance to normalize camera framing, provided it preserves all relative motion/geometry and does not introduce dynamic camera motion.

## Pose driver v3 — IMPLEMENTED / NEXT QA

Versioned:

- `tools/video-studio/synthesize_behavioral_pose_driver_v3.py`
- `tools/video-studio/run_behavior_first_pose_driver_v3_and_qa.ps1`

v3 retains the same three-source library and overlap compositor but changes retrieval and framing:

1. **base + hands are selected jointly** rather than sequentially;
2. retargeted hand in-frame ratio is a retrieval constraint, attempted at floors `0.90 -> 0.86 -> 0.82 -> 0.78 -> 0.74`;
3. multiple high-quality primary/SIENA base pairs are considered so the base can change if a visually good body unit cannot support in-frame hands;
4. hand-pair scoring now includes retrieval, predicted framing, hand-shape continuity and forward source-time adjacency;
5. face-pair selection favors forward/adjacent secondary units and scores facial shape + velocity continuity, not static shape alone;
6. after composition, one **constant** robust similarity transform normalizes the full 4.5 s driver into the target canvas; it never changes frame-to-frame and therefore adds no synthetic camera motion;
7. the canonical transform has a minimum scale of `0.82`, so framing problems cannot be hidden by shrinking the figure arbitrarily.

Output directory:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3`

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_v3_and_qa.ps1'
```

This performs v3 synthesis and overlap-aware numeric QA only. No DWPose and no Wan.

Then upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3\behavioral_driver_pose_preview.mp4`

PASS intent for this gate is evidence-based rather than a newly invented magic number: hand OOB must fall materially below v2, face transition acceleration must fall materially below `2.40x`, body transition must remain at least as stable as v2, and the preview must read as one continuous performance rather than stitched source motion.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. Do not leave long-running terminal tasks silent.

## Final quality criterion

> this does not merely look like João; this moves and reacts like João.
