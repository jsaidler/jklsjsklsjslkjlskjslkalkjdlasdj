# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA CURATED PASS / UNIFIED LIBRARY PASS / DRIVER v1 FAIL / DRIVER v2 NOT PASS / DRIVER v3 POSE QA PASS / WAN RAW-RGB CONTRACT VERIFIED / RGB PROXY QA NEXT**

Continue in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/build_wan_animate2_rgb_driver_proxy.py`;
6. `tools/video-studio/run_wan_animate2_rgb_driver_proxy.ps1`.

## Hard constraints

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current local route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred;
- do not replace the validated source/library/pose compositor because of downstream adapter failures;
- use only the already-installed Wan-Animate-2 through its verified raw-RGB driving-video contract.

## Curated sources

### PRIMARY
`VID_20260911_140124885.mp4` — torso/hands/gesture/posture.

```text
123 total
118 eligible
5 excluded
24.1–37.5 s / u0012-u0016 excluded
```

### SECONDARY
`VID_20260819_124008056.mp4` — face/head/microexpression; body support only.

```text
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands disabled
face/head median quality 0.913145
```

### SIENA
`SIENA_BRUTO.mp4` — alternate posture/head/coarse arm.

```text
49 total
12 hard excluded
37 clean
hands disabled
generic whole-upper disabled
```

Locked exclusions:

```text
4.6–10.3 s    u0003-u0004
18.7–24.7 s   u0009-u0010
43.7–55.7 s   u0021-u0025
67.9–74.0 s   u0031-u0033
```

## Unified library — PASS

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

```text
271 total units
primary 118
secondary 116
tertiary 37
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## Driver history

### v1 — FAIL

```text
transition q90 / normal q90
body_head  6.1729x
face       3.1519x
left_hand  3.0979x
right_hand 1.5199x
hand OOB left 41.71% / right 44.09%
```

### v2 — improved but NOT PASS

```text
body transition q90 ratio 0.7920x
face transition q90 ratio 2.4043x
hand OOB left 21.87% / right 27.73%
```

### v3 — POSE QA PASS

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3`

```text
4.5 s / 24 fps / 108 frames
base primary -> tertiary
overlap 1.875–2.625 s / 0.75 s
base continuity 0.602250
predicted hand in-frame 0.947619
canonical framing scale 0.942959
```

Selected:

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

QA:

```text
OOB overall
coarse_head      0.0000%
upper_body       0.0000%
lower_body/foot  0.0000%
face             0.0000%
left_hand        0.0000%
right_hand       1.1023%

transition-only OOB 0% all groups

transition q90 / normal q90
body_head   0.792506x
face        1.411900x
left_hand   0.682394x
right_hand  0.944349x
```

Visual preview passed: source transition reads continuously, hands remain available, no visually material face discontinuity.

Classification: **FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 PASS**.

## Camera framing — LOCKED

Absolute source-camera translation/scale is acquisition geometry, not behavioral identity. One constant global similarity transform may normalize the complete synthesized performance if relative motion/geometry are preserved and no dynamic camera motion is introduced.

## Wan-Animate-2 local contract — VERIFIED

Node: `WanAnimate2ToVideo` in `comfy_extras\nodes_wan.py`.

Critical facts from the installed source/object info:

```text
pose_video type = IMAGE
reference_image type = IMAGE
pose_video is resized to requested width/height
pose_video is VAE-encoded directly:
  pose_values["pose_video_latent"] = vae.encode(pose_video[:, :, :, :3])
```

There is no COCO/OpenPose/DWPose extractor in this node. Saved W0/W1 prompts wire `pose_video <- GetVideoComponents` from real MP4 driving videos. The installed Animate2 node has no separate `face_video`; face/body/hands motion all travel in the single RGB driving video.

Therefore:

```text
COCO-133 v3 behavioral driver = canonical behavior/control representation
RGB driving video             = required Wan conditioning representation
```

Classification: **WAN-ANIMATE-2 RAW RGB DRIVING-VIDEO CONTRACT VERIFIED**.

## RGB adapter v1 — IMPLEMENTED / NEXT

Versioned:

- `tools/video-studio/build_wan_animate2_rgb_driver_proxy.py`
- `tools/video-studio/run_wan_animate2_rgb_driver_proxy.ps1`

Adapter behavior:

1. auto-select a clean eligible PRIMARY João frame with usable body/face/hands;
2. extract it at `512×912`;
3. use its real pixels as a texture atlas;
4. build a fixed Delaunay mesh on reliable COCO WholeBody points;
5. piecewise-affine warp those pixels through the 108-frame v3 trajectory;
6. neutral background; no source-background/camera motion;
7. emit full 108-frame proxy plus a 65-frame `4n+1` spike clip covering the complete source overlap.

Output root:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3\wan_rgb_proxy`

Expected:

```text
rgb_proxy_anchor_reference.png
behavioral_driver_rgb_proxy.mp4
behavioral_driver_rgb_proxy_spike65.mp4
behavioral_driver_rgb_proxy_contact.jpg
rgb_driver_proxy_manifest.json
```

This adapter is deliberately non-generative. It is a dense RGB motion proxy to test Wan's end-to-end driving branch. If it fails, patch the RGB adapter; do not throw away the validated pose-domain behavior system.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_wan_animate2_rgb_driver_proxy.ps1'
```

Paste the complete terminal output and upload:

```text
...\first_driver_v3\wan_rgb_proxy\behavioral_driver_rgb_proxy_contact.jpg
...\first_driver_v3\wan_rgb_proxy\behavioral_driver_rgb_proxy_spike65.mp4
```

Do **not** run Wan-Animate-2 before visual QA of the RGB proxy. If proxy QA passes, prepare the first low-cost Wan render at `512×912`, 65 frames, using the existing BF16 Animate2 model and no new model downloads.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
