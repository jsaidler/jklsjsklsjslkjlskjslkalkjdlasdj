# Local Video Studio — canonical architecture

Status date: **2026-09-18**  
Status: **ACTIVE ORCHESTRATION PROTOTYPE / LOCAL VIDEO-CONDITIONED PERSONALIZATION NEXT**

Canonical cross-chat state: `docs/PROJECT_STATE.md`.
Canonical execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`.

## Objective

Create short realistic videos of João without requiring a new camera recording for each publication.

Normal input:

`written dialogue + target scene + optional clothing/framing`

Persistent profile input:

`visual identity references + behavioral video reference(s) + voice reference`

Target output:

`high-quality vertical MP4 that looks like João, sounds like João and moves/expresses itself like João`

Target program duration is up to approximately one minute, eventually assembled from short shots.

## Non-negotiable identity model

The profile has three distinct identity channels:

1. **visual identity** — appearance;
2. **voice identity** — voice/tone/accent;
3. **behavioral identity** — expressions, gestures, head motion, posture and delivery rhythm learned from João's actual footage.

A renderer that receives only a static image plus audio may be useful as a visual benchmark, but it cannot satisfy the product requirement if it invents generic body language.

The project must not confuse `natural motion` with `João's motion`.

## Execution policy — LOCKED

All active production stages must run **locally/self-hosted**.

- no external hosted avatar/generation platform;
- no cloud/SaaS inference API;
- no subscriptions, paid credits or paid hosted generation;
- no paid local tool/model/license unless explicitly approved by João before any cost;
- personal video/voice/identity material stays local;
- web access may be used to research and download free/local code, models and documentation.

## Architecture rule

The product is an orchestrator, not a wrapper around one specific model.

```text
Local Video Studio UI
        |
        v
persistent João profile
  visual identity/look references
  behavioral reference videos
  voice reference
        |
new script + scene + appearance + framing
        |
        +-- local voice stage
        |      +-- CosyVoice remains a candidate
        |
        +-- optional local scene/look preparation
        |      +-- Qwen / FLUX / future local image backend
        |
        +-- local personal-avatar / video-conditioned render adapter
        |      +-- candidate to be selected after capability research
        |      +-- Wan2.2-S2V — visual/structural baseline only
        |      +-- H3 — historical research baseline
        |      +-- HunyuanVideo-Avatar — local practicality fail on 12 GB at quality gate
        |
        +-- evidence / timing / metadata
        +-- final assembly / captions
        v
final MP4
```

## Canonical production route

Use a **local renderer/personalization system that consumes João's real video footage as behavioral conditioning or learned personal motion identity**.

Static-image + audio generation is not enough for the final product.

The HeyGen / Avatar V branch is retired because it violates the local-only / zero-cost execution policy. Its earlier documentation remains historical only and must not drive current work.

## Behavioral source library

Three original videos are preserved locally as the canonical behavioral library:

- `SIENA_BRUTO.mp4` — alternate motion/look material;
- `VID_20260819_124008056.mp4` — close facial/microexpression material;
- `VID_20260911_140124885.mp4` — strongest upper-body behavioral source.

A 1080p H.264 derivative was also prepared locally from the last source. It is a generic local reference derivative despite its historical HeyGen-oriented filename.

## Wan2.2-S2V result and scope

Wan S2V was tested with static visual reference + speech audio.

It remains useful for visual likeness, anatomy stability, texture stability, lipsync and local runtime evidence.

It does **not** validate behavioral identity because João's reference video was not used as behavior conditioning.

The reviewed 20-step result was visually close enough to João, but expressions and movements felt like another person and were caricatured.

Therefore do not resume prompt-only acting refinement as if it solved behavioral identity.

## HunyuanVideo-Avatar local result

The local 720p / 129-frame / 30-step WanGP test timed out after about three hours at `0/30` because the RTX 3060 12 GB required severe block offload.

Classification:

**runtime functional / local quality path impractical / no visual verdict.**

## Scene/look strategy

Do not require one model to solve identity, behavior, wardrobe, scene and voice simultaneously.

Preferred local route after behavioral identity passes:

1. persistent behavioral identity comes from local video-conditioned personalization;
2. visual look can come from a selected/generated local scene-specific look;
3. voice comes from the local voice stage;
4. local renderer creates the performance;
5. multiple validated shots are assembled automatically.

## Existing implementation

`tools/video-studio/` already provides orchestration infrastructure such as profile handling, shot splitting, serial jobs, FFmpeg assembly, manifests and evidence.

Refactor target:

```text
RendererAdapter
  prepare_profile()
  prepare_motion_identity()
  submit_shot()
  poll()
  fetch_output()
  report_metadata()
```

The profile schema must make behavioral video explicit rather than optional/implicit.

## Development order — LOCKED

1. research local/self-hosted candidates that genuinely use video reference or learned behavioral identity;
2. verify license, model size, Windows support, RTX 3060 12 GB feasibility and runtime before any download;
3. select the strongest viable route;
4. run one short new-speech benchmark using João's behavioral footage;
5. approve/reject behavioral identity separately from visual identity;
6. only if it passes, integrate that local renderer as an adapter;
7. then finalize local voice/TTS;
8. then validate scene/look swaps;
9. only after a short-shot production pass, resume one-minute multi-shot automation.

Do not use an external paid service as a shortcut around local model limitations.