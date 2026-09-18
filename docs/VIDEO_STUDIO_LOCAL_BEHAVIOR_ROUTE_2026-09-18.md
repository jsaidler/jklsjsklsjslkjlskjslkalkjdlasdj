# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Status: **ACTIVE TECHNICAL DIRECTION / NO NEW LARGE DOWNLOAD YET**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

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

MimicTalk can train a person-specific expressive talking face from source video with roughly 8 GB VRAM at batch size 1 and can use an optional style video. Style-Talking clones speaking style from reference video and target audio.

These are relevant for face/head expression but are not full upper-body co-speech gesture generators.

Classification:

**USEFUL FACE BRANCH / NOT COMPLETE BODY SOLUTION.**

## Research result — motion generation

### PersonaGesture / PersonaGest

Recent research directly formulates the desired problem: new speech plus a short reference motion clip from an unseen speaker should produce new co-speech gestures while preserving that speaker's gesture style.

At the time of this decision record, no reliable public implementation/checkpoint was found for immediate installation. Do not build the project around an unavailable repository.

Classification:

**IDEAL RESEARCH DIRECTION / NOT ACTIONABLE YET.**

### ZeroEGGS

Ubisoft La Forge's ZeroEGGS is public and generates speech-driven gestures in the style of a short example motion clip. Code and pretrained models are available, but its style reference/output are BVH/3D motion rather than raw João video.

It is a valid future motion-model candidate if we add video-to-motion retargeting, but it adds an avoidable 3D conversion problem before we have tested a simpler route.

Reference: `https://github.com/ubisoft/ubisoft-laforge-ZeroEGGS`

Classification:

**ACTIONABLE R&D FALLBACK / NOT FIRST IMPLEMENTATION.**

## Renderer finding — reuse what is already installed

Wan-Animate-2 is especially important because unlike the S2V benchmark it **directly consumes a driving video**. The current Wan/ComfyUI implementation feeds the driving video's latents directly into the transformer rather than reducing them to a generic motion prompt. The model is explicitly designed to reproduce body movement and facial expression while preserving a reference character's identity.

Official references:

- `https://github.com/Wan-Video/Wan-Animate-2`
- `https://docs.comfy.org/tutorials/video/wan/wan2-2-animate`

The project already has the large `wan_animate_2_bf16.safetensors` payload under the WanAnimate2 installation. Therefore **do not download VACE/Motion Mirror yet**. First determine whether the installed Animate-2 route can be reused as the pixel renderer.

Motion Mirror / Wan2.1-VACE remains a fallback renderer because its 1.3B path can run around 8–9 GB VRAM on Windows, but it would require roughly another 20 GB model cache and its 1.3B identity fidelity is explicitly described as loose. That download is not justified before exhausting the already-installed Animate-2 path.

## Selected architecture — behavioral driver synthesis

The first local implementation will not try to train a 14B avatar model on eleven minutes of João footage. It will build a **behavior compiler** from João's own recorded movements.

### Persistent profile build

For each source video:

1. extract whole-body/hand/face pose descriptors for analysis;
2. extract local speech/prosody descriptors (speech/pause, energy, pitch/rhythm where reliable);
3. split the footage into short motion units around speech pauses and low-motion transition points;
4. store normalized start/end pose, head motion, hand activity, motion energy and source timing;
5. retain the original RGB clip for every unit.

Initial source priority:

1. `VID_20260911_140124885.mp4` — primary upper-body behavior library;
2. `VID_20260819_124008056.mp4` — facial/microexpression evidence;
3. `SIENA_BRUTO.mp4` — alternate gesture material, excluding object-occluded spans where needed.

### New speech -> new behavioral driver

For new local speech audio:

1. divide the new audio into prosodic windows;
2. retrieve João motion units with compatible energy/pause/emphasis profile;
3. score transitions by pose continuity so cuts happen where hands/head/body can connect naturally;
4. penalize repeated use of the same motion unit;
5. time-adjust only within conservative limits;
6. assemble a **new driving video** from multiple João motion units;
7. replace its audio with the new target speech.

This is not a fixed replay: the driving performance is newly assembled from João's own behavioral vocabulary. It has the useful property that the gestures are literally João's rather than a generic model's invented choreography.

Semantic retrieval can be added later by locally transcribing/indexing the source corpus, but it is not required for the first behavioral gate. Prosody + continuity is sufficient to test whether this direction preserves recognizable mannerisms.

## Pixel generation

Priority renderer:

**installed Wan-Animate-2**

Inputs:

- target João look/reference image;
- newly synthesized João driving video;
- scene/viewpoint prompt where supported.

The first renderer gate should be short, around 4–5 seconds, and should not change wardrobe/scene dramatically. It tests whether the synthesized driver survives Animate-2 without losing recognizable behavior.

## Mouth / speech synchronization

Wan-Animate-2 copies facial performance from the driving video; the source mouth motion will not necessarily match new target audio after motion-unit recombination.

Therefore lip synchronization is a separate local finishing stage.

Current lightweight candidates:

- **MuseTalk 1.5** — MIT code, Windows instructions, tested as low as 4 GB VRAM; modifies the face region from target audio;
- **LatentSync 1.5** — local audio-driven lip sync, approximately 8 GB VRAM minimum in the official release.

Do not download either until the behavioral-driver + Animate-2 gate works. There is no value fixing lips on a body performance that still feels like another person.

## Voice stage

CosyVoice or another local voice-clone/TTS stage remains separate. It provides the final target audio that the behavior compiler analyzes and the lip-sync stage follows.

For initial engineering of the behavior compiler, an existing local speech WAV can be used as a mechanical target; voice quality is not part of that gate.

## Why this route is first

It satisfies all current constraints:

- local/self-hosted;
- zero paid-service dependency;
- uses João's actual videos as behavioral material;
- does not ask a text prompt to invent João's gestures;
- reuses the already-installed Wan-Animate-2 renderer before downloading another large model;
- separates behavior generation, pixel rendering, voice and lip sync so each failure can be diagnosed independently;
- leaves room to replace the retrieval motion generator later with PersonaGesture/ZeroEGGS/a custom learned model without replacing the rest of the Video Studio.

## Stop conditions

Do not download another 14B renderer while the installed Animate-2 route is unaudited.

Do not install MuseTalk/LatentSync until body/head behavior survives the renderer gate.

Do not claim that a stitched RGB driver alone is the final product; it is an internal motion representation used to condition the renderer.

Do not accept a final result merely because it is anatomically plausible. João must recognize his own motion language.

## Immediate action

Run a **no-download local preflight** to determine exactly what Animate-2, DWPose/pose tooling and reusable runtime pieces are already present on `Z:\AI` before modifying the installation or downloading weights.

Repository tool: `tools/video-studio/preflight_local_behavior_route.ps1`.
