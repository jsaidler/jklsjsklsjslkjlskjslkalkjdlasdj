# Local Video Studio — Current Project State

Status date: **2026-09-19**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. `docs/NEXT_CHAT_HANDOFF_VIDEO_STUDIO_LOCAL_BEHAVIOR_2026-09-18.md`
6. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
7. `docs/VIDEO_STUDIO.md`
8. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
9. `tools/video-studio/inspect_local_behavior_tooling.ps1`
10. `tools/video-studio/probe_wangp_dwpose_runtime.ps1`
11. `tools/video-studio/extract_dwpose_track.py`
12. `tools/video-studio/extract_behavior_profile.py`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Execution policy — LOCKED

The Video Studio is **local/self-hosted and zero-cost by default**.

Hard constraints:

- no external hosted generation/training/avatar platform;
- no SaaS/cloud inference API;
- no credit-based or subscription generation service;
- no paid tool/model/license unless João explicitly changes this rule in advance;
- do not upload João's personal video/voice/identity material to a third-party avatar/generation provider;
- internet use is allowed only for research/documentation and download of freely usable local components;
- do not download another large renderer before the active behavior gate passes.

HeyGen/Avatar V is retired. Wan S2V, H3 and Hunyuan are historical diagnostic branches, not the next step. MuseTalk/LatentSync and CosyVoice remain deferred.

## Active objective — LOCKED

Generate new videos from new text/audio in which the result:

1. looks like João;
2. sounds like João;
3. **moves and reacts like João**.

Behavioral identity is a hard requirement. Generic plausible motion is a failure.

## Canonical architecture

```text
João behavioral videos
    -> local pose + prosody analysis
    -> persistent library of João motion units

new local speech/audio
    -> prosody windows
    -> motion-unit retrieval + sequencing
    -> pose continuity + diversity
    -> NEW driving performance composed from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A fixed source driving clip is not sufficient.

## Behavioral source library

Canonical originals:

- `VID_20260911_140124885.mp4` — 300.4 s, 3840x2160 HEVC + audio — **primary upper-body/gesture source**;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 + audio — facial/microexpression source;
- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 + audio — alternate gesture/look source with problematic object-occluded spans excluded later.

Primary source path:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

## Installed Wan-Animate-2 — REUSE PASS

Already present:

- transformer: `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- text encoder: `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- VAE: `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- native code: `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

Do not run it until a complete inspectable behavior profile exists.

## Behavior-profile implementation — ACTIVE

Versioned tooling:

- `behavior_profile_schema_v1.json` — persistent `behavior-profile/v1` contract;
- `extract_behavior_profile.py` — renderer-independent motion-unit segmentation/prosody/profile builder;
- `inspect_local_behavior_tooling.ps1` — bounded no-download local inventory;
- `probe_wangp_dwpose_runtime.ps1` — exact WanGP/DWPose runtime validation, including one real frame;
- `extract_dwpose_track.py` — converts the primary source to normalized `coco_wholebody_133` JSONL using the existing WanGP DWPose stack;
- `run_behavior_pose_smoke.ps1` — short pose-only smoke test; does not call Wan-Animate-2.

`extract_behavior_profile.py` stores source/timestamps/RGB span, start/end pose, head/hand/body activity, motion energy, speech/pause descriptors, available prosody and transition quality. Runs without pose are explicitly `status=incomplete_pose` and do **not** pass the gate.

## Machine-local tooling result — 2026-09-19 00:40

The corrected bounded inspector completed.

### Windows launcher

```text
py launcher: c:\windows\py.exe
py -3.11: NOT RESOLVED
```

Registered launcher inventory showed Python 3.7 and `C:\Python314\python.exe`; there is no launcher-registered Python 3.11. Therefore the old preflight label claiming `Python 3.11 PASS / C:\Python314\python.exe / 3.14.3` is definitively invalid.

**Do not install Python 3.11 from this fact.**

### Existing WanGP runtime evidence

The project already created and previously validated the isolated WanGP environment at:

`Z:\AI\WanGP\env_uv\Scripts\python.exe`

Historical validated runtime from the Hunyuan branch:

- Python 3.11.14;
- Torch 2.10.0+cu130;
- CUDA 13.0;
- WanGP v13.02.

The existing Hunyuan runner already hardcodes this exact interpreter path. The current active branch must verify that environment still exists and can execute DWPose; it must not reinstall Python first.

### Pose tooling — REUSE FOUND / NO DOWNLOAD REQUIRED

Targeted local search found the complete WanGP DWPose assets:

- code: `Z:\AI\WanGP\preprocessing\dwpose`;
- whole-body model: `Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx` — 128.2 MB;
- person detector: `Z:\AI\WanGP\ckpts\pose\yolox_l.onnx` — 206.7 MB.

Classification:

**POSE TOOLING PAYLOAD REUSE: PASS.**

There is no justification to download DWPose-L or another pose package.

The upstream WanGP implementation uses OpenCV + NumPy + ONNX Runtime and its requirements include OpenCV and ONNX Runtime GPU. The new project adapter consumes the original COCO WholeBody 133 output rather than WanGP's display-oriented OpenPose remapping, preserving the standard groups used by the behavior schema:

- body: 0–16;
- feet: 17–22;
- face: 23–90;
- left hand: 91–111;
- right hand: 112–132.

## Next runtime gate — LOCKED

Before a full 300 s pose pass, run the targeted runtime probe:

`tools/video-studio/probe_wangp_dwpose_runtime.ps1`

It validates:

- `Z:\AI\WanGP\env_uv\Scripts\python.exe`;
- `cv2`, NumPy and ONNX Runtime imports;
- available ONNX providers;
- both existing ONNX models;
- actual detector + 133-keypoint inference on one frame from the primary source.

No download/install/model mutation occurs.

If this passes, run `run_behavior_pose_smoke.ps1` for a short ~5 s pose track. Only after the smoke result is credible should the full 6 fps pose track be generated for the complete source.

## Disk pressure

Last measured Z: free space: ~22.32 GB.

Retired first cleanup candidate if genuinely needed:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Do not delete it reflexively. The active DWPose route requires no large download and therefore does not currently justify cleanup.

## Historical renderer evidence

- Wan2.2-S2V 20-step: visual identity strong, behavioral identity not tested, production fail for actual objective.
- H3: functional pass, production visual/behavioral fail.
- Hunyuan Avatar 720p local: functional runtime pass, no visual verdict, practicality fail on RTX 3060 12 GB.
- HeyGen/Avatar V: retired because external hosted service violates policy.

Do not reopen these branches without new technical evidence.

## Quality gate — LOCKED

The human gate remains:

> this does not merely look like João; it moves and reacts like João.

## Immediate next action

1. pull `main`;
2. run `probe_wangp_dwpose_runtime.ps1`;
3. if PASS, run the short `run_behavior_pose_smoke.ps1`;
4. inspect keypoint count, provider, detection/fallback rate and confidence;
5. then generate the full 6 fps pose track for `VID_20260911_140124885.mp4`;
6. feed that full track to `extract_behavior_profile.py` and require `status=complete`;
7. inspect `manifest.json` + `motion_units.csv`;
8. only after profile validation, compose a new 4–5 s performance from multiple units;
9. only then run installed Wan-Animate-2.

Do not download another renderer, DWPose package, lip-sync package or new Python environment at this stage.
