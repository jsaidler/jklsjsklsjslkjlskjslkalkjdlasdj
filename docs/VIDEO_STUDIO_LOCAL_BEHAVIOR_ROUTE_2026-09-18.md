# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Status: **ACTIVE TECHNICAL DIRECTION / BEHAVIOR PROFILE IMPLEMENTATION STARTED**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`  
Preflight result: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`

## Problem being solved

The existing local Wan2.2-S2V benchmark proved that a generated person can look recognizably like João while still behaving like another person. The reason is architectural: that test received a still image plus audio, not João's real behavioral video.

The missing component is therefore not another prompt or more sampling steps. It is a local mechanism that turns João's real footage into a reusable **behavioral driver** for new speech.

The target is:

```text
João behavioral videos
        |
        v
persistent local behavior profile
        |
new João speech audio
        |
        v
new motion/performance in João's gesture language
        |
        v
local character/video renderer
        |
local lip-sync / face finishing when needed
        v
final video
```

The generated performance must be new. Replaying one fixed source clip is not sufficient.

## Research result — monolithic systems

### TAVR — technically exact, hardware-invalid

HeyGen Research released TAVR as open local code under Apache 2.0. It is not the HeyGen SaaS product. TAVR takes `ref.mp4 + target image + target audio` and is architecturally very close to the project requirement.

However the official repository states that inference was tested on a Hopper-class CUDA GPU with **at least 80 GB VRAM**, and FlashAttention 3 is the only supported attention backend. It is therefore not a rational first route for RTX 3060 12 GB.

Reference: `https://github.com/heygen-com/TAVR`

Classification:

**CORRECT CONDITIONING MODEL / LOCAL OPEN SOURCE / CURRENT HARDWARE FAIL.**

### EchoMimicV3-Flash / StableAvatar / LongCat Avatar

These fit some or all of the talking-avatar problem but their public pipelines are driven primarily by image + audio/text. They do not provide the required reusable João whole-body behavioral identity from the three supplied videos.

Classification:

**NOT THE BEHAVIORAL SOLUTION.**

### MimicTalk / Style-Talking

MimicTalk can train a person-specific expressive talking face from source video and can use optional style video; Style-Talking clones speaking style from reference video and target audio. These remain relevant for face/head expression but are not full upper-body co-speech gesture generators.

Classification:

**USEFUL FACE BRANCH / NOT COMPLETE BODY SOLUTION.**

## Research result — motion generation

### PersonaGesture / PersonaGest

Recent research directly formulates the desired problem: new speech plus a short reference motion clip from an unseen speaker should produce new co-speech gestures while preserving that speaker's gesture style.

At the time of this decision record, no reliable public implementation/checkpoint was found for immediate installation.

Classification:

**IDEAL RESEARCH DIRECTION / NOT ACTIONABLE YET.**

### ZeroEGGS

Ubisoft La Forge's ZeroEGGS is public and generates speech-driven gestures in the style of a short example motion clip. Code and pretrained models are available, but its style reference/output are BVH/3D motion rather than raw João video.

It remains a valid R&D fallback if video-to-motion retargeting becomes worthwhile.

Classification:

**ACTIONABLE R&D FALLBACK / NOT FIRST IMPLEMENTATION.**

## Renderer finding — reuse what is already installed

Wan-Animate-2 is the priority renderer because unlike the S2V benchmark it **directly consumes a driving video** and is designed to reproduce body movement/facial expression while preserving reference-character identity.

Official references:

- `https://github.com/Wan-Video/Wan-Animate-2`
- `https://docs.comfy.org/tutorials/video/wan/wan2-2-animate`

The project already has the large Animate-2 payload locally. The no-download preflight on 2026-09-18 confirmed:

- transformer present: `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — **30.538 GiB**;
- text encoder present: `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — **10.586 GiB**;
- VAE present: `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — **0.236 GiB**;
- native model code present: `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

Classification:

**INSTALLED RENDERER REUSE: PASS.**

Therefore:

**DO NOT DOWNLOAD VACE/MOTION MIRROR OR ANOTHER LARGE RENDERER BEFORE BUILDING AND TESTING THE BEHAVIOR PROFILE WITH INSTALLED WAN-ANIMATE-2.**

Motion Mirror / Wan2.1-VACE remains fallback only.

## Behavioral source library — PREFLIGHT PASS

All protected sources are present, readable and contain audio:

1. `VID_20260911_140124885.mp4` — 300.4 s, 3840x2160 HEVC — primary upper-body behavior library;
2. `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 — facial/microexpression evidence;
3. `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 — alternate gesture material, with object-occluded spans excluded where needed.

The generic 1080p H.264 derivative is also present locally and may be used as a convenient analysis/render source if needed; its historical provider-oriented filename has no architectural meaning.

## Selected architecture — behavioral driver synthesis

The first local implementation will not train a 14B avatar model on the source corpus. It will build a **behavior compiler** from João's own recorded movements.

### Persistent profile build

For each source video:

1. extract whole-body/hand/face pose descriptors for analysis;
2. extract local speech/prosody descriptors such as speech/pause, energy and reliable pitch/rhythm features;
3. split footage into short motion units around speech pauses and low-motion transition points;
4. store normalized start/end pose, head motion, hand activity, body activity, motion energy and source timing;
5. retain a reference to the original RGB span for every unit;
6. mark/exclude units with problematic foreground-object occlusion when relevant.

### New speech -> new behavioral driver

For new local speech audio:

1. divide the new audio into prosodic windows;
2. retrieve João motion units with compatible energy/pause/emphasis profile;
3. score transitions by pose continuity;
4. penalize repeated use of the same motion unit;
5. time-adjust only within conservative limits;
6. assemble a **new driving performance** from multiple João motion units;
7. attach/replace audio with the new target speech.

This is not a fixed replay. The useful property is that the gesture vocabulary comes from João's actual recorded behavior instead of a generic model's invented choreography.

Semantic transcript retrieval can be added later; the first gate uses prosody + pose continuity.

## Behavior-profile implementation — 2026-09-18

The first implementation is now versioned in `tools/video-studio/`.

### Strict local environment inspector

`inspect_local_behavior_tooling.ps1`

Purpose:

- resolve what `py -3.11` actually executes by checking the interpreter's own `sys.version_info`;
- inspect explicit Python candidates and selected existing AI runtimes without installing anything;
- report whether likely runtimes already contain useful dependencies such as ONNX Runtime, Torch, OpenCV or MediaPipe;
- search likely local AI roots for DWPose/whole-body/hand-pose assets and compatible directories;
- keep the scan bounded and targeted instead of blindly crawling the entire Z: drive;
- write local TXT/JSON evidence under the ignored `tools/video-studio/reports/` directory.

Mode is strictly:

**READ ONLY / NO DOWNLOAD / NO INSTALL / NO DELETE.**

### Persistent schema

`behavior_profile_schema_v1.json`

Schema id/version:

`behavior-profile/v1`

Every unit records at least:

- source file;
- start/end/duration;
- original RGB source span;
- start/end pose;
- head motion;
- left/right/combined hand activity;
- body activity;
- mean/peak/entry/exit motion energy;
- speech/pause classification and speech ratio;
- pause context around the boundaries;
- available prosody descriptors;
- boundary/transition quality.

### First extractor

`extract_behavior_profile.py`

Current scope is deliberately limited to the primary source first:

`VID_20260911_140124885.mp4`

Implementation choices:

- FFmpeg/ffprobe are the base media runtime;
- visual motion energy uses low-resolution grayscale frame differences so segmentation does not wait on a pose framework;
- prosody v1 uses local audio RMS/dBFS, normalized energy and speech/pause evidence;
- cuts prioritize **pause + low motion**, then target duration;
- default motion units target roughly 2.2 s with a bounded short-unit range;
- output is an inspectable `manifest.json` plus `motion_units.csv`;
- pose ingestion is backend-independent through normalized JSONL frames, allowing reuse of whichever local whole-body pose tooling the machine already has.

Pose is not optional for a valid profile gate. If the extractor is deliberately run with `--allow-missing-pose`, the manifest is marked:

`status=incomplete_pose`

That mode exists only to inspect segmentation/prosody. It must **not** be accepted as a behavioral-profile pass.

### Prosody scope v1

The currently implemented reliable descriptors are speech/pause, RMS dBFS and normalized audio energy. Pitch is intentionally `null` until a local dependency/backend is selected and validated. The schema already preserves the field so a later validated pitch implementation can populate it without changing the profile contract.

## Preflight result — 2026-09-18 23:45

Canonical preflight report:

`docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`

Local raw report:

`tools/video-studio/reports/local_behavior_route_preflight_20260918_234516.txt`

Result:

```text
BEHAVIOR SOURCES: PASS
WAN-ANIMATE-2 PAYLOAD: PASS
WAN-ANIMATE-2 NATIVE CODE: PASS
POSE TOOLING: NOT FOUND UNDER WAN ROOT
NEXT ROUTE GATE: BUILD BEHAVIOR PROFILE WITHOUT NEW LARGE RENDERER DOWNLOAD
```

### Pose tooling gap

No DWPose whole-body model was found **under the Wan root**. The preflight did not perform an exhaustive `Z:\AI` search, so absence is not yet proven globally.

The required next evidence is now produced by `inspect_local_behavior_tooling.ps1`. Only after its targeted no-download scan can the project decide whether pose tooling can be reused or a small dependency is genuinely missing.

If absent and required, enumerate the exact small component, source, license, size and destination before downloading.

A DWPose-L-class weight around ~350 MB remains acceptable in principle as a small supporting dependency if genuinely required; this is not authorization to download it before the local search result.

### Python warning

The preflight printed:

`Python 3.11: PASS / C:\Python314\python.exe / 3.14.3`

This is internally inconsistent. Do not consider Python 3.11 validated.

The new inspector fixes the diagnostic method by checking the actual resolved executable/version rather than trusting the launcher selector label. No interpreter is canonically selected until that script is run on the local machine.

### Disk pressure

Z: had **22.32 GB free** at preflight time.

A retired Hunyuan transformer remains reclaimable:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — **12.486 GiB**.

Do not delete it automatically as part of behavior-profile coding, but treat it as the first obvious retired payload if real storage pressure appears.

## Pixel generation gate

Priority renderer:

**installed Wan-Animate-2**.

The first renderer gate should be short, around **4–5 seconds**, with no dramatic wardrobe/scene change. It tests whether a synthesized João behavioral driver survives Animate-2 while preserving recognizable behavior and identity.

Do not run this gate until an inspectable **complete** behavior profile and motion-unit inventory exist.

## Mouth / speech synchronization — DEFERRED

Wan-Animate-2 will copy facial performance from the driving video, so recombined source-mouth motion will not necessarily match new audio.

Potential later local finishing stages:

- MuseTalk 1.5;
- LatentSync 1.5.

Do not install either until body/head behavior passes.

## Voice stage — DEFERRED

CosyVoice or another local voice-clone/TTS stage remains separate. For behavior-compiler engineering, an existing local speech WAV may be used as a mechanical target.

## Why this route remains first

It satisfies the project constraints:

- local/self-hosted;
- zero paid-service dependency;
- João's actual videos are the behavioral source;
- no prompt is asked to invent João's gestures;
- already-installed Wan-Animate-2 is reused before any large download;
- behavior, rendering, voice and lip sync remain separately diagnosable.

## Stop conditions

- Do not download another large renderer.
- Do not resume Wan S2V prompt acting as a substitute for behavioral conditioning.
- Do not install MuseTalk/LatentSync before the body/head gate.
- Do not claim a stitched RGB driver alone is the final product; it is a behavioral conditioning representation.
- Do not accept `incomplete_pose` as a valid behavior profile.
- Do not accept mere anatomical plausibility. João must recognize his own motion language.

## Immediate action — LOCKED

The schema and base extractor are implemented. Continue in this exact order:

1. run `tools/video-studio/inspect_local_behavior_tooling.ps1` on the local Windows machine;
2. establish the real Python interpreter candidates and targeted pose-tooling inventory from that report;
3. reuse compatible local whole-body/hand pose tooling if present;
4. if none exists, enumerate the smallest required local dependency before any download;
5. implement the selected pose adapter to the normalized JSONL pose-track contract;
6. build a **complete** profile for `VID_20260911_140124885.mp4`;
7. inspect `manifest.json` and `motion_units.csv` before any diffusion render;
8. only after profile validation, synthesize a new ~4–5 s driving performance from several João motion units;
9. then send that driver to the already-installed Wan-Animate-2.

No new large renderer download is allowed before this gate. Wan-Animate-2 must not be run yet.