# Local Video Studio — local behavior route preflight

Date: **2026-09-18**  
Run timestamp: **2026-09-18 23:45:16**  
Follow-up: **2026-09-19 strict tooling probe partially completed**  
Status: **PASS FOR INSTALLED WAN-ANIMATE-2 REUSE / PYTHON 3.11 NOT RESOLVED / POSE SEARCH MUST BE RERUN**

Canonical state: `docs/PROJECT_STATE.md`  
Technical route: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Purpose

This preflight was intentionally **read-only** with respect to models and runtime. It performed no download, no installation, no deletion and no model mutation.

Repository tool:

`tools/video-studio/preflight_local_behavior_route.ps1`

Local report:

`D:\GOOGLE DRIVE\DEV\Roguelite\tools\video-studio\reports\local_behavior_route_preflight_20260918_234516.txt`

## Result summary

```text
BEHAVIOR SOURCES: PASS
WAN-ANIMATE-2 PAYLOAD: PASS
WAN-ANIMATE-2 NATIVE CODE: PASS
POSE TOOLING: NOT FOUND UNDER WAN ROOT
NEXT ROUTE GATE: BUILD BEHAVIOR PROFILE WITHOUT NEW LARGE RENDERER DOWNLOAD
```

The preflight therefore closes the question of whether another large renderer must be downloaded before continuing: **no**. The installed Wan-Animate-2 payload and native code are present and should be reused.

## System snapshot

- OS context: Windows 11 project runtime.
- GPU: **NVIDIA GeForce RTX 3060 12 GB**.
- NVIDIA driver: **595.95**.
- VRAM reported: **12288 MB total / 11579 MB free** at preflight time.
- `ffmpeg`: present.
- `ffprobe`: present.
- `nvidia-smi`: present.
- Z: free space: **22.32 GB**.
- Z: used space: **424.80 GB**.

### Python resolution warning — SUPERSEDED BY STRICT FOLLOW-UP

The original preflight printed:

```text
Python 3.11: PASS / C:\Python314\python.exe / 3.14.3
```

That line was internally inconsistent and is no longer authoritative.

The strict follow-up inspector on 2026-09-19 reached:

```text
py launcher: c:\windows\py.exe
py -3.11: NOT RESOLVED
```

Therefore **Python 3.11 is not currently registered/resolvable through the Windows launcher**. Do not install or reinstall Python from this fact alone. The corrected inspector still needs to inventory Python executables bundled in existing local AI runtimes before an interpreter is selected for pose tooling.

The first strict-inspector run then hit a Windows PowerShell 5.1 collection-binder defect (`Argument types do not match`) before completing the targeted pose scan. That was a script defect, not evidence that pose tooling is absent. `inspect_local_behavior_tooling.ps1` was corrected at commit `c5f6000bc8caf0f3739e1323f7b870abe93c9315` to use `.ToArray()` for generic lists and to capture legacy launcher inventory without treating stderr as fatal.

## Behavioral source library — PASS

All three protected originals are present and readable with audio:

- `SIENA_BRUTO.mp4` — **113.3 s**, **1080x1920**, H.264, audio present;
- `VID_20260819_124008056.mp4` — **282.6 s**, **1920x1080**, H.264, audio present;
- `VID_20260911_140124885.mp4` — **300.4 s**, **3840x2160**, HEVC, audio present.

The generic full-duration 1080p local derivative is also present at about **1.48 GB**. Its HeyGen-oriented filename is historical only; it remains a local file and no external upload is authorized.

## Wan-Animate-2 reuse audit — PASS

Installed components:

- transformer: `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — **30.538 GiB**;
- UMT5 text encoder: `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — **10.586 GiB**;
- VAE: `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — **0.236 GiB**;
- native Animate-2 code: `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

Large transformer SHA-256 verification was intentionally skipped. Use `-VerifyLargeSha` only if integrity verification becomes necessary; do not hash 30.5 GiB as routine work.

### Native/custom-node state

- `comfyui_controlnet_aux`: not found under Wan root;
- KJNodes: not found under Wan root.

Neither absence invalidates the installed Animate-2 model/code pass.

## Pose / behavior tooling — GAP NOT YET GLOBALLY RESOLVED

No DWPose whole-body model was found **under the Wan root** by the original preflight.

Important scope limitation: this did not perform an expensive full `Z:\AI` crawl for pose models. The first strict targeted scan aborted because of the now-fixed PowerShell list-return bug. Therefore **pose tooling is still unresolved globally**.

The correct next action is to rerun the corrected `tools/video-studio/inspect_local_behavior_tooling.ps1`. Only if that bounded search finds no reusable whole-body/hand pose tooling should a new small dependency be considered.

If no reusable whole-body pose model exists anywhere locally, a DWPose-class component may be considered as a small support dependency, not as a renderer, only after exact file, official source, license, destination and disk impact are enumerated.

Do not download it merely because the Wan-root scan was negative.

## Deferred components — unchanged

- Motion Mirror: not installed; expected fallback only.
- MuseTalk: not installed; lip-sync remains deferred.
- LatentSync: not installed; lip-sync remains deferred.

Do not install these before the body/head behavioral gate.

## Reclaimable retired payload

The retired Hunyuan transformer is still present:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors`

Size: **12.486 GiB**.

It is not part of the active route. With only **22.32 GB** free on Z:, this is the first obvious reclaimable large payload if later storage pressure requires cleanup. The preflight did not delete it.

## Canonical interpretation

The active route is now:

```text
three João behavioral videos
        |
        +--> build local behavior profile / motion-unit library
        |      +-- pose descriptors
        |      +-- prosody descriptors
        |      +-- source RGB clip references
        |
new local speech audio
        |
        +--> retrieve/sequence João motion units
        +--> synthesize new João driving performance
        |
installed Wan-Animate-2
        |
local lip-sync later, only if needed
```

The next development task is **not renderer selection**. Renderer reuse has passed.

## Immediate next action — LOCKED

Continue the first **behavior-profile / motion-unit extractor** gate.

Current exact order:

1. pull `main` and rerun corrected `tools/video-studio/inspect_local_behavior_tooling.ps1`;
2. inventory bundled local Python interpreters and reusable whole-body/hand pose tooling;
3. do not install Python 3.11 merely because `py -3.11` is unresolved;
4. if a usable local pose stack exists, connect it to the normalized JSONL pose-track contract already accepted by `extract_behavior_profile.py`;
5. only if no suitable pose tooling exists, enumerate the smallest required local dependency before downloading anything;
6. run the extractor on `VID_20260911_140124885.mp4` with real pose data;
7. inspect `manifest.json` and `motion_units.csv` before any Wan render.

The next gate remains a locally generated behavior profile and inspectable motion-unit inventory. Do not run another multi-hour diffusion benchmark before that profile exists.