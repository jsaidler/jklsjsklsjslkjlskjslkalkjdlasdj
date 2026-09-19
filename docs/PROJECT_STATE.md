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

- `VID_20260911_140124885.mp4` — 300.352 s, coded 3840x2160 HEVC + audio, displayed portrait by rotation metadata — **primary torso/hands/posture/gesture source**;
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

## Initial CPU smoke — TECHNICAL PASS, QUALITY EVIDENCE INVALIDATED BY ORIENTATION BUG

The earlier 30–35 s smoke produced 30/30 frames and zero detector fallback, but used analysis dimensions 960x540 derived from the **coded** 3840x2160 stream dimensions.

The source is actually displayed portrait through rotation metadata. FFmpeg autorotated the decoded frames, after which the pipeline forced them into 960x540. Therefore DWPose inferred on a severely distorted portrait subject.

The earlier numeric smoke remains evidence that the local runtime executes, but it is **not** valid pose-quality evidence.

## First visual gate — REJECTED AS SAMPLE

30–35 s was already rejected because João was holding a large object that occluded both hands and crossed the torso. This was not a DWPose failure.

## Candidate sampler — COMPLETE

The source-only contact sheet sampled eight 5-second candidate windows. Canonical clean interval:

**C3 = 88.7 s → 93.7 s.**

Why C3:

- both hands free and visible;
- meaningful arm/hand motion;
- torso and wrists unobstructed;
- no held object crossing the body;
- stronger tracking challenge than quieter candidates.

## Selected C3 visual gate — FAIL / PIPELINE ORIENTATION DEFECT IDENTIFIED

The uploaded C3 overlay was inspected frame-by-frame.

Observed failure:

- body skeleton lines repeatedly cross the face and torso instead of following shoulders/elbows/wrists;
- face landmarks are geometrically unstable/misplaced;
- some hand landmarks are locally plausible, but global body geometry is not usable;
- the failure persists across the 5-second clean interval and cannot be attributed to object occlusion.

Root cause identified in `extract_dwpose_track.py`:

1. `ffprobe` returned coded dimensions 3840x2160;
2. the extractor computed analysis size 960x540 from those coded dimensions;
3. FFmpeg autorotated the source to portrait during decode;
4. the already-rotated portrait frame was then forcibly scaled to 960x540 before YOLOX/DWPose;
5. DWPose therefore saw a heavily squashed subject.

Classification:

**C3 VISUAL GATE: FAIL DUE TO PREPROCESSING ORIENTATION BUG, NOT YET A DWPose MODEL FAIL.**

Full 300 s extraction remains blocked.

## Orientation fix — IMPLEMENTED / RERUN NEXT

`tools/video-studio/extract_dwpose_track.py` now:

- reads rotation from ffprobe stream side-data or `rotate` tag;
- distinguishes coded dimensions from display dimensions;
- swaps width/height for 90°/270° display rotation;
- computes analysis dimensions from the **display orientation** used by FFmpeg autorotation;
- records `coded_width`, `coded_height`, `display_width`, `display_height`, and `rotation_degrees` in the summary.

For this source, the corrected gate is expected to analyze portrait frames at approximately **540x960**, not 960x540.

The same versioned runner remains the next action:

`tools/video-studio/run_behavior_pose_selected_gate.ps1`

It overwrites the C3 JSONL/summary/overlay with the corrected extraction.

Required rerun check:

- summary must report portrait `analysis_width`/`analysis_height` consistent with display orientation;
- then visually inspect the new overlay for torso/arms, wrists/hands/fingers, face, left/right consistency and temporal stability.

Only a corrected visual PASS authorizes the full 300 s extraction.

## Behavior-profile tooling — ACTIVE

- `behavior_profile_schema_v1.json` — schema `behavior-profile/v1`;
- `extract_behavior_profile.py` — motion/prosody segmentation and profile builder;
- `extract_dwpose_track.py` — normalized COCO WholeBody 133 extractor with display-rotation handling;
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
2. rerun `tools/video-studio/run_behavior_pose_selected_gate.ps1` on the same C3 window;
3. confirm the summary reports portrait analysis dimensions (expected ~540x960 for this source);
4. upload the regenerated C3 overlay;
5. inspect corrected pose geometry;
6. only after visual PASS, generate the full 6 fps primary-source pose track;
7. build `status=complete` behavior profile and inspect `manifest.json` + `motion_units.csv`;
8. compose a new 4–5 s performance from multiple motion units;
9. only then invoke installed Wan-Animate-2.

Do not install/download another renderer, pose stack, lip-sync package, Python or CUDA dependency at this stage.
