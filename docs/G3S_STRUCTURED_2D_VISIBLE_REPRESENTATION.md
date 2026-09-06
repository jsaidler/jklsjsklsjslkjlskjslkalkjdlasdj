# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — NUDE BODY REFERENCE APPROVED / B3B AUTHORED NATIVE-PIXEL BODY CANDIDATE CURRENT**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets/guides -> persistent 2D pixel assets -> deterministic 2D transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB, alpha or final sprite silhouette.

## Visible-ownership invariant — LOCKED

G3V is authoritative: direct visible 3D failed and was closed.

Therefore:

- 3D may guide anatomy, motion, topology, sockets, contacts, depth and occlusion;
- 3D may not be mechanically promoted into final visible sprite geometry;
- a 3D render or mask is not a sprite template;
- cropping/recoloring/quantizing a projected 3D mask/render is rejected;
- high-resolution 2D reference art likewise may not be mechanically resized/quantized/traced and promoted as production sprite geometry;
- final character pixels are owned by persistent structured 2D assets;
- runtime/export uses sprites.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI work by the user;
- no beauty-render shrink/pixel-filter route as final art;
- recurring work remains scriptable/headless;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer.

## Model-discard cleanup rule — LOCKED

Whenever a model/route is declared FAIL/CLOSED/REJECTED and no longer required, include exact PowerShell cleanup commands for its model-specific files. Shared runtimes still in use are preserved.

Closed direct sprite-model routes remain Qwen-native, SD1.5, PixelLock and Alucard. Do not reopen model hunting.

## Correct staged character build — LOCKED

1. **B3 — complete body base**: adult female, hairless, complete under future layers, owned as native 2D sprite art.
2. **B4 — hair**: independent persistent 2D asset/layer family.
3. **B5 — clothing/restraints/accessories**: chest wrap, hip cloth, bindings, cuffs/shackles, chain segments and other equipment, each with independent ownership/state.
4. **G3S-C — layered motion proof**: hidden rig drives 2D deformation/ordering guides; exported/runtime result remains sprite-based.

## Nudity — LOCKED SYSTEMIC STATE

Nudity is a normal supported state, not a special variant. Runtime composition is:

`complete body base + optional hair + body-state overlays + zero or more garment/equipment/accessory layers`

No censor garment is structurally required. Presentation may be neutral, sensual, erotic, heroic, brutal or vulnerable according to scene intent.

## B3A history

- B3A V1 — FAIL/CLOSED REVISION: wrong MPFB gender polarity.
- B3A V2 — PASS/CLOSED: adult-female structural anatomy, complete geometry, zero forbidden layers, locked `128 px` visible gameplay height.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3A RGB/mask/silhouette remain guide data only.

## B3B history

### V1 — FAIL/CLOSED ROUTE

Copied B3A projected mask into final silhouette; hidden 3D still owned visible geometry.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

### V2 — FAIL/CLOSED VISUAL ROUTE

Technically 2D-owned but visually unacceptable: procedural/mannequin anatomy, distorted proportions, poor hands/feet, crude pelvis/thigh transitions, pseudo-3D banding and absent Exilada identity.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v2_visual_failure.json`

### V3 — FAIL/CLOSED VISUAL AND METHOD ROUTE

V3 isolated the approved high-resolution three-quarter reference, mechanically downscaled it to `128 px`, retained the reduced reference mask/silhouette, quantized colors and applied local cleanup.

Reviewed output reads as a **miniaturized render**, not authored pixel art. It collapses face/hands/feet, retains render-like value noise and proves no intentional native pixel-cluster language.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

Reviewed contact sheet SHA256:

`ded6e53cd5c36b106a7d7729534cd2f12241862a6f3b0e3a27b6e706ded08047`

V3 is closed and must not be rerun or promoted. No model cleanup applies because it downloaded no model weights.

## Approved high-resolution nude body reference — PASS

A user-supplied Grok **fully nude** four-view turnaround is approved as the primary body reference for B3B authoring.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Source identity:

- SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`;
- `2048×1401`;
- front/back/profile/front-three-quarter;
- adult natural feminine proportions at ~162 cm identity;
- lean/functional/resilient, olive/brown, bald/hairless for body-reference purposes, barefoot;
- mature, severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell;
- complete pelvic anatomy visible;
- no occluding garment.

Canonical expected local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

The old covered reference remains historical evidence only.

## 128 px clarification — LOCKED

`128 px` is the target **visible standing body height** in the native `640×360` gameplay raster with the locked orthographic `26°` camera. It is not a universal source/frame canvas dimension. Hair, weapons and extreme animation bounds may use larger transparent frames while preserving this body scale.

## Current gate — B3B authored native-pixel body candidate

The next artifact must **start as actual pixel art**, not as a transformed copy of the high-resolution reference.

The approved nude turnaround may guide:

- adult anatomy and proportions;
- body mass and silhouette intent;
- severe/sensual/dangerous sword-and-sorcery presence;
- consistency of chest, pelvis, hips, thighs, hands and feet.

It may **not**:

- be resized and called pixel art;
- be quantized and called pixel art;
- be mechanically traced into final silhouette ownership;
- supply final production RGB/alpha through filtering or reduction.

The valid next artifact is one deliberately authored gameplay-view body sprite at approximately `128 px` visible standing height, reviewed at native 1× and in `640×360` context.

No B3B runner is currently approved. B4 hair, B5 clothing/restraints/accessories and G3S-C motion remain blocked until the authored body candidate passes.
