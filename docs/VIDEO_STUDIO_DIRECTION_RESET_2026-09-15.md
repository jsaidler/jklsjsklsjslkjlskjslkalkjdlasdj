# Video Studio — direction reset after local H3 quality ceiling

Date: **2026-09-15**  
Corrected: **2026-09-18**  
Status: **CANONICAL DECISION RECORD / LOCAL-ONLY CORRECTION**

## Core decision

The product requirement is not merely to create a convincing person who looks like João. It is:

> generate publishable videos from new text in which the person looks like João, sounds like João and retains João's recognizable expressions, gestures, posture and delivery rhythm, without recording each new performance.

The renderer must therefore be a personal-avatar/personalization system trained or conditioned from João's real footage, or an equivalent local system that explicitly carries forward behavioral identity.

## Execution constraint — LOCKED

The project does not use external hosted generation/training platforms or paid generation services.

- local/self-hosted execution only for avatar/profile construction, generation, training/fine-tuning and voice cloning;
- no SaaS/cloud inference API;
- no paid credits/subscriptions/hosted avatar tools;
- no paid local software/model/license unless João explicitly changes the rule before any cost;
- personal video/voice/identity material stays local;
- the web may be used to research and download freely usable local code/model weights.

Canonical policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`.

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

The Wan result therefore confirms the architectural requirement:

**appearance alone is not sufficient.**

## Hardware reality

The RTX 3060 12 GB is the fixed local GPU available to the project. The solution must be designed around it rather than escaping to a hosted renderer.

HunyuanVideo-Avatar showed one current local limit: the 720p / 129-frame / 30-step WanGP path timed out after nearly three hours at `0/30` because of heavy offload.

That rules out that specific quality path on this machine; it does not relax the local-only requirement.

## Production renderer strategy

Research and select a **local/self-hosted video-conditioned personalization route** that uses João's actual footage as behavioral identity.

Required capabilities:

1. real João video reference(s), not only a still image;
2. visual-identity preservation;
3. behavioral/motion identity preservation or learning;
4. new speech/audio input producing a new performance;
5. no fixed replay of one driving clip as the final product model;
6. zero paid-service dependency;
7. practical enough to run on Windows 11 / RTX 3060 12 GB / 48 GB RAM, including controlled CPU/RAM offload if needed.

The former HeyGen Avatar V / Digital Twin proposal is **retired** because it violates this execution constraint. It must not be used as a benchmark or fallback.

## Behavioral source library

The three supplied originals remain valuable and local:

- `VID_20260911_140124885.mp4` — strongest upper-body behavioral coverage;
- `VID_20260819_124008056.mp4` — close facial/microexpression coverage;
- `SIENA_BRUTO.mp4` — alternate motion/look coverage.

They should be used to condition/train/evaluate the selected local route rather than uploaded to a hosted avatar provider.

## Benchmark design — LOCKED

The first local behavioral benchmark must use:

1. one or more real João source videos as the personal behavior reference/training material;
2. a new Portuguese script/audio not spoken in the source section used for validation;
3. no prompt-only attempt to describe João's gestures in words as a substitute for video conditioning;
4. separate human verdicts for visual identity and behavioral identity.

The key question remains:

> When speaking completely new words, does the generated person still move and react recognizably like João?

## Arbitrary-scenario architecture

```text
persistent local profile
  João visual identity
  João behavioral video identity
  João voice identity
        |
new text + scene + wardrobe
        |
        +--> local scene/look preparation when needed
        +--> local voice stage
        +--> local video-conditioned personal-avatar renderer
        v
short production shot
```

## Development consequence

`tools/video-studio/` remains useful and renderer-pluggable, but every production adapter must be local/self-hosted.

Required interface direction:

```text
RendererAdapter
  prepare_profile()
  prepare_motion_identity()
  submit_shot()
  poll()
  fetch_output()
  report_metadata()
```

## Stop conditions

Until a genuine local behavioral-conditioning candidate is selected:

- do not use HeyGen, Kling or another hosted avatar service;
- do not buy credits/subscriptions;
- do not resume Wan prompt-only acting experiments as a substitute for behavior reference;
- do not rerun local Hunyuan at reduced quality merely to get any output;
- do not resume one-minute UI/product polish;
- do not integrate final TTS as though renderer selection were complete.

The next investment is research/engineering time on the correct **local video-conditioned problem**, not money or external-service dependence.