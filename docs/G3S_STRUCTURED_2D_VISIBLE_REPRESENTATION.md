# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY PASS/CLOSED / B4 HAIR DEFERRED / C0 SINGLE-STILL MOTION ROUTE CLOSED / HIDDEN-3D-GUIDED NATIVE-2D POSE SOURCE CURRENT**

Canonical animation architecture lock:

`docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`

## Locked architecture

`real/captured motion -> validated hidden rig -> full pose/contact/depth/laterality/occlusion guides -> persistent native-2D pose assets -> deterministic timing/depth composition -> native sprite -> QA`

Hidden 3D may own motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB, alpha or final sprite silhouette.

The hidden rig must guide the **entire pose state**, not merely export joint deltas. A pose guide may include projected semantic shapes/masks and 3D-derived silhouette reference, but those are guide/control data only and may not be promoted into final sprite geometry.

## Production constraints

- final visible character art is owned by persistent native 2D assets;
- no per-frame diffusion as runtime animation owner;
- no routine frame-by-frame repainting by the user;
- no beauty-render shrink/pixel-filter route;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer;
- animation may not assume one static raster contains every hidden surface needed by every pose.

## Canonical B3 body — PASS/CLOSED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing body height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- authored front-three-quarter view facing **screen-left**.

This B3B asset remains the approved static body identity/style anchor for that view. It is not by itself an animation-ready source for arbitrary gait silhouettes.

## Facing/laterality rule — LOCKED

A 3/4 raster cannot infer anatomical left/right or near/far ownership from screen-x alone. Any animation source family must explicitly register:

- screen facing;
- anatomical side;
- near/far limb ownership;
- occlusion order;
- pose/rest basis relative to hidden motion guides.

The current B3B family faces screen-left; travel using that family must move screen-left unless another direction family is authored.

## B4 hair — DEFERRED

Hair remains structurally separate and later must still satisfy:

`rear_hair -> body -> front_hair`

No hair candidate is approved. No B4C generated pixels were promoted. The user paused hair on 2026-09-06.

## G3S-C0 — BODY-ONLY MOTION DIAGNOSTIC

Motion infrastructure retained:

- G2 real-motion/topology = PASS;
- CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- G3V-R `DIRECTION_SPACE_FK` = PASS.

### C0 V1 — FAIL/CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`

Method: hard body-part cutout + independent rigid rotation from the single B3B still.

Failure: detached joints and broken/loop-like stride silhouettes.

### C0 V2 — FAIL/CLOSED VISUAL + METHOD

Reviewed contact sheet SHA256:

`6d6199aa7bc159cad344c8dbc31b52577f2c70bb70f674ab5216ea40db67fba3`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v2_visual_failure.json`

Method: continuous chain warp of arms/legs from the same single still.

Failure: anatomically impossible limb arcs persisted.

Root cause is architectural:

- the hidden-3D guide was incorrectly reduced to projected joint deltas;
- sprite-facing/laterality/near-far ownership was not registered;
- sprite rest/camera basis and hidden-rig projected-motion basis were not a validated common coordinate system;
- real gait depth and foreshortening were collapsed into 2D chain deformation;
- the still lacks hidden anatomy revealed by changing occlusion;
- bbox-bottom placement is not true contact/root grounding.

Therefore the entire following class is closed when the **only visible source** is the single B3B still:

`single still -> projected joints -> cutout / chain warp / cage warp -> manufacture full gait`

A smoother weighted mesh is not a solution to missing visible surfaces or wrong near/far anatomy.

V2 runner is disabled:

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1`

## Hidden-3D-guided animation-ready source — CURRENT REQUIREMENT

The first real walk proof uses the hidden 3D as a **full pose guide**, exactly as originally intended.

For each selected gait event, the hidden rig must export at least:

- projected joints;
- anatomical side labels;
- near/far limb identity;
- depth and occlusion order;
- contact foot and foot-roll state;
- root/pelvis transform;
- projected semantic body-part shapes/guide masks;
- fixed G1 camera and scale.

Those guides define the pose completely enough to author visible 2D anatomy, but remain non-visible production controls.

The first left-facing walk family targets eight persistent native-2D key poses:

1. left contact;
2. left down/loading;
3. left passing;
4. left up;
5. right contact;
6. right down/loading;
7. right passing;
8. right up.

Each accepted pose owns complete visible anatomy for that event, including foreshortening, pelvis/torso counter-motion, hip/knee/ankle geometry, contact foot, silhouette and occlusion.

The hidden rig supplies guide/control information; persistent 2D art owns final RGB/alpha/silhouette.

No new animation runner is approved until one non-rest hidden-3D-guided pose can be authored at production quality without manual frame redraw by the user.

## Full layered motion remains later

C0 does not waive eventual persistent hair, clothing, restraints and equipment. Full layered G3S-C approval still waits for those layer families after the body animation source architecture is viable.
