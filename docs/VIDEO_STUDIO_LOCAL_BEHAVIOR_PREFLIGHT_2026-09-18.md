# Local Video Studio — local behavior route preflight

Date: **2026-09-18**  
Original run: **2026-09-18 23:45:16**  
Strict tooling follow-up: **2026-09-19 00:40:53**  
Runtime probe: **2026-09-19 01:41**  
CPU smoke: **2026-09-19**  
Status: **WAN-ANIMATE-2 REUSE PASS / LOCAL DWPOSE REUSE PASS / CPU POSE SMOKE PASS / VISUAL POSE GATE NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Technical route: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Locked execution constraints

This route remains fully local/self-hosted and zero-service-cost. No João identity media is sent to third parties. No new large renderer, DWPose package or Python environment is justified by current evidence.

## Behavioral sources — PASS

- `VID_20260911_140124885.mp4` — 300.352 s, 3840x2160 HEVC + audio — primary behavior source;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 + audio;
- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 + audio.

Primary:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

## Wan-Animate-2 reuse — PASS

Present locally:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

No new renderer is justified. Wan-Animate-2 remains blocked until the complete behavior profile is inspected.

## Python resolution — CORRECTED

Windows `py -3.11` does not resolve a launcher-registered interpreter. This does not justify installing Python because the existing isolated WanGP runtime is present and now revalidated:

`Z:\AI\WanGP\env_uv\Scripts\python.exe` — **Python 3.11.14**.

## DWPose payload reuse — PASS

Existing local assets:

```text
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx   ~128.2 MB
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx           ~206.7 MB
```

No DWPose-L, ControlNet Aux or alternate pose stack download is required.

## Runtime probe — FUNCTIONAL PASS / CUDA ORT NOT VALIDATED

The corrected runtime probe used the versioned `extract_dwpose_track.py` for a single real frame from the primary source.

Confirmed:

- WanGP Python runs;
- OpenCV, NumPy, ONNX Runtime and WanGP DWPose imports work;
- detector returns the subject;
- output schema is `coco_wholebody_133`;
- one frame completed with detector fallback ratio 0.0.

CUDA caveat:

ONNX Runtime reports available providers including CUDA, but attempts to initialize CUDA emitted an error because `onnxruntime_providers_cuda.dll` depends on missing `cublasLt64_13.dll`, together with CUDA 13/cuDNN requirements. Therefore the reported requested provider is not accepted as evidence of real CUDA execution.

Classification:

```text
DWPose functional runtime: PASS
DWPose ONNX CUDA acceleration: FAIL / NOT VALIDATED
```

Do not install CUDA dependencies at this stage; CPU can carry the current quality gate.

## 5 s CPU pose smoke — PASS

Actual smoke parameters:

- source window: 30.0–35.0 s;
- sample rate: 6 fps;
- analysis size: 960x540;
- provider: `CPUExecutionProvider`.

Result:

```text
frames: 30
last_timestamp_s: 34.833333
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.13263878929229625
elapsed_s: 26.750566244125366
frames_per_second_wall: 1.1214715877869776
```

Track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s.jsonl`

The aggregate keypoint score is recorded but is not used as a standalone gate because it cannot establish anatomical correctness or temporal continuity.

## Visual pose validation — NEXT

Before any full 300 s pass, inspect the actual keypoints over the source frames.

Versioned tooling:

- `tools/video-studio/render_pose_overlay.py`;
- `tools/video-studio/run_behavior_pose_visual_gate.ps1`.

Expected output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s_overlay.mp4`

Acceptance is human/visual:

- torso and limbs align with the subject;
- hands remain attached to the correct wrists;
- hand/finger landmarks are behaviorally usable;
- face landmarks remain on the face;
- no obvious left/right swaps, jumps or background tracking.

Only after this visual inspection passes should the full 6 fps pose track be generated.

## Deferred components — unchanged

- Motion Mirror: fallback only;
- MuseTalk / LatentSync: deferred;
- final TTS / voice-clone integration: deferred;
- CUDA ONNX repair: deferred unless CPU becomes a practical blocker after quality is established.

## Reclaimable retired payload

Potential first cleanup candidate only if actual disk pressure appears:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Do not delete reflexively.

## Current exact gate

```text
existing WanGP Python + existing YOLOX/DWPose
    -> runtime functional PASS
    -> 5 s CPU pose smoke PASS
    -> visual pose overlay inspection NEXT
    -> full 6 fps normalized COCO WholeBody 133 pose track
    -> extract_behavior_profile.py
    -> status=complete manifest + motion_units.csv
    -> profile inspection
    -> new 4–5 s multi-unit behavioral driver
    -> installed Wan-Animate-2
```

Do not run Wan-Animate-2 before the complete behavior profile is inspected.
