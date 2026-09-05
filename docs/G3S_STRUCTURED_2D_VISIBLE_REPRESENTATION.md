# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-B3B V2 AUTHORED NATIVE 2D BODY SOURCE READY FOR REVIEW**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets/guides -> persistent 2D pixel assets -> deterministic 2D transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB, alpha or final sprite silhouette.

## Visible-ownership invariant — LOCKED

G3V is authoritative: the direct visible-3D route failed and was closed.

Therefore:

- 3D may guide anatomy, motion, topology, sockets, contacts, depth and occlusion;
- 3D may not be mechanically promoted into final visible sprite geometry;
- a 3D render or mask is not a sprite template;
- cropping/recoloring/quantizing a projected 3D mask or render remains a 3D-owned visible route;
- final character pixels are owned by persistent structured 2D assets;
- runtime/export uses sprites.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI operation by the user;
- no beauty-render shrink/pixel-filter route as final art;
- no bilinear filtering;
- recurring work remains scriptable/headless;
- animation consumes persistent 2D parts rather than independently generated frames;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer.

## Model-discard cleanup rule — LOCKED

Whenever a model/route is declared **FAIL/CLOSED/REJECTED** and no longer required, the same response must include exact PowerShell cleanup commands for its model-specific files. Shared runtimes still in use are preserved; small evidence outputs remain unless explicitly removed.

Closed direct sprite-model routes remain Qwen-native, SD1.5, PixelLock and Alucard. Do not reopen model hunting.

# Correct staged character build — LOCKED

1. **G3S-B3 — complete body base**
   - adult female body;
   - hairless;
   - no clothing/bindings;
   - no cuffs/shackles/chains;
   - complete scalp/head/neck/torso/limbs under all future layers;
   - owned as a native 2D sprite asset.

2. **G3S-B4 — hair**
   - independent persistent 2D asset/layer family;
   - later separable into back/front/submasses for wind and secondary motion;
   - never part of body pixels.

3. **G3S-B5 — clothing and accessories**
   - chest wrap;
   - hip cloth;
   - arm/leg bindings;
   - cuffs/shackles;
   - chain segments;
   - each owns coverage, sockets, depth and state independently.

4. **G3S-C — four-phase walk proof**
   - only after B3/B4/B5 assets are layered correctly;
   - validated motion frames `1568,1588,1608,1628`;
   - hidden rig drives 2D deformation/ordering guides;
   - no independently regenerated animation frame;
   - exported/runtime result is sprite-based.

# Nudity — LOCKED SYSTEMIC STATE

Nudity is a normal supported state, not a special variant and not a runtime generation task.

Runtime composition:

`complete body base + optional hair + body-state overlays + zero or more garment/equipment/accessory layers`

The body remains complete beneath every removable layer. No censor garment is structurally required. Presentation may be neutral, sensual, erotic, heroic, brutal or vulnerable according to scene intent.

# G3S-B3 — Body Base — CURRENT

Canonical logs:

- `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
- `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`

## G3S-B3A V1 — FAIL/CLOSED REVISION

The first guide run used the wrong MPFB gender polarity. This was a script revision failure only.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3a_v1_failure.json`

## G3S-B3A V2 — PASS/CLOSED

The corrected V2 structural guide validates adult-female anatomy, complete body geometry, zero forbidden layer objects and the locked `128 px` gameplay scale.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3A is closed. Its RGB, mask and projected silhouette are reference/guide data only.

## G3S-B3B V1 — FAIL/CLOSED ROUTE

V1 copied the B3A projected binary mask into the final native alpha/silhouette and procedurally colored it. It was rejected because hidden 3D still owned the visible silhouette.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

The invalid V1 runner/script were removed before user execution. No model cleanup command applies.

## G3S-B3B V2 — READY FOR REVIEW

V2 commits the actual visible body source as an independently authored native 2D asset:

`assets/source/characters/exilada/body/g3s_b3b_body_base_source_v2.png`

SHA256:

`0fc90ca6a86e3adceba4d8fe100eb0d8e8e06337d6820585c6e535515fdfab53`

The asset itself owns:

- visible RGB;
- alpha;
- silhouette;
- pixel clusters/value structure.

B3A rendered output is not loaded or sampled by the validator. It remains an already-passed structural reference only.

Current source facts:

- native `128×128`;
- visible height `128 px`;
- bbox `[17, 0, 120, 127]`;
- 8 opaque palette colors;
- binary alpha;
- zero hair/clothing/binding/restraint/chain ownership.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b3b_body_base_source_v2.json`
- `tools/structured-2d-character-pipeline/g3s_b3b_validate_authored_body_v2.py`
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_authored_body_v2.ps1`

Technical ownership is correct, but **visual PASS is not automatic**. The source must be reviewed at native 1× for anatomy, Exilada-compatible proportions, hands/feet, chest/pelvis and intentional modern pixel-art language.

If V2 fails visually, revise the committed 2D asset directly. Do not return to 3D-mask authoring and do not reopen source-model search.

# G3S-B4 — Hair

Blocked until B3B body approval.

# G3S-B5 — Clothing / restraints / chains

Blocked until B3B body approval.

# G3S-C — Four-phase walk proof

Blocked until B3/B4/B5 are structurally correct.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\12_run_g3s_b3b_authored_body_v2.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_authored_body_v2\g3s_b3b_contact_sheet_v2.png`

or the complete console error.
