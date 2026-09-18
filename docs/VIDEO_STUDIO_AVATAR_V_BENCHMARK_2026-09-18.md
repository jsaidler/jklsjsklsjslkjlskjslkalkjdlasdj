# Local Video Studio — HeyGen Avatar V behavioral-identity benchmark

Date: **2026-09-18**  
Status: **NEXT PRODUCTION BENCHMARK / SOURCE ROLES ASSIGNED / PRIMARY HEYGEN PREP NEXT / NO AVATAR RESULT YET**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

This benchmark tests the requirement that previous static-image + audio renderers did not test:

> Can a generated video use completely new words while preserving João's recognizable expressions, gestures, head movement, posture and delivery rhythm from his real footage?

The benchmark is primarily a **behavioral-identity test**.

## Why Avatar V / Digital Twin

Current HeyGen documentation separates appearance, voice and motion. The Digital Twin is trained from real footage and Avatar V is specifically intended to reuse a person's own gestures, expressions and mannerisms rather than generalized presenter motion.

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

These are not interchangeable preparation steps. The project first inventories and reviews the full originals, then assigns source roles. Only then is a short motion segment selected if the provider UI requires one.

## Existing source library — INVENTORY PASS 2026-09-18

Source folder:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

Technical inventory passed for all three originals:

| Source | Duration | Resolution | FPS | Codec | Digital Twin >=2 min | Avatar V >=15 s |
|---|---:|---:|---:|---|---|---|
| `SIENA_BRUTO.mp4` | 113.313 s | 1080x1920 | 29.970 | H.264 + AAC | NO | YES |
| `VID_20260819_124008056.mp4` | 282.574 s | 1920x1080 | 30.030 | H.264 + AAC | YES | YES |
| `VID_20260911_140124885.mp4` | 300.352 s | 3840x2160 | 30.009 | HEVC + AAC | YES | YES |

Inventory manifest:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\avatar_v_source_inventory.json`

Successful inventory report:

`tools/video-studio/reports/avatar_v_source_inventory_20260918_170817.txt`

Contact sheets were successfully generated for all three sources.

## Contact-sheet review — SOURCE ROLES ASSIGNED

Visual review of the three uploaded contact sheets gives a clear source hierarchy.

### Primary base source — `VID_20260911_140124885.mp4`

Selected as the **primary Digital Twin / Video Look candidate**.

Reasons:

- stable seated upper-body framing;
- both hands repeatedly visible;
- broad but natural facial-expression range;
- useful head-angle variation without obvious profile extremes;
- direct enough camera engagement across the sampled timeline;
- consistent scene and camera position;
- no foreground props repeatedly covering the face;
- body language is visible, not reduced to a talking head;
- longest qualifying source and technically strongest capture at 4K.

Known caution from the contact sheet: the bright window creates backlight/highlight pressure, so the actual video must still be judged for exposure stability. This does not outweigh the behavioral coverage advantage.

### Secondary facial/close-up source — `VID_20260819_124008056.mp4`

Retain as **supplemental facial/microexpression material**, not the primary behavioral source.

Reasons:

- face is large and clear;
- eyeglasses, beard and mouth behavior are easy to inspect;
- however the selfie-like crop contains little upper-body and hand language;
- outdoor illumination/background are less controlled;
- it is weaker for learning full upper-body behavioral identity.

### Alternate motion/look source — `SIENA_BRUTO.mp4`

Retain as **alternate motion/reference/look material**, not the base Digital Twin source.

Reasons:

- useful seated upper-body coverage and a different wardrobe/look;
- some natural hand and posture information is present;
- several sampled moments include photographic objects/cards/camera components moving close to the lens or obscuring face/body regions;
- current HeyGen troubleshooting specifically warns that moving objects and items that leave/re-enter frame can increase duplication/glitch risk;
- duration is also below the current >=2-minute base-source recommendation.

## Provider-safe preparation — NEXT

The selected primary source is 4K HEVC. Preserve the original unchanged, but prepare a provider-safe full-duration derivative before upload:

- 1920x1080;
- H.264;
- AAC;
- full continuous duration;
- no trimming;
- no splicing;
- no looping;
- no stabilization;
- no retiming;
- no interpolation;
- no content edits.

Repository script:

`tools/video-studio/prepare_heygen_digital_twin_primary.ps1`

Default source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

Prepared output:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\prepared\joao_heygen_digital_twin_primary_1080p_h264.mp4`

This conversion is conservative: current HeyGen guidance recommends 1080p as the standard quality target, MP4 is recommended, and provider error guidance explicitly says over-large or unsupported footage should be re-exported/downscaled if ingestion fails. The original 4K HEVC remains authoritative and untouched.

## Source review policy — LOCKED

Source selection is based on representativeness, not maximum motion or maximum resolution.

The strongest base source should show as much as possible of:

- João speaking naturally and continuously;
- normal facial-expression range;
- characteristic head timing;
- typical hand/arm gestures;
- normal posture and idle behavior;
- direct enough gaze for reliable avatar training;
- stable lighting/focus;
- no disruptive cuts inside the useful section;
- clean enough speech audio for provider ingestion.

The contact sheets establish framing/coverage and justify the primary-source assignment. Final behavioral quality still depends on the actual generated Avatar V result; contact sheets do not by themselves prove cadence or motion identity.

## Creation strategy

1. prepare the selected primary source as a 1080p H.264/AAC full-duration upload derivative;
2. create the Digital Twin / Video Look from that full continuous source;
3. retain both other originals as supplemental behavioral evidence and alternate motion/look material;
4. if the current Avatar V UI requests a short motion reference, choose it from the existing behavioral library rather than inventing new motion;
5. complete the required live consent recording;
6. generate one short video with a **new Portuguese script not spoken in the reference material**;
7. use no custom motion prompt for the first gate;
8. judge visual identity and behavioral identity separately.

## First script policy

The test text must be ordinary and should not instruct the avatar to act, smile, be serious, gesture or perform an emotion. The behavior should come from the learned personal motion identity.

Suggested first benchmark text:

> Hoje eu estava pensando numa coisa simples: quando uma ferramenta começa a exigir mais atenção do que o próprio trabalho, talvez seja hora de rever o caminho e escolher outra solução.

If this text appears in any reference source, replace it before generation.

## Voice for first benchmark

The first benchmark may use HeyGen's standalone voice clone if convenient, but voice is scored separately. Do not delay the behavioral-identity gate solely to integrate CosyVoice.

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

1. Pull current `main`.
2. Run `tools/video-studio/prepare_heygen_digital_twin_primary.ps1`.
3. Upload the resulting full-duration 1080p H.264/AAC file as the first Digital Twin / Video Look source.
4. Complete HeyGen's required live consent step.
5. Generate exactly one short Avatar V benchmark with new Portuguese text and no custom motion prompt.
6. Review that output before spending credits on additional looks or motion references.
7. Do not return to Wan/H3/Hunyuan before this personal-avatar route is tested.
