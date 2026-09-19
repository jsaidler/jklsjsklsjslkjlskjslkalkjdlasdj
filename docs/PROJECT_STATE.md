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

Interpretation: current SIENA pose-reliability weight is non-discriminative across the 37 clean units. This does not invalidate the source, but retrieval ranking within SIENA currently depends on motion/prosody/transition/duration rather than pose-quality differentiation.

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

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## First multi-source behavioral pose driver — GENERATED / QA PENDING

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

`0.528554` has no canonical pass/fail threshold and must not be interpreted alone.

## First driver numeric QA v1 — COMPLETE / INSUFFICIENT FOR VERDICT

Observed:

```text
frames: 108
all-finite coordinate OOB: 2568/14364 = 0.178780
body/head nonboundary jump q90: 0.009728
face nonboundary jump q90: 0.013127
left-hand nonboundary jump q90: 0.032354
right-hand nonboundary jump q90: 0.060746
exact boundary jumps: 0.0 for all groups
hand-root/body-wrist distance: 0.0 left and right
```

Interpretation is intentionally **not** PASS/FAIL yet:

1. the `17.878%` OOB figure counted every finite coordinate, including low-confidence off-frame landmarks; it must be separated into confidence-qualified semantic groups before judging severity;
2. the exact source-boundary jump is zero by construction because the current compositor begins the 0.25 s blend by copying the previous pose; a single boundary pair is therefore not a valid continuity measurement;
3. continuity must be evaluated across the entire 0.25 s transition window and compared with the driver's non-transition movement distribution;
4. zero hand-root/wrist distance confirms the hand retargeter attaches the hand root exactly to the current wrist, but visual hand geometry still requires preview inspection.

## Driver numeric QA v2 — IMPLEMENTED / NEXT

`tools/video-studio/inspect_behavioral_pose_driver.py` now reports schema `behavioral-pose-driver-qa/v2` and adds:

- all-finite OOB separately from confidence-qualified OOB;
- confidence-qualified OOB by `coarse_head`, `upper_body`, `lower_body_foot`, `face`, `left_hand`, `right_hand`;
- exact-boundary jump retained only as a diagnostic explaining the compositor behavior;
- full **0.25 s transition-window** jump q90/max per body/head, face and hands;
- transition q90/max divided by the driver's own non-transition q90.

No automatic threshold is invented. Visual preview remains authoritative together with these source-relative diagnostics.

## Immediate next action

Run the revised QA only; the driver does not need to be regenerated:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_qa.ps1'
```

Then paste the complete v2 terminal output and upload:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_pose_preview.mp4`

Do not invoke Wan-Animate-2 before v2 numeric + visual QA are reviewed.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. Do not leave long-running terminal tasks silent.

## Final quality criterion

> this does not merely look like João; this moves and reacts like João.
