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
    -> RGB driving-video representation compatible with installed Wan-Animate-2
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
4.6–10.3 s    u0003-u0004   graphic/still overlay + subject occlusion
18.7–24.7 s   u0009-u0010   held print/photo/book + prop/hand occlusion
43.7–55.7 s   u0021-u0025   lens/camera foreground interaction + occlusion
67.9–74.0 s   u0031-u0033   held purple card + face/body occlusion
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

Observed neutral gate:

```text
4.5 s / 24 fps / 108 frames
base source order primary -> tertiary
overlap 1.875–2.625 s / 0.75 s
base continuity 0.602250
hand framing floor 0.90
predicted hand in-frame 0.947619
hand continuity 0.587692 / source gap 0.0
face shape continuity 0.943299
face velocity continuity 0.725175 / source gap 0.0
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

Visual QA passed: source transition reads continuously in pose space, hands remain available, and the remaining face acceleration is not materially discontinuous.

Classification: **FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 PASS**.

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

No COCO/OpenPose/DWPose conversion occurs inside this node. Saved local W0/W1 workflows feed `pose_video` from real MP4 through `GetVideoComponents`. There is no separate `face_video` input in the installed node.

Classification: **WAN-ANIMATE-2 RAW RGB DRIVING-VIDEO CONTRACT VERIFIED**.

## RGB adapter experiments

### Still-image Delaunay warp — RETIRED

Stalled before frame 1 even after mesh/resolution reduction. Do not resume.

### Still-image IDW/remap — VISUAL FAIL / RETIRED

The IDW path completed, but visual QA showed severe non-anatomic melting of face, torso and arms. This representation is unusable as Wan driving input. No Wan inference was run with it. Do not resume still-image deformation.

### Real-RGB PRIMARY + SIENA xfade spike — TECHNICALLY COMPLETE / NOT A VALID RENDER GATE

Versioned:

- `tools/video-studio/build_wan_animate2_real_rgb_driver_spike.py`;
- `tools/video-studio/run_wan_animate2_real_rgb_driver_spike.ps1`.

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3\wan_real_rgb_spike\pose_video_real_spike65.mp4`

The 65-frame `512×912 @ 24 fps` file uses the actual PRIMARY and SIENA RGB spans selected by v3. Each source span is individually coherent, but the `0.75 s` raw RGB `xfade` creates a visibly double-exposed person/background during the source transition. Because Wan consumes the RGB sequence itself, this would confound the first renderer test.

Classification: **REAL-RGB MULTI-SOURCE XFADE NOT PASS AS FIRST WAN DRIVING INPUT**.

This does **not** invalidate v3 pose composition. It shows that pose-space blending cannot be represented by a naive RGB crossfade between acquisition domains.

## Current gate — ISOLATED PRIMARY WAN RENDER

Before solving learned/identity-preserving RGB synthesis across multiple sources, isolate the renderer itself with a clean, single-source real RGB driver.

Versioned:

- `tools/video-studio/run_wan_animate2_primary_baseline_render.py`;
- `tools/video-studio/run_wan_animate2_primary_baseline_render.ps1`.

The gate:

1. uses the already validated v3 window-0 PRIMARY base unit `primary:VID_20260911_140124885_u0041` only;
2. builds a real RGB 65-frame `512×912 @ 24 fps` driving clip from that source span;
3. extracts a matching clean reference image;
4. reuses an existing local `w*_api_prompt.json` that contains `WanAnimate2ToVideo` and the installed `wan_animate_2_bf16.safetensors`;
5. patches only the driver/reference media and 65-frame render geometry;
6. starts/reuses the protected local ComfyUI portable runtime with `--lowvram`;
7. validates required nodes and exact BF16 visibility before submission;
8. performs the **first actual Wan-Animate-2 inference in this behavioral route**;
9. prints a heartbeat every ~20 s while inference is active;
10. downloads nothing and installs nothing.

Purpose: determine whether the installed Wan-Animate-2 can faithfully transfer one clean real PRIMARY motion span to the reference under the actual RTX 3060 12 GB runtime. A failure here is a renderer/runtime/conditioning issue, not a multi-source stitching issue.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_wan_animate2_primary_baseline_render.ps1'
```

Paste the complete terminal output. If a final MP4 is produced, upload it for visual QA.

## Final quality criterion

> isso não apenas parece João; isso se move e reage como João.
