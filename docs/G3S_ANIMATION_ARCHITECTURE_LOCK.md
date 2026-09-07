# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / LOCKED — COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME; RAW-VIDEO DUAL-REFERENCE AUTHORING REQUIRED; NO MANUAL ANIMATION/CLEANUP; WAN-ANIMATE-2 EXHAUSTION ACTIVE**

## Presentation lock

The game uses an elevated arcade beat'em-up / belt-scroller false-3D presentation:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall at gameplay scale;
- first canonical locomotion family is screen-left and mostly lateral/three-quarter;
- current facing baseline = `72 deg` azimuth from travel heading (`90 deg` pure side).

## Final runtime representation — LOCKED

The runtime consumes **complete, already-composed character frames**:

`complete authored frames -> complete-character spritesheet PNG(s) + metadata -> ordinary sprite playback`

Every runtime frame contains the whole visible character state for that animation/variant. The runtime does **not** assemble the visible character from body/hair/clothing/armor/accessory layers.

Runtime character-layer assembly is **ABOLISHED/CLOSED**.

## Complete-frame motion requirement — LOCKED

A valid exported animation must bake the whole visible motion state, including where present:

- body locomotion and weight transfer;
- soft-tissue/jiggle motion;
- hair secondary motion;
- base-clothing/binding motion;
- material/wind response;
- shackles/chains/restraints motion;
- accessories visible in the chosen state;
- all occlusion changes produced by those motions.

A body-only animation may be used as an internal diagnostic, but it is never the final/runtime sprite artifact.

## Initial Exilada state — LOCKED

Canonical initial-state visual reference:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines the Exilada's **entire initial visible state** for current animation production.

## Dual-reference authoring contract — LOCKED 2026-09-07

The production animation model must receive two distinct semantic sources:

1. **appearance reference:** `exilada_master.png`;
2. **motion reference:** a real driving video.

The motion performer may be unrelated to the Exilada and may come from arbitrary Internet footage. Matching costume, hair, body identity or accessories is not required.

The model must use motion information richer than a skeleton/body-pose sequence. The intended class is raw-video or equivalently dense end-to-end motion conditioning capable of carrying non-rigid temporal information.

The target behavior is automatic learned inference of:

- locomotion and body dynamics;
- jiggle/soft response;
- long-hair inertia;
- cloth lag/folding/material response;
- wind effects where visible/appropriate;
- restraints/chains/accessories follow-through.

The internal mechanism does not need to be a literal physics solver. The output must merely be convincing and automatic.

## No-manual-production rule — LOCKED 2026-09-07

Any route that requires routine manual character-animation work is unsuitable as the production foundation.

Disallowed as required production steps:

- manual rigging/weight painting;
- manual keyframing;
- manual hair-bone animation;
- manual cloth simulation setup/repair;
- manual chain animation;
- manual pose alignment;
- manual mask correction;
- per-frame repainting/retouching;
- hand compositing or frame cleanup.

Allowed:

- fully scripted installation/inference;
- automatic crop/resize;
- automatic segmentation/mask generation;
- automatic background removal;
- automatic frame extraction/spritesheet packing;
- deterministic scripted QA/metadata.

## Equipment / armor variation — OPEN LATER GATE

Armor/equipment/accessory/damage variation remains an offline state-generation problem. Each runtime artifact still exports as a complete precomposed character spritesheet family/state.

## Model-exhaustion rule — LOCKED

Do not switch model families because one configuration produces a bad result.

A model can reach `MODEL/TASK FAIL` / `EXHAUSTED_FAIL` only after:

1. official/reference behavior is reproduced locally where practical;
2. loader/checkpoint/integration semantics are verified;
3. input-domain correctness is verified;
4. project cross-identity task is tested in controlled stages;
5. meaningful high-leverage variants are tested with fixed seed/input and one variable at a time;
6. the decisive failure persists;
7. no manual rescue is used.

## Runner 34 / Moore+SSD — RESEARCH RESULT

Runner 34 proved the complete-character export architecture:

- full-character frames from the complete master;
- RGBA transparency;
- complete-character spritesheet + metadata;
- ordinary sprite playback.

The visible temporal result was poor for production.

More importantly, the current Moore/AnimateAnyone route is conditioned primarily through body pose. Under the new dual-reference/raw-video requirement it is **not eligible as the final production authoring foundation**, regardless of whether more pose tuning could improve body locomotion.

Reason: pose maps discard exactly the non-rigid temporal information the final model must exploit — hair, cloth, jiggle, wind/material and accessory dynamics.

Retain Moore/SSD as research evidence for appearance/pose transfer. Exact public SSD remains separately BLOCKED by the missing custom SSD pose-guider checkpoint.

## Wan-Animate-2 — CURRENT MODEL EXHAUSTION TARGET

Wan-Animate-2 belongs to the required class because it directly consumes a character reference image and the raw driving video, explicitly avoiding intermediate motion extractors.

The historical 2026-09-04 project result remains a failed **configuration**, not an exhausted model family.

Audit finding:

- historical local run: approximately `384×576`, `17` frames, seed `42`;
- upstream Base config currently declares `640×800`, `37` frames, `16 fps`, `20` steps and base seed `0`;
- upstream Diffusers Base example uses `640×800`, 40 steps.

The old local test therefore materially differed from upstream spatial/temporal defaults and ran under a heavily constrained RTX 3060 12 GB integration.

The old Wan workspace was deleted prematurely. Rebuild is permitted now **only as part of the finite exhaustion protocol** documented in:

`docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

## SCAIL-2 — NEXT OPEN/LOCAL CANDIDATE

If Wan-Animate-2 reaches `EXHAUSTED_FAIL`, SCAIL-2 is the next selected candidate because it also supports end-to-end raw driving video + reference-image animation while explicitly bypassing pose/skeleton intermediates.

Operationally relevant properties:

- open model/code;
- native ComfyUI integration;
- automatic SAM3 mask path;
- official end-to-end driving at 512p/704p;
- community Q4_K_M GGUF around 10.9 GB makes a 12 GB proof plausible.

Do not install it before the Wan exhaustion gate closes.

## External benchmark class

DreamActor-M2 and Kling Video 3.0 Motion Control satisfy much of the semantic dual-reference requirement but are not current local/self-hosted production dependencies. They may serve as quality benchmarks unless the deployment constraint is explicitly relaxed.

## Closed routes / assumptions

Closed unless explicitly reopened:

- runtime construction of the visible character from body/hair/clothing/equipment layers;
- body-pose-only animation as the final complete-motion production solution;
- manual hidden-3D/2D secondary animation as a production requirement;
- hidden 3D render as final visible pixel art;
- independent unconstrained full-body redraw per frame;
- C0 nearest-segment hard partition as production route;
- single-still whole-body chain/cage warp as gait solution;
- MPFB skinned body as mandatory visible guide;
- implicit return to isometric/multi-directional character production.

## Current validation question

> Can Wan-Animate-2, when tested close to its intended raw-video operating regime and without manual rescue, preserve the complete Exilada while automatically transferring full body and non-rigid secondary dynamics strongly enough to produce a usable complete-character spritesheet?

If the finite Wan exhaustion matrix answers no, move to SCAIL-2 rather than another pose-only model.
