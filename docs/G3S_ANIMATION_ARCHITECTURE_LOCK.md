# G3S — Animation Architecture Lock

Status date: **2026-09-06**

Status: **CANONICAL / LOCKED**

This document resolves the recurring ambiguity between hidden-3D motion infrastructure and final visible 2D animation.

## Final architecture

The production animation architecture is:

`real/captured motion -> hidden 3D rig -> full pose-specific 3D guide package -> selected gait/action events -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

### Hidden 3D owns

- real motion and retargeting;
- full-body topology;
- anatomical left/right identity;
- near/far limb identity;
- complete 3D pose for each sampled event/frame;
- foreshortening reference;
- occlusion/depth order;
- foot contacts and foot roll timing;
- pelvis/root translation;
- sockets/attachments;
- secondary-motion drivers;
- semantic/body-part guides.

### Hidden 3D does NOT own

- final visible RGB;
- final visible alpha;
- final production sprite silhouette;
- final pixel-art clusters/value language.

Any rendered hidden-3D RGB, mask or silhouette may be used only as a **pose/anatomy/occlusion guide**. It may not be cropped, recolored, quantized or promoted into final visible sprite geometry.

## Critical correction

The failed C0 V1/V2 experiments incorrectly reduced the hidden-3D role to projected joint deltas that were then imposed on the single B3B still.

That was **not** the intended architecture.

The hidden 3D must guide the **entire pose state**, including near/far ownership, foreshortening, occlusion, pelvis orientation, contact foot and surfaces that were hidden in the rest pose.

Therefore the following route is closed:

`single 3/4 still -> projected joints -> cutout/warp/cage -> manufacture full walk`

The problem is not insufficient smoothing. One still does not contain the visible information required by other gait poses.

## First walk implementation

For the first body-only walk proof, the hidden rig will define a small left-facing key-pose family from the real CMU walk.

Initial target events:

1. left contact;
2. left down/loading;
3. left passing;
4. left up;
5. right contact;
6. right down/loading;
7. right passing;
8. right up.

Each event receives a **full hidden-3D guide package**, not just joint coordinates. At minimum that package must include:

- projected joints;
- anatomical-side labels;
- near/far labels;
- depth/body-part ordering;
- contact foot;
- root/pelvis transform;
- projected semantic body-part shapes or guide masks;
- fixed G1 camera/scale.

The guide package is reference/control data only.

## Visible 2D ownership

Each accepted key event must have a complete persistent native-2D body pose at production scale. These key-pose assets own their own visible anatomy, silhouette, RGB and alpha.

The approved B3B V4 still remains:

- the canonical identity/body-style anchor for the current left-facing family;
- one valid static pose;
- **not** the sole pixel source to be stretched into every other pose.

The source-authoring step for new pose assets must be automated or assistant-operated. The user is not expected to redraw frames manually.

A visual authoring model/tool may be used **offline to create persistent source candidates** only if explicitly approved for that gate. It does not become the runtime/per-frame animation owner. Every accepted result is frozen as a native-2D asset and validated against the hidden-3D guide and canonical Exilada identity.

## Runtime / playback

Once the pose family exists, gameplay animation is ordinary sprite animation driven by motion-derived timing/contact metadata.

For the first proof, no interpolation is required between the eight authored gait states. If later interpolation/deformation is used, it is limited to small local changes between already-valid neighboring pose assets and must pass visual QA.

Travel direction follows the selected directional family. The current family faces screen-left and therefore travels screen-left.

## Why this is the locked route

This preserves the decisions already made:

- hidden 3D is retained because it solves motion, topology, laterality, depth and contacts;
- visible 3D rendering remains rejected because it failed the pixel-art look;
- a single 2D still is not forced to invent hidden anatomy;
- final visible ownership remains persistent native pixel art;
- no manual frame-by-frame work is shifted to the user;
- no per-frame diffusion owns runtime animation.

## Supersession note

Where older sections of `docs/CHARACTER_PRODUCTION_PIPELINE.md` or `docs/ANIMATION_PIPELINE.md` imply that hidden-3D semantic rendering itself directly constructs the final Exilada sprite, this document plus `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md` and `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md` supersede that older assumption.

The retained hidden-3D backbone is **guide/control infrastructure**, not the final visible-image owner.

## Current next technical gate

Do **not** create another single-still warp runner.

The next implementation is a **3D pose-guide exporter for one non-rest gait event**, followed by a proof that a matching native-2D pose can be authored at production quality without manual redraw by the user.
