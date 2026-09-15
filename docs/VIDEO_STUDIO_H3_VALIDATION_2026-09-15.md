# MiniMax H3 — personal text-to-video validation

Date: **2026-09-15**  
Hardware: **Windows 11 / RTX 3060 12 GB / 48 GB RAM**  
Status: **PASS / PRODUCTION HYPOTHESIS VALIDATED**

This document records the pivot from the former game-motion use of MiniMax H3 to the current personal short-video use.

## Goal

Prove locally that the installed H3 stack can generate a new video of the user from text without requiring a new recorded performance for each output.

Required properties:

1. preserve recognizable identity;
2. produce a convincing version of the user's voice saying new text;
3. synchronize mouth motion to the new speech;
4. generate body motion without a driving video;
5. place the same person in a scenario different from the source-reference room.

## Source material

A new vertical source recording was supplied for the spike:

- `IA_TEST.mp4` — 9:16 source recording;
- `IA_TEST.WAV` — matching clean voice recording.

A short reference segment was prepared as:

- `joao_ref_video.mp4` — ~12 s visual reference, normalized to 24 fps for H3;
- `joao_ref_voice.wav` — matching voice reference.

Later tests extracted identity stills, culminating in cropped identity references:

- `joao_id_face.png`;
- `joao_id_shoulders.png`;
- `joao_id_upperbody.png`.

## Test 1 — video identity/motion + voice

Output supplied back for review:

`MiniMax_H3_00001_.mp4`

Observed output was approximately 480×864, 24 fps, 124 frames (~5.17 s), using the fast 4-step path.

Result:

- identity: strong pass;
- temporal face stability: pass;
- voice: **user explicitly judged it good**;
- lip sync: pass candidate;
- hands/body: acceptable for the test;
- independence from source performance: **not proven**.

The generated performance inherited substantial posture/gesture trajectory from the reference video. This proved H3 could generate the user but not yet that recording a movement reference was unnecessary.

## Test 2 — three full-frame identity stills + voice, no driving video

Output:

`MiniMax_H3_00002_.mp4`

Observed output was approximately 768×1376, 24 fps, ~6.58 s.

Result:

- identity: strong pass;
- voice: pass, already user-approved;
- autonomous body motion without driving video: **pass**;
- requested new scene: **fail**.

H3 generated new gestures but strongly reconstructed the room visible in the three full-frame identity references. Conclusion: the scene in an identity photograph carries substantial reference authority unless explicitly removed from the input representation.

## Test 3 — cropped identity stills + voice, no driving video + new scenario

Output:

`MiniMax_H3_00003_.mp4`

Observed output was approximately 768×1376, 24 fps, ~6.58 s.

The references were changed to crops that preserve identity/anatomy evidence while drastically reducing background evidence. The prompt also explicitly declared those pictures to be identity-only references and rejected visual continuity with their source room.

Result:

- recognizable identity: **PASS**;
- identity stability through shot: **PASS**;
- user-approved voice identity: **PASS**;
- new dialogue: **PASS**;
- autonomous blinking/head/body/hand motion: **PASS**;
- no driving video: **PASS**;
- scenario different from source room: **PASS**;
- local RTX 3060 execution: **PASS**.

## Canonical conclusion

The working production relation is proven:

```text
3 cropped identity images
+ one voice reference
+ new written dialogue
+ target scenario
+ optional appearance/framing
--------------------------------
= new local talking video of the user
```

No per-video movement recording is required for the normal use case.

## Quality interpretation

The pass does **not** claim perfect realism or that the current preset is the global optimum. Residuals include occasional generic "AI presenter" hand language and the need for controlled quality comparisons.

It does establish that MiniMax H3 is fit to become the main engine of the Local Video Studio rather than remaining only a game-motion research model.

## Production decision

- promote MiniMax H3 Ref2VA to active Video Studio engine;
- make cropped identity references + standalone voice the default profile;
- keep driving video out of normal authoring;
- make new-scene separation a hard prompt/input contract;
- use the successful 4-step high-resolution path as the first production preset;
- expose Base20/Base50 only as controlled quality comparisons until they demonstrate a material improvement for this specific use;
- stop requiring the user to operate ComfyUI graphs manually.
