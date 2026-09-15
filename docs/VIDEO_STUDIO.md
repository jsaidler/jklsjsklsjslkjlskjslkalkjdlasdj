# Local Video Studio — canonical architecture

Status date: **2026-09-15**  
Status: **ACTIVE / MVP IMPLEMENTATION**

Canonical cross-chat state: `docs/PROJECT_STATE.md`.

## Objective

Create short, realistic videos of the user without requiring a new camera recording for each publication.

Normal input:

`written dialogue + target scene + optional clothing/framing`

Persistent profile input:

`cropped identity references + voice reference`

Normal output:

`vertical MP4 with the user's preserved identity, cloned/referenced voice, new lip-synced dialogue, autonomous body motion and the requested scene`

Target program duration is up to approximately one minute. One minute is assembled from H3-safe short shots rather than generated as one continuous diffusion sequence.

## Canonical architecture

```text
Local web UI (127.0.0.1:8765)
        |
        v
Video Studio orchestrator
        |
        +-- profile: identity crops + voice reference
        +-- script segmentation
        +-- scene/appearance/framing prompt compiler
        +-- MiniMax H3 API graph builder
        +-- serial GPU job queue
        +-- run evidence/manifest store
        |
        v
Existing ComfyUI portable @ Z:\AI\MiniMaxH3
        |
        v
MiniMax H3 Ref2VA
        |
        +-- native generated video
        +-- native generated voice/audio
        |
        v
FFmpeg final assembly
        |
        v
Z:\AI\MiniMaxH3\VideoStudioRuns\<job>\video_studio_<job>.mp4
```

ComfyUI is an inference runtime, not the normal authoring UI. The user should not need to understand, repair or operate the node graph for routine jobs.

## Persistent profile

Current validated profile inputs:

- `joao_id_face.png`
- `joao_id_shoulders.png`
- `joao_id_upperbody.png`
- `joao_ref_voice.wav`

The three images intentionally contain progressively more anatomy while minimizing scene/background authority.

This separation is a production rule: full-frame identity references caused H3 to reproduce the original room even when the prompt requested a new environment. Cropped references removed that coupling.

## Prompt contract

Every production prompt must make reference roles explicit:

- `<Picture 1..N>` = **identity only**;
- `<Audio 1>` = **voice identity only**;
- no normal `<Video 1>` driving reference;
- scenario text = authority for environment;
- optional appearance text = authority for clothing;
- framing preset = authority for camera crop;
- H3 generates body performance autonomously.

Identity prompt language explicitly excludes background, room, furniture, windows, bottles, equipment, colors and lighting from the reference images.

Dialogue is encoded as:

```text
<d>[Portuguese] ...</d>
```

The user has explicitly judged the generated voice from the validation run as good.

## Engine

Active engine: **MiniMax H3 Ref2VA**.

Installed production payload:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors`
- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`

Generation is 24 fps. Production vertical canvas is currently `768×1344`.

## Production preset

Current default is **Turbo 4-step**, not because it is theoretically maximal quality but because this exact use case passed the practical validation gate:

- recognizable/stable identity;
- user-approved voice;
- lip synchronization;
- autonomous motion without driving video;
- new scene separated from identity-reference backgrounds.

Preset:

- 768×1344;
- 4 steps;
- `res_multistep`;
- `simple` scheduler;
- Ref2V Turbo LoRA strength 1.0;
- `ref_image_size=max`;
- MiniMax H3 sigma shifts video/audio 12/3.

Base 20- and 50-step modes remain available as controlled quality experiments. The historical 2026-09-08 game-motion result that rejected Turbo4 cannot be generalized to this different talking-video task.

## Script segmentation

The orchestrator estimates speech duration at roughly 2.2 words/second plus headroom and keeps an individual generated shot at <= ~12.5 seconds.

For a longer script it:

1. splits on sentence boundaries;
2. packs sentences within the shot budget;
3. breaks oversized sentences when required;
4. computes a target duration;
5. snaps to H3's valid 24 fps `17k+5` frame grid;
6. renders shots sequentially;
7. re-encodes/concatenates them into one final MP4.

A scenario field may contain several scene descriptions separated by a line containing `---`. Scene 1 applies to shot 1, scene 2 to shot 2, and the final provided scene is reused for any remaining shots.

## Evidence policy

Each job stores:

- original request;
- per-shot compiled prompt;
- per-shot ComfyUI API graph;
- ComfyUI prompt id;
- elapsed time;
- generated shot copy;
- SHA-256 for shots, profile refs and final MP4;
- final run manifest.

Generated media is local and is not committed to Git.

## Current UI

Implementation lives at `tools/video-studio/`.

Normal controls:

- dialogue;
- scenario;
- optional clothing/appearance;
- framing;
- quality preset;
- seed;
- Generate.

The interface intentionally does **not** expose sampler graphs, VAE wiring, model paths or ComfyUI internals.

## Future gates

The following are useful next experiments, but are not prerequisites for the MVP:

1. controlled A/B: validated Turbo4 vs Base20 vs Base50 on the same talking-video prompt;
2. better automatic shot planning for 30–60 second scripts, including deliberate visual cut variation;
3. canonical neutral-background identity pack created/refined through Qwen/FLUX if it materially improves identity/scenario separation;
4. optional subtitle generation and burn-in/SRT output;
5. continuity controls across adjacent shots where desired;
6. optional B-roll shots that do not show the speaker.

Do not install a second talking-avatar engine merely because it exists. A competing model is justified only by a concrete quality deficiency that H3 cannot resolve after controlled testing.
