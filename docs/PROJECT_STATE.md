# Local Video Studio — Current Project State

Status date: **2026-09-19**

GitHub living documents are the canonical source of truth.

## Policy — LOCKED

- 100% local/self-hosted, zero service cost;
- never upload João's video/voice/identity to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer while this route is active;
- no new Python/DWPose/CUDA install while the validated local route works;
- Wan S2V, H3, Hunyuan and HeyGen remain retired/historical;
- MuseTalk/LatentSync/CosyVoice remain deferred;
- use the already-installed Wan-Animate-2 only through its verified local contract;
- source-camera framing is acquisition geometry, not behavioral identity.

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
    -> dense RGB behavioral driving-video adapter
    -> installed Wan-Animate-2 raw driving-video branch
    -> render QA
```

The pose-domain driver is the canonical behavioral representation. Wan-Animate-2 does **not** consume the COCO-133 JSONL directly; it consumes RGB driving-video frames.

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
```

Locked exclusion: **24.1–37.5 s / u0012–u0016** for held object, hand occlusion and prop interaction.

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

SIENA `head/posture/coarse_arm` reliability weights are saturated at `1.0 / 1.0 / 1.0` q10/median/q90 and therefore do not rank the 37 clean units meaningfully. Retrieval within SIENA is differentiated by motion/prosody/transition/duration.

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

## Behavioral driver history

### v1 — FAIL

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

Visual preview confirmed source-change body reconfiguration and severe hand loss below frame. Library remained valid.

### v2 — MAJOR IMPROVEMENT / NOT PASS

```text
body transition q90 ratio 0.7920x
face transition q90 ratio 2.4043x
hand OOB left 21.87% / right 27.73%
```

Visual preview confirmed body transition fixed but hand clipping and face acceleration remained.

### v3 — POSE QA PASS

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3`

Observed neutral synthesis:

```text
4.5 s / 24 fps / 108 frames
base primary -> tertiary
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

transition-only OOB: 0% for every group

transition q90 / normal q90
body_head   0.792506x
face        1.411900x
left_hand   0.682394x
right_hand  0.944349x
```

Visual QA confirms one continuous primary -> SIENA performance, hands stay available, and the remaining face acceleration is not visibly discontinuous.

Classification: **FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 PASS**.

## Camera framing rule — LOCKED

Absolute source-camera translation/scale is not João behavior. Relative pose, gesture, head motion, hand shape/motion and facial deformation are behavioral.

One constant global similarity transform may normalize a synthesized performance into the target canvas if it preserves relative motion/geometry and adds no dynamic camera motion. v3 applies exactly one constant transform to the full 4.5 s driver.

## Wan-Animate-2 local contract — VERIFIED

Installed model/code:

```text
Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors
  ~30.538 GiB
Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py
Z:\AI\WanAnimate2\comfy_extras\nodes_wan.py
```

The local node is `WanAnimate2ToVideo`, category `model/conditioning/wan/animate`.

Verified execute signature:

```text
execute(
  positive, negative, vae,
  width, height, length, batch_size, video_frame_offset,
  reference_image=None,
  pose_video=None,
  clip_vision_output=None,
  positive_pose=None,
  clip_vision_output_pose=None,
  continue_motion=None,
  pose_strength=1.0,
  pose_start_percent=0.0,
  pose_end_percent=1.0,
  reference_image_strength=1.0
)
```

Critical contract evidence:

```text
pose_video type: IMAGE
pose_video tooltip: "The video whose motion is transferred to the reference character."
node description: replicates facial animation, body motion and hand gestures from the driving video
```

Inside `WanAnimate2ToVideo.execute`:

```text
pose_video -> frame slicing/padding
pose_video -> common_upscale(..., width, height, ...)
pose_video -> vae.encode(pose_video[:, :, :, :3])
pose_values["pose_video_latent"] = encoded RGB video
```

There is **no COCO/OpenPose/DWPose conversion inside this node**. The current Wan-Animate-2 generation path is end-to-end raw driving video. Saved local W0/W1 workflows confirm `pose_video <- GetVideoComponents` from actual MP4 driver files such as `official_demo1_template.mp4`.

The installed `WanAnimate2ToVideo` also has no separate `face_video` input. Facial animation, body motion and hand gestures must therefore coexist in the same RGB driving sequence.

Classification: **WAN-ANIMATE-2 RAW RGB DRIVING-VIDEO CONTRACT VERIFIED**.

## RGB behavioral adapter — IMPLEMENTED / QA NEXT

Versioned:

- `tools/video-studio/build_wan_animate2_rgb_driver_proxy.py`;
- `tools/video-studio/run_wan_animate2_rgb_driver_proxy.ps1`.

Purpose: bridge the validated COCO-133 v3 driver into the actual raw-RGB Wan contract without introducing a second generative model.

Adapter v1 strategy:

1. automatically select a clean eligible PRIMARY João frame with face and hands visible;
2. extract it at the target `512×912` portrait canvas;
3. use that real frame as a texture atlas;
4. build a fixed Delaunay mesh from reliable COCO WholeBody points;
5. piecewise-affine warp the real pixels through all 108 validated v3 poses;
6. use a neutral background so source-camera/background motion is not injected into the driver;
7. emit both the full 108-frame proxy and a **65-frame** (`4n+1`) spike clip that covers the complete 1.875–2.625 s primary->SIENA overlap.

This is deliberately non-generative and fully local. It is a dense RGB motion proxy, not a skeleton preview and not claimed to be photorealistic resynthesis.

Expected output root:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3\wan_rgb_proxy`

Expected outputs:

```text
rgb_proxy_anchor_reference.png
behavioral_driver_rgb_proxy.mp4
behavioral_driver_rgb_proxy_spike65.mp4
behavioral_driver_rgb_proxy_contact.jpg
rgb_driver_proxy_manifest.json
```

A Wan render is **not** authorized until the RGB proxy itself is visually reviewed. If the RGB proxy fails, fix the adapter rather than the validated behavior library/compositor.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_wan_animate2_rgb_driver_proxy.ps1'
```

Then paste the complete terminal output and upload:

```text
...\first_driver_v3\wan_rgb_proxy\behavioral_driver_rgb_proxy_contact.jpg
...\first_driver_v3\wan_rgb_proxy\behavioral_driver_rgb_proxy_spike65.mp4
```

Only after visual QA of that RGB driver should the first low-cost Wan-Animate-2 render spike be built.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. Do not leave long-running terminal tasks silent.

## Final quality criterion

> this does not merely look like João; this moves and reacts like João.
