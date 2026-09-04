# Character Animation Production — Living Decision Record

Status: **FLUX.2 Klein Base 4B FP8 + RefControl Pose remains the strongest character re-posing route tested so far. V1 preserved identity strongly but had anatomy/continuity defects. V2 improved anatomy but failed as a walk because left/right phase pairs collapsed into nearly repeated poses. V3 deterministic controls now PASS: all four gait phases have genuinely different screen-space geometry and unique color-independent silhouette hashes. The immediate next gate is one-shot V3 inference with the V2 correction prompt held constant.**

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

V1 fixed contract:

- four walk key poses;
- `768 × 1024` controls;
- seed `20260904`;
- one generation per pose;
- no retry/inpainting/seed search/interpolation.

Result:

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

V3 changes the actual visible skeleton geometry so opposite gait phases remain different even if COCO colors are removed.

### V3 control names

- `pose_00_contact_L_v3`
- `pose_01_passing_L_v3`
- `pose_02_contact_R_v3`
- `pose_03_passing_R_v3`

### V3 geometry rules

- four genuinely different screen-space limb geometries;
- no crossed-leg X shapes;
- support and swing legs readable directly from silhouette;
- opposite contact phases use physically different stride geometry;
- opposite passing phases use physically different support/swing geometry;
- arm opposition changes with phase;
- slight 3/4 side-facing-right asymmetry retained.

### STEP 8A — V3 controls: PASS

Tool:

`tools/flux2-refcontrol-spike/08_prepare_v3_inputs.ps1`

User-observed execution:

- `generated_v3_poses=4`;
- `silhouette_uniqueness=PASS`;
- no model loaded;
- no inference performed.

Hashes:

- `pose_00_contact_L_v3` — PNG `48f7988c8107c6ac741908d8604347423fe57b18df2c93ebf5f55900333193fa`; silhouette `f24c1ddcd7e396c47e946109465756ae86d57bbdb9d90b9d0caf16bccbf52ba0`;
- `pose_01_passing_L_v3` — PNG `5a06ba6cc32e76da4e1a8aad42e67a8c5a0258cbd9eb7464c54a4800dccfc465`; silhouette `a5e260fb5119d47ca58886d74f982cdcee01906563e7e37b536936b91510ee02`;
- `pose_02_contact_R_v3` — PNG `637ea37ebe25b43134d6374ec3e334646f9034b39c6e6b35be3c2ddb9cd08650`; silhouette `aa94a2f6a7d2908dfb20078aee8146b13b60d0b068342a0b2df89bb0096dfabd`;
- `pose_03_passing_R_v3` — PNG `ff98c35f70f49136c9cb55c0d6f93fdbf5b6d449d164402ee0348ba72dcdc58a`; silhouette `476ff26d61e80d05140eda6c75862280c1fc4adcd96d6159de334c11220d4098`.

Visual QA: **PASS to inference**.

The intended gait semantics are visibly present in geometry:

- contact_L: left leg physically leads;
- passing_L: right supports, left swings;
- contact_R: right leg physically leads;
- passing_R: left supports, right swings.

## STEP 8B — V3 one-shot inference

Runner:

`tools/flux2-refcontrol-spike/09_run_v3.ps1`

Experimental isolation:

**only V3 screen-space skeleton geometry changes relative to the V2 correction run.**

Held constant:

- canonical identity master;
- FLUX.2 Klein Base 4B FP8;
- RefControl Pose LoRA strength `1.0`;
- V2 correction prompt contract;
- seed `20260904`;
- `768×1024`;
- 20 steps;
- CFG 5.0;
- Euler;
- one prompt submission per pose;
- no retry, inpainting, interpolation or seed search.

Runner safeguards:

- safe PowerShell JSON depths only (`<=64`);
- validates `input_manifest_v3.json` revision;
- validates every pose PNG against its spec hash;
- requires four unique binary silhouette hashes;
- refuses to run if V3 sentinel, run manifest or V3 PNG output already exists;
- writes request JSON before submission;
- writes accepted `prompt_id` evidence immediately after each successful submission;
- writes history and final run manifest.

## Workspace — LOCKED

Canonical FLUX workspace:

`Z:\AI\Flux2RefControlSpike`

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Exact next gate

Run exactly once:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\flux2-refcontrol-spike\09_run_v3.ps1" -Workspace "Z:\AI\Flux2RefControlSpike"
```

Then stop and share:

- the four V3 generated images;
- `Z:\AI\Flux2RefControlSpike\run_v3\step8b_v3_run_manifest.json`.

Next QA question:

**Did V3 restore four distinct left/right gait phases while retaining the V2 anatomy gains and strong Exilada identity?**
