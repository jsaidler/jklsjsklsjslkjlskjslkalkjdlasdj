# Local Video Studio — HeyGen Avatar V behavioral-identity benchmark

Date: **2026-09-18**  
Status: **NEXT PRODUCTION BENCHMARK / REFERENCE PREPARATION SCRIPT READY / NO RESULT YET**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

This benchmark tests the requirement that previous static-image + audio renderers did not test:

> Can a generated video use completely new words while preserving João's recognizable expressions, gestures, head movement, posture and delivery rhythm from his real footage?

The benchmark is not primarily a lipsync or resolution test. It is a **behavioral-identity test**.

## Why Avatar V

Current HeyGen documentation describes Avatar V as a personal-avatar model trained from the user's own footage so it can learn that person's specific gestures, expressions, mannerisms, cadence and motion rather than applying generalized motion.

Official references:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://help.heygen.com/en/articles/15544929-avatar-voice-faq-troubleshooting-best-practices-and-credits`
- `https://help.heygen.com/en/articles/8389138-digital-twin-video-avatar-filming-tips`
- `https://www.heygen.com/avatars/avatar-v`
- consent requirements: `https://help.heygen.com/en/articles/12092609-recording-your-consent-video`

Important current-product distinction:

- Avatar V specifically emphasizes a **15-second motion/reference recording** as the critical behavioral input;
- broader Digital Twin guidance also says longer clean footage can improve facial-expression/emotional range;
- therefore the existing ~38-second João source remains valuable as the canonical source, while a representative 15-second uninterrupted segment should be selected for the first Avatar V motion-reference gate.

## Input policy — LOCKED

Use João's **existing real footage first**. Do not record replacement behavioral footage unless the existing source is rejected technically or the selected segment does not represent João's normal mannerisms.

Preferred motion-reference characteristics:

- uninterrupted natural speaking;
- about 15 seconds for the first Avatar V motion-reference gate;
- face clearly visible;
- upper body and normal hand gestures visible where possible;
- normal João delivery, not deliberately exaggerated performance;
- speech audio present;
- no edits/splices inside the selected motion reference.

The source footage may be longer. Do not pad or loop a short derivative. Select a genuine uninterrupted 15-second segment from the original footage.

## Reference preparation — REPOSITORY AUTOMATION

Repository script:

`tools/video-studio/prepare_avatar_v_reference.ps1`

Purpose:

1. locate the existing `IA_TEST.mp4` when it is in the known Video Studio roots, or accept an explicit `-SourceVideo` path;
2. verify that the source contains video + speech audio and is at least 15 seconds long;
3. preserve the full uninterrupted source as a high-quality H.264/AAC canonical upload-safe copy;
4. create three **15-second uninterrupted candidate motion references** from early, middle and late regions of the source;
5. record SHA-256, timing and technical metadata in `avatar_v_reference_manifest.json`;
6. place the persistent behavioral profile under:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\`

Selection rule:

> Choose the candidate that most closely resembles João's **normal** speaking behavior. Do not choose a clip merely because it has the largest gestures or highest energy.

This rule is intentional. HeyGen recommends expressive reference footage because flat footage can become robotic, but the project's previous Wan output was already rejected for caricatured/foreign performance. The benchmark therefore needs recognizable João behavior, not maximum motion intensity.

## Creation flow

1. Prepare the source/candidate files with the repository script.
2. Watch candidate A/B/C once and select the clip that feels most representative of normal João delivery.
3. In HeyGen, choose `Avatars` -> `Clone a Real Person`.
4. Upload the selected existing João footage / motion-reference material as the Digital Twin source according to the current UI.
5. Complete the platform-required consent video with the displayed consent text. This must be recorded by João; do not reuse AI-generated material for consent.
6. Create the Digital Twin.
7. Keep the first test look simple and easy to judge; do not introduce a complex new scene before behavioral identity is proven.
8. In the Avatar V/Advanced Settings motion-reference control, select the representative João video reference.
9. Generate one short video from a **new Portuguese script not spoken in the reference footage**.
10. Do not add a custom motion prompt for the first gate. Avatar V prioritizes audio/reference/image behavior, and prompt-driven choreography would confound the behavioral-identity test.

## First script policy

The test text must be semantically ordinary and must not instruct the avatar to act, gesture, smile, be serious or perform an emotion. Motion should come from the learned personal model rather than theatrical prompting.

Suggested first benchmark text:

> Hoje eu estava pensando numa coisa simples: quando uma ferramenta começa a exigir mais atenção do que o próprio trabalho, talvez seja hora de rever o caminho e escolher outra solução.

If this exact text is found in any reference footage, replace it with another neutral sentence before generation.

## Voice for first benchmark

The first benchmark may use HeyGen's standalone voice clone created from João's material if available. Voice quality is recorded separately and must not obscure the behavioral verdict.

Do not delay the motion-identity benchmark solely to integrate CosyVoice. The goal of this stage is to determine whether Avatar V preserves João's behavior on new text.

## First-look policy

For the first behavioral benchmark:

- use a look close enough to the real footage that visual identity remains easy to judge;
- avoid a dramatic wardrobe change;
- avoid a complex generated set;
- avoid strong camera-angle changes;
- keep gaze/framing close to the behavioral reference.

Only after behavioral identity passes should the project test Avatar V's appearance flexibility across different looks/scenes.

## Pass criteria

The benchmark is a pass only if both are true:

1. **Visual identity:** the person remains convincingly João.
2. **Behavioral identity:** João recognizes his own mannerisms in the new performance rather than a generic avatar/presenter performance.

Behavioral checks:

- facial-expression range resembles João;
- eyebrow/eye behavior is characteristic rather than stock animation;
- head movement timing feels familiar;
- hand/arm gesture language feels familiar;
- posture and idle behavior feel familiar;
- pauses and emphasis produce a plausible João response;
- performance is not caricatured or theatrically exaggerated;
- no generic mirrored/repetitive presenter choreography.

## Failure interpretation

- **Looks right, moves wrong:** behavioral-identity fail; do not paper over with prompt tuning.
- **Moves right, looks wrong:** visual/look pipeline problem; Avatar V motion model may still be useful.
- **Both wrong:** reject Avatar V for the current project route.
- **Both right:** promote Avatar V to production-renderer integration and proceed to look/scene flexibility plus final voice-stage integration.

## Evidence to retain

Record:

- provider/model: HeyGen Avatar V;
- avatar/profile ID where available;
- original source filename + SHA-256;
- selected 15-second motion-reference candidate + SHA-256 + source time range;
- motion-reference provider asset ID where available;
- selected look ID/source;
- test script;
- voice source/ID;
- generation duration;
- credit/cost usage if visible;
- final MP4;
- user's human verdict for visual identity and behavioral identity separately.

## Immediate action

Run `tools/video-studio/prepare_avatar_v_reference.ps1`, review the three 15-second candidates, choose the one that most resembles normal João behavior, and then use it to create the first Avatar V Digital Twin / motion-reference benchmark. Do not return to Wan/H3/Hunyuan tuning before this result is reviewed.