# Character Animation Production — Living Decision Record

Status: **complete-character spritesheet runtime is locked. Route switching is paused while the retained Moore/SSD branch undergoes a controlled exhaustion/integration audit. Historical bad outputs are not promoted to model-family rejection without a baseline-and-exhaustion protocol.**

Canonical end-to-end production roadmap:

`docs/CHARACTER_PRODUCTION_PIPELINE.md`

This document records animation-specific research/decisions. The exact current operational gate lives in `docs/PROJECT_STATE.md` and `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`.

## Hard production constraints

The animation pipeline must:

- start from the approved complete Exilada initial-state reference;
- preserve adult anatomy, face, long black hair mass, clothing state, scars/restraints and equipment state;
- provide explicit inspectable motion control;
- maintain normal body topology across every frame;
- maintain stable anatomical side assignment for accessories/equipment;
- produce natural locomotion;
- bake body, hair, cloth, jiggle and restraint/accessory motion into complete runtime frames;
- run reproducibly on Windows 11 / RTX 3060 12 GB / ~48 GB RAM;
- avoid routine manual frame-by-frame repainting or hand animation;
- use free/local/self-hosted tools and assets unless explicitly approved otherwise;
- scale to many actions, characters, equipment states and world conditions;
- require no recurring specialist animation-tool operation from the user.

Canonical complete initial-state Exilada reference:

`assets/source/characters/exilada/reference/exilada_master.png`

## Runtime representation — LOCKED

Runtime visible-character layer assembly is abolished.

`offline authoring/control -> complete visible frames -> spritesheet/atlas + metadata -> ordinary sprite playback`

Offline controls may be modular; runtime frames are complete/precomposed.

## Model exhaustion protocol — LOCKED 2026-09-07

A single poor result proves only that a **tested configuration** failed unless stronger evidence exists.

Use these classifications:

- **INFRASTRUCTURE FAIL** — runtime/install/loader/path/OOM/dependency;
- **INTEGRATION FAIL** — incompatible graph/checkpoint/preprocessing/input contract;
- **CONFIGURATION FAIL** — valid run, inadequate result in the tested settings;
- **BLOCKED** — exact route cannot be reproduced with available components/hardware;
- **MODEL/TASK FAIL** — model family/route exhausted under valid conditions and repeatedly fails the decisive requirement.

Before MODEL/TASK FAIL is allowed, where practical:

1. reproduce official/reference baseline behavior in the same local runtime;
2. verify exact loader/checkpoint semantics;
3. verify input preprocessing/domain/registration;
4. test an easy matched project case before maximum complexity;
5. test meaningful parameters one at a time with fixed seed/input;
6. require the same decisive failure across multiple valid configurations.

Controlled sweeps are diagnostics. Random seed hunting/rerolling is not a production strategy.

Cleanup occurs only after genuine abandonment/model-task failure or an explicit decision to discard a blocked route. A configuration failure alone does not justify deleting the workspace.

## Critical integration lesson — runner 30

The project already has direct evidence that integration errors can masquerade as model limitations.

An earlier SSD pose-preprocessing path distorted the 640×360 control into 512×512 with a `1.7778×` relative vertical stretch. Runner 30 corrected the registration and materially improved pose response/lower-limb reconstruction.

Therefore all future model verdicts must explicitly separate model behavior from our preprocessing/integration behavior.

## Current SSD / Moore branch

Exact published Sprite Sheet Diffusion is **BLOCKED**, not visually rejected, because the public weights available to us omit the custom SSD pose-guider checkpoint required by the exact published graph.

Current runnable compatibility reconstruction:

`Moore AnimateAnyone graph + Moore baseline pose guider/motion module + released SSD reference/denoising UNets`

Runner 34 produced a valid complete-character spritesheet but poor temporal behavior. Correct classification:

> **current Moore-compatible SSD configuration quality FAIL; SSD model capability unresolved.**

The next gate is not another art-direction tweak and not another model. It is a component-isolation audit:

`pure Moore baseline -> identical-input SSD UNet substitution -> pose-domain audit -> pose-guider bottleneck diagnosis`

Only after that sequence reaches a repeatable ceiling may we decide whether recovering/retraining a compatible SSD pose guider is justified or whether the public SSD recreation should be closed as BLOCKED/exhausted for our constraints.

## Wan-Animate-2 historical evidence — RECLASSIFIED

Wan-Animate-2 Base INT8 ConvRot was genuinely run locally on 2026-09-04. The tested configuration showed:

- comparatively decent Exilada identity/coarse anatomy retention;
- weak locomotor transfer;
- smooth painted/video-diffusion appearance rather than the desired discrete game-art language.

Those are real negative results for that configuration.

However, the whole Wan model family was closed too quickly. The historical project did not first document a successful official/reference baseline in the exact local runtime and then systematically isolate conditioning/input variables before rejection.

The earlier Wan workspace was already deleted. Do not rebuild it while Moore/SSD remains unexhausted. If Wan is revisited later, the first gate must be official/reference baseline reproduction, not another Exilada art test.

## Other diffusion/edit research history

### RefControl V1

Useful identity retention; failures in feet/toes, arms, body drift and chains. Research evidence only.

### RefControl V2

Improved feet/arms/body stability; opposite gait phases collapsed. Configuration FAIL.

### RefControl V3

Distinct controls returned, but one frame produced three visible legs/feet plus chain/clothing drift. Direct-frame route failed in that tested formulation.

### Qwen-Image-Edit-2509

Paused. May later assist constrained editing/reference work, but is not the current animation gate.

The model-exhaustion protocol applies to these historical routes too if they are reconsidered.

## Motion-source rule — LOCKED

Do not invent final locomotion key poses manually.

Use real motion-capture data, motion extracted from human performance, or a deterministic locomotion solver.

Current retained gait infrastructure uses CMU `105_34 NormalWalk` and the locked 72-degree gameplay-facing projection. Runner 33 V2 is provisional motion timing/body treatment, not final locomotion approval.

## Secondary-motion requirement

Final complete frames must include coherent:

- body motion;
- heavy-hair inertia;
- clothing/binding motion;
- soft-tissue/jiggle where appropriate;
- shackles/chains/restraints/accessories;
- occlusion changes.

Diagnostics may isolate these systems temporarily, but final runtime art may not return to visible layer assembly.

## Mandatory animation QA order

1. integration/input contract;
2. topology across the full sequence;
3. motion/grounding/pose adherence;
4. stable body proportions/anatomical sides;
5. stable attachments/equipment;
6. identity mapping;
7. secondary motion;
8. final game-art quality/readability;
9. loop/cadence suitability.

A single good or bad frame cannot qualify or disqualify a model family.

## Immediate next implementation sequence — LOCKED

Do not install another model yet.

Implement the retained Moore/SSD branch audit in this order:

`pure Moore baseline A -> identical-input SSD-weight substitution B -> pose-domain/registration audit -> pose-guider bottleneck diagnosis -> controlled next experiment within same branch`

Only after that branch is explicitly exhausted may another large model/workspace become the current gate.
