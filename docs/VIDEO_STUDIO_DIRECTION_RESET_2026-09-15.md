# Video Studio — direction reset after local H3 quality ceiling

Date: **2026-09-15**  
Status: **CANONICAL DECISION RECORD**

## Trigger

The user reviewed the local MiniMax H3 outputs and identified persistent low effective visual resolution. The proposed next step — slower local inference plus temporal upscaling — was judged likely to consume hours while still missing the expected production standard.

That diagnosis changes the project direction.

## What was wrong with the previous path

The project had started optimizing the renderer that happened to be installed rather than selecting the renderer that best fits the actual product requirement.

The actual requirement is not "make H3 work locally." It is:

> generate convincing publishable videos of the user from text, with chosen scenarios, without recording each new performance.

A general-purpose local 768p-class video model on an RTX 3060 12 GB is a poor place to impose a local-only constraint when the output already fails the visible quality bar.

## MiniMax H3 conclusion

Local H3 remains technically valuable. It proved:

- still-reference identity conditioning;
- standalone voice conditioning;
- useful Portuguese speech and lip sync;
- autonomous gestures without a driving video;
- scene separation after identity-reference cropping.

But it is not approved as the final renderer because:

- spatial detail looks substantially softer than expected from the nominal frame dimensions;
- slower Base sampling did not obviously solve the main complaint;
- official H3 2K relies on Regenerate-2K, which is not currently available as the normal open/local stage;
- adding a heavy conventional upscaler would increase runtime without evidence that it restores the missing generative detail;
- hands, gesture language and other temporal artifacts also remain open.

Classification:

**FUNCTIONAL PASS / FINAL-RENDER PRODUCTION FAIL.**

## Hardware reality

The RTX 3060 12 GB remains excellent project infrastructure but is not a rational hard ceiling for state-of-the-art photorealistic avatar rendering in 2026.

Relevant open alternatives illustrate the mismatch:

- LongCat-Video-Avatar 1.5 targets much larger GPU memory in reference deployments even with INT8/8-step inference;
- HunyuanVideo-Avatar has low-memory community paths but remains slow and 720p-class;
- InfiniteTalk provides long audio-driven generation but does not automatically solve the final-resolution/time problem on this hardware.

Therefore model-hopping among large local diffusion avatars is not the immediate plan.

## New production hypothesis

Use a renderer designed specifically for personal avatars and train/condition it from the user's actual footage.

First benchmark:

- **HeyGen Digital Twin / Avatar V** if available to the account;
- otherwise **Avatar IV Digital Twin**.

Why this fits the requirement better:

- built from a real reference video of the person;
- learns body language, expression and delivery style;
- supports script-driven generation without new recording;
- full-body behavior is supported;
- high-resolution output and API integration are production features rather than afterthoughts.

Second benchmark if needed:

- **Kling Avatar 2.0 Pro**, especially for shots driven from a deliberately prepared scene-specific avatar image plus audio/action prompt.

## Arbitrary-scenario architecture

Do not require one model to solve identity, set design, wardrobe, speech and motion simultaneously.

Preferred pipeline:

```text
text + scene + wardrobe
        |
        +--> high-quality still/look generation with identity preserved
        |
voice/script
        |
        +--> avatar renderer specialized in motion/lip sync
        |
        v
short production shot
```

A longer video can use several scene-specific looks and short shots.

This is expected to be more controllable than asking one local diffusion-video model to invent everything in one pass.

## Cost/time principle

A short hosted benchmark is preferred over hours of local inference when it can answer the production-quality question for roughly the cost of a single coffee.

Optimize cost only after the quality threshold is demonstrated.

## Development consequence

`tools/video-studio/` remains useful, but its renderer must become pluggable.

Required interface direction:

```text
RendererAdapter
  prepare_profile()
  submit_shot()
  poll()
  fetch_output()
  report_cost_and_metadata()
```

Keep H3 as a local research adapter. Add a production adapter only after actual visual approval.

## Stop conditions

Until the hosted benchmark is reviewed:

- do not run Base50 merely because it exists;
- do not install SeedVR2 as the presumed solution;
- do not download another massive local avatar model;
- do not resume one-minute UI/product polish.

The next investment must buy information about **production quality**, not merely more computation.