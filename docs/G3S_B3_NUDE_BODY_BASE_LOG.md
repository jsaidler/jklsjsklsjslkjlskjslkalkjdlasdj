# G3S-B3 — Nude Body Base

Status date: **2026-09-05**

Gate status: **B3-A V2 PASS/CLOSED — B3-B V1 3D-MASK ROUTE FAIL/CLOSED — CORRECT B3-B 2D SOURCE METHOD NOT YET IMPLEMENTED**

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

Runtime composition is:

`body base + optional hair + optional body-state overlays + zero or more clothing/equipment/accessory layers`

A fully nude state is therefore the same persistent body base with garment/equipment layers omitted.

Production consequences:

- the body must be anatomically complete at gameplay scale, including chest and pelvic anatomy required for a coherent adult human silhouette;
- nudity may be matter-of-fact, heroic, sensual, erotic, vulnerable or brutal according to scene intent;
- the project references Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell, so erotic charge is a legitimate part of the visual vocabulary;
- no censor garment is structurally required;
- clothing removal/damage never requires reconstructing hidden body pixels;
- blood, wounds, scars, wetness and dirt attach to the body owner where appropriate;
- sever/dismemberment operates on the complete body regions while clothing/accessories inherit or detach according to their own state rules.

## Source strategy — LOCKED

The body base must not be extracted by subtraction from `exilada_master.png` or the Qwen composite scaffold.

Allowed inputs are references/constraints only:

- canonical Exilada proportions/identity from `exilada_master.png`;
- G1 gameplay scale/camera constraints;
- deterministic anatomical/topology guides from the validated hidden rig/MPFB infrastructure;
- existing visible skin palette as a color-reference signal, not as proof of hidden anatomy.

The body-base art itself must be a **dedicated native 2D sprite asset**.

## Visible-ownership invariant — LOCKED

The G3V failure is authoritative here.

Hidden 3D was explicitly demoted from visible-image ownership. It may provide:

- real motion;
- topology;
- left/right identity;
- projected joints;
- sockets;
- depth/occlusion guides;
- physics and secondary-motion drivers;
- anatomy/proportion references.

It may **not** own the final visible body silhouette or RGB.

Therefore a projected 3D render or binary mask is a guide, not a sprite template. A final sprite cannot be created by directly copying that mask and recoloring it.

## B3-A — deterministic anatomy guide

B3-A creates a complete adult female, hairless, unclothed structural reference using the existing deterministic MPFB/hidden-rig infrastructure.

This output is **guide data only**, never final visible art. It provides:

- complete body continuity;
- adult-female anatomy reference;
- limb proportions;
- chest/pelvis/hip reference;
- projected joint positions;
- deterministic camera/scale reference.

### B3-A V1 — FAIL/CLOSED REVISION

The first B3A run used `MPFB gender = 1.0`, which resolves male in the pinned MPFB semantics. This was a revision failure only.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3a_v1_failure.json`

MPFB `2.0.17` remains active structural infrastructure; no model cleanup command applies.

### B3-A V2 — PASS/CLOSED 2026-09-05

The corrected guide passes the structural gate.

Recorded V2 audit:

- revision: `G3S_B3A_NUDE_ANATOMY_GUIDE_V2`;
- resolved gender: `female`;
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
- camera: orthographic `26 deg` pitch, `8 deg` guide yaw;
- art authority: guide only, not final pixel art.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3-A is now closed. Do not iterate the MPFB body as visible art.

## B3-B V1 — FAIL/CLOSED ROUTE 2026-09-05

A first B3B implementation was briefly added after B3A review, then rejected on canonical-architecture review **before the user ran it**.

The V1 code:

1. loaded the B3A binary body mask;
2. cropped that projected mask directly into a native `128×128` alpha silhouette;
3. used the same mask as the body coverage owner;
4. procedurally applied a small skin palette and anatomy accents with Python/Pillow/Numpy rules.

This is not acceptable merely because the lit 3D RGB was not copied.

### Why it fails

The direct mask copy means the hidden 3D projection still owns the final visible silhouette. The subsequent procedural coloring also revives the previously rejected mannequin-style Python/Pillow art-authoring route.

That violates:

- `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`: hidden 3D is demoted from visible-image owner and retained only as motion/topology/guide infrastructure;
- `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`: final visible character pixels are owned by persistent structured 2D assets;
- `docs/PIXEL_ART_PRODUCTION.md`: primitive Python/Pillow artistic mannequin authoring is not an accepted final character-art route.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

The invalid files were removed from `main`:

- `tools/structured-2d-character-pipeline/g3s_b3b_native_body_source.py`;
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_native_body_source.ps1`.

No model was downloaded or discarded by this correction, so no model-file cleanup command applies.

## B3-B — CURRENT CORRECT REQUIREMENT

B3-B must author one genuine native `128×128` persistent **2D nude body sprite source**.

### Allowed role of B3A

B3A may be consulted for:

- anatomy reference;
- adult-female proportion reference;
- joint/topology reference;
- camera/scale reference;
- structural sanity checks.

### Forbidden promotion of B3A into visible art

B3B may not:

- copy B3A lit RGB;
- copy B3A mask as final alpha;
- copy the projected 3D silhouette as final sprite silhouette;
- downsample/quantize/recolor a 3D render and call it native authored 2D art;
- use a procedural mannequin renderer to invent the final character appearance.

### What B3B must independently own

The native 2D body sprite itself must independently own:

- silhouette;
- body proportions as finally read on the gameplay pixel grid;
- head/torso/limb shapes;
- chest/pelvic pixel language;
- hands/feet readability;
- palette/value clusters;
- edge treatment;
- final alpha coverage.

After this one native 2D source is visually approved, the hidden rig may drive deterministic 2D deformation/animation guides. Exported/runtime art remains sprite-based.

## B3-B PASS criteria

1. complete adult anatomy at native `128×128`;
2. independently authored 2D silhouette, not a copied 3D mask;
3. no hair pixels;
4. no clothing/binding pixels;
5. no restraint/chain pixels;
6. chest, pelvis, hands and feet read coherently at native 1×;
7. silhouette and proportions remain recognizably Exilada-like;
8. gameplay preview remains readable at `640×360` with the locked ~`128 px` protagonist scale;
9. source reads as intentional modern pixel art rather than low-resolution 3D or procedural mannequin rendering;
10. output is deterministic/reusable as the base owner for later layers;
11. no routine manual frame-by-frame repair is introduced.

Erotic charge is neither a PASS nor FAIL requirement by itself. The body asset must support the project's mature visual vocabulary without structural censorship or forced neutralization.

## After B3-B PASS

Only then proceed to:

- G3S-B4 hair;
- G3S-B5 clothing/restraints/accessories;
- G3S-C motion.

## No-model-search rule

Do not reopen the closed local sprite-model search. The next task is to define a correct 2D source-authoring method, not to hunt another diffusion model.

## Exact next action

**No B3B runner is currently approved. Do not run one.**

Before any new code is committed, the B3B authoring method itself must be checked against the visible-ownership invariant above.
