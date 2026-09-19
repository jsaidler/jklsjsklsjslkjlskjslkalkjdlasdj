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

## Curated sources — PASS

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
```

### SIENA — `SIENA_BRUTO.mp4`
Role: alternate posture / head / coarse-arm vocabulary.

```text
113.313208 s
680 pose frames @ 6 fps
0 fallback
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

SIENA `head/posture/coarse_arm` reliability weights are saturated at `1.0 / 1.0 / 1.0` q10/median/q90 and therefore do not rank its clean units meaningfully. Retrieval within SIENA is differentiated by motion/prosody/transition/duration.

## Unified source-preserving library — PASS

Artifact:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

```text
271 total units
primary   118
secondary 116
tertiary   37

face                  116 secondary only
head                  271
posture               271
coarse_arm            155 primary + tertiary
left/right/both_hands 118 each, primary only
generic_whole_upper   118 primary only
body_support          271
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## First multi-source behavioral pose driver v1 — FAIL

Neutral QA synthesis only, no target audio:

```text
duration 4.5 s
fps 24
frames 108
base order primary -> tertiary
planner boundary continuity 0.528554
```

Numeric QA v2:

```text
confidence-qualified OOB total = 0.161972
coarse_head OOB = 0.000000
face OOB        = 0.000000
upper_body OOB  = 0.177083
left_hand OOB   = 0.417108
right_hand OOB  = 0.440917

transition q90 / non-transition q90:
body_head  6.1729x
face       3.1519x
left_hand  3.0979x
right_hand 1.5199x
```

Visual inspection of `behavioral_driver_pose_preview.mp4` confirms the numeric failure:

- around the `primary -> SIENA` source change the skeleton drops/reconfigures too quickly instead of flowing into a natural posture change;
- the visible failure is concentrated roughly across `2.29–2.50 s` under the v1 0.25 s transition;
- after the transition, arms/hands fall through the lower frame boundary and much of the manual gesture disappears;
- face/head remain comparatively stable, consistent with `0%` confidence-qualified OOB for those groups.

Interpretation: **v1 fails because of compositor/retrieval continuity + framing, not because the curated source library failed.** Wan-Animate-2 remains blocked.

## Behavioral pose compositor v2 — IMPLEMENTED / LOCAL RUN NEXT

New synthesizer:

`tools/video-studio/synthesize_behavioral_pose_driver_v2.py`

New overlap-aware QA:

`tools/video-studio/inspect_behavioral_pose_driver_overlap.py`

One-shot runner:

`tools/video-studio/run_behavior_first_pose_driver_v2_and_qa.ps1`

v2 changes are evidence-driven from the v1 failure:

1. **base retrieval** samples top primary/SIENA candidates and gives much stronger weight to source-relative pose continuity;
2. **base framing** considers upper-body in-frame coverage plus safe wrist room before a unit is selected;
3. **hands are selected jointly with the chosen base**, using predicted retargeted in-frame coverage instead of independent retrieval;
4. **face donor pairs** are selected with normalized facial-shape continuity between windows;
5. **hand donor pairs** are selected with both normalized hand-shape continuity and predicted post-retarget framing;
6. source change uses a **0.75 s symmetric overlap** with quintic easing rather than the v1 incremental 0.25 s copy/blend;
7. v1 artifacts remain untouched under `first_driver`; v2 writes to `first_driver_v2`.

Default v2 timing for a 4.5 s gate:

```text
segment duration: 2.625 s
overlap: 1.875 -> 2.625 s
blend duration: 0.75 s
```

No DWPose or Wan-Animate-2 is invoked by the v2 runner.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver_v2_and_qa.ps1'
```

Expected artifacts:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\driver_plan.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\behavioral_driver_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\behavioral_driver_pose_preview.mp4
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2\driver_qa.json
```

Paste the complete terminal output and upload the v2 preview. Do not invoke Wan-Animate-2 until v2 numeric + visual QA pass.

## Final quality criterion

> this does not merely look like João; this moves and reacts like João.
