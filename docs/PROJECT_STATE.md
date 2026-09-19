# Local Video Studio — Current Project State

Status date: **2026-09-19**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Execution policy — LOCKED

The Video Studio remains **100% local/self-hosted and zero-service-cost**.

Hard constraints:

- no hosted avatar/generation/training service;
- no SaaS/cloud inference API, credits or subscriptions;
- never upload João's video, voice or identity to third parties;
- do not download another large renderer while the behavior route is active;
- Wan S2V, H3, Hunyuan and HeyGen remain historical/retired branches;
- MuseTalk/LatentSync/CosyVoice remain deferred until behavioral body/head validation passes;
- no new Python/DWPose/CUDA installation while the validated local route works.

## Active objective — LOCKED

Generate new video from new text/audio in which the result:

1. looks like João;
2. sounds like João;
3. chiefly **moves and reacts like João**.

Generic plausible presenter motion is a failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior profiles / motion units
    -> unified persistent João motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve/sequence compatible motion units across sources
    -> pose continuity + diversity + source-quality constraints
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A fixed source clip is not sufficient. A single source video is also **not** the final behavior library.

## Canonical behavior sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

- `VID_20260911_140124885.mp4` — 300.352 s, coded 3840x2160 with portrait display rotation — **primary torso/hands/posture/gesture source**;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 + audio — **facial/head/microexpression source**;
- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 + audio — **additional gesture/posture source**, with object/occluded spans excluded or down-weighted.

Current work processes the first video to validate the complete profile path. After that profile is inspected, the same pipeline must process the other two sources and then build a unified library while preserving each unit's source/timestamps.

## Installed Wan-Animate-2 — REUSE PASS

Already present:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

Do not invoke Wan-Animate-2 until behavior-profile inventory and synthesis are validated.

## Local DWPose reuse — PASS

Validated local stack:

- runtime: `Z:\AI\WanGP\env_uv\Scripts\python.exe` — Python 3.11.14;
- code: `Z:\AI\WanGP\preprocessing\dwpose`;
- detector: `Z:\AI\WanGP\ckpts\pose\yolox_l.onnx`;
- whole-body model: `Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx`.

DWPose functional runtime: **PASS**.

ONNX CUDA acceleration remains **not validated** because `cublasLt64_13.dll` was missing when CUDA EP initialized. CPU is the validated route; do not repair CUDA yet.

## Portrait orientation defect — FIXED

The primary file is coded landscape but displayed portrait via rotation metadata. Earlier pose preprocessing used coded dimensions while FFmpeg autorotated, causing a portrait frame to be squeezed to `960x540`.

`extract_dwpose_track.py` now:

- reads stream rotation metadata;
- distinguishes coded from display dimensions;
- derives analysis geometry from display dimensions.

Correct primary pose analysis geometry: **540x960**.

The same class of bug was also found in `extract_behavior_profile.py`: motion energy previously forced every source to `128x72`. It is now display-orientation aware and preserves aspect ratio with a 128 px long side. For the portrait primary source, motion analysis is **72x128**.

## Visual pose gate — PASS

Canonical clean interval: **C3 = 88.7–93.7 s**.

After the portrait fix, the corrected 30-frame / 6 fps overlay was inspected.

Observed:

- face landmarks stay on face;
- shoulders/elbows/wrists/hips remain anatomically aligned;
- both hand skeletons follow the gestures;
- no subject switch;
- no gross left/right swap or upper-body temporal jump.

QA overlay displayed points at score >= 0.05; behavior-profile v1 metrics use `CONF = 0.20`. v1 active groups are head 0–4, body 5–12, left hand 91–111, right hand 112–132. Noisy low-confidence lower-body/off-frame lines visible in QA are excluded from these metrics.

Classification: **C3 corrected upper-body visual pose gate PASS.**

## Full primary pose extraction — PASS

Completed on 2026-09-19 with the corrected portrait geometry.

Result:

```text
source_duration_s: 300.352
coded: 3840x2160
display: 2160x3840
rotation_degrees: 90
sample_fps: 6.0
analysis: 540x960
frames: 1801
last_timestamp_s: 300.0
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.7549247491487903
onnx_provider: CPUExecutionProvider
elapsed_s: 2780.1648166179657
frames_per_second_wall: 0.6478033205926593
```

Track:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl`

Summary:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl.summary.json`

Interpretation:

- full decode/sample path: PASS;
- correct display orientation: PASS;
- detector continuity: PASS, **0/1801 fallback**;
- aggregate keypoint confidence: strong at **0.7549**;
- combined with the already-passed clean visual gate, the full primary pose track is authorized for behavior-profile construction.

## Behavior-profile v1 — BUILD NEXT

Core extractor:

`tools/video-studio/extract_behavior_profile.py`

Current corrected behavior analysis:

- pose: external normalized `coco_wholebody_133` track;
- pose confidence floor: 0.20;
- motion energy: FFmpeg grayscale, 6 fps, aspect-ratio-preserving 128 px long side;
- primary portrait source motion geometry: **72x128**;
- audio/prosody v1: mono 16 kHz, 50 ms RMS/dBFS + normalized energy;
- segmentation target ~2.2 s, bounded 0.8–3.8 s, preferring pause + low motion boundaries;
- pitch remains intentionally null in v1.

New versioned tools:

- `tools/video-studio/inspect_behavior_profile.py` — dependency-free structural/inventory inspector;
- `tools/video-studio/run_behavior_profile_primary.ps1` — builds the primary complete profile and immediately inspects it.

Expected outputs:

- `manifest.json`;
- `motion_units.csv`;
- `profile_inspection.json`.

A valid first profile must have `status=complete`, continuous source coverage, valid COCO WholeBody 133 pose snapshots and usable activity descriptors. Structural PASS does **not** yet mean the entire behavioral library is production-ready: occluded/object spans still require quality annotation, and the other two source videos still need processing.

## Multi-video library requirement — LOCKED

The first 300 s profile is a validation milestone, not the final João model.

After primary-profile inspection:

1. process `VID_20260819_124008056.mp4` through the same validated route, emphasizing facial/head behavior;
2. process `SIENA_BRUTO.mp4`, with occlusion/object quality exclusions;
3. preserve source ID and timestamps for every motion unit;
4. build a unified searchable library;
5. allow retrieval across all sources rather than privileging a single recording blindly.

Source roles may be weighted differently; the three videos are not assumed equivalent.

## Known quality work after profile build

- identify and mark object-occluded/unusable spans;
- inspect motion-unit duration/class distribution and activity coverage;
- later improve facial descriptors beyond v1 head points 0–4 if evidence shows this is necessary;
- repair CUDA ORT only if CPU processing becomes a meaningful practical blocker.

## Disk pressure

Last measured Z: free ~22.32 GB.

Retired cleanup candidate only if actual space pressure appears:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Do not delete reflexively.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

1. pull `main`;
2. run `tools/video-studio/run_behavior_profile_primary.ps1`;
3. paste the final inspection output;
4. inspect primary `manifest.json` / motion-unit inventory;
5. add/validate quality exclusions for unusable source spans;
6. process the other two behavior videos with the validated pipeline;
7. unify the motion-unit library;
8. synthesize a new 4–5 s multi-source behavioral driver;
9. only then invoke installed Wan-Animate-2.
