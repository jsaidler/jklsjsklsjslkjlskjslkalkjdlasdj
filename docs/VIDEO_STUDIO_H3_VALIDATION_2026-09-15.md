# MiniMax H3 — personal text-to-video functional validation

Date: **2026-09-15**  
Hardware: **Windows 11 / RTX 3060 12 GB / 48 GB RAM**  
Status: **FUNCTIONAL PASS / PRODUCTION QUALITY NOT APPROVED**

Canonical project state: `docs/PROJECT_STATE.md`.  
Active production-quality gate: `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`.

## Scope of this document

This record proves the architecture required by the Local Video Studio. It does **not** certify publication/production visual quality.

The earlier wording `PASS / PRODUCTION HYPOTHESIS VALIDATED` was too broad and is retired. The user explicitly rejected the claim that the generated result had production quality after reviewing the videos.

Canonical classification:

**FUNCTIONAL / ARCHITECTURAL PASS — PRODUCTION QUALITY FAIL / OPEN GATE.**

## Functional goal

Prove locally that the installed H3 stack can generate a new video of the user from persistent identity/voice references without requiring a new recorded performance for each output.

Required functional properties:

1. preserve recognizable identity;
2. produce a convincing version of the user's voice saying new text;
3. synchronize mouth motion to the new speech sufficiently to validate the mechanism;
4. generate body motion without a driving video;
5. place the same person in a scenario different from the source-reference room;
6. execute locally on the RTX 3060.

These are architectural requirements, not the complete production acceptance criteria.

## Source material

A vertical source recording was supplied:

- `IA_TEST.mp4` — 9:16 source recording;
- `IA_TEST.WAV` — matching clean voice recording.

Prepared references:

- `joao_ref_video.mp4` — short visual reference normalized to 24 fps;
- `joao_ref_voice.wav` — voice reference.

Identity stills culminated in:

- `joao_id_face.png`;
- `joao_id_shoulders.png`;
- `joao_id_upperbody.png`.

## Test 1 — video identity/motion + voice

Output:

`MiniMax_H3_00001_.mp4`

Approximate result: 480×864, 24 fps, 124 frames (~5.17 s), fast 4-step path.

Functional result:

- identity: strong pass for the spike;
- temporal face stability: sufficient for the spike;
- voice: **user explicitly judged it good**;
- lip sync: useful functional pass candidate;
- hands/body: sufficient only to continue experimentation;
- independence from source performance: **not proven**.

The generated performance inherited substantial posture/gesture trajectory from the reference video. Therefore this test did not solve the recording-free goal.

## Test 2 — three full-frame identity stills + voice, no driving video

Output:

`MiniMax_H3_00002_.mp4`

Approximate result: 768×1376, 24 fps, ~6.58 s.

Functional result:

- recognizable identity: pass;
- voice: pass, already user-approved;
- autonomous body motion without driving video: **pass**;
- requested new scene: **fail**.

H3 generated new gestures but strongly reconstructed the room visible in the three full-frame identity references. Conclusion: source background carries strong reference authority.

## Test 3 — cropped identity stills + voice, no driving video + new scenario

Output:

`MiniMax_H3_00003_.mp4`

Approximate result: 768×1376, 24 fps, ~6.58 s.

Cropped references reduced background authority and the prompt explicitly defined them as identity-only.

Functional result:

- recognizable identity: **PASS**;
- sufficient identity stability to validate the approach: **PASS**;
- user-approved voice identity: **PASS**;
- new dialogue: **PASS**;
- autonomous body motion: **PASS**;
- no driving video: **PASS**;
- scenario different from source room: **PASS**;
- local RTX 3060 execution: **PASS**.

Production visual-quality result:

**FAIL / NOT APPROVED.**

The result still exhibits visible AI-generation defects. Discussion already identified generic presenter-like gesture language and problematic hand/pose behavior; the complete visual defect set must be judged against the canonical quality checklist rather than inferred away from the functional successes.

## Functional conclusion

The following relation is technically proven:

```text
cropped identity images
+ voice reference
+ new written dialogue
+ target scenario
+ optional appearance/framing
--------------------------------
= new local talking video of the user without a driving performance video
```

This proves feasibility of the workflow only.

It does **not** prove that the current H3/Turbo4 output is ready to publish.

## Engine interpretation

MiniMax H3 remains the first engine candidate because it satisfies the required local architecture and voice/identity mechanism. It is not yet the final production engine.

The next decision must come from a controlled quality ladder:

1. Turbo4 high-resolution baseline;
2. Base20 under identical conditions;
3. Base50 if warranted;
4. stronger canonical identity references if sampling alone does not solve the defects;
5. only then evaluate a different local video/avatar engine if H3 remains visually inadequate.

## Retained rules

- cropped identity references are preferable to full-frame room references for scene independence;
- standalone voice reference remains valid;
- no driving video is required for the normal recording-free hypothesis;
- direct ComfyUI graph operation should not be part of normal end-user use;
- visible human review controls the production verdict.

## Retired claims

Do not repeat any of the following until the quality gate actually passes:

- `production validated`;
- `production preset` for Turbo4;
- `production-ready`;
- `the visual problem is only calibration`;
- `the remaining work is merely UI/productization`.

The current bottleneck is **visual generation quality**.