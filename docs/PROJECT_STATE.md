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

## Canonical production strategy — RESTORED / LOCKED

The decision recorded on 2026-09-15 remains the correct direction: use a personal-avatar system that is trained/conditioned from João's actual footage, rather than a static-image + audio renderer that invents its own body language.

The first production benchmark is now **HeyGen Digital Twin / Avatar V**.

Current HeyGen documentation confirms that Avatar V is available and is specifically designed to learn a real person's gestures, expressions, mannerisms and motion from a short video reference, then reuse that learned motion identity with new scripts and different looks/scenes.

Official references:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://www.heygen.com/avatars/avatar-v`

Fallback if Avatar V cannot be used on the account: **Avatar IV Digital Twin**. Second external comparison only if needed: **Kling Avatar 2.0 Pro**.

## Existing user footage — PURPOSE

Existing João footage is not merely an identity source. It is the behavioral-reference material.

For the Avatar V benchmark, use an uninterrupted natural speaking segment from the existing source footage, with visible normal João expressions and gestures. Prefer the original source footage rather than the 12.6 s derivative if the derivative is below the Avatar V 15 s motion-reference target.

Do not record new material unless the existing footage is rejected technically or is demonstrably unrepresentative of João's normal behavior.

## Wan2.2-S2V — DIAGNOSTIC BASELINE, NOT PRODUCT ROUTE

Wan2.2-S2V proved useful local rendering facts but did **not** test the project's behavioral-identity requirement because it was fed a static image plus audio, not João's behavior video.

10-step baseline:

- Wan2.2 S2V 14B FP8 scaled;
- 480x832;
- 77 generated frames at 16 fps;
- 10 steps / CFG 6;
- measured runtime **28.55 min**;
- structurally promising but production quality failed.

20-step result, reviewed by João on 2026-09-18:

- visual likeness improved enough that João described it as essentially himself visually;
- performance remained wrong: expressions and movements felt like another person and the result was caricatured;
- this is **not evidence that Wan failed to preserve supplied behavioral identity**, because behavioral footage was never supplied to the Wan S2V test.

Canonical classification:

**WAN S2V 20-STEP: VISUAL IDENTITY PASS/NEAR-PASS / BEHAVIORAL IDENTITY NOT TESTED / PRODUCTION FAIL FOR THE ACTUAL PRODUCT.**

Do not spend another local hour on prompt tuning, 720p, more steps or generic motion refinement before testing a renderer that actually consumes João's motion identity.

## HunyuanVideo-Avatar — LOCAL PRACTICALITY FAIL

The 720x1280 / 129-frame / 30-step WanGP path timed out after about 3 hours while still at `0/30` denoising steps because of severe transformer block offload on RTX 3060 12 GB.

Classification:

**FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / LOCAL PRACTICALITY FAIL.**

Do not rescue this route by lowering its quality target merely to force an output.

## H3 conclusion

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

H3 remains historical/research evidence only.

## Quality gate — LOCKED

A production candidate must pass both visual quality and personal-performance quality. In addition to the existing visual checks, the human reviewer must be able to say:

> this does not merely look like João; it moves and reacts like João.

Generic presenter choreography, exaggerated expressions, plausible-but-uncharacteristic gestures or a different delivery rhythm are production failures even when facial identity is excellent.

## Current implementation direction

`tools/video-studio/` remains the orchestration layer and must stay backend-pluggable:

```text
persistent João profile
    +-- visual identity/look references
    +-- behavioral motion reference/video
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

1. Stop local renderer escalation.
2. Use João's existing footage to create the first **Avatar V Digital Twin / motion identity**.
3. Generate a short benchmark with a **new Portuguese script not present in the training/reference clip** so generalization is actually tested.
4. Judge visual identity and behavioral identity separately.
5. Only after that benchmark passes, integrate the chosen avatar backend into `tools/video-studio/` and then add the final voice-clone/TTS stage.

The purpose of the next benchmark is not to prove that an avatar can speak. It is to prove that a new performance still feels recognizably like João.