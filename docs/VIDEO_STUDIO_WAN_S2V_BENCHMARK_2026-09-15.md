# Local Video Studio — Wan2.2 S2V benchmark

Date: **2026-09-18**  
Status: **20-STEP REVIEWED / VISUAL IDENTITY STRONG / BEHAVIORAL IDENTITY NOT TESTED / LOCAL ESCALATION STOPPED**

Canonical state: `docs/PROJECT_STATE.md`.

## Scope correction

Wan2.2-S2V was tested with a static image reference plus speech audio. It did **not** receive João's behavioral reference video.

Therefore this benchmark can evaluate visual identity, anatomy, temporal image quality, lipsync and local runtime, but it cannot answer the project's core behavioral question:

> does the generated person move, react and express himself like João?

Any generic presenter motion produced by Wan is invented by the model rather than a failed preservation of supplied João behavior.

## Preparation

Validated local environment:

- NVIDIA RTX 3060 12 GB;
- 47.7 GB system RAM;
- FFmpeg available;
- native `WanSoundImageToVideo`, `AudioEncoderLoader`, and `AudioEncoderEncode` support.

Payload:

- `wan2.2_s2v_14B_fp8_scaled.safetensors`;
- `wav2vec2_large_english_fp16.safetensors`;
- reused UMT5 FP16;
- reused Wan2.1 VAE BF16.

Benchmark assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`;
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`.

## 10-step baseline

Settings:

- Wan2.2 S2V 14B FP8 scaled;
- 480x832;
- 77 generated frames at 16 fps;
- 10 steps;
- CFG 6;
- `uni_pc` / `simple`;
- shift 8;
- seed 0;
- real João speech audio;
- no CosyVoice;
- no upscaler.

Measured runtime:

- **1713.2926 s = 28.55 min**.

Verdict:

**STRUCTURALLY PROMISING / PRODUCTION QUALITY FAIL.**

Positive findings:

- stable body topology and shoulders;
- materially better hands than H3;
- broadly coherent face after opening transient;
- stable background, clothing and framing.

Blockers included insufficient detail, eyeglass drift, beard/hair texture crawl, mouth/teeth/jaw softness and moving-hand detail loss.

## 20-step corrected quality baseline — REVIEWED

The non-Lightning documented quality path is 20 steps / CFG 6, so a controlled repeat was run using the same reference/audio/seed and existing 480x832 setup.

Human verdict from João on 2026-09-18:

> visually, it is me; but it did not preserve my expressions and movements — in that respect it is another person.

Additional description: the performance felt **caricatured**.

Interpretation:

- **visual identity:** strong enough to count as pass/near-pass for this stage;
- **behavioral identity:** **not tested**, because no behavioral video was supplied to the S2V path;
- **production result:** fail for the actual product, because generic invented performance is unacceptable even when the face looks correct.

Canonical classification:

**WAN S2V 20-STEP FP8: VISUAL IDENTITY PASS/NEAR-PASS / BEHAVIORAL IDENTITY NOT TESTED / PRODUCTION FAIL FOR PROJECT REQUIREMENTS.**

## Why prompt tuning is not the next step

The current failure is not merely that Wan's gestures are too energetic. The project requirement is not `natural generic behavior`; it is `João's behavior`.

Prompt phrases such as `subtle movement`, `restrained gestures` or `no exaggerated expression` may change generic acting style but do not provide the missing personal motion information.

Therefore do not spend another long run on:

- 720p;
- more steps;
- sampler changes;
- prompt-only personality correction;
- arbitrary motion suppression.

Those would improve or restrain an invented performance rather than test the intended personal-avatar architecture.

## Relation to original project plan

`docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md` already selected the correct strategy before this local detour:

> use a renderer designed specifically for personal avatars and train/condition it from João's actual footage.

The Wan result strengthens that decision: image likeness alone is insufficient.

## Next action

Stop local Wan escalation and benchmark a personal avatar that explicitly learns motion identity from video.

Current first choice: **HeyGen Avatar V / Digital Twin** using existing João footage, followed by a new-script test that is not present in the reference video.

Wan remains valuable as a local rendering baseline and possible future component, but it is not the active production route unless a future implementation can consume João's behavioral identity directly.