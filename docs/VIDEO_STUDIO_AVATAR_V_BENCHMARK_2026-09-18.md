# Local Video Studio — HeyGen Avatar V behavioral-identity benchmark

Date: **2026-09-18**  
Status: **NEXT PRODUCTION BENCHMARK / THREE SOURCES INVENTORIED / CONTACT SHEETS READY / SOURCE ROLE REVIEW NEXT / NO AVATAR RESULT YET**

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

These are not interchangeable preparation steps. The project must first determine which of João's existing source videos are suitable for the base Digital Twin/Video Look role and which provide the best motion identity. Only then should any short motion segment be selected if the provider requires one.

## Existing source library — INVENTORY PASS 2026-09-18

Source folder:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

Technical inventory passed for all three originals:

| Source | Duration | Resolution | FPS | Codec | Digital Twin >=2 min | Avatar V >=15 s |
|---|---:|---:|---:|---|---|---|
| `SIENA_BRUTO.mp4` | 113.313 s | 1080x1920 | 29.970 | H.264 + AAC | NO | YES |
| `VID_20260819_124008056.mp4` | 282.574 s | 1920x1080 | 30.030 | H.264 + AAC | YES | YES |
| `VID_20260911_140124885.mp4` | 300.352 s | 3840x2160 | 30.009 | HEVC + AAC | YES | YES |

Interpretation:

- `VID_20260819_124008056.mp4` and `VID_20260911_140124885.mp4` both clear the current long-footage duration gate for the base Digital Twin / Video Look role.
- `VID_20260911_140124885.mp4` has the strongest technical resolution at 4K, but resolution alone does **not** make it the behavioral winner.
- `SIENA_BRUTO.mp4` is below the current 2-minute base-source gate, but remains valid behavioral/motion-reference material because it is well over 15 seconds.
- Preserve all three originals exactly as supplied.

Inventory manifest:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\avatar_v_source_inventory.json`

Successful inventory report:

`tools/video-studio/reports/avatar_v_source_inventory_20260918_170817.txt`

Contact sheets were successfully generated for all three sources:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\contact_sheets\SIENA_BRUTO_contact.jpg`

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\contact_sheets\VID_20260819_124008056_contact.jpg`

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\contact_sheets\VID_20260911_140124885_contact.jpg`

The earlier contact-sheet generation bug is closed. The patched inventory run produced valid metadata and all three JPG review assets.

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

Contact sheets are only a framing/coverage aid. They cannot determine speech rhythm, timing, gesture language or whether the performance genuinely feels like João. That judgment requires watching the original videos.

Do not choose a source merely because it is 4K, longer, more energetic or contains larger gestures. The target is **recognizable João behavior**.

## Creation strategy after source-role review

After contact-sheet review and actual behavioral review of the originals:

1. assign the strongest qualifying long source to the **Digital Twin / Video Look** role;
2. retain the other long source as alternate behavioral/profile evidence rather than discarding it;
3. retain `SIENA_BRUTO.mp4` as valid motion-reference material even though it is below two minutes;
4. choose a representative Avatar V motion reference only when the current provider UI actually requires/accepts it;
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

1. Review the three contact sheets for framing and visible gesture/body coverage.
2. Review the two long originals and `SIENA_BRUTO.mp4` for actual behavioral representativeness.
3. Select the base Digital Twin source only after that review.
4. Do not trim or upload anything before source roles are settled.
5. Do not return to Wan/H3/Hunyuan before the personal-avatar route is tested.
