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
- no Wan-Animate-2 until the first multi-source behavioral pose driver passes local numeric + visual QA.

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

## Source 1 — PRIMARY CURATED PASS

`VID_20260911_140124885.mp4` — torso / hands / gesture / primary posture.

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

`VID_20260819_124008056.mp4` — face / head / microexpression; body support only.

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

## Source 3 — SIENA CURATED PASS

`SIENA_BRUTO.mp4` — alternate posture / head / coarse-arm vocabulary.

```text
113.313208 s
680 pose frames @ 6 fps
0 fallback
mean keypoint score 0.6698323212
49 behavior units
12 hard excluded
37 semantically clean
```

Locked exclusions from the full inventory review:

```text
4.6–10.3 s    u0003-u0004   graphic/still overlay + subject occlusion
18.7–24.7 s   u0009-u0010   held print/photo/book + prop/hand occlusion
43.7–55.7 s   u0021-u0025   lens/camera foreground interaction + occlusion
67.9–74.0 s   u0031-u0033   held purple card + face/body occlusion
```

Retrieval roles on clean units:

- `head`: enabled;
- `posture`: enabled;
- `coarse_arm`: enabled;
- hands: disabled;
- generic whole-upper: disabled.

Observed SIENA role-weight quantiles are fully saturated:

```text
head q10/median/q90 = 1.0 / 1.0 / 1.0
posture q10/median/q90 = 1.0 / 1.0 / 1.0
coarse_arm q10/median/q90 = 1.0 / 1.0 / 1.0
```

Interpretation: current SIENA pose-reliability weight is non-discriminative across the 37 clean units. This does not invalidate the source, but retrieval ranking within SIENA currently depends on motion/prosody/transition/duration rather than pose-quality differentiation. Do not claim the SIENA quality weight meaningfully ranks clean units.

## Unified source-preserving library — PASS

Schema: `joao-motion-library/v1`.

Artifact:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

Observed build:

```text
271 total units
primary:   118
secondary: 116
tertiary:   37
```

Observed role candidate counts:

```text
face:                116  secondary only
head:                271  primary 118 + secondary 116 + tertiary 37
posture:             271  primary 118 + secondary 116 + tertiary 37
coarse_arm:          155  primary 118 + tertiary 37
left_hand:           118  primary only
right_hand:          118  primary only
both_hands:          118  primary only
generic_whole_upper: 118  primary only
body_support:        271  primary 118 + secondary 116 + tertiary 37
```

Locked role/source priorities remain:

```text
face:       secondary only / tier 0
head:       secondary tier 0 -> primary tier 1 -> SIENA tier 2
posture:    primary tier 0 -> SIENA tier 1 -> secondary support tier 2
coarse_arm: primary tier 0 -> SIENA tier 1
hands:      primary only
generic whole-upper: primary only
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## First multi-source behavioral pose driver — GENERATED / QA PENDING

Synthesizer: `tools/video-studio/synthesize_behavioral_pose_driver.py`  
Runner: `tools/video-studio/run_behavior_first_pose_driver.ps1`

Observed neutral QA synthesis:

```text
duration: 4.5 s
fps: 24
frames: 108
target audio: none / neutral QA only
base source order: primary -> tertiary
planner boundary continuity score: 0.528554
```

Selected windows:

```text
window 0
  base:  primary:VID_20260911_140124885_u0114
  hands: primary:VID_20260911_140124885_u0114
  face:  secondary:VID_20260819_124008056_u0026

window 1
  base:  tertiary:SIENA_BRUTO_u0037
  hands: primary:VID_20260911_140124885_u0075
  face:  secondary:VID_20260819_124008056_u0105
```

Artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\driver_plan.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_pose_preview.mp4
```

`0.528554` has no canonical pass/fail threshold and must not be interpreted alone. The first driver remains **QA PENDING**.

## Driver numeric QA — IMPLEMENTED / NEXT

Inspector: `tools/video-studio/inspect_behavioral_pose_driver.py`  
Runner: `tools/video-studio/run_behavior_first_pose_driver_qa.ps1`

The inspector performs no inference and applies no invented automatic threshold. It reports:

- per-frame coordinate out-of-bounds ratio;
- frame-to-frame normalized jumps for body/head, face, left hand and right hand;
- the source-boundary jump compared with the driver's own non-boundary q90;
- upper-arm and forearm length distributions normalized by shoulder width;
- inter-eye / shoulder ratio;
- retargeted hand-root / body-wrist attachment distances.

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\driver_qa.json`

Visual preview remains authoritative together with numeric diagnostics.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_qa.ps1'
```

Then paste the complete terminal output and upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_pose_preview.mp4`

Do not invoke Wan-Animate-2 before numeric + visual QA are reviewed.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. Do not leave long-running terminal tasks silent.

## Final quality criterion

> this does not merely look like João; it moves and reacts like João.
