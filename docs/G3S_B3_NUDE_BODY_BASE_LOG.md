# G3S-B3 — Nude Body Base

Status date: **2026-09-05**

Gate status: **PLANNED / IMPLEMENTATION NEXT**

## Why this gate exists

G3S-B2 proved the correct layer architecture but also proved that the composite master cannot be converted into a complete body by simply subtracting hair and clothing.

Measured B2 facts:

- source opaque pixels: `2974`;
- currently visible body pixels: `1538`;
- hair pixels: `826`;
- clothing pixels: `610`;
- body pixels still hidden/unknown under hair or clothing: `1205`.

Therefore the body base must be authored as an independent asset. The current master remains a design/proportion reference only; it is not a source from which hidden skin can be recovered mechanically.

Approval marker for B2:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

## Locked stage order

The structured 2D character is now built in this order:

1. **G3S-B3 — complete nude body base, no hair, no clothing, no restraints.**
2. **G3S-B4 — hair authored as its own persistent asset/layer family.**
3. **G3S-B5 — clothing, bindings, cuffs/shackles and chain pieces authored as independent equipment/accessory layers.**
4. **G3S-C — layered four-phase walk proof.**

Do not compose hair, clothing or restraints before the nude body base is visually accepted.

## Body-base ownership — LOCKED

The body base is the complete persistent adult anatomy. It must:

- exist under every removable garment and every hair mass;
- remain complete when all equipment layers are removed;
- contain no hair pixels;
- contain no clothing/binding pixels;
- contain no shackle/chain pixels;
- own skin, anatomical silhouette and permanent body-side identity;
- expose stable body-region and limb ownership for damage/gore systems;
- be reusable by all later outfit/equipment states.

A separate face-detail layer may remain replaceable, but the head/scalp/neck skin base still belongs to the complete body.

## Nudity — canonical production handling

Nudity is a normal supported character state in this mature game world. It is **not** implemented as a special alternate sprite and is not generated on demand.

Runtime composition is simply:

`body base + optional hair + optional body-state overlays + zero or more clothing/equipment/accessory layers`

A fully nude state is therefore the same persistent body base with garment/equipment layers omitted.

Production consequences:

- the body must be anatomically complete at gameplay scale, including chest and pelvic anatomy required for a coherent adult human silhouette;
- representation remains matter-of-fact and non-erotic;
- native pixel resolution naturally limits microdetail;
- no censor garment is structurally required;
- clothing removal/damage never requires reconstructing hidden body pixels;
- blood, wounds, scars, wetness and dirt attach to the body owner where appropriate;
- sever/dismemberment operates on the complete body regions, while clothing/accessories inherit or detach according to their own state rules.

## Source strategy

The body base must not be extracted by subtraction from `exilada_master.png` or the Qwen composite scaffold.

Allowed inputs are references/constraints only:

- canonical Exilada proportions/identity from `exilada_master.png`;
- G1 gameplay scale/camera constraints;
- deterministic anatomical/topology guides from the validated hidden rig/MPFB infrastructure;
- existing visible skin palette as a color-reference signal, not as proof of hidden anatomy.

The body-base art itself must be a dedicated native 2D source asset.

## B3 implementation plan

B3 is split internally into two bounded steps, but remains one production gate:

### B3-A — deterministic anatomy guide

Create a complete adult female, hairless, unclothed structural reference using the existing deterministic MPFB/hidden-rig infrastructure.

This output is **guide data only**, never final visible art. It provides:

- complete silhouette;
- head/scalp/neck/body continuity;
- limb proportions;
- chest/pelvis/hip anatomy;
- body-region IDs;
- pivots/joints/sockets;
- depth and occlusion reference.

### B3-B — native body source

Author one native `128×128` persistent body-base source against that guide.

PASS requires that this 2D asset itself — not the 3D guide — is visually credible as intentional modern pixel art and can stand alone with no hair or clothing.

No animation begins until B3-B passes.

## PASS criteria

Review order:

1. one complete adult human body with one head/torso, two arms/hands and two legs/feet;
2. no hair pixels;
3. no clothing/binding pixels;
4. no cuffs, shackles or chain pixels;
5. scalp/head/neck and all body regions are complete rather than holes left by removed layers;
6. chest, pelvis, hands and feet read as coherent adult anatomy at native 1×;
7. silhouette and proportions remain recognizably Exilada-like;
8. body remains readable at `640×360` with the locked ~`128 px` protagonist scale;
9. the native 2D source reads as authored pixel art, not a filtered 3D render;
10. output is deterministic and reusable as the base owner for later layers.

## After PASS

Only then proceed to:

- G3S-B4 hair;
- G3S-B5 clothing/restraints/accessories;
- G3S-C motion.

## No-model-search rule

Do not reopen the closed local sprite-model search. B3 uses deterministic anatomy infrastructure and dedicated native source authoring; it is not another diffusion-model experiment.
