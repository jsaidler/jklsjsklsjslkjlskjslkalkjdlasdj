# G3S-B3 — Nude Body Base

Status date: **2026-09-05**

Gate status: **B3-A READY TO RUN / B3-B BLOCKED UNTIL GUIDE REVIEW**

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
- nudity may be framed matter-of-factly, heroically, sensually, erotically, vulnerably or brutally according to scene intent; there is no blanket anti-erotic rule;
- the project references Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell, so erotic charge is a legitimate part of the visual vocabulary rather than something to sanitize away;
- native pixel resolution naturally limits microdetail;
- no censor garment is structurally required;
- clothing removal/damage never requires reconstructing hidden body pixels;
- blood, wounds, scars, wetness and dirt attach to the body owner where appropriate;
- sever/dismemberment operates on the complete body regions, while clothing/accessories inherit or detach according to their own state rules.

The production distinction is **intentional framing**, not mandatory desexualization. Adult attractiveness and erotic charge may coexist with danger, suffering, violence, dirt, wounds and vulnerability.

## Source strategy

The body base must not be extracted by subtraction from `exilada_master.png` or the Qwen composite scaffold.

Allowed inputs are references/constraints only:

- canonical Exilada proportions/identity from `exilada_master.png`;
- G1 gameplay scale/camera constraints;
- deterministic anatomical/topology guides from the validated hidden rig/MPFB infrastructure;
- existing visible skin palette as a color-reference signal, not as proof of hidden anatomy.

The body-base art itself must be a dedicated native 2D source asset.

## B3 implementation plan

B3 is split internally into two bounded steps, but remains one production gate.

### B3-A — deterministic anatomy guide — READY

Create a complete adult female, hairless, unclothed structural reference using the existing deterministic MPFB/hidden-rig infrastructure.

This output is **guide data only**, never final visible art. It provides:

- complete silhouette;
- head/scalp/neck/body continuity;
- limb proportions;
- chest/pelvis/hip anatomy;
- projected joint positions;
- deterministic camera/scale reference.

B3-A deliberately creates **zero** hair, clothing, cuff/shackle or chain objects.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b3_mpfb_bootstrap.py`
- `tools/structured-2d-character-pipeline/g3s_b3a_nude_anatomy_guide.py`
- `tools/structured-2d-character-pipeline/g3s_b3a_contact_sheet.py`
- `tools/structured-2d-character-pipeline/11_run_g3s_b3a_nude_anatomy_guide.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3a_nude_guide`

Expected review artifact:

`g3s_b3a_contact_sheet.png`

The contact sheet must be read as **anatomical/structural reference only**. A 3D-looking guide is not a failure by itself because B3-A does not own final visible pixels.

### B3-B — native body source — BLOCKED UNTIL B3-A REVIEW

Author one native `128×128` persistent body-base source against the approved structural guide.

PASS requires that this 2D asset itself — not the 3D guide — is visually credible as intentional modern pixel art and can stand alone with no hair or clothing.

No animation begins until B3-B passes.

## PASS criteria

### B3-A structural review

1. one complete adult human body with one head/torso, two arms/hands and two legs/feet;
2. no hair object/layer;
3. no clothing/binding object/layer;
4. no cuffs, shackles or chain objects;
5. scalp/head/neck and all body regions are structurally complete;
6. proportions are suitable for the Exilada target and G1 scale;
7. output is clearly marked guide-only.

### B3-B visual body review

1. complete adult anatomy at native `128×128`;
2. no hair pixels;
3. no clothing/binding pixels;
4. no restraint pixels;
5. chest, pelvis, hands and feet read coherently at native 1×;
6. silhouette and proportions remain recognizably Exilada-like;
7. gameplay preview remains readable at `640×360` with the locked ~`128 px` protagonist scale;
8. the source reads as authored pixel art, not a filtered 3D render;
9. output is deterministic and reusable as the base owner for later layers.

Erotic charge is neither a PASS nor FAIL requirement by itself. The body asset must be capable of supporting intentional mature framing without structural censorship or forced neutralization.

## After PASS

Only then proceed to:

- G3S-B4 hair;
- G3S-B5 clothing/restraints/accessories;
- G3S-C motion.

## No-model-search rule

Do not reopen the closed local sprite-model search. B3 uses deterministic anatomy infrastructure and dedicated native source authoring; it is not another diffusion-model experiment.

## Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\11_run_g3s_b3a_nude_anatomy_guide.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3a_nude_guide\g3s_b3a_contact_sheet.png`
