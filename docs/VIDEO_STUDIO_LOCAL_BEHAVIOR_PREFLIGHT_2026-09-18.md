# Local Video Studio — local behavior route preflight

Date: **2026-09-18**  
Original run: **2026-09-18 23:45:16**  
Strict tooling follow-up completed: **2026-09-19 00:40:53**  
Status: **WAN-ANIMATE-2 REUSE PASS / LOCAL DWPOSE PAYLOAD REUSE PASS / WANGP DWPOSE RUNTIME PROBE NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Technical route: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Original no-download preflight

The original preflight was read-only. It performed no download, installation, deletion or model mutation.

Result:

```text
BEHAVIOR SOURCES: PASS
WAN-ANIMATE-2 PAYLOAD: PASS
WAN-ANIMATE-2 NATIVE CODE: PASS
POSE TOOLING: NOT FOUND UNDER WAN ROOT
NEXT ROUTE GATE: BUILD BEHAVIOR PROFILE WITHOUT NEW LARGE RENDERER DOWNLOAD
```

That result proved only that DWPose was not under `Z:\AI\WanAnimate2`; it never proved global absence.

System snapshot at that run:

- Windows 11;
- RTX 3060 12 GB;
- NVIDIA driver 595.95;
- ffmpeg/ffprobe/nvidia-smi present;
- Z: free **22.32 GB**;
- Z: used **424.80 GB**.

## Behavioral sources — PASS

- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 + audio;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 + audio;
- `VID_20260911_140124885.mp4` — 300.4 s, 3840x2160 HEVC + audio.

Primary behavior-profile source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

## Wan-Animate-2 reuse — PASS

Present locally:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

No new large renderer is justified.

## Python resolution — CORRECTED

The original preflight incorrectly emitted:

```text
Python 3.11: PASS / C:\Python314\python.exe / 3.14.3
```

The strict follow-up established:

```text
py launcher: c:\windows\py.exe
py -3.11: NOT RESOLVED
```

The Windows launcher currently registers Python 3.7 and `C:\Python314\python.exe`; it does not register Python 3.11.

This does **not** justify installing another Python. The project already has historical evidence of an isolated WanGP runtime at:

`Z:\AI\WanGP\env_uv\Scripts\python.exe`

That environment was previously validated as Python 3.11.14 with Torch 2.10.0+cu130 / CUDA 13.0 during the Hunyuan branch. Existing project runners already use that exact interpreter path.

Therefore the next action is to validate/reuse that isolated environment, not reinstall Python.

## Pose tooling targeted search — REUSE PASS

The corrected bounded inspector completed on 2026-09-19 00:40:53 and found:

```text
DIR  Z:\AI\WanGP\preprocessing\dwpose
FILE Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx  ~128.2 MB
FILE Z:\AI\WanGP\ckpts\pose\yolox_l.onnx          ~206.7 MB
POSE TOOLING RESULT: REUSE CANDIDATES FOUND = 3
```

Classification:

**LOCAL DWPOSE PAYLOAD REUSE: PASS.**

No DWPose download is required. Do not download DWPose-L, ControlNet Aux or another pose package for this gate.

The WanGP implementation uses the existing YOLOX person detector plus DWPose whole-body ONNX model. The behavior adapter will consume original COCO WholeBody 133 coordinates before WanGP's display-oriented remapping.

## Runtime validation still required

Payload presence is not equivalent to runtime validation. The project now has:

`tools/video-studio/probe_wangp_dwpose_runtime.ps1`

This probe is local/read-only with respect to installed tooling. It checks:

- `Z:\AI\WanGP\env_uv\Scripts\python.exe` exists and runs;
- `cv2`, NumPy and ONNX Runtime import successfully;
- available ONNX providers;
- both existing ONNX sessions can be created;
- one actual frame from the primary source produces person detection and a 133-keypoint whole-body result.

It performs no download, installation or model mutation.

If that passes, the next step is the short pose-only runner:

`tools/video-studio/run_behavior_pose_smoke.ps1`

Only after that smoke is credible should the full pose track be generated.

## Deferred components — unchanged

- Motion Mirror: fallback only;
- MuseTalk: deferred;
- LatentSync: deferred;
- final TTS/voice-clone integration: deferred.

## Reclaimable retired payload

Still present and not part of the active route:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Do not delete it reflexively. The active behavior-profile route currently requires no large download.

## Current exact gate

```text
existing WanGP Python + existing YOLOX/DWPose
    -> one-frame runtime probe
    -> 5 s pose smoke
    -> full 6 fps normalized COCO WholeBody 133 pose track
    -> extract_behavior_profile.py
    -> status=complete manifest + motion_units.csv
    -> human/technical inspection
    -> new 4–5 s multi-unit behavioral driver
    -> installed Wan-Animate-2
```

Do not run Wan-Animate-2 before the complete profile is inspected. Do not install/download another pose/runtime stack unless new evidence shows the existing WanGP stack cannot be reused.
