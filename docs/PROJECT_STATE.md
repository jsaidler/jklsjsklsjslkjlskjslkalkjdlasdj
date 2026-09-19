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
- use the already-installed Wan-Animate-2 only after its actual local conditioning interface is statically inspected and understood.

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
    -> local Wan-Animate-2 conditioning adapter
    -> first render spike
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

## Driver v1 — FAIL

4.5 s / 24 fps / neutral QA.

```text
transition q90 / normal q90
body_head  6.1729x
face       3.1519x
left_hand  3.0979x
right_hand 1.5199x

hand OOB
left  41.71%
right 44.09%
```

Visual preview confirmed body reconfiguration and hands lost below frame. Library remained valid.

Classification: **COMPOSITOR v1 FAIL**.

## Driver v2 — MAJOR IMPROVEMENT / NOT PASS

```text
base primary -> tertiary
overlap 1.875–2.625 s / 0.75 s
base continuity 0.615637
face continuity 0.937309
hand continuity 0.783131
predicted hand in-frame 0.707143
```

QA:

```text
OOB
coarse_head 0.00%
upper_body  6.37%
lower_body  3.42%
face        0.00%
left_hand  21.87%
right_hand 27.73%

transition q90 / normal q90
body_head  0.7920x
face       2.4043x
left_hand  0.2085x
right_hand 0.8727x
```

Visual review confirmed smooth body-source transition, but excessive hand clipping remained and the face accelerated through the overlap.

Classification: **v2 NOT PASS**.

## Camera framing is not behavioral identity — LOCKED

Absolute source-camera translation/scale is acquisition geometry, not João behavior. Relative pose, gesture, head motion, hand shape/motion and facial deformation are behavioral.

A behavioral driver may therefore apply one constant global similarity transform to the complete synthesized performance to normalize framing, provided all relative motion/geometry are preserved and no dynamic camera motion is introduced.

## Driver v3 — POSE QA PASS

Versioned:

- `tools/video-studio/synthesize_behavioral_pose_driver_v3.py`;
- `tools/video-studio/run_behavior_first_pose_driver_v3_and_qa.ps1`.

Observed neutral synthesis:

```text
duration 4.5 s
24 fps
108 frames
base source order primary -> tertiary
overlap 1.875–2.625 s = 0.750 s
base continuity 0.602250
hand framing floor used 0.90
predicted retargeted-hand in-frame ratio 0.947619
hand continuity 0.587692 / source gap 0.0
face shape continuity 0.943299 / velocity continuity 0.725175 / source gap 0.0
canonical framing scale 0.942959 / dx 0.022041 / dy -0.122904
```

Selected units:

```text
window 0
  base  primary:VID_20260911_140124885_u0041
  hands primary:VID_20260911_140124885_u0117
  face  secondary:VID_20260819_124008056_u0046
  predicted hand framing 0.990476

window 1
  base  tertiary:SIENA_BRUTO_u0035
  hands primary:VID_20260911_140124885_u0118
  face  secondary:VID_20260819_124008056_u0047
  predicted hand framing 0.904762
```

Numeric QA:

```text
confidence-qualified OOB
  coarse_head      0/540  = 0.000000
  upper_body       0/864  = 0.000000
  lower_body/foot  0/288  = 0.000000
  face             0/7344 = 0.000000
  left_hand        0/2268 = 0.000000
  right_hand      25/2268 = 0.011023

transition q90 / normal q90
  body_head   0.792506x
  face        1.411900x
  left_hand   0.682394x
  right_hand  0.944349x

transition max / normal q90
  body_head   0.865985x
  face        1.555957x
  left_hand   0.985312x
  right_hand  1.107439x

transition-only OOB
  coarse_head      0%
  upper_body       0%
  lower_body/foot  0%
  face             0%
  left_hand        0%
  right_hand       0%

hand-root/body-wrist distance
  left  q10/median/q90/max = 0/0/0/0
  right q10/median/q90/max = 0/0/0/0
```

Visual QA of `first_driver_v3\behavioral_driver_pose_preview.mp4` confirms:

- the primary -> SIENA transition reads as one continuous performance rather than a skeleton swap;
- hands stay visually available instead of disappearing below frame;
- no visible discontinuity or deformation accompanies the face's remaining `1.41x` transition acceleration;
- the residual right-hand OOB is only `1.10%` overall, occurs outside the transition, and does not present as materially relevant clipping in the preview.

Classification: **FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 PASS**.

This PASS validates the pose-domain composition architecture. It does **not** yet prove that the installed Wan-Animate-2 accepts this COCO-133 representation directly.

## Installed Wan-Animate-2 — conditioning interface preflight NEXT

Known installed state from prior validation:

```text
Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors
  ~30.538 GiB
Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py
text encoder ~10.586 GiB
VAE ~0.236 GiB
```

Before any render, inspect the actual local code/config path rather than assuming the model consumes our COCO-133 JSONL or skeleton preview.

Versioned static inspector:

- `tools/video-studio/inspect_wan_animate2_conditioning.py`;
- `tools/video-studio/run_wan_animate2_conditioning_preflight.ps1`.

The preflight performs **source/config inspection only**. It does not import ComfyUI/torch/model weights and does not run inference. It inventories model files and searches the installed code for:

- `model_type=animate2` / loader references;
- Animate2 model forward/signature paths;
- Comfy node `INPUT_TYPES` / `NODE_CLASS_MAPPINGS`;
- pose / driving / reference / control / conditioning / mask / face / video interfaces.

Expected report:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\wan_animate2_conditioning_preflight.json`

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_wan_animate2_conditioning_preflight.ps1'
```

Paste the complete terminal output. From that evidence, implement the smallest adapter from the validated v3 driver into the **actual installed** Wan-Animate-2 conditioning interface, then prepare a low-cost first render spike.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. Do not leave long-running terminal tasks silent.

## Final quality criterion

> this does not merely look like João; this moves and reacts like João.
