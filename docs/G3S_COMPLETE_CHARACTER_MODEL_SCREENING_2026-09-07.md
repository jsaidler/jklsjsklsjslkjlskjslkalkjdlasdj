# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL SCREENING / RAW-VIDEO MOTION CONTRACT LOCKED / WAN-ANIMATE-2 TO BE EXHAUSTED FIRST / SCAIL-2 NEXT OPEN LOCAL CANDIDATE**

## Purpose

Select only model classes capable of generating the Exilada as a **complete animated character** from two distinct references:

1. `exilada_master.png` owns appearance/state;
2. an arbitrary real driving video owns motion/performance.

The driving performer does **not** need to wear the Exilada's costume and may come from an Internet video.

## Hard production contract — LOCKED

A production candidate must:

- accept a complete character reference image and a separate driving video;
- consume motion information richer than a body skeleton alone;
- preserve the target character's appearance as strongly as possible across the sequence;
- infer convincing full-body locomotion and weight transfer;
- infer secondary body motion/jiggle automatically;
- infer long-hair inertia and follow-through automatically;
- infer cloth deformation/lag and material response automatically;
- infer plausible wind/material response when present in the motion/context;
- keep shackles/chains/accessories attached and temporally coherent;
- require **no manual keyframing, rigging, cloth simulation, hair-bone work, frame repaint, per-frame cleanup or manual compositing**;
- permit fully automatic preprocessing such as resize, crop, segmentation/masks or background removal;
- output the whole visible character per frame so it can be packed into a complete-character spritesheet;
- preserve the Exilada/game-art language closely enough to survive native gameplay scale.

Internal physics simulation is not required. The output only needs to exhibit convincing learned physical behavior automatically.

## Immediate consequence for pose-only routes

Body-pose-only methods are not valid final production foundations under this contract because the conditioning signal discards non-rigid motion classes such as hair, cloth, soft-tissue motion, wind and accessory dynamics.

This includes the current Moore/AnimateAnyone + SSD-weight substitution route as a **final complete-motion author**. It may remain useful research/diagnostic evidence for appearance and body-pose transfer, but it is structurally below the required information bandwidth.

## Candidate screening

### A — Wan-Animate-2 / Wan2.2-Animate-2-14B

**Class:** direct raw-driving-video + reference-image character animation.

**Architectural fit:** YES.

The upstream model directly consumes the driving video inside the Diffusion Transformer and explicitly exists to avoid information loss from intermediate motion extractors. This is the correct class for the new contract.

Historical local test result: one configuration failed visually, with weak motion transfer and painted/smoothed output. That test is retained as evidence, but it no longer qualifies as proof that the model family is exhausted.

Important audit finding: the historical project run used approximately `384×576`, `17` frames and seed `42`, while the current upstream Base configuration declares `640×800`, `37` frames, `16 fps`, `20` steps and base seed `0`. The upstream README also shows Base Diffusers inference at `640×800` / `40` steps. Therefore the old local result materially differed from upstream spatial/temporal defaults and was executed through a constrained 12 GB integration.

**Decision:** REOPEN AS A MODEL-EXHAUSTION GATE. Do not call it production-approved. Do not call it disproven.

### B — SCAIL-2

**Class:** end-to-end raw-driving-video + reference-image character animation, Wan2.1 14B backbone.

**Architectural fit:** YES.

SCAIL-2 is explicitly designed to bypass skeleton/intermediate motion representations by concatenating the driving video into the model context. It therefore has access to non-rigid visual dynamics that a pose map discards. Its paper/repository specifically position end-to-end driving as the answer to skeleton ambiguity/information loss.

Operational positives:

- open weights/code;
- Apache/MIT open-source ecosystem depending distribution;
- official/native ComfyUI support (`WanSCAILToVideo`, `SCAIL2ColoredMask`);
- masks can be produced automatically with SAM3, so no manual frame work is required;
- end-to-end driving supports 512p/704p in the official model;
- community GGUF quantizations exist around Q4_K_M ≈10.9 GB, making a 12 GB local proof plausible with offload/memory mapping;
- complete long-video chunking is supported, though the first spritesheet proof only needs a short clip.

Risk:

- still a generative video model, so Exilada pixel/game-art fidelity and chain/detail persistence remain empirical questions;
- a raw video can provide non-rigid dynamics, but successful transfer to *different* target hair/cloth/accessory geometry is not guaranteed.

**Decision:** strongest open/local next candidate if Wan-Animate-2 reaches a documented exhaustion FAIL.

### C — DreamActor-M2

**Class:** pose-free end-to-end RGB driving + reference image through spatiotemporal in-context learning.

**Architectural fit:** EXCELLENT.

The research directly targets the identity-vs-motion tradeoff and reports state-of-the-art results for end-to-end RGB-driven character animation, including complex motions and human-object interaction.

**Operational fit:** NOT CURRENTLY ACCEPTABLE AS LOCAL PRODUCTION FOUNDATION.

No public self-hostable model weights are available from the research project as of this screening; current practical access is hosted/closed API service. Keep as an external quality benchmark unless the project's free/local/self-hosted constraint is explicitly relaxed.

### D — Kling Video 3.0 Motion Control

**Class:** reference image + motion-reference video, closed hosted system.

**Architectural fit:** YES.

**Operational fit:** NOT CURRENTLY ACCEPTABLE under the local/free/self-hosted rule. Keep as external benchmark only.

## Disqualified classes for the final production contract

The following can remain useful research references but are not primary final-author candidates because their motion conditioning is fundamentally pose/SMPL/intermediate-centric and therefore discards exactly the secondary dynamics now required:

- Moore / AnimateAnyone pose-only pipeline;
- current Moore + SSD released-UNet hybrid;
- exact public SSD reconstruction unless a richer motion-conditioning path exists;
- MimicMotion;
- UniAnimate / similar DWPose-driven families;
- Animate-X when used through its extracted motion representation;
- Champ (SMPL/depth/normal/semantic guidance);
- MTVCrafter (3D motion tokens / SMPL-derived motion);
- manual 2D puppet/mesh deformation;
- manual hidden-3D secondary animation.

## Model Exhaustion Protocol — LOCKED

A model family is not rejected because one artistic run looks bad.

A candidate reaches `EXHAUSTED_FAIL` only after the following finite sequence:

1. **Upstream baseline:** reproduce the authors' official reference + official driver through our chosen local integration as closely as hardware allows.
2. **Cross-identity baseline:** keep the official driver, replace only the appearance reference with `exilada_master.png`.
3. **Target locomotion:** use a clean real full-body Internet driving clip that contains the desired walk/performance. No costume match is required.
4. **Secondary-motion stress:** use at least one real driving clip with visible non-rigid dynamics (hair, loose cloth, wind/body bounce) and assess whether the target Exilada automatically develops plausible corresponding dynamics.
5. **Controlled implementation variants only:** test documented high-leverage variants tied to hypotheses (Base vs Distilled, upstream resolution/frame window vs memory-constrained mode, official precision vs one justified quantization, documented reference/motion/viewpoint controls). Keep the seed fixed unless stochasticity itself is the hypothesis.
6. **No manual rescue:** no hand alignment, keyframes, manual masks, repainting, rigging, cloth/hair simulation or per-frame repair. If the route depends on them, it fails the production contract regardless of final prettiness.
7. **No seed fishing:** random-seed search cannot turn a structural fail into a pass.

## Wan-Animate-2 exhaustion order — CURRENT PRIORITY

Because Wan-Animate-2 already belongs to the correct raw-video class and was abandoned after only a constrained configuration, **do not switch models yet**.

Exhaust it first in this order:

### W0 — local integration sanity

Use the official Wan reference image and official driving video. Reproduce upstream behavior through the exact local route selected for the RTX 3060 12 GB machine.

Target upstream Base semantics where feasible:

- `640×800`;
- `37` frames;
- `16 fps`;
- `20` steps for the repo Base config (or the exact documented inference path being tested);
- seed/base seed `0`;
- no cosmetic post-filtering.

If hardware requires quantization/offload, record that as an implementation deviation. A local-integration baseline that cannot reproduce credible official motion cannot fairly judge the Exilada.

### W1 — Exilada cross-identity

Same official driver and model settings. Change only the reference image to `exilada_master.png`.

Question: can the model preserve the complete Exilada state while following the known-good driver?

### W2 — target walking driver

Use a clean real full-body walking video selected from the Internet, ideally fixed camera, single subject, continuous shot, enough framing for full limbs and at least one complete gait cycle.

Question: does the Exilada inherit convincing locomotion without costume matching?

### W3 — secondary-motion stress

Use a real clip that visibly contains body bounce/soft response and non-rigid motion such as long hair, loose cloth or wind.

Question: does the generated Exilada automatically show plausible target-specific hair, cloth, soft-body and restraint dynamics without manual animation?

### W4 — finite high-leverage variants

Only if W0–W3 isolate a fixable tradeoff:

- Base vs Distilled;
- upstream frame/resolution window vs the smallest hardware-safe equivalent;
- one justified higher-quality quantization if memory permits;
- documented viewpoint control when driver orientation differs from locked gameplay facing;
- prompt/caption correction only when it changes a documented appearance/viewpoint condition, not as random cosmetics.

After W4, classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Complete-character QA for every candidate

Every raw-video candidate is judged on the complete sequence, not a hero frame:

1. target identity / face / body proportions;
2. full locomotion adherence and grounding;
3. hands/feet/limb topology;
4. hair mass persistence + inertia/follow-through;
5. cloth topology + lag/folding response;
6. subtle body soft-motion/jiggle when physically expected;
7. restraints/chains/accessories remain attached and temporally plausible;
8. no leakage of the driver's identity, clothing or body shape into the Exilada;
9. no background/camera contamination that prevents spritesheet extraction;
10. result still reads as the approved Exilada/game-art language at about `128 px` gameplay height;
11. loopable/segmentable frames can be automatically extracted and packed as a complete-character spritesheet;
12. zero manual cleanup.

## Current ranking

For the project's current local/self-hosted constraints:

1. **Wan-Animate-2 — exhaust first because it is the correct raw-video class and the previous test was materially constrained.**
2. **SCAIL-2 — strongest new open/local candidate if Wan reaches EXHAUSTED_FAIL.**
3. **DreamActor-M2 — strongest research/hosted benchmark, but not self-hostable from released weights.**
4. **Kling 3.0 Motion Control — hosted benchmark only.**

No additional pose-only model should be installed as the next production candidate.
