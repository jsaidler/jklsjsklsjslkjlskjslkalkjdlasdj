# Video Studio — direction reset after local H3 quality ceiling

Date: **2026-09-15**  
Reaffirmed: **2026-09-18**  
Status: **CANONICAL DECISION RECORD / REAFFIRMED AFTER WAN 20-STEP REVIEW**

## Core decision

The product requirement is not merely to create a convincing person who looks like João. It is:

> generate publishable videos from new text in which the person looks like João, sounds like João and retains João's recognizable expressions, gestures, posture and delivery rhythm, without recording each new performance.

The renderer must therefore be a personal-avatar system trained/conditioned from João's real footage, or an equivalent system that explicitly carries forward behavioral identity.

## Why static-image avatar generation is insufficient

A static image plus audio can preserve appearance and produce plausible human motion, but it does not tell the system how João actually moves.

The project must distinguish:

- visual identity;
- voice identity;
- behavioral identity.

`Natural motion` is not enough. Generic presenter choreography is a failure even if it is anatomically plausible.

## H3 conclusion

MiniMax H3 proved identity and audio conditioning but failed production visual quality and produced generic autonomous gestures.

Classification:

**FUNCTIONAL PASS / FINAL-RENDER PRODUCTION FAIL.**

## Wan 20-step reaffirmation

Wan2.2-S2V later produced a result that João judged visually close enough to himself, but the expressions and movements felt like another person and the performance was caricatured.

This does **not** prove that Wan failed to preserve João's behavioral identity, because the Wan S2V test only received a static image plus audio. João's behavioral video never entered that pipeline.

The Wan result therefore confirms the architectural requirement rather than overturning it:

**appearance alone is not sufficient.**

## Hardware reality

The RTX 3060 12 GB is useful project infrastructure but is not a rational hard ceiling for the final personal-avatar renderer.

HunyuanVideo-Avatar confirmed the local limitation: the 720p / 129-frame / 30-step path timed out after nearly three hours at `0/30` because of heavy offload.

Do not keep changing local diffusion models when the next question is about behavioral identity.

## Production renderer strategy

Use a renderer designed specifically for personal avatars and train/condition it from João's actual footage.

### First benchmark — LOCKED

**HeyGen Avatar V / Digital Twin.**

As of 2026-09-18 HeyGen officially documents Avatar V as a personal-avatar model that learns a real human's specific motion, gestures, expressions and mannerisms from short video footage and can then reuse that motion identity with new scripts and different looks.

Official references:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://www.heygen.com/avatars/avatar-v`

Current product guidance uses roughly a **15-second motion recording** for Avatar V. The benchmark should therefore use an uninterrupted segment from João's existing footage that actually represents his normal expressions and gestural language.

Do not record new footage merely because it is convenient. Reuse the existing supplied material first unless it is rejected technically or does not contain representative behavior.

### Fallbacks

- Avatar IV Digital Twin if Avatar V is unavailable on the account;
- Kling Avatar 2.0 Pro only as a second external comparison if the first route fails the quality gate.

## Benchmark design — LOCKED

The first personal-avatar benchmark must use:

1. a real João motion/reference video from the existing footage;
2. a new Portuguese script not spoken in that motion-reference clip;
3. a look that keeps identity evaluation easy;
4. no deliberate theatrical prompt or exaggerated emotion;
5. separate human verdicts for visual identity and behavioral identity.

The key question is:

> When speaking completely new words, does the generated person still move and react recognizably like João?

If the answer is no, the avatar route fails even if rendering quality is excellent.

## Arbitrary-scenario architecture

Do not require one model to solve identity, set design, wardrobe, speech and behavior simultaneously.

Preferred pipeline:

```text
persistent profile
  João visual identity
  João behavioral video identity
  João voice identity
        |
new text + scene + wardrobe
        |
        +--> scene/look preparation when needed
        +--> voice stage
        +--> personal-avatar renderer
        v
short production shot
```

A longer video can use several scene-specific looks and short shots while retaining the same behavioral identity.

## Development consequence

`tools/video-studio/` remains useful, but the renderer is pluggable.

Required interface direction:

```text
RendererAdapter
  prepare_profile()
  prepare_motion_identity()
  submit_shot()
  poll()
  fetch_output()
  report_cost_and_metadata()
```

## Stop conditions

Until the Avatar V benchmark is reviewed:

- do not resume Wan 720p or prompt-only acting experiments;
- do not run more H3 quality ladders;
- do not rerun local Hunyuan at reduced quality merely to get an output;
- do not resume one-minute UI/product polish;
- do not integrate final TTS/CosyVoice as though renderer selection were complete.

The next investment must answer the behavioral-identity question directly.