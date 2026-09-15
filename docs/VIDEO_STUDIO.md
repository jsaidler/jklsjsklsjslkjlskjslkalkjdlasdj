# Local Video Studio — canonical architecture

Status date: **2026-09-15**  
Status: **ACTIVE PROTOTYPE / PRODUCTION QUALITY GATE OPEN**

Canonical cross-chat state: `docs/PROJECT_STATE.md`.  
Quality gate: `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`.

## Objective

Create short, realistic videos of the user without requiring a new camera recording for each publication.

Normal input:

`written dialogue + target scene + optional clothing/framing`

Persistent profile input:

`cropped identity references + voice reference`

Target output:

`vertical MP4 with the user's preserved identity, referenced/cloned voice, new lip-synced dialogue, autonomous body motion and the requested scene`

Target program duration is up to approximately one minute, assembled from short H3-safe shots.

## Current status — IMPORTANT

The architecture is proven, but **production visual quality is not**.

The 2026-09-15 tests established that H3 can use still identity references plus a standalone voice reference, generate autonomous movement without a driving video, and create a different scene. The user did **not** approve the visual result as production quality.

Therefore:

- H3 Ref2VA is the active engine candidate, not yet a production-approved engine;
- the existing Turbo4 path is a functional baseline, not a production preset;
- UI/productization work is subordinate to the active visual-quality gate;
- no one-minute/multi-shot output should be treated as production-ready until one short shot passes the quality gate.

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
        +-- generated video
        +-- generated voice/audio
        |
        v
FFmpeg final assembly
        |
        v
Z:\AI\MiniMaxH3\VideoStudioRuns\<job>\video_studio_<job>.mp4
```

ComfyUI remains an inference runtime, not the intended authoring interface.

## Persistent profile

Current functionally validated profile inputs:

- `joao_id_face.png`
- `joao_id_shoulders.png`
- `joao_id_upperbody.png`
- `joao_ref_voice.wav`

The images intentionally contain progressively more anatomy while minimizing scene/background authority.

Full-frame identity references reproduced the source room even when a new environment was requested. Cropped references materially reduced that coupling, so the identity-only role is retained.

## Prompt contract

For image-only recording-free experiments:

- `<Picture 1..N>` = **identity only**;
- `<Audio 1>` = **voice identity only**;
- no normal `<Video 1>` driving reference;
- scenario text = environment authority;
- optional appearance text = clothing authority;
- framing preset = camera crop authority;
- H3 generates body performance autonomously.

Dialogue is encoded as:

```text
<d>[Portuguese] ...</d>
```

The user explicitly judged the generated voice as good. That voice verdict does not imply a visual-quality pass.

## Engine candidate

Active candidate: **MiniMax H3 Ref2VA**.

Installed payload:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors`
- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`

Generation is 24 fps. Current comparison canvas is 768-class vertical (`768×1344` requested; H3 may align the realized canvas to its internal constraints).

## Presets — EXPERIMENTAL

Backend keys are retained for compatibility with the first MVP code, but their human meaning is:

### `draft`

- Turbo4;
- 480×864;
- cheap prompt/composition smoke test only.

### `production` — LEGACY KEY NAME ONLY

- Turbo4;
- 768×1344;
- 4 steps;
- `res_multistep` + `simple`;
- `ref_image_size=max`.

This key must **not** be described as production approved. It is only the high-resolution fast functional baseline from the initial spike.

### `quality`

- Base H3;
- no Turbo LoRA;
- 20 steps;
- `res_multistep` + `beta`;
- 768×1344;
- `ref_image_size=max`.

This is the first active quality candidate.

### `max`

- Base H3;
- no Turbo LoRA;
- 50 steps;
- `res_multistep` + `beta`;
- 768×1344;
- `ref_image_size=max`.

This is the maximum currently defined H3 quality candidate. It may be extremely slow on the RTX 3060 and is justified only after controlled comparison.

## Production visual-quality gate

No preset is promoted until it passes `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`.

The gate includes:

- face/identity stability;
- eyes/glasses/hair/beard;
- mouth/teeth/jaw;
- hands/fingers/wrists/arms;
- natural body performance rather than generic AI-presenter gestures;
- skin/detail texture;
- clothing continuity;
- background geometry stability;
- lighting/camera coherence;
- voice/AV sync;
- overall publishability without manual frame repair.

A conspicuous visual artifact is a production failure even if voice/identity technically work.

## Current implementation

Implementation lives at `tools/video-studio/`.

It already provides:

- localhost UI;
- dialogue/scenario/appearance/framing inputs;
- profile injection;
- H3 API graph construction;
- serial GPU execution;
- shot splitting;
- FFmpeg assembly;
- run evidence and manifests.

This is useful infrastructure, but it is presently a **prototype harness** for quality development, not a finished production tool.

## Current development order

1. controlled Turbo4 vs Base20 comparison under identical conditions;
2. Base50 only if warranted by the comparison;
3. if sampling does not solve the visible defects, improve the canonical identity reference pack;
4. repeat the best H3 sampling path;
5. if H3 remains visually inadequate, compare another local video/avatar engine on the same benchmark;
6. only after a short-shot quality pass, resume long-form/multi-shot productization.

Do not spend the next cycle on subtitles, B-roll, cosmetic UI work or one-minute continuity while the single-shot image quality is still below the user's standard.

## Evidence policy

Every controlled quality run should store:

- exact prompt;
- exact preset/model paths;
- seed;
- identity/voice reference hashes;
- dimensions/frame count/fps;
- elapsed time;
- output MP4 and SHA-256;
- explicit human visual verdict.

No automatic metric overrides visible defects.