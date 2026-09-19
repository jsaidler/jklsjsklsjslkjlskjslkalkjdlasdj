# Local Video Studio — Current Project State

Status date: **2026-09-19**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

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

- `VID_20260911_140124885.mp4` — 300.352 s, coded 3840x2160 with portrait display rotation — **primary torso/hands/posture/gesture source**;
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

- runtime: `Z:\AI\WanGP\env_uv\Scripts\python.exe` — Python 3.11.14;
- code: `Z:\AI\WanGP\preprocessing\dwpose`;
- detector: `Z:\AI\WanGP\ckpts\pose\yolox_l.onnx` — ~206.7 MB;
- whole-body model: `Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx` — ~128.2 MB.

No DWPose download and no new Python are justified.

## Runtime probe — FUNCTIONAL PASS / CUDA ORT NOT VALIDATED

Probe executed 2026-09-19 01:41.

Confirmed:

- WanGP Python 3.11.14 runs;
- OpenCV / NumPy / ONNX Runtime / WanGP DWPose imports work;
- YOLOX detects the subject;
- DWPose returns `coco_wholebody_133`;
- one real source frame completed with no detector fallback.

CUDA caveat:

- ONNX Runtime advertises TensorRT/CUDA/CPU;
- CUDA provider load emitted missing `cublasLt64_13.dll` plus CUDA/cuDNN dependency warnings;
- therefore requested `CUDAExecutionProvider` is not proof of actual CUDA execution.

Classification:

- **DWPose functional runtime: PASS**;
- **DWPose ONNX CUDA acceleration: FAIL / not validated**.

CPU is the current validated path. Do not install CUDA components yet.

## Orientation/preprocessing defect — FIXED

The first DWPose runs used coded dimensions `3840x2160` to choose analysis geometry even though FFmpeg autorotated the source to portrait display. That forced the displayed portrait frame into `960x540`, severely distorting João before pose inference.

`extract_dwpose_track.py` now reads stream rotation metadata, distinguishes coded vs display dimensions and derives analysis size from display geometry. For the primary source the correct analysis geometry is portrait, approximately `540x960`.

Classification:

**portrait display-orientation preprocessing: FIXED.**

## Visual gate history

### 30–35 s

Rejected only because João was holding a large object across the hands/torso. Not evidence against DWPose.

### C3 clean gate

Canonical clean interval: **88.7–93.7 s**, selected because both hands are free, gestures are active, and torso/wrists are unobstructed.

The first C3 overlay before the orientation fix was invalid because the portrait frame had been distorted to landscape analysis geometry.

After the orientation fix, the new uploaded C3 overlay is `540x960`, 30 frames at 6 fps and was inspected frame-by-frame.

Observed after correction:

- face landmarks stay on the face;
- shoulders, elbows, wrists and hips remain anatomically aligned;
- both hand skeletons follow the moving hands through open, closing, clasped and separated configurations;
- no subject switch was observed;
- no gross left/right swap or temporal pose jump was observed in the profile-relevant upper-body groups.

The overlay still shows distracting white lines toward the bottom of frame. Those are low-confidence/off-frame knee/ankle/foot landmarks plus visualization edges. They are not used by behavior-profile v1 upper-body descriptors.

Important behavior-profile confidence rule:

`extract_behavior_profile.py` uses `CONF = 0.20`, while the QA overlay was rendered with `min_score = 0.05`. Therefore many noisy lines visible in the overlay are intentionally excluded from actual behavior metrics.

Behavior-profile v1 pose groups are:

- head: keypoints 0–4;
- body: 5–12;
- left hand: 91–111;
- right hand: 112–132;
- low-confidence points below 0.20 are ignored when computing group centroids/activity.

Classification:

**C3 corrected upper-body visual pose gate: PASS.**

This authorizes full primary-source pose extraction.

## Full primary pose extraction — NEXT

Versioned runner:

`tools/video-studio/run_behavior_pose_full.ps1`

Defaults:

- source: primary 300.352 s video;
- 6 fps;
- long side 960;
- portrait-aware display geometry;
- `CPUExecutionProvider`;
- output: `Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`;
- summary: same path + `.summary.json`.

The runner invokes DWPose only. It does not run Wan-Animate-2.

After completion, inspect at minimum:

- frame count;
- display and analysis dimensions;
- provider;
- detector fallback count/ratio;
- mean keypoint score.

Do **not** build the behavior profile until that full extraction result has been reviewed.

## Behavior-profile tooling — ACTIVE

- `behavior_profile_schema_v1.json` — schema `behavior-profile/v1`;
- `extract_behavior_profile.py` — motion/prosody segmentation and profile builder;
- `extract_dwpose_track.py` — normalized COCO WholeBody 133 extractor, now portrait/display-rotation aware;
- `render_pose_overlay.py` — visual QA overlay;
- `sample_behavior_gate_candidates.py` — clean interval sampler;
- `run_behavior_pose_selected_gate.ps1` — selected C3 gate runner;
- `run_behavior_pose_full.ps1` — full primary pose runner.

A pose-less profile remains `status=incomplete_pose` and never passes the production gate.

## Known future cleanup/quality work

- object-occluded spans in behavior sources must be excluded or down-weighted before motion-unit retrieval;
- overlay visualization should not be confused with actual v1 metrics because it currently displays points down to 0.05 confidence and includes lower-body edges outside the active upper-body feature groups;
- CUDA ORT acceleration can be revisited only if CPU throughput becomes a practical blocker.

## Disk pressure

Last measured Z: free ~22.32 GB.

Only if real space pressure appears, first retired cleanup candidate remains:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Do not delete it reflexively; the active route currently needs no large download.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

1. pull `main`;
2. run `tools/video-studio/run_behavior_pose_full.ps1`;
3. paste the resulting summary/output;
4. review full-track integrity;
5. then run `extract_behavior_profile.py` with the full pose track and require `status=complete`;
6. inspect `manifest.json` + `motion_units.csv`;
7. exclude/down-weight occluded or unusable motion units;
8. compose a new 4–5 s performance from multiple motion units;
9. only then invoke installed Wan-Animate-2.

Do not install/download another renderer, pose stack, lip-sync package, Python or CUDA dependency at this stage.
