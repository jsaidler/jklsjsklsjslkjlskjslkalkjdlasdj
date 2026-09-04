# Character Animation Production — Living Decision Record

Status: **RefControl is no longer accepted as a direct animation-frame generator. V1 showed strong identity retention but anatomy/prop drift; V2 improved anatomy but collapsed left/right gait phases; V3 restored phase differentiation but produced a catastrophic extra-limb failure (three legs in `pose_01_passing_L_v3`). This establishes a structural reliability ceiling for the current FLUX.2 Klein + RefControl Pose route. The next experiment must use a materially different model architecture, not another RefControl V4.**

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

Canonical Exilada identity reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design master, not the final gameplay sprite.

## Architecture principle

The useful decomposition remains:

`motion/key poses -> explicit structure/control -> controlled character renderer/editor -> gameplay-scale/native-raster translation -> temporal completion if needed -> QA`

The critical new rule is:

**the character renderer/editor must preserve body topology before identity, style, props or gait quality are judged.**

## Mandatory QA order — LOCKED

Every future generated pose/frame must be evaluated in this order:

1. **topology/anatomy count:** exactly one head, one torso, two arms, two hands, two legs, two feet; no extra/duplicated/fused/missing major limbs;
2. **pose adherence:** requested contact/passing/support/swing geometry is actually present;
3. **identity continuity:** same Exilada face, body type, hair mass, clothing language and scars;
4. **prop continuity:** shackles/chains/equipment remain on stable anatomical sides;
5. **visual quality/gameplay readability.**

Failure at level 1 is immediately eliminatory for that output and blocks any downstream praise/approval.

## RefControl research history — FROZEN

### V1

FLUX.2 Klein Base 4B FP8 + RefControl Pose, fixed seed `20260904`, four COCO-18 gait poses, one-shot/no-retry.

Result:

- identity retention: strong;
- four phases: distinct;
- right-foot/toe error: present;
- left-arm inconsistency: present;
- body drift: small;
- chain/shackle drift: present.

Verdict: **CONDITIONAL PASS as research/upstream reference; FAIL as final walk.**

### V2

Changed control geometry + stricter anatomy/continuity prompt while holding model/seed/render settings constant.

Improvements:

- feet better;
- arms better;
- body stability better;
- identity remained strong.

Critical failure:

- `contact_L` ≈ `contact_R`;
- `passing_L` ≈ `passing_R`.

Root cause: opposite phases used nearly identical screen-space silhouettes and relied too heavily on COCO semantic left/right labels.

Verdict: **FAIL as a usable walk.**

### V3

Changed actual screen-space geometry so all four controls had unique color-independent silhouettes.

STEP 8A controls: PASS.

Generated V3 result:

- left/right phase differentiation returned;
- identity remained strong;
- but `pose_01_passing_L_v3` contains **three visible legs / three feet**.

This is a catastrophic topology failure. Secondary chain/shackle drift also remains.

Verdict: **FAIL as a direct animation-frame route.**

### RefControl final decision — LOCKED

Do **not** create a V4, do not prompt-tune, seed-fish, inpaint, or iterate further trying to repair the same class of failure.

RefControl may remain useful only as:

- a pose/identity reference generator for non-final upstream material;
- research history.

It is **rejected as the production direct-frame generator** because it does not guarantee body topology.

## New candidate architecture — Qwen-Image-Edit-2511

The next generative spike must change model class, not merely parameters.

Candidate:

**Qwen-Image-Edit-2511**, local/self-hosted, Apache 2.0.

Why it is materially different:

- it is an image-editing architecture rather than a reference-fusion LoRA attached to a generative base;
- the Qwen-Image-Edit family is designed to preserve source appearance/semantics while applying edits;
- the 2511 revision specifically targets lower image drift, improved character consistency and stronger geometric reasoning;
- the edit family supports keypoint/control conditioning and multi-image inputs;
- ComfyUI has a native Qwen 2511 edit workflow.

### Hardware strategy for RTX 3060 12 GB

Do not attempt the full BF16 model first.

Initial local smoke-test target:

- Qwen-Image-Edit-2511 GGUF quantized transformer;
- start with **Q3_K_M (~9.7 GB transformer)** for VRAM safety;
- text encoder/VAE offloaded as needed to system RAM;
- use existing 48 GB RAM and SSD workspace;
- if and only if topology passes, later evaluate a higher-quality Q4 quant.

Canonical workspace remains:

`Z:\AI\Flux2RefControlSpike`

A new sub-workspace may be created under `Z:\AI\QwenImageEditSpike` rather than contaminating the frozen RefControl evidence.

## Hard next gate — ONE difficult pose only

Do not generate four frames first.

The first Qwen test uses exactly one difficult passing pose — preferably the same structural case that produced the V3 extra leg.

Inputs:

1. canonical `exilada_master.png`;
2. one explicit keypoint/pose control for the difficult passing phase;
3. fixed prompt requiring the same Exilada and exact normal human topology.

One output only. No retry, no seed fishing.

### Acceptance criteria

The single-pose spike passes only if all are true:

- exactly **2 arms / 2 hands / 2 legs / 2 feet**;
- no extra or fused major limb;
- requested passing pose is visibly obeyed;
- Exilada identity/hair/body/clothing remain recognizably stable;
- no catastrophic prop-body fusion.

If this one difficult pose fails topology, **reject Qwen as a direct-frame generator immediately**. Do not start a prompt-tuning loop.

If it passes, only then run the four-pose set.

## Deterministic fallback if Qwen also fails

If the Qwen one-pose topology gate fails, stop testing diffusion-based direct frame synthesis.

Next architecture becomes **deterministic rig-first animation**, where topology and gait are guaranteed by a 2D mesh/skeletal or hidden 3D rig, and generative tools are allowed only for non-topological tasks such as reference, texture/style guidance or downstream native-pixel authoring.

This prevents an endless sequence of models hallucinating limbs while we repeatedly repair prompts.
