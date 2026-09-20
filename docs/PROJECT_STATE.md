# Local Video Studio — Current Project State

Status date: **2026-09-20**

GitHub living documents are canonical. Do not reconstruct decisions from chat memory when this document says otherwise.

## Policy — LOCKED

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS, paid API, credits, subscriptions or cloud generation/training;
- no new large renderer while this route is active;
- no new Python/DWPose/CUDA install while the validated local route works;
- Wan S2V, H3, Hunyuan and HeyGen remain retired/historical;
- MuseTalk, LatentSync and CosyVoice remain deferred;
- use the already-installed Wan-Animate-2 only;
- source-camera framing is acquisition geometry, not behavioral identity;
- long-running local passes must emit visible progress/heartbeat.

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
    -> RGB driving representation compatible with installed Wan-Animate-2
    -> local Wan-Animate-2 render
    -> render QA
```

The pose-domain driver is the canonical behavioral representation. The installed Wan-Animate-2 does **not** consume COCO-133 directly; its `pose_video` path consumes RGB frames.

## Curated sources — PASS

### PRIMARY — `VID_20260911_140124885.mp4`

Role: torso / hands / gesture / primary posture.

```text
300.352 s
1801 pose frames @ 6 fps
0 fallback
123 motion units
118 eligible
5 hard excluded
locked exclusion 24.1–37.5 s / u0012-u0016
```

### SECONDARY — `VID_20260819_124008056.mp4`

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

### TERTIARY / SIENA — `SIENA_BRUTO.mp4`

Role: alternate posture / head / coarse arm.

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

Locked SIENA exclusions:

```text
4.6–10.3 s    u0003-u0004
18.7–24.7 s   u0009-u0010
43.7–55.7 s   u0021-u0025
67.9–74.0 s   u0031-u0033
```

SIENA head/posture/coarse-arm reliability weights are saturated at `1.0` and do not rank the 37 clean units meaningfully. Motion/prosody/transition/duration differentiate retrieval inside SIENA.

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

Priority policy:

```text
face       secondary tier 0 only
head       secondary 0 -> primary 1 -> SIENA 2
posture    primary 0 -> SIENA 1 -> secondary body-support 2
coarse_arm primary 0 -> SIENA 1
hands      primary only
generic whole-upper primary only
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## Behavioral pose compositor

### v1 — FAIL

Body/source seam and severe hand clipping. Library remained valid.

### v2 — NOT PASS

Body transition improved, but hand clipping and face acceleration remained.

### v3 — PASS

Output root:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3`

```text
4.5 s / 24 fps / 108 frames
base source order primary -> tertiary
overlap 1.875–2.625 s / 0.75 s
base continuity 0.602250
predicted hand in-frame 0.947619
hand continuity 0.587692
face shape continuity 0.943299
face velocity continuity 0.725175
canonical framing scale 0.942959 / dx 0.022041 / dy -0.122904
```

Selected units:

```text
window 0
  base  primary:VID_20260911_140124885_u0041
  hands primary:VID_20260911_140124885_u0117
  face  secondary:VID_20260819_124008056_u0046

window 1
  base  tertiary:SIENA_BRUTO_u0035
  hands primary:VID_20260911_140124885_u0118
  face  secondary:VID_20260819_124008056_u0047
```

Numeric QA:

```text
OOB overall
coarse_head      0.0000%
upper_body       0.0000%
lower_body/foot  0.0000%
face             0.0000%
left_hand        0.0000%
right_hand       1.1023%

transition-only OOB: 0% every group

transition q90 / normal q90
body_head   0.792506x
face        1.411900x
left_hand   0.682394x
right_hand  0.944349x
```

Visual QA passed. Classification: **FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 PASS**.

## Wan-Animate-2 local contract — VERIFIED

Installed model/code:

```text
Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors  ~30.538 GiB
Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py
Z:\AI\WanAnimate2\comfy_extras\nodes_wan.py
```

Node: `WanAnimate2ToVideo`.

Verified interface includes:

```text
reference_image=None
pose_video=None
clip_vision_output=None
positive_pose=None
clip_vision_output_pose=None
continue_motion=None
pose_strength=1.0
pose_start_percent=0.0
pose_end_percent=1.0
reference_image_strength=1.0
```

Critical behavior:

```text
pose_video type = IMAGE
pose_video -> slice/pad -> resize -> vae.encode(RGB)
```

No COCO/OpenPose/DWPose conversion occurs inside this node. Saved W0/W1 workflows feed `pose_video` from real MP4 through `GetVideoComponents`. There is no separate `face_video` input.

Classification: **WAN-ANIMATE-2 RAW RGB DRIVING-VIDEO CONTRACT VERIFIED**.

## RGB adapter experiments

### Still-image Delaunay warp — RETIRED

Stalled before frame 1 even after reduction. Do not resume.

### Still-image IDW/remap — VISUAL FAIL / RETIRED

Completed but produced severe non-anatomic melting. Do not resume still-image deformation.

### Real-RGB PRIMARY + SIENA xfade — NOT PASS

The actual PRIMARY and SIENA spans were combined by raw RGB xfade. Each span was individually coherent, but the overlap showed strong double exposure because acquisition domains differ. Pose-space blending therefore cannot be represented by naive RGB crossfade.

This does not invalidate the v3 pose compositor.

## First actual Wan-Animate-2 renderer gate — PASS

Run directory:

`Z:\AI\VideoStudioRuns\wan-animate2-behavior\primary-baseline-20260920_113651`

Manifest:

`run_manifest.json`

Runtime facts:

```text
RTX 3060 12 GB
48 GB RAM
ComfyUI 0.34.0
PyTorch 2.13.0+cu130
LOW_VRAM
DynamicVRAM enabled
wan_animate_2_bf16.safetensors
65 frames
512x912
24 fps
30 sampling steps
prompt total 01:19:25
sampling 01:17:19
no OOM
no execution_error
```

Generated artifact returned by the Comfy workflow:

`wan_animate2_bf16_exilada_aspectmatched_ref10_pose080_steps30_00001_.mp4`

Visual QA: identity/background remain stable, motion transfers, hands/arms remain coherent enough for the gate, and there is no material anatomy collapse. This is a renderer-isolation test using PRIMARY reference and PRIMARY driving RGB from the same source/acquisition domain.

Classification: **WAN-ANIMATE-2 PRIMARY BASELINE RENDER PASS**.

Known runner bug: the first baseline runner copied the first MP4 in the returned output list to `wan_animate2_primary_baseline65.mp4`; that first MP4 was the driving input itself. The actual generated output was the second returned MP4 above. Do not use the mislabeled copied driver as generated evidence.

## Current gate — CROSS-SOURCE SIENA MOTION TRANSFER

The next question is no longer whether Wan runs. It is whether a driving RGB clip from a **different acquisition domain** can transfer motion while the PRIMARY reference controls identity/appearance.

Versioned:

- `tools/video-studio/run_wan_animate2_cross_source_siena_render.py`;
- `tools/video-studio/run_wan_animate2_cross_source_siena_render.ps1`.

Gate design:

1. reference image: PRIMARY unit `primary:VID_20260911_140124885_u0041` midpoint;
2. driving video: SIENA unit `tertiary:SIENA_BRUTO_u0035` selected by v3;
3. real RGB only; no DWPose, no skeleton render, no xfade, no still warp;
4. 65 frames / 512x912 / 24 fps;
5. same installed BF16 Animate2 path and low-VRAM runtime;
6. deterministic output selection excludes the driving input and prefers the actual Wan-generated MP4;
7. expected runtime is similar to the ~80 minute PRIMARY baseline.

Success criterion: the output must preserve the PRIMARY reference identity/appearance while reproducing materially recognizable SIENA body/head/coarse-arm motion without carrying over the SIENA acquisition appearance as the dominant result.

If this passes, the next architectural task is to use Animate2 continuation/chunking rather than raw RGB xfade to join source-specific generated motion spans under one stable reference identity.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_wan_animate2_cross_source_siena_render.ps1'
```

Upload the resulting `wan_animate2_cross_source_siena65_GENERATED.mp4` and paste the terminal output if there is any error.

## Final quality criterion

> isso não apenas parece João; isso se move e reage como João.
