# G3S — Animation Architecture Lock

Status date: **2026-09-06**

Status: **CANONICAL / LOCKED — BELT-SCROLLER SEGMENTED 2D PUPPET**

## Presentation constraint that makes the animation feasible

The project is **not** targeting true isometric multi-directional character animation.

That option was deliberately abandoned in favor of an elevated arcade beat'em-up / belt-scroller presentation because it radically reduces the visible character problem while preserving a walkable depth band.

Locked presentation consequences:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist standing body height about `128 px`;
- first canonical visible family: screen-left front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime world-depth movement and z-order are separate from visible facing;
- do not multiply view families unless a later explicit gate proves one is necessary.

This simplification is a production contract, not a temporary test convenience.

## Final production architecture

`real/captured motion -> hidden skeleton/rig -> persistent segmented native-2D body parts -> anatomical pivots/bindings -> projected bone transforms -> camera-space depth ordering -> deterministic 2D composition -> sprite playback -> QA`

The hidden 3D is a **skeleton/armature**, not a hidden character render.

The visible character is a constrained **2D skeletal puppet** assembled from persistent authored parts. The same visible pixels persist through motion; the body is not regenerated independently per frame.

### Hidden skeleton owns

- real motion and skeletal topology;
- complete bone/joint transforms for each sampled state;
- anatomical left/right identity;
- near/far chain identity from camera-space depth;
- projected segment direction and length;
- contact/support-foot timing;
- pelvis/root travel;
- sockets and attachment transforms;
- secondary-motion driving data.

### Hidden skeleton does not own or require

- a skinned human body mesh;
- detailed 3D anatomy;
- final RGB or alpha;
- final sprite silhouette;
- final pixel-art clusters/value language.

Simple lines/capsules may be rendered only as debug visualization of bone data.

### Visible 2D puppet owns

- Exilada's persistent identity and anatomy;
- head/neck, torso, pelvis and bilateral limb-part pixels;
- joint overlap/cover pixels required to prevent visible gaps;
- any small reusable orientation/foreshortening variant that later proves necessary;
- hair/clothing/restraints/equipment as later separate persistent layers.

## Simplification rule for the first walk proof

Do not pre-emptively rebuild complexity that the belt-scroller decision removed.

The first segmented-body walk proof must use the smallest viable asset set:

- one screen-left body family;
- one persistent part per major anatomical segment;
- explicit pivots;
- deliberate hidden overlap at shoulders, elbows, hips, knees and ankles;
- skeleton-driven translation/rotation/projected length;
- depth sorting from camera-space skeleton depth;
- no generative redraw;
- no extra direction families;
- no foreshortening variants unless the first composed walk demonstrates a specific unavoidable failure.

If a reusable part variant becomes necessary, it is added only for the failing projection case and then reused across frames/actions. Variants are not frame-specific redraws.

## Closed routes

The following remain closed:

- hidden 3D render -> final visible pixel art;
- independent full-body generative redraw for each animation frame;
- single B3B still -> nearest-segment hard partition + exposed rigid joints -> full gait;
- single B3B still -> continuous whole-body chain/cage warp -> full gait;
- MPFB skinned body as mandatory pose/anatomy/silhouette/depth guide;
- reopening isometric/multi-directional animation complexity without an explicit presentation decision.

The B3B V4 body remains the approved visible identity/body-style source. Its original file remains unchanged.

## C1A — skeleton walk cycle — PASS/CLOSED

Approved states:

1. `1588` — left contact;
2. `1598` — left down;
3. `1608` — left passing;
4. `1618` — left up;
5. `1628` — right contact;
6. `1638` — right down;
7. `1648` — right passing;
8. `1658` — right up.

C1A uses `G2_CANONICAL_RIG` and CMU `105_34 NormalWalk`. It supplies motion/spatial control only.

## C1B — current visible body animation source

C1B is now the segmented native-2D puppet proof.

Current architecture:

`C1A approved skeleton -> B3B-derived persistent body-part atlas -> binding manifest -> eight composed walk states -> GIF/contact-sheet review`

The user is not expected to draw or repair frames manually.

Hair remains deferred until the body locomotion puppet is proven.

## Runtime

Gameplay playback uses ordinary deterministic sprite/part animation plus root/contact metadata. Because the presentation is a belt-scroller rather than true isometric, movement through the gameplay depth band does not imply new directional character art. Screen-right handling is deferred until the left-facing family is viable.
