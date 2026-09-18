# Local Video Studio — HeyGen Avatar V behavioral-identity benchmark

Date: **2026-09-18**  
Status: **PRIMARY DIGITAL TWIN SOURCE PREPARED / HEYGEN CREATION NEXT / NO AVATAR RESULT YET**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

This benchmark tests the requirement that previous static-image + audio renderers did not test:

> Can a generated video use completely new words while preserving João's recognizable expressions, gestures, head movement, posture and delivery rhythm from his real footage?

The benchmark is primarily a **behavioral-identity test**.

## Why Avatar V / Digital Twin

Current HeyGen documentation separates appearance, voice and motion. A Digital Twin is trained from real footage and Avatar V is specifically intended to reuse a person's own gestures, expressions and mannerisms rather than generalized presenter motion.

Official references:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://help.heygen.com/en/articles/8389138-digital-twin-video-avatar-filming-tips`
- `https://help.heygen.com/en/articles/9964694-avatar-looks-explained`
- consent: `https://help.heygen.com/en/articles/12092609-recording-your-consent-video`

## Current product distinction — LOCKED

Do not collapse all HeyGen inputs into a single arbitrary 15-second clip.

Current HeyGen guidance exposes two related but distinct footage roles:

1. **Digital Twin / Video Look source footage** — current filming guidance recommends at least **2 minutes of uninterrupted speech** for a strong Digital Twin; adding a Video Look requires **2+ minutes** of footage with the person's face visible.
2. **Avatar V motion reference** — Avatar V guidance emphasizes about **15 seconds** of representative motion/reference footage as the critical motion-style input.

These are not interchangeable preparation steps.

## Existing source library — INVENTORY PASS 2026-09-18

Source folder:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

Technical inventory passed for all three originals:

| Source | Duration | Resolution | FPS | Codec | Digital Twin >=2 min | Avatar V >=15 s |
|---|---:|---:|---:|---|---|---|
| `SIENA_BRUTO.mp4` | 113.313 s | 1080x1920 | 29.970 | H.264 + AAC | NO | YES |
| `VID_20260819_124008056.mp4` | 282.574 s | 1920x1080 | 30.030 | H.264 + AAC | YES | YES |
| `VID_20260911_140124885.mp4` | 300.352 s | 3840x2160 | 30.009 | HEVC + AAC | YES | YES |

Contact-sheet review established the source hierarchy:

### Primary base source — `VID_20260911_140124885.mp4`

Selected as the **primary Digital Twin / Video Look source** because it gives the strongest combined coverage of face, torso, hands, posture, head movement and normal conversational gesture language while keeping a stable camera and scene.

### Secondary facial source — `VID_20260819_124008056.mp4`

Retained as supplemental facial/microexpression material. The face is large and clear but the framing is too tight to carry the full body-language role.

### Alternate motion/look source — `SIENA_BRUTO.mp4`

Retained as alternate behavioral/motion/look material. It has useful torso/gesture coverage but repeated object handling and occasional foreground occlusion make it weaker as the base source.

## Provider-safe preparation — COMPLETE 2026-09-18

Repository script:

`tools/video-studio/prepare_heygen_digital_twin_primary.ps1`

The user confirmed the preparation completed successfully.

Prepared full-duration upload derivative:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\prepared\joao_heygen_digital_twin_primary_1080p_h264.mp4`

Preparation policy:

- source behavior remains continuous;
- full roughly five-minute performance retained;
- H.264 video + AAC audio;
- 1920x1080 provider-safe MP4;
- no cutting, splicing, looping, retiming, stabilization, interpolation or behavioral editing.

The original 4K HEVC source remains authoritative and must be preserved.

## HeyGen creation flow — NEXT

Current HeyGen guidance says:

1. Open HeyGen and go to `Avatars`.
2. Choose `New Avatar` / `Create New Avatar`.
3. Choose `Clone a Real Person`.
4. Import the prepared upload derivative above.
5. Complete the required consent step with João himself reading the consent text shown by HeyGen.
6. Submit the Digital Twin and wait for processing.

Do **not** record new behavioral footage for this first creation. The purpose is to test the existing representative source library.

## First Avatar V benchmark after creation

Once the Digital Twin is ready:

- use the trained video-based look;
- keep the first scene visually close to the source look;
- use a short **new Portuguese script not spoken in the source footage**;
- do not add a custom motion prompt for the first gate;
- if Advanced Settings exposes a motion-reference selector, use a representative João source rather than a theatrical clip;
- judge behavior separately from voice quality.

Suggested script:

> Hoje eu estava pensando numa coisa simples: quando uma ferramenta começa a exigir mais atenção do que o próprio trabalho, talvez seja hora de rever o caminho e escolher outra solução.

## Pass criteria

The benchmark passes only if both are true:

1. **Visual identity:** the person remains convincingly João.
2. **Behavioral identity:** João recognizes his own mannerisms in the new performance rather than a generic avatar/presenter performance.

Behavioral checks include facial-expression range, eyebrow/eye behavior, head timing, hand/arm gesture language, posture, idle behavior, pauses/emphasis and absence of caricatured or repetitive presenter choreography.

## Failure interpretation

- **Looks right, moves wrong:** behavioral-identity fail; do not paper over with prompt tuning.
- **Moves right, looks wrong:** visual/look pipeline problem; the motion model may still be useful.
- **Both wrong:** reject this Avatar V/Digital Twin route.
- **Both right:** promote it to production-renderer integration and proceed to look/scene flexibility plus final voice-stage integration.

## Evidence to retain

Record provider/model, avatar/profile ID, original source filenames and SHA-256, assigned source roles, selected motion-reference source/time range or provider asset ID, selected look, test script, voice source, generation duration, credit/cost usage, final MP4 and João's separate visual/behavioral verdicts.

## Immediate action

Create the Digital Twin in HeyGen with `joao_heygen_digital_twin_primary_1080p_h264.mp4`, complete the required live consent step and wait for avatar processing. Do not return to Wan/H3/Hunyuan before this personal-avatar route is tested.