# Local Video Studio — Current Project State

Status date: **2026-09-18**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_AVATAR_V_BENCHMARK_2026-09-18.md`
3. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
4. `docs/VIDEO_STUDIO.md`
5. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
6. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
7. `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`
8. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Active objective — LOCKED

Build a tool that lets João write dialogue, choose a scenario and optionally specify appearance/framing, then generate a realistic video of himself speaking the new text without recording a new performance.

A production pass requires three separate identities to remain João:

1. **visual identity** — face, body, glasses, beard, hair and overall appearance;
2. **voice identity** — cadence/timbre/accent after the later TTS/voice-clone stage;
3. **behavioral identity** — characteristic facial expressions, head movement, gesture language, posture and delivery rhythm learned from João's actual video footage.

**Behavioral identity is a hard requirement. Generic plausible motion is not acceptable.**

Target program length: up to approximately one minute, eventually assembled from short shots.

## Canonical production strategy — LOCKED

Use a personal-avatar system trained/conditioned from João's actual footage rather than a static-image + audio renderer that invents body language.

The first production benchmark is **HeyGen Digital Twin / Avatar V**.

## Behavioral source library — INVENTORY + VISUAL REVIEW PASS

Protected originals:

- `SIENA_BRUTO.mp4` — 113.313 s, 1080x1920, H.264 + AAC;
- `VID_20260819_124008056.mp4` — 282.574 s, 1920x1080, H.264 + AAC;
- `VID_20260911_140124885.mp4` — 300.352 s, 3840x2160, HEVC + AAC.

Canonical source roles:

- **Primary Digital Twin / Video Look source:** `VID_20260911_140124885.mp4`
- **Secondary facial/microexpression source:** `VID_20260819_124008056.mp4`
- **Alternate motion/look source:** `SIENA_BRUTO.mp4`

Why the primary won: strongest combined face + torso + hands + posture + natural conversational gesture coverage under a stable camera/scene.

## Provider-safe primary preparation — COMPLETE 2026-09-18

Repository script:

`tools/video-studio/prepare_heygen_digital_twin_primary.ps1`

The user confirmed successful completion.

Prepared upload file:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\prepared\joao_heygen_digital_twin_primary_1080p_h264.mp4`

Preparation constraints:

- full duration retained;
- continuous source;
- 1920x1080 H.264 + AAC MP4;
- no trimming/splicing/looping;
- no stabilization;
- no retiming/interpolation;
- no behavioral/content edits.

The 4K HEVC original remains authoritative and protected.

## Wan2.2-S2V — DIAGNOSTIC BASELINE, NOT PRODUCT ROUTE

20-step result:

**VISUAL IDENTITY PASS/NEAR-PASS / BEHAVIORAL IDENTITY NOT TESTED / PRODUCTION FAIL FOR THE ACTUAL PRODUCT.**

Do not spend more local time on Wan prompt tuning, 720p or extra steps before the personal-avatar route is tested.

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

`tools/video-studio/` remains the orchestration layer and must stay backend-pluggable:

```text
persistent João profile
    +-- visual identity/look references
    +-- behavioral source library / motion reference
    +-- voice reference

new text + scene + wardrobe/framing
        |
        +--> voice stage
        +--> look/scene stage when needed
        +--> personal-avatar renderer
        +--> evidence/timing/metadata
        +--> final assembly
```

## Immediate next action — LOCKED

1. Open HeyGen and create a new avatar with `Avatars` -> `New Avatar` / `Create New Avatar` -> `Clone a Real Person`.
2. Upload `joao_heygen_digital_twin_primary_1080p_h264.mp4` as the avatar footage.
3. Complete the required live consent step with João himself reading the on-screen consent text.
4. Submit the Digital Twin and wait for provider processing.
5. Once ready, generate exactly one short Avatar V benchmark with new Portuguese text and **no custom motion prompt**.
6. Judge visual identity and behavioral identity separately before spending credits on additional looks or motion references.
7. Only after that benchmark passes, integrate HeyGen as a renderer adapter and finalize the voice-clone/TTS stage.
