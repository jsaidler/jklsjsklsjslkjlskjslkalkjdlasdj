# Local Video Studio — HeyGen Avatar V behavioral-identity benchmark

Date: **2026-09-18**  
Status: **NEXT PRODUCTION BENCHMARK / REFERENCE FOOTAGE REQUIRED / NO RESULT YET**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

This benchmark tests the requirement that previous static-image + audio renderers did not test:

> Can a generated video use completely new words while preserving João's recognizable expressions, gestures, head movement, posture and delivery rhythm from his real footage?

The benchmark is not primarily a lipsync or resolution test. It is a **behavioral-identity test**.

## Why Avatar V

Current HeyGen documentation describes Avatar V as a personal-avatar model that learns a real human's specific gestures, expressions, mannerisms and motion from a short reference video, then reuses that learned motion identity with new scripts and alternate looks.

Official references:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://www.heygen.com/avatars/avatar-v`
- consent requirements: `https://help.heygen.com/en/articles/12092609-recording-your-consent-video`

## Input policy — LOCKED

Use João's **existing real footage first**. Do not record replacement behavioral footage unless the existing source is rejected technically or the selected segment does not represent João's normal mannerisms.

Preferred motion-reference source characteristics:

- uninterrupted natural speaking;
- at least about 15 seconds for Avatar V;
- face clearly visible;
- upper body and normal hand gestures visible where possible;
- normal João delivery, not deliberately exaggerated performance;
- speech audio present;
- no edits/splices inside the selected motion reference.

If a previously prepared derivative is shorter than the Avatar V target, use the longer original source footage instead of padding/looping it.

## Creation flow

1. In HeyGen, choose `Avatars` -> `Clone a Real Person`.
2. Upload the selected existing João motion-reference footage.
3. Complete the platform-required consent video with the displayed consent text.
4. Create the Digital Twin with Avatar V.
5. Keep the first test look simple and easy to judge; do not introduce a complex new scene before behavioral identity is proven.
6. Use the Avatar V motion-reference/advanced setting where exposed by the current UI.
7. Generate one short video from a **new Portuguese script not spoken in the reference footage**.

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
- avoid strong camera-angle changes.

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
- motion-reference source filename/provider asset ID;
- motion-reference duration;
- selected look ID/source;
- test script;
- voice source/ID;
- generation duration;
- credit/cost usage if visible;
- final MP4;
- user's human verdict for visual identity and behavioral identity separately.

## Immediate action

Use the existing João source footage to create the first Avatar V Digital Twin and generate exactly one neutral new-script benchmark. Do not return to Wan/H3/Hunyuan tuning before this result is reviewed.