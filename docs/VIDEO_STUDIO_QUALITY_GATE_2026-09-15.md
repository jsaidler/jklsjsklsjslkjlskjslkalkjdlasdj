# Local Video Studio — production visual-quality gate

Date: **2026-09-15**  
Status: **ACTIVE / PRODUCTION QUALITY NOT APPROVED**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why this gate exists

The first MiniMax H3 tests proved the architecture required by the project: identity can come from still references, voice can come from a persistent audio reference, body motion can be generated without a driving video, and the requested scene can differ from the source-reference room.

That is a functional success, not a production-quality verdict.

The generated clips still contain visual behavior that is not acceptable to promote as finished production. The user explicitly rejected the previous claim that the tested Turbo4 path was production validated.

Canonical classification of the existing tests:

**FUNCTIONAL / ARCHITECTURAL PASS — PRODUCTION QUALITY FAIL / OPEN GATE.**

## Known/open visual concerns

Already identified in discussion:

- generic "AI presenter" hand/arm language;
- hand/pose behavior that can become overly symmetric or synthetic.

The actual MP4s must also be reviewed for every criterion below. This document does not invent a pass for defects that have not yet been resolved.

## Hard acceptance checklist

A production candidate must be acceptable at normal viewing size and under full-resolution frame inspection for all of the following:

1. **Identity** — facial geometry remains recognizably the same person across the full clip.
2. **Eyes / glasses** — no eye drift, double rims, warped lenses, disappearing temples, or frame-to-frame geometry changes that call attention to themselves.
3. **Hair / beard** — no crawling edges, shape changes, texture boiling, or identity-changing hairline/beard behavior.
4. **Mouth / teeth / jaw** — lip sync is natural and the mouth does not become rubbery, over-articulated, melted, or structurally inconsistent.
5. **Hands / fingers / wrists** — no conspicuous anatomy errors, fused fingers, implausible wrists, impossible contact, or unstable finger count/shape.
6. **Arms / shoulders / body topology** — no attachment drift, body-part reconfiguration, or unnatural symmetry.
7. **Performance** — gestures feel human and context-appropriate rather than repetitive, mirrored, generic presenter choreography.
8. **Skin / texture** — no distracting waxy diffusion surface, crawling pore/detail texture, or temporal sharpening/softening pulses.
9. **Clothing** — garment topology, seams, collar, sleeves and material remain coherent through motion.
10. **Scene geometry** — background objects, straight lines and surfaces do not melt, breathe, bend or transform without cause.
11. **Lighting** — face/body/background illumination stays physically coherent rather than flickering or changing direction arbitrarily.
12. **Camera / composition** — framing is stable and follows the requested shot without unexplained zooming/reframing.
13. **Voice / AV sync** — the user's voice identity remains convincing and synchronization does not visibly slip.
14. **Overall release standard** — the clip can be published without manual frame-by-frame repair.

A conspicuous failure in any major category means **production fail**, regardless of whether identity and voice technically work.

## Controlled H3 quality ladder

Do not change multiple variables at once.

Fixed across comparisons:

- `joao_id_face.png`;
- `joao_id_shoulders.png`;
- `joao_id_upperbody.png`;
- `joao_ref_voice.wav`;
- dialogue;
- scenario;
- appearance;
- framing;
- seed;
- 768-class vertical canvas;
- 24 fps;
- same H3 Ref2VA checkpoint and Qwen3-VL/audio/video VAEs.

### Q0 — Turbo4 baseline

Purpose: reproduce the fast functional baseline under the same benchmark prompt.

- Ref2V Turbo LoRA 1.0;
- 4 steps;
- `res_multistep`;
- `simple`;
- `ref_image_size=max`.

Status before benchmark: **functionally proven, production quality not accepted**.

### Q1 — Base20

Purpose: determine whether removing Turbo and increasing denoising work materially improves temporal/detail quality.

- no Turbo LoRA;
- 20 steps;
- `res_multistep`;
- `beta`;
- `ref_image_size=max`.

Decision:

- if clearly worse/equivalent, do not assume Base50 will rescue every defect; inspect the type of failure;
- if materially better but still short of production, proceed to Q2.

### Q2 — Base50

Purpose: test the highest already-established H3 sampling regime before blaming the model family.

- no Turbo LoRA;
- 50 steps;
- `res_multistep`;
- `beta`;
- `ref_image_size=max`.

This can be extremely slow on the RTX 3060. It is justified only as a controlled quality test, not as an automatic default.

## If sampling is not enough

If Base20/Base50 leave the same structural defects, the next experiment is the **identity-reference pack**, not random prompt churn.

Candidate improvements:

1. create a higher-quality neutral-background canonical identity set;
2. use several genuinely different face/head angles rather than three crops from one short recording;
3. include a clean upper-body reference with hands either absent or anatomically unambiguous;
4. retain strict identity-only authority and no source-room authority;
5. compare `ref_image_size=max` with the best sampler path;
6. test whether an image-preparation stage through Qwen/FLUX produces a cleaner identity pack without changing the person's identity.

Only one reference-pack variable should change per comparison.

## When to consider another video engine

A second engine becomes justified when H3 has been tested with:

- Base20;
- Base50 where warranted;
- the strongest reasonable identity-reference pack;
- a controlled prompt;
- the same objective acceptance checklist;

and still exhibits production-blocking visual defects.

At that point, compare candidates on the same task rather than switching because a model is newer or larger.

## Current development priority

The Local Video Studio interface/orchestrator remains useful, but feature development is subordinate to this gate.

Do not prioritize:

- one-minute multi-shot polish;
- subtitle features;
- B-roll automation;
- interface cosmetics;
- additional scene controls;

until a single short shot can pass the production visual-quality standard.

## Required evidence per quality run

Store:

- exact preset and model paths;
- exact prompt;
- identity/voice reference hashes;
- seed;
- frame count / fps / dimensions;
- elapsed time;
- MP4 SHA-256;
- full-resolution MP4;
- human verdict per acceptance category;
- explicit final classification: `PASS`, `FAIL`, or `INCONCLUSIVE`.

No automatic metric may override visible human defects.