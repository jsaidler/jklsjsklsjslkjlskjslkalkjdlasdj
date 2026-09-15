# Local Video Studio — canonical architecture

Status date: **2026-09-15**  
Status: **ACTIVE ORCHESTRATION PROTOTYPE / FINAL RENDER BACKEND OPEN**

Canonical cross-chat state: `docs/PROJECT_STATE.md`.  
Direction reset: `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`.

## Objective

Create short realistic videos of the user without requiring a new camera recording for each publication.

Normal input:

`written dialogue + target scene + optional clothing/framing`

Persistent profile input:

`identity references/video + voice reference`

Target output:

`high-quality vertical MP4 with preserved identity, convincing voice, natural lip-synced performance and the requested scene`

Target program duration is up to approximately one minute.

## Architecture correction

The first implementation coupled the product too tightly to MiniMax H3 because H3 was already installed and proved the functional relation.

That coupling is now retired.

The product is an **orchestrator**, not an H3 wrapper.

```text
Local Video Studio UI
        |
        v
profile + script + scene + appearance + framing
        |
        +-- optional local reference/look preparation
        +-- provider-independent shot plan
        +-- render adapter
        |      +-- hosted production avatar backend
        |      +-- local H3 research/fallback backend
        |      +-- future competing backends
        |
        +-- evidence / cost / timing manifest
        +-- final assembly / captions
        v
final MP4
```

## H3 status

MiniMax H3 Ref2VA remains preserved because it proved:

- identity reference conditioning;
- good voice behavior;
- useful lip sync;
- autonomous movement without driving video;
- scene separation using cropped identity references.

It failed the user's production visual-quality standard, especially effective spatial detail/resolution. Turbo4 and Base20 do not justify further hours of local sampler escalation as the default direction.

H3 is therefore:

**research/fallback backend — not current final production renderer.**

Base50 and heavy local upscaling are no longer automatic next steps.

## Quality-over-local rule

Local execution remains preferred for private assets, preprocessing and experimentation, but the final renderer may be hosted when that produces materially better quality in practical time.

The repository, profile management, prompt logic, shot planning, output assembly and manifests should remain under user control even when the render request is remote.

## First production renderer benchmark

The first candidate is a personal-avatar engine trained from actual footage rather than a general video model forced into that role.

Priority:

1. HeyGen Digital Twin / Avatar V where available, otherwise Avatar IV Digital Twin;
2. Kling Avatar 2.0 Pro for scene-specific image+audio animation comparison;
3. open/cloud GPU models only when their quality/cost/runtime justify them.

The benchmark must use a short identical script and should answer one question quickly: is the visual result materially closer to publishable production than local H3?

## Scene strategy

The product goal includes arbitrary scenarios. Do not require the avatar backend itself to solve every scene-generation problem.

Preferred compositional strategy when necessary:

1. generate or prepare a high-quality still/look of the user in the desired setting;
2. feed that look plus speech/audio into an avatar renderer specialized in human motion/lip sync;
3. use different looks/shots for a longer video;
4. assemble them automatically.

This separates **scene/image quality** from **talking-avatar motion quality**.

## Persistent profile

Current local H3 profile assets remain useful evidence:

- `joao_id_face.png`
- `joao_id_shoulders.png`
- `joao_id_upperbody.png`
- `joao_ref_voice.wav`

For a production Digital Twin backend, prefer the user's best existing continuous high-quality footage because modern video-reference avatar systems learn body language and identity more effectively from video than from three still crops.

## Existing implementation

`tools/video-studio/` already provides:

- localhost UI;
- dialogue/scenario/appearance/framing inputs;
- profile management;
- shot splitting;
- serial jobs;
- FFmpeg assembly;
- manifests and evidence.

Refactor target:

- define a renderer/provider adapter interface;
- preserve the current H3 adapter as one implementation;
- add the chosen production backend after benchmark approval;
- record per-provider cost, latency and output metadata.

## Development order

1. stop H3/Base50/upscaler escalation;
2. perform one cheap short hosted-avatar benchmark;
3. compare against the already-generated H3 reference clips;
4. select the renderer only after viewing the actual output;
5. refactor Video Studio around the selected provider adapter;
6. resume one-minute multi-shot automation only after one short shot is genuinely publishable.

Do not optimize a renderer that already misses the quality bar.