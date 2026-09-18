# Local Video Studio — Current Project State

Status date: **2026-09-18**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
4. `docs/VIDEO_STUDIO.md`
5. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
6. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
7. `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`
8. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
9. `docs/VIDEO_STUDIO_AVATAR_V_BENCHMARK_2026-09-18.md` — historical/retired external branch only

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
- internet use is allowed for research, documentation and downloading freely usable local code/model weights.

Canonical policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`.

The HeyGen Digital Twin / Avatar V route is therefore **retired as invalid for this project**. No upload or paid provider use is authorized.

## Active objective — LOCKED

Build a local tool that lets João write dialogue, choose a scenario and optionally specify appearance/framing, then generate a realistic video of himself speaking the new text without recording a new performance.

A production pass requires three separate identities to remain João:

1. **visual identity** — face, body, glasses, beard, hair and overall appearance;
2. **voice identity** — cadence/timbre/accent after the later local TTS/voice-clone stage;
3. **behavioral identity** — characteristic facial expressions, head movement, gesture language, posture and delivery rhythm learned from João's actual video footage.

**Behavioral identity is a hard requirement. Generic plausible motion is not acceptable.**

Target program length: up to approximately one minute, eventually assembled from short shots.

## Behavioral source library — INVENTORY + VISUAL REVIEW PASS

Protected originals:

- `SIENA_BRUTO.mp4` — 113.313 s, 1080x1920, H.264 + AAC;
- `VID_20260819_124008056.mp4` — 282.574 s, 1920x1080, H.264 + AAC;
- `VID_20260911_140124885.mp4` — 300.352 s, 3840x2160, HEVC + AAC.

Source-role review remains useful locally:

- `VID_20260911_140124885.mp4` — strongest primary upper-body behavioral source;
- `VID_20260819_124008056.mp4` — strongest close facial/microexpression source;
- `SIENA_BRUTO.mp4` — alternate motion/look source with useful gesture coverage but foreground-object occlusions.

The locally prepared derivative:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\prepared\joao_heygen_digital_twin_primary_1080p_h264.mp4`

was created successfully before the external-route mistake was caught. It remains only a generic local 1080p H.264 copy; the filename is historical and does not authorize HeyGen use.

## Wan2.2-S2V — DIAGNOSTIC BASELINE

20-step result:

**VISUAL IDENTITY PASS/NEAR-PASS / BEHAVIORAL IDENTITY NOT TESTED / PRODUCTION FAIL FOR THE ACTUAL PRODUCT.**

Reason: the test used static image + audio and therefore gave the model no João behavioral reference. Do not treat generic prompt-based acting as a substitute for behavioral conditioning.

## HunyuanVideo-Avatar — LOCAL PRACTICALITY FAIL

The 720x1280 / 129-frame / 30-step WanGP path timed out after about 3 hours at `0/30` because of severe transformer offload on RTX 3060 12 GB.

Classification:

**FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / LOCAL PRACTICALITY FAIL.**

## H3 conclusion

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

## Quality gate — LOCKED

A production candidate must pass both visual quality and personal-performance quality. The human reviewer must be able to say:

> this does not merely look like João; it moves and reacts like João.

Generic presenter choreography, exaggerated expressions, plausible-but-uncharacteristic gestures or a different delivery rhythm are production failures even when facial identity is excellent.

## Current implementation direction

`tools/video-studio/` remains the orchestration layer and must stay backend-pluggable, but every active backend must be local/self-hosted:

```text
persistent João profile
    +-- visual identity/look references
    +-- behavioral source library / video conditioning
    +-- voice reference

new text + scene + wardrobe/framing
        |
        +--> local voice stage
        +--> local look/scene stage when needed
        +--> local video-conditioned personal-avatar renderer
        +--> evidence/timing/metadata
        +--> final assembly
```

## Immediate next action — LOCKED

Research and select a **local/self-hosted, zero-cost video-conditioned personalization route** that can consume João's real footage as behavioral identity and generate a new performance for new speech/audio.

Required before any new heavy run:

1. identify candidate models/pipelines that genuinely use reference video or learned personal motion identity;
2. reject static-image + audio systems that merely invent behavior;
3. verify license, local availability, Windows/RTX 3060 12 GB feasibility, model sizes and expected runtime before downloading anything;
4. prefer reuse of already installed local infrastructure/models where possible;
5. do not use external paid services as a shortcut.
