# Character Animation Production — Living Decision Record

Status date: **2026-09-07**

Status: **RAW-VIDEO DUAL-REFERENCE COMPLETE-CHARACTER GENERATION IS THE ACTIVE PRODUCTION CLASS. BODY-POSE-ONLY AND MANUAL RIG/SIMULATION ROUTES ARE RESEARCH-ONLY FOR FINAL PRODUCTION. WAN-ANIMATE-2 MUST BE EXHAUSTED BEFORE SWITCHING; SCAIL-2 IS NEXT OPEN/LOCAL CANDIDATE.**

Canonical screening/protocol:

`docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

Canonical end-to-end project state:

`docs/PROJECT_STATE.md`

## Hard production constraints

The animation pipeline must:

- start from `assets/source/characters/exilada/reference/exilada_master.png` as the complete initial-state appearance reference;
- accept a **separate real driving video** for motion/performance;
- allow the driving performer to differ completely in identity, clothing, hair and accessories;
- preserve the Exilada's face, body proportions, hair mass, clothing state, scars/restraints and accessories across the sequence;
- infer full-body locomotion automatically;
- infer jiggle/soft-body motion automatically;
- infer hair inertia/follow-through automatically;
- infer cloth/material/wind response automatically;
- infer restraint/chain/accessory dynamics automatically;
- require no manual keyframing, rigging, cloth/hair simulation, per-frame repainting, manual masks or frame cleanup;
- run through scripted/reproducible tooling on Windows 11 / RTX 3060 12 GB / ~48 GB RAM where possible;
- prefer free/local/self-hosted tools and assets unless explicitly approved otherwise;
- scale to many actions, characters, equipment states and world conditions;
- output complete visible frames ready for spritesheet packing.

## Final runtime contract

Runtime representation:

`complete generated frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

The runtime never assembles the visible character from body/hair/clothing/equipment layers.

## No-manual rule — LOCKED

The production solution may use automatic preprocessing and automatic postprocessing, but may not require recurring artistic/manual animation work.

Allowed automatic operations:

- resize/crop/frame sampling;
- auto segmentation/mask generation;
- auto background removal;
- auto alpha cleanup that does not involve hand painting;
- automated spritesheet packing;
- automated temporal/identity QA;
- scripted inference parameterization.

Disallowed required operations:

- manual rigging/weight painting;
- manual keyframes;
- manual hair bones;
- manual cloth simulation;
- manual chain simulation;
- manual pose alignment;
- manual mask fixes;
- per-frame repainting;
- hand compositing/cleanup.

## Motion-source rule — UPDATED

Final production motion must come from **real driving video consumed in a richer form than body skeleton alone**.

Internet video is acceptable. Costume matching is not required.

The model is expected to infer target-specific secondary behavior from raw spatiotemporal information plus learned priors.

A skeleton, SMPL sequence or mocap may still be used for diagnostics/research, but cannot be the sole production motion signal because it discards non-rigid information such as hair, cloth, body soft motion, wind and accessory trajectories.

## Model-exhaustion protocol — LOCKED

Do not change model families after a single ugly generation.

Classify failures as:

- infrastructure;
- integration;
- configuration;
- blocked;
- exhausted model/task failure.

Before `EXHAUSTED_FAIL`:

1. reproduce official/reference behavior where practical;
2. validate local loader/checkpoint/input semantics;
3. test the project cross-identity case in controlled stages;
4. change one high-leverage variable at a time;
5. keep seed/input fixed unless stochasticity is itself under test;
6. prohibit manual rescue;
7. require the decisive failure to persist across a finite valid matrix.

## Historical direct-frame diffusion research — FROZEN

### RefControl V1

Strength: strongest Exilada identity retention among early direct-frame tests; controls produced different poses.

Failures: feet/toes, arms, body drift, chain/shackle topology.

Verdict: research reference only.

### RefControl V2

Improved feet/arms/body stability; opposite gait phases collapsed.

Verdict: FAIL configuration/research route.

### RefControl V3

Recovered pose differentiation but produced catastrophic extra-leg/extra-foot topology in one phase.

Verdict: direct per-frame route rejected for production.

### Qwen-Image-Edit-2509

Paused/research-only. A good isolated pose would not solve the complete temporal/non-rigid production contract.

## Deterministic rig / hidden 3D history — SUPERSEDED AS PRODUCTION FOUNDATION

The project previously favored:

`real/procedural motion -> deterministic rig/topology -> deterministic secondary attachments -> semantic passes -> pixel translation`

That path remains useful research infrastructure and topology diagnosis, but it is no longer the final production recommendation because the user explicitly rejects workflows that require manual rigging/simulation/animation work and wants the generative model to infer the complete animated character automatically.

Historical benefits such as stable sockets/topology are acknowledged, but they do not outweigh the no-manual production contract.

## Moore / AnimateAnyone / SSD research status

The current Moore-compatible SSD route:

`Moore AnimateAnyone graph + Moore baseline pose guider/motion module + released SSD reference/denoising UNets`

is not exact published Sprite Sheet Diffusion because the custom SSD pose-guider checkpoint is absent from the public release available to the project.

Runner 34 proved:

- complete-character frames can be generated/packed as a spritesheet;
- Exilada identity can persist reasonably;
- broad body pose can transfer to a degree.

Runner 34 also showed poor hair/cloth/jiggle/chain temporal behavior.

Under the new production contract the more decisive limitation is architectural: body-pose conditioning is not the complete raw spatiotemporal signal required for automatic secondary dynamics.

Therefore Moore/SSD is research-only as the final authoring foundation. Do not spend the next production gate tuning its body skeleton.

## Current production-class candidate 1 — Wan-Animate-2

Wan-Animate-2 directly consumes:

- a reference character image;
- a raw driving video.

It explicitly eliminates intermediate motion extractors, placing it in the correct class for the target problem.

The historical 2026-09-04 project run failed in its tested configuration, but the model was not exhausted.

Audit finding:

- old project run ≈ `384×576`, `17` frames, seed `42`;
- upstream Base config = `640×800`, `37` frames, `16 fps`, `20` steps, base seed `0`;
- upstream Diffusers Base example = `640×800`, 40 steps.

Therefore the prior result is configuration evidence, not a final family verdict.

The old isolated Wan workspace was deleted. A rebuild is permitted only under the finite exhaustion protocol.

### Wan exhaustion stages

- **W0:** official reference + official driver baseline;
- **W1:** same known-good driver, Exilada appearance reference only;
- **W2:** clean real Internet walking driver;
- **W3:** raw-video stress with visible non-rigid dynamics (hair/cloth/wind/body bounce);
- **W4:** finite hypothesis-driven variants only: Base vs Distilled, upstream vs hardware-safe window, one justified quantization tier, documented viewpoint control.

No manual rescue and no seed fishing.

## Next production-class candidate — SCAIL-2

If Wan reaches `EXHAUSTED_FAIL`, test SCAIL-2 next.

Why:

- open-source end-to-end character animation;
- reference image + raw driving video;
- explicitly bypasses skeleton/intermediate motion representations;
- native ComfyUI path;
- automatic SAM3 mask generation can keep the workflow hands-off;
- end-to-end 512p/704p support;
- community Q4_K_M GGUF around 10.9 GB gives a plausible RTX 3060 12 GB path.

Do not install before Wan exhaustion closes.

## External benchmark models

### DreamActor-M2

Pose-free/raw-RGB end-to-end character animation with strong reported benchmark results and fine-grained complex-motion handling.

Not a current production dependency because no public self-hostable weights are available from the research release.

### Kling Video 3.0 Motion Control

Reference image + motion-reference video and strong hosted motion-control capabilities.

Not a current production dependency because it is closed/hosted and outside the locked local/free/self-hosted preference.

## Disqualified final-production classes

Unless materially redesigned to accept rich end-to-end motion rather than body pose only:

- AnimateAnyone / Moore pose-only;
- current public SSD reconstruction;
- MimicMotion;
- UniAnimate-style pose pipelines;
- Animate-X pose representation route;
- Champ SMPL/depth/normal/semantic route;
- MTVCrafter SMPL/3D-motion-token route;
- manual 2D puppet animation;
- manual hidden-3D rig/cloth/hair/chain animation.

They may still provide diagnostic ideas or data, but they do not satisfy the final contract.

## Mandatory complete-sequence QA

Judge every production-class candidate on the entire generated sequence:

1. Exilada identity/face/body proportions;
2. body motion adherence/grounding;
3. limb/hands/feet topology;
4. hair mass persistence and secondary motion;
5. cloth topology and material response;
6. body jiggle/soft response;
7. chains/restraints/accessories attachment coherence;
8. no leakage of the driver's identity/clothing/body shape;
9. stable camera/background suitable for automatic extraction;
10. game-art language at ~128 px gameplay height;
11. loop/segment suitability for spritesheet packing;
12. zero manual repair.

## Immediate next implementation sequence

Do not implement another pose-only runner.

Do not install SCAIL-2 yet.

Next:

`Wan rebuild preflight -> W0 official baseline -> W1 Exilada cross-identity -> W2 Internet walking driver -> W3 secondary-motion stress -> W4 finite variants -> PASS_CANDIDATE or EXHAUSTED_FAIL`

Before any Wan model download, enumerate exact files, approximate sizes, required disk, workspace layout and hardware deviations.
