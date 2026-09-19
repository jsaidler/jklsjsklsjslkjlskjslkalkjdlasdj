# Local Video Studio — Current Project State

Status date: **2026-09-19**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. `docs/NEXT_CHAT_HANDOFF_VIDEO_STUDIO_LOCAL_BEHAVIOR_2026-09-18.md`
6. `tools/video-studio/extract_dwpose_track.py`
7. `tools/video-studio/render_pose_overlay.py`
8. `tools/video-studio/run_behavior_pose_visual_gate.ps1`
9. `tools/video-studio/extract_behavior_profile.py`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Execution policy — LOCKED

The Video Studio is **100% local/self-hosted and zero-cost by default**.

Hard constraints:

- no hosted avatar/generation/training service;
- no SaaS/cloud inference API, credits or subscriptions;
- never upload João's video, voice or identity to third parties;
- do not download another large renderer while the behavior route is active;
- Wan S2V, H3, Hunyuan and HeyGen are historical/retired branches, not the next step;
- MuseTalk/LatentSync/CosyVoice remain deferred until the body/head behavioral gate passes.

## Active objective — LOCKED

Generate new video from new text/audio in which the result:

1. looks like João;
2. sounds like João;
3. chiefly **moves and reacts like João**.

Generic plausible presenter motion is a failure.

## Canonical architecture

```text
João behavioral videos
    -> local pose + prosody
    -> persistent motion-unit library from João's own footage

new local speech/audio
    -> prosodic windows
    -> retrieve/sequence compatible João motion units
    -> pose continuity + diversity
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A fixed driving clip is not sufficient.

## Canonical behavior sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

- `VID_20260911_140124885.mp4` — 300.352 s, 3840x2160 HEVC + audio — **primary torso/hands/posture/gesture source**;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 + audio — facial/microexpression source;
- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 + audio — alternate gesture/look source; object/occlusion spans excluded later.

## Installed Wan-Animate-2 — REUSE PASS

Already present:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

Do not invoke Wan-Animate-2 until a complete, inspected behavior profile exists.

## Local DWPose reuse — PASS

Present locally in WanGP:

- code: `Z:\AI\WanGP\preprocessing\dwpose`;
- detector: `Z:\AI\WanGP\ckpts\pose\yolox_l.onnx` — ~206.7 MB;
- whole-body model: `Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx` — ~128.2 MB;
- isolated runtime: `Z:\AI\WanGP\env_uv\Scripts\python.exe` — Python 3.11.14.

No DWPose download and no new Python are justified.

## Runtime probe — FUNCTIONAL PASS / CUDA ORT NOT VALIDATED

Probe executed 2026-09-19 01:41.

Confirmed:

- WanGP Python 3.11.14 runs;
- OpenCV / NumPy / ONNX Runtime / WanGP DWPose imports work;
- YOLOX detects the subject;
- DWPose returns `coco_wholebody_133`;
- one real source frame completed with no detector fallback.

Important CUDA result:

- ONNX Runtime advertises `TensorrtExecutionProvider`, `CUDAExecutionProvider`, `CPUExecutionProvider`;
- loading `onnxruntime_providers_cuda.dll` emitted a missing dependency error for `cublasLt64_13.dll` and CUDA/cuDNN prerequisites;
- therefore the probe's reported `CUDAExecutionProvider` must **not** be treated as proof that CUDA inference actually executed.

Classification:

- **DWPose functional runtime: PASS**;
- **DWPose ONNX CUDA acceleration: FAIL / not validated**.

Do not install CUDA components yet. CPU is sufficient to continue the quality gate.

## CPU pose smoke — PASS

A 5 s smoke was generated from 30.0–35.0 s of the primary source at 6 fps / analysis 960x540 using `CPUExecutionProvider`.

Observed summary:

```text
schema: coco_wholebody_133
frames: 30
last_timestamp_s: 34.833333
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.13263878929229625
onnx_provider: CPUExecutionProvider
elapsed_s: 26.750566244125366
frames_per_second_wall: 1.1214715877869776
```

Interpretation:

- temporal extraction/count: PASS;
- detector continuity over the smoke: PASS;
- no fallback frames: PASS;
- the aggregate mean score is recorded but is **not** used as a standalone quality threshold.

## Visual pose gate — NEXT / BLOCKING FULL PASS

Numeric summaries cannot prove anatomical correctness, hand consistency or absence of keypoint jumps. Before processing the full 300 s source, visually inspect the already-generated smoke track.

Versioned tools:

- `tools/video-studio/render_pose_overlay.py`;
- `tools/video-studio/run_behavior_pose_visual_gate.ps1`.

The visual gate renders an MP4 overlay from the existing JSONL. It does **not** rerun DWPose and does not call Wan-Animate-2.

Default input:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s.jsonl`

Default output:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s_overlay.mp4`

Human gate for this step:

- torso/arms follow the correct anatomy;
- left/right hands remain attached to the correct wrists;
- fingers/hand landmarks are plausible enough for behavioral descriptors;
- face landmarks remain on the face;
- no obvious frame-to-frame jumps, mirrored swaps or tracking of background objects.

Only after this visual gate passes is the full 6 fps pose extraction authorized.

## Behavior-profile implementation — ACTIVE

- `behavior_profile_schema_v1.json` — schema `behavior-profile/v1`;
- `extract_behavior_profile.py` — motion/prosody segmentation and profile builder;
- `extract_dwpose_track.py` — normalized COCO WholeBody 133 extractor;
- `render_pose_overlay.py` — visual QA overlay;
- `run_behavior_pose_visual_gate.ps1` — visual gate runner.

A pose-less run remains `status=incomplete_pose` and never passes the production gate.

## Disk pressure

Last measured Z: free ~22.32 GB.

Only if real space pressure appears, first retired cleanup candidate remains:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Do not delete it reflexively; the active route currently needs no large download.

## Historical renderer evidence

- Wan2.2-S2V 20-step: visual identity pass/near-pass, behavioral identity not tested, production fail for current objective;
- H3: functional pass, production visual/behavior fail;
- Hunyuan Avatar local 720p: functional runtime but severe offload/practicality fail;
- HeyGen/Avatar V: retired because hosted service violates project policy.

Do not reopen these branches without new technical evidence.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

1. pull `main`;
2. run `tools/video-studio/run_behavior_pose_visual_gate.ps1`;
3. open `pose_smoke_5s_overlay.mp4` and inspect body, hands, face and temporal stability;
4. if visual gate PASS, generate the full primary-source pose track at 6 fps;
5. feed the full track to `extract_behavior_profile.py` and require `status=complete`;
6. inspect `manifest.json` + `motion_units.csv`;
7. compose a new 4–5 s performance from multiple motion units;
8. only then invoke installed Wan-Animate-2.

Do not install/download another renderer, pose stack, lip-sync package, Python or CUDA dependency at this stage.
