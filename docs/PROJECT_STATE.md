# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/PIXEL_ART_PRODUCTION.md`
6. `docs/ANIMATION_PIPELINE.md`
7. current tooling under `tools/`

After every material step: update thematic docs + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity

The game is a **systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a living world**.

Immediate gameplay baseline: **elevated 2D belt-scroller / false 3D**.

Character-art/animation feasibility remains the current priority because it is the largest production risk; code capability is not the current unknown.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite. Final visible art remains true modern pixel art; simple high-resolution generation followed by resize/quantization is not accepted as the final-sprite route.

## RefControl direct-frame route — REJECTED

FLUX.2 Klein + RefControl Pose was the strongest identity-preserving route tested, but it has now reached a structural reliability limit.

### V1

Strengths:

- strong Exilada identity retention;
- four gait phases visibly distinct.

Defects:

- right-foot/toe error;
- left-arm inconsistency;
- small body drift;
- chain/shackle topology drift.

Verdict: **CONDITIONAL PASS as research/upstream reference; FAIL as final walk.**

### V2

Improvements:

- feet better;
- arms better;
- body stability better;
- identity remained strong.

Critical failure:

- `contact_L` and `contact_R` collapsed to nearly the same pose;
- `passing_L` and `passing_R` collapsed to nearly the same pose.

Root cause: opposite phases used nearly identical screen-space geometry and relied too heavily on COCO left/right semantics.

Verdict: **FAIL as walk.**

### V3

STEP 8A control preparation passed with four unique color-independent silhouettes and restored real left/right phase geometry.

Generated result restored phase differentiation but produced a catastrophic anatomy error:

- `pose_01_passing_L_v3` contains **three visible legs / three feet**.

This is a level-1 topology failure. Chain/shackle drift also remains.

Verdict: **FAIL as direct animation-frame generation.**

### Locked decision

Do **not** create a RefControl V4. Do not prompt-tune, seed-fish, inpaint, or continue repairing the same route.

RefControl is frozen as research history / possible non-final pose-reference support only.

It is **rejected as the production direct-frame generator** because it does not reliably preserve body topology.

## Mandatory QA order — LOCKED

Future generated character frames are judged in this order:

1. exactly one head/torso, two arms, two hands, two legs, two feet; no extra/missing/fused major limbs;
2. pose/gait adherence;
3. identity continuity;
4. prop/equipment continuity;
5. visual quality/gameplay readability.

Failure at step 1 immediately fails the output.

## New active animation feasibility candidate

### Qwen-Image-Edit-2511

The next experiment changes model architecture rather than tweaking RefControl.

Why this candidate:

- image-editing architecture instead of reference-fusion LoRA generation;
- designed to preserve source appearance/semantics during edits;
- 2511 targets lower drift, improved character consistency and stronger geometric reasoning;
- Qwen-Image-Edit supports keypoint/control conditioning and multi-image editing;
- ComfyUI has a native Qwen 2511 image-edit workflow.

### Target-machine strategy

Machine:

- Windows 11;
- RTX 3060 12 GB;
- ~48 GB RAM;
- SSD workspace available.

Do not start with full BF16.

Initial smoke-test target:

- Qwen-Image-Edit-2511 GGUF;
- **Q3_K_M (~9.7 GB transformer)** for VRAM safety;
- offload text encoder/VAE to RAM as needed;
- new workspace recommended: `Z:\AI\QwenImageEditSpike`.

If topology passes, a higher-quality Q4 quant may be evaluated later.

## Exact next gate

Do **one difficult passing pose only**, using the canonical Exilada master and explicit pose/keypoint control.

No four-pose batch yet. No retry. No seed fishing.

Pass requires:

- exactly 2 arms / 2 hands / 2 legs / 2 feet;
- no extra/fused/missing major limb;
- requested passing pose obeyed;
- Exilada identity/hair/body/clothing recognizably preserved;
- no catastrophic prop/body fusion.

If that single difficult pose fails topology, **reject Qwen immediately as a direct-frame generator**. Do not begin prompt iteration.

If it passes, only then run the four-pose set.

## Deterministic fallback — already defined

If Qwen also fails the one-pose topology gate, stop testing diffusion-based direct frame synthesis.

Next architecture becomes **deterministic rig-first animation** (2D mesh/skeletal or hidden 3D rig), guaranteeing body topology and gait mechanically. Generative tools may then assist only in non-topological tasks such as concept/reference, texture/style guidance or final native-pixel authoring.

This is the hard stop that prevents endless repetition of limb-hallucination experiments.

## Workspace state

Frozen RefControl workspace:

`Z:\AI\Flux2RefControlSpike`

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

Proposed new Qwen spike workspace:

`Z:\AI\QwenImageEditSpike`

## Gameplay-scale / Production Pixel Master gate — queued

Gameplay-scale/native-raster validation remains queued until an upstream animation representation passes the topology/pose gate.

High-resolution AI outputs remain motion/identity references unless and until a separate native-grid production route is validated.
