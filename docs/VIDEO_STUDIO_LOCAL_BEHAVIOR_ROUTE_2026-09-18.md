# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Status: **ACTIVE TECHNICAL DIRECTION / PREFLIGHT PASS / BEHAVIOR PROFILE NEXT**

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

Before downloading anything:

1. search likely existing local AI roots for DWPose/whole-body pose assets and compatible runtime;
2. reuse existing tooling if present;
3. if absent and required, enumerate the exact small component, source, license, size and destination before downloading.

A DWPose-L-class weight around ~350 MB is acceptable as a small supporting dependency if genuinely required; it is not a reason to introduce another large renderer.

### Python warning

The preflight printed:

`Python 3.11: PASS / C:\Python314\python.exe / 3.14.3`

This is internally inconsistent. Do not consider Python 3.11 validated. Resolve the intended interpreter/venv explicitly before adding new Python pose/prosody dependencies.

### Disk pressure

Z: had **22.32 GB free** at preflight time.

A retired Hunyuan transformer remains reclaimable:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — **12.486 GiB**.

Do not delete it automatically as part of behavior-profile coding, but treat it as the first obvious retired payload if real storage pressure appears.

## Pixel generation gate

Priority renderer:

**installed Wan-Animate-2**.

The first renderer gate should be short, around **4–5 seconds**, with no dramatic wardrobe/scene change. It tests whether a synthesized João behavioral driver survives Animate-2 while preserving recognizable behavior and identity.

Do not run this gate until an inspectable behavior profile and motion-unit inventory exist.

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
- Do not accept mere anatomical plausibility. João must recognize his own motion language.

## Immediate action — LOCKED

Build the first **behavior-profile / motion-unit extractor** under `tools/video-studio/`.

Order:

1. resolve the Python interpreter inconsistency;
2. perform a targeted no-download search for reusable whole-body pose tooling in existing local AI roots;
3. define the persistent behavior-profile/motion-unit schema;
4. implement extraction first for `VID_20260911_140124885.mp4`;
5. generate an inspectable manifest/inventory before any diffusion render;
6. only after the profile is validated, synthesize a new ~4–5 s driving performance and send that to installed Wan-Animate-2.

No new large renderer download is allowed before this gate.