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

Do not install CUDA components yet. CPU is sufficient to continue the quality gate.

## CPU pose smoke — TECHNICAL PASS

5 s smoke from 30.0–35.0 s, 6 fps, 960x540, `CPUExecutionProvider`:

```text
frames: 30
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.13263878929229625
elapsed_s: 26.750566244125366
frames_per_second_wall: 1.1214715877869776
```

Interpretation:

- temporal extraction/count: PASS;
- detector continuity: PASS;
- no fallback frames: PASS;
- aggregate score is recorded but is not a standalone quality threshold.

## First visual gate — REJECTED AS SAMPLE, NOT AS DWPose

The overlay for 30–35 s was rendered and inspected. João is holding a large object through most of the window. The object heavily occludes both hands and crosses the torso region.

Classification:

**30–35 s VISUAL GATE SAMPLE: REJECTED DUE TO OBJECT OCCLUSION.**

This is **not** a DWPose failure. Do not use this interval as evidence for or against pose quality.

## Candidate sampler — COMPLETE

The source-only contact sheet sampled eight 5-second candidate windows. It was visually inspected.

Selected clean gate:

**C3 = 88.7 s → 93.7 s.**

Why C3:

- both hands are free and visible;
- there is meaningful arm/hand motion across the window;
- torso and wrists are unobstructed;
- no held object crosses the body;
- framing provides a stronger tracking challenge than quieter candidates.

C2 was usable but less demanding. C3 is the canonical visual gate interval.

## Selected clean visual gate — NEXT / BLOCKING FULL PASS

Versioned runner:

`tools/video-studio/run_behavior_pose_selected_gate.ps1`

Defaults:

- start: 88.7 s;
- duration: 5.0 s;
- sample rate: 6 fps;
- provider: CPU;
- analysis resolution inherited from `extract_dwpose_track.py` (960 px long side);
- track: `Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\selected_gate\pose_gate_c3_88p7_93p7_coco133.jsonl`;
- overlay: `Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\selected_gate\pose_gate_c3_88p7_93p7_overlay.mp4`.

The runner performs only:

1. 5 s DWPose CPU extraction for C3;
2. overlay rendering from that track.

It does **not** run Wan-Animate-2.

Human inspection must validate torso/arms, wrists/hands/fingers, face, left/right consistency and temporal stability. Only a visual PASS authorizes full 300 s extraction.

## Behavior-profile tooling — ACTIVE

- `behavior_profile_schema_v1.json` — schema `behavior-profile/v1`;
- `extract_behavior_profile.py` — motion/prosody segmentation and profile builder;
- `extract_dwpose_track.py` — normalized COCO WholeBody 133 extractor;
- `render_pose_overlay.py` — visual QA overlay;
- `sample_behavior_gate_candidates.py` — clean interval sampler;
- `run_behavior_gate_candidate_sampler.ps1` — sampler runner;
- `run_behavior_pose_selected_gate.ps1` — selected C3 extract+overlay runner.

A pose-less run remains `status=incomplete_pose` and never passes the production gate.

## Disk pressure

Last measured Z: free ~22.32 GB.

Only if real space pressure appears, first retired cleanup candidate remains:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Do not delete it reflexively; the active route currently needs no large download.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

1. pull `main`;
2. run `tools/video-studio/run_behavior_pose_selected_gate.ps1`;
3. upload `pose_gate_c3_88p7_93p7_overlay.mp4`;
4. inspect the selected clean gate visually;
5. only after visual PASS, generate the full 6 fps primary-source pose track;
6. build `status=complete` behavior profile and inspect `manifest.json` + `motion_units.csv`;
7. compose a new 4–5 s performance from multiple motion units;
8. only then invoke installed Wan-Animate-2.

Do not install/download another renderer, pose stack, lip-sync package, Python or CUDA dependency at this stage.
