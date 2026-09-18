# Local Video Studio — HeyGen Avatar V behavioral-identity benchmark

Date: **2026-09-18**  
Status: **NEXT PRODUCTION BENCHMARK / THREE BEHAVIORAL SOURCES STAGED / SOURCE INVENTORY NEXT / NO RESULT YET**

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

Current HeyGen guidance exposes two related but distinct requirements:

1. **Digital Twin / Video Look source footage** — current filming guidance recommends at least **2 minutes of uninterrupted speech** for a strong Digital Twin; adding a Video Look requires **2+ minutes** of footage with the person's face visible.
2. **Avatar V motion reference** — Avatar V guidance emphasizes about **15 seconds** of representative motion/reference footage as the critical motion-style input.

These are not interchangeable preparation steps. The project must first determine which of João's existing source videos are suitable for the base Digital Twin/Video Look role and which provide the best motion identity. Only then should any 15-second motion segment be selected.

## Existing source library — CURRENT STATE

João has now placed **three good candidate source videos** under:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

Preserve these originals exactly as supplied. Do not trim, recompress, concatenate or choose a winner automatically.

Repository inventory tool:

`tools/video-studio/inventory_avatar_v_sources.ps1`

The tool:

- scans all three originals;
- records duration, resolution, fps, codecs, audio presence, file size and SHA-256;
- marks whether each source meets the current **2-minute Digital Twin/Video Look** duration gate;
- marks whether each source meets the **15-second Avatar V motion-reference** duration gate;
- creates a 12-frame contact sheet for each video for fast visual inspection;
- writes `avatar_v_source_inventory.json` under the persistent profile review folder;
- does **not** trim or select any source.

The older `prepare_avatar_v_reference.ps1` single-source auto-trimming flow is deprecated and blocked because it would prematurely reduce a multi-video behavioral library to one arbitrary source.

## Source review policy — LOCKED

Source selection is based on representativeness, not maximum motion.

The strongest source should show as much as possible of:

- João speaking naturally and continuously;
- normal facial-expression range;
- characteristic head timing;
- typical hand/arm gestures;
- normal posture and idle behavior;
- direct enough gaze for reliable avatar training;
- stable lighting/focus;
- no disruptive cuts inside the useful section;
- clean enough speech audio for provider ingestion.

Do not choose a source merely because it has the biggest gestures or highest energy. The desired target is **recognizable João behavior**, not theatrical expressiveness.

## Creation strategy after inventory

After technical inventory and visual review:

1. assign the best qualifying long source to the **Digital Twin / Video Look** role when the current HeyGen UI accepts it;
2. retain the other videos as behavioral evidence and alternate motion candidates;
3. choose a representative Avatar V motion reference only after seeing the actual source coverage and current account UI;
4. complete the required live consent recording;
5. generate one short video with a **new Portuguese script not spoken in the reference material**;
6. use no custom motion prompt for the first gate;
7. judge visual identity and behavioral identity separately.

If none of the three existing videos satisfies the base Digital Twin technical requirements, only then decide whether a new recording is necessary. Do not assume that before inventory.

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

Run `tools/video-studio/inventory_avatar_v_sources.ps1` against the three originals already placed in the persistent source folder. Review the resulting technical report and contact sheets before trimming or uploading anything. Do not return to Wan/H3/Hunyuan tuning before this personal-avatar route is tested.
