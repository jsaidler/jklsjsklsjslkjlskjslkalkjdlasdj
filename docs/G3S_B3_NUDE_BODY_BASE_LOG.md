# G3S-B3 — Nude Body Base

Status date: **2026-09-05**

Gate status: **B3-A V2 PASS/CLOSED — B3-B NATIVE 128×128 BODY SOURCE ACTIVE / REVIEW REQUIRED AFTER RUN**

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

The structured 2D character is built in this order:

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

## B3-A — deterministic anatomy guide

B3-A creates a complete adult female, hairless, unclothed structural reference using the existing deterministic MPFB/hidden-rig infrastructure.

This output is **guide data only**, never final visible art. It provides:

- complete silhouette;
- head/scalp/neck/body continuity;
- limb proportions;
- chest/pelvis/hip anatomy;
- projected joint positions;
- deterministic camera/scale reference.

B3-A deliberately creates **zero** hair, clothing, cuff/shackle or chain objects.

### B3-A V1 — FAIL/CLOSED REVISION

The first B3A run proved the layer/scale mechanics but used `MPFB gender = 1.0`, which in the pinned MPFB semantics resolves male. Therefore it did not satisfy the required adult-female phenotype.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3a_v1_failure.json`

This was a revision failure only. MPFB `2.0.17`, the bootstrap, rig, camera/scale pipeline and zero-layer audit remain active. No model cleanup command applies.

### B3-A V2 — PASS/CLOSED 2026-09-05

The corrected contact sheet passes the structural gate.

Observed/recorded V2 audit:

- revision: `G3S_B3A_NUDE_ANATOMY_GUIDE_V2`;
- macro gender: `0.0`;
- resolved gender: `female`;
- macro age: `0.52`;
- resolved life stage: `adult`;
- female targets: `21`;
- male targets: `0`;
- adult targets: `21`;
- minor targets: `0`;
- complete body geometry: `True`;
- hair objects: `0`;
- clothing objects: `0`;
- restraint objects: `0`;
- chain objects: `0`;
- visible height: `128 px`;
- camera: orthographic `26 deg` pitch, `8 deg` yaw;
- body is clearly marked structural guide only, not final pixel art.

Visual structural review also passes: one complete adult female body, coherent head/neck/torso/limbs/hands/feet, female chest/pelvis/hip silhouette, no hair or equipment, and proportions suitable as an Exilada authoring guide at the locked G1 scale.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3-A is now closed. Do not iterate MPFB body appearance as final art; final visible body pixels belong to B3-B.

## B3-B — native `128×128` nude body source — ACTIVE

B3-B authors the actual persistent visible body source. It is deliberately separated from B3-A so hidden 3D remains structural infrastructure rather than final art authority.

Current V1 authoring route:

- uses the approved B3-A **binary structural mask at the locked 640×360 gameplay raster**;
- crops the body into a `128×128` native asset at 1:1 pixel scale; there is no post-generation resizing;
- does **not** sample or transfer the B3-A lit RGB/shading;
- authors final body RGB through an explicit native palette and deterministic pixel-cluster rules;
- uses projected B3-A joints only as semantic anchors for face/chest/abdomen/pelvis/shoulder/knee clusters;
- owns zero hair, clothing, binding, cuff, shackle or chain pixels;
- outputs a binary-alpha source, mask, gameplay preview, manifest and contact sheet for review.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b3b_native_body_source.py`
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_native_body_source.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_native_body_source`

Expected review artifact:

`g3s_b3b_contact_sheet.png`

### B3-B PASS criteria

1. complete adult anatomy at native `128×128`;
2. no hair pixels;
3. no clothing/binding pixels;
4. no restraint/chain pixels;
5. chest, pelvis, hands and feet read coherently at native 1×;
6. silhouette and proportions remain recognizably Exilada-like;
7. gameplay preview remains readable at `640×360` with the locked ~`128 px` protagonist scale;
8. the source reads as authored modern pixel art, not a filtered/downsampled 3D render;
9. output is deterministic and reusable as the base owner for later layers;
10. no routine manual frame-by-frame repair is introduced.

Erotic charge is neither a PASS nor FAIL requirement by itself. The body asset must be capable of supporting intentional mature framing without structural censorship or forced neutralization.

## After B3-B PASS

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
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\12_run_g3s_b3b_native_body_source.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_native_body_source\g3s_b3b_contact_sheet.png`

or the complete console error if the runner fails.
