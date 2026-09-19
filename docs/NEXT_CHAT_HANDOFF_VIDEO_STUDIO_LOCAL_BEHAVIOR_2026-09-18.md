# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA CURATED PASS / UNIFIED LIBRARY PASS / DRIVER v1 FAIL / DRIVER v2 NOT PASS / DRIVER v3 POSE QA PASS / WAN CONDITIONING PREFLIGHT NEXT**

Continue in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/inspect_wan_animate2_conditioning.py`;
6. `tools/video-studio/run_wan_animate2_conditioning_preflight.ps1`.

## Hard constraints

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current CPU route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred;
- use only the already-installed Wan-Animate-2 once its real local conditioning path is known.

## Curated sources

### Primary
`VID_20260911_140124885.mp4` — torso/hands/gesture/posture.

```text
123 total
118 eligible
5 excluded
24.1–37.5 s / u0012-u0016 excluded
```

### Secondary
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

SIENA pose-reliability weights are saturated at 1.0 and do not rank clean units meaningfully.

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

Visual preview showed a source-change skeleton swap and severe hand loss below frame.

### v2 — improved but NOT PASS

```text
body transition q90 ratio 0.7920x
face transition q90 ratio 2.4043x
hand OOB left 21.87% / right 27.73%
```

Visual preview confirmed body transition fixed but hand clipping and face acceleration remained.

## Driver v3 — POSE QA PASS

Output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3`

Observed:

```text
4.5 s / 24 fps / 108 frames
base primary -> tertiary
overlap 1.875–2.625 s / 0.75 s
base continuity 0.602250
hand framing floor 0.90
predicted hand in-frame 0.947619
hand pair source gap 0.0
face pair source gap 0.0
canonical framing scale 0.942959
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

Visual QA of `behavioral_driver_pose_preview.mp4` passed:

- source transition reads continuously;
- hands remain available;
- no visually material face discontinuity;
- residual right-hand OOB is outside transition and not materially visible.

Classification: **FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 PASS**.

This validates the pose compositor, not yet the Wan input adapter.

## Wan-Animate-2 installed route — PRELIGHT NEXT

Known install root:

`Z:\AI\WanAnimate2`

Known model/code:

```text
Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors
Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py
```

Do not assume Wan directly consumes COCO-133 JSONL or the skeleton preview. First inspect the actual installed code path.

Versioned:

- `tools/video-studio/inspect_wan_animate2_conditioning.py`;
- `tools/video-studio/run_wan_animate2_conditioning_preflight.ps1`.

The inspector is static only: no Comfy launch, no torch/model import, no DWPose, no Wan inference. It inventories model files and searches code/config for `animate2`, loader/model type, `INPUT_TYPES`, node mappings, pose/driving/reference/control/conditioning/mask/face/video paths and relevant class/function signatures.

Expected report:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\wan_animate2_conditioning_preflight.json`

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_wan_animate2_conditioning_preflight.ps1'
```

Paste the complete terminal output. Then determine the smallest adapter from v3 into the **actual installed** Wan-Animate-2 conditioning interface and prepare the first low-cost render spike.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
