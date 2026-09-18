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

Use a personal-avatar system trained/conditioned from João's actual footage rather than a static-image + audio renderer that invents body language.

The first production benchmark is **HeyGen Digital Twin / Avatar V**.

Current official product guidance separates two relevant footage roles:

- **Digital Twin / Video Look source:** current HeyGen filming guidance recommends at least **2 minutes of uninterrupted speech** for a strong Digital Twin; Video Looks require **2+ minutes** of footage.
- **Avatar V motion reference:** Avatar V guidance emphasizes about **15 seconds** of representative motion/reference footage.

Do not prematurely reduce João's source library to one arbitrary 15-second clip. First inventory and review the available originals, then assign roles.

Official references:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://help.heygen.com/en/articles/8389138-digital-twin-video-avatar-filming-tips`
- `https://help.heygen.com/en/articles/9964694-avatar-looks-explained`
- `https://help.heygen.com/en/articles/12092609-recording-your-consent-video`

Fallback if Avatar V cannot be used on the account: **Avatar IV Digital Twin**. Second external comparison only if needed: **Kling Avatar 2.0 Pro**.

## Behavioral source library — INVENTORY PASS 2026-09-18

Source folder:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

Three original candidate videos are staged and must remain unchanged.

Final technical inventory:

- `SIENA_BRUTO.mp4` — **113.313 s**, **1080x1920**, **29.970 fps**, H.264 + AAC, **274.93 MB**; below current 2-minute base Digital Twin gate; valid >=15 s Avatar V motion-reference material;
- `VID_20260819_124008056.mp4` — **282.574 s**, **1920x1080**, **30.030 fps**, H.264 + AAC, **682.14 MB**; qualifies for current >=2-minute base Digital Twin gate and >=15 s motion reference;
- `VID_20260911_140124885.mp4` — **300.352 s**, **3840x2160**, **30.009 fps**, HEVC + AAC, **1262.04 MB**; qualifies for current >=2-minute base Digital Twin gate and >=15 s motion reference.

Inventory manifest:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\avatar_v_source_inventory.json`

Successful rerun report:

`tools/video-studio/reports/avatar_v_source_inventory_20260918_170817.txt`

Contact sheets were successfully generated for all three sources under:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\contact_sheets\`

Files:

- `SIENA_BRUTO_contact.jpg`
- `VID_20260819_124008056_contact.jpg`
- `VID_20260911_140124885_contact.jpg`

Important: the 4K source is technically strongest in resolution but is **not automatically the behavioral winner**. Base-source selection must consider natural João delivery, framing, uninterrupted speech, gesture visibility, gaze, lighting, cuts and audio.

The first contact-sheet bug is closed. The patched inventory uses explicit FFmpeg argument arrays and treats contact-sheet failure as fatal.

The older `prepare_avatar_v_reference.ps1` single-source auto-trimming flow remains **deprecated and blocked**. It would throw away useful behavioral coverage before the source library is reviewed.

## Wan2.2-S2V — DIAGNOSTIC BASELINE, NOT PRODUCT ROUTE

Wan2.2-S2V proved useful local rendering facts but did **not** test behavioral identity because it was fed a static image plus audio.

10-step baseline:

- Wan2.2 S2V 14B FP8 scaled;
- 480x832;
- 77 generated frames at 16 fps;
- 10 steps / CFG 6;
- measured runtime **28.55 min**;
- structurally promising but production quality failed.

20-step result, reviewed by João on 2026-09-18:

- visual likeness improved enough that João described it as essentially himself visually;
- expressions and movements still felt like another person and the result was caricatured;
- this is **not evidence that Wan failed to preserve supplied behavioral identity**, because behavioral footage was never supplied to that test.

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

1. Review the three generated contact sheets for framing, continuity and visible body/gesture coverage.
2. Review the original videos for actual behavioral representativeness; contact sheets alone cannot judge speech rhythm or mannerisms.
3. Choose the base Digital Twin source between `VID_20260819_124008056.mp4` and `VID_20260911_140124885.mp4` only after that review; keep `SIENA_BRUTO.mp4` as additional behavioral/motion-reference material.
4. Create the first Avatar V/Digital Twin in HeyGen, complete the required live consent step and generate exactly one short benchmark with new Portuguese text and no custom motion prompt.
5. Judge visual identity and behavioral identity separately.
6. Only after that benchmark passes, integrate the chosen avatar backend into `tools/video-studio/` and finalize the voice-clone/TTS stage.

The purpose of the next benchmark is not to prove that an avatar can speak. It is to prove that a new performance still feels recognizably like João.
