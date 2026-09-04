# Character Animation Production — Living Decision Record

Status: **FLUX.2 Klein Base 4B FP8 + RefControl Pose remains the strongest character re-posing route tested so far, but no walk cycle is approved. V1 preserved identity strongly but had anatomy/continuity defects. V2 improved anatomy but failed because left/right phase pairs collapsed into nearly repeated poses. V3 restored distinct screen-space gait phases, but visual QA exposed a catastrophic extra-limb hallucination: `pose_01_passing_L_v3` contains three legs / three visible feet. Therefore V3 FAILS as a usable walk set. QA order is now locked: gross anatomy/limb count first, gait semantics second, continuity/props third, visual quality last.**

This document is canonical across chats. Update it after every material animation test, PASS/FAIL decision or pipeline change.

## Hard production constraints

The animation pipeline must:

- start from the approved Exilada identity reference;
- preserve adult anatomy, face, long black hair mass, clothing state, scars/restraints and equipment state;
- provide explicit inspectable pose/motion control;
- run reproducibly on Windows 11 / RTX 3060 12 GB / ~48 GB RAM;
- avoid routine manual frame-by-frame repainting, seed fishing and artistic retry loops;
- use free/local/self-hosted code and weights unless explicitly approved otherwise;
- scale to many characters, equipment states and actions.

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

This is the **high-detail identity/design master**, not the final gameplay pixel sprite.

Stable identity anchors:

- adult woman;
- lean functional anatomy;
- severe face;
- very long heavy black hair;
- minimal degraded beige cloth;
- wounds/scars;
- wrist and ankle restraints / broken chains;
- barefoot base state;
- no permanent weapon.

## Architecture

`motion/key poses -> explicit skeletons -> controlled character renderer -> gameplay-scale/native-raster translation -> temporal completion if needed -> QA`

Motion generation and character re-posing are separate problems.

FLUX.2 Klein + RefControl Pose currently owns the **character re-posing** layer. MoMask remains a possible later numeric motion/pose-sequence generator only after the renderer and gameplay-raster representation are stable.

## Mandatory visual-QA order — LOCKED after V3 miss

Every generated character frame must now be evaluated in this order. A frame that fails an earlier layer is not meaningfully judged on later layers.

### QA-0 — gross anatomy / limb-count gate

Immediate FAIL if any of the following occurs:

- more or fewer than two legs;
- more or fewer than two feet;
- more or fewer than two arms;
- more or fewer than two hands;
- duplicated or fused major limb;
- impossible attachment of a limb to pelvis/shoulder;
- catastrophic hand/foot/body fusion.

### QA-1 — requested pose / gait semantics

Only after QA-0 passes:

- target support leg correct;
- target swing/contact leg correct;
- left/right phase visibly distinct;
- foot placement and weight transfer plausible;
- no unintended phase collapse.

### QA-2 — identity and continuity

Only after QA-0/1 pass:

- same Exilada body proportions;
- same face/hair mass;
- same clothing/scars;
- restraints/chains remain on intended anatomical sides;
- no unexplained body-size or topology drift.

### QA-3 — visual quality / gameplay usefulness

Only after QA-0/1/2 pass:

- silhouette quality;
- visual polish;
- pixel-art suitability;
- gameplay-scale readability.

This order is mandatory specifically because the V3 review incorrectly discussed gait quality before noticing an obvious third leg.

## Rejected routes

Do not revive casually:

- Sprite Sheet Diffusion — tested locally; identity/anatomy/motion coherence failed;
- Wan-Animate-2 Base INT8 — tested locally; motion adherence failed;
- generic video diffusion as primary animation architecture;
- manual frame-by-frame repainting;
- paid hosted sprite/interpolation APIs as the default production path;
- one-shot generic sprite-sheet generation.

## RefControl contract

Current local route:

- base: FLUX.2 Klein Base 4B FP8;
- LoRA: `refcontrol-pose-klein-4b.safetensors`;
- text encoder: `qwen_3_4b.safetensors`;
- VAE: `flux2-vae.safetensors`;
- image 1: target OpenPose-style skeleton;
- image 2: Exilada identity reference;
- trigger: `refcontrol`;
- fixed seed: `20260904`.

RefControl expects an **OpenPose-style COCO-18** skeleton. COCO-18 has ankle joints but no toe/heel joints. Foot/toe errors must therefore be attacked by cleaner hip-knee-ankle geometry plus textual orientation constraints.

## V1 — strong identity / structural defects

V1 result:

- runtime: PASS;
- identity retention: strong;
- four phases: distinct;
- right-foot/toe error: present;
- left-arm inconsistency: present;
- body drift: small;
- chain/shackle topology drift: present.

Verdict:

**CONDITIONAL PASS as upstream re-posing route; FAIL as final walk.**

## V2 — anatomy correction / gait collapse

V2 preserved model, reference, seed and render settings, while changing control geometry and adding a stricter anatomy/continuity prompt.

Improvements:

- feet materially better;
- arms materially better;
- body stability better;
- Exilada identity remained strong.

Critical failure:

- `contact_L` and `contact_R` rendered nearly the same;
- `passing_L` and `passing_R` rendered nearly the same.

Root cause — LOCKED:

V2 left/right pairs had nearly identical **screen-space skeleton geometry** and differed mainly through COCO left/right colors/labels. RefControl followed visible geometry more strongly than the semantic side reassignment.

V2 verdict:

**FAIL as a usable walk cycle. Do not expand to eight frames.**

Secondary unresolved defect:

- chain/shackle topology remains inconsistent.

## V3 — structural left/right correction

V3 changed actual visible skeleton geometry so opposite gait phases remained different even if COCO colors were removed.

### STEP 8A — V3 controls: PASS

Tool:

`tools/flux2-refcontrol-spike/08_prepare_v3_inputs.ps1`

Observed preparation:

- `generated_v3_poses=4`;
- `silhouette_uniqueness=PASS`;
- no model loaded;
- no inference performed.

Hashes:

- `pose_00_contact_L_v3` — PNG `48f7988c8107c6ac741908d8604347423fe57b18df2c93ebf5f55900333193fa`; silhouette `f24c1ddcd7e396c47e946109465756ae86d57bbdb9d90b9d0caf16bccbf52ba0`;
- `pose_01_passing_L_v3` — PNG `5a06ba6cc32e76da4e1a8aad42e67a8c5a0258cbd9eb7464c54a4800dccfc465`; silhouette `a5e260fb5119d47ca58886d74f982cdcee01906563e7e37b536936b91510ee02`;
- `pose_02_contact_R_v3` — PNG `637ea37ebe25b43134d6374ec3e334646f9034b39c6e6b35be3c2ddb9cd08650`; silhouette `aa94a2f6a7d2908dfb20078aee8146b13b60d0b068342a0b2df89bb0096dfabd`;
- `pose_03_passing_R_v3` — PNG `ff98c35f70f49136c9cb55c0d6f93fdbf5b6d449d164402ee0348ba72dcdc58a`; silhouette `476ff26d61e80d05140eda6c75862280c1fc4adcd96d6159de334c11220d4098`.

Control-level verdict: **PASS** — four genuinely different screen-space silhouettes.

### STEP 8B — V3 inference: completed, visual set FAIL

The user produced four V3 character outputs.

Positive result:

- V3 did restore visible left/right phase differentiation; the V2 two-pose collapse did not recur.

Catastrophic failure:

- `pose_01_passing_L_v3` contains **three legs / three visible feet**;
- this is an immediate QA-0 gross-anatomy FAIL and invalidates the frame regardless of gait/readability quality.

Other unresolved issues visible across V3 remain secondary to QA-0:

- chain/shackle topology still varies;
- some passing-pose anatomy remains awkward;
- fine body/prop continuity is not yet production-stable.

V3 verdict:

**FAIL as a usable walk set.**

Important research conclusion:

**Distinct control geometry can restore phase differentiation, but FLUX.2 Klein + RefControl Pose still does not guarantee one-to-one major-limb topology. Extra-limb hallucination remains a production-blocking risk.**

## Workspace — LOCKED

Canonical FLUX workspace:

`Z:\AI\Flux2RefControlSpike`

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Exact next gate

Do **not** expand to eight frames and do **not** approve any V3 frame set yet.

Before another inference round, decide how to handle major-limb topology failures. Any next experiment must explicitly target the extra-limb risk and retain the new mandatory QA-0 limb-count gate.

The next route should be chosen from evidence, not by simply rerunning V3 with another seed.
