# G3S — Animation Architecture Lock

Status date: **2026-09-06**

Status: **CANONICAL / LOCKED — HIDDEN 3D = SKELETON/RIG GUIDE, NOT SKINNED BODY**

## Final architecture

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact guide data -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

## Hidden 3D owns

- the animation skeleton / armature topology;
- real motion and retargeting;
- complete joint transforms for each sampled event/frame;
- anatomical left/right identity;
- near/far limb identity from camera-space depth;
- foreshortening of bone chains;
- foot contacts and foot-roll timing;
- pelvis/root translation;
- sockets/attachments;
- secondary-motion drivers;
- per-bone / per-chain depth and occlusion ordering.

## Hidden 3D does NOT require or own

- a skinned human body mesh;
- detailed 3D anatomy;
- production body topology;
- final visible RGB;
- final visible alpha;
- final sprite silhouette;
- final pixel-art clusters/value language.

A skinned MPFB body is **not part of the animation-guide requirement**. The previous C1A revisions incorrectly conflated "full pose guide" with "render a posed 3D human mesh". That is now superseded.

The hidden guide may be literally an armature/skeleton. If a particular control task later benefits from volume, only simple deterministic non-skinned debug primitives/capsules may be generated from bone transforms. Such primitives are optional control visualizations, never character anatomy or final art.

## Critical distinction

"Full pose" means the rig provides the full spatial state of the pose, not that a full 3D human surface must exist.

For each gait/action event, the guide package needs, at minimum:

- projected joints;
- full bone-chain transforms;
- anatomical-side labels;
- near/far labels;
- per-chain camera-space depth;
- contact foot/contact state;
- root/pelvis transform;
- travel direction;
- fixed camera/view metadata.

That is enough to control authorship of a complete 2D pose without asking one static 2D raster to deform into every other pose.

## Visible 2D ownership

Each accepted key event has a complete persistent native-2D body pose at production scale. Those 2D assets own visible anatomy, silhouette, RGB and alpha.

The approved B3B V4 body remains:

- the canonical identity/body-style anchor for the current screen-left family;
- one valid static pose;
- not the sole pixel source for every animated pose.

The source-authoring step for new poses must be automated or assistant-operated. The user is not expected to redraw frames manually.

A visual authoring model/tool may be used offline to create persistent source candidates only when explicitly approved for that gate. It does not become the runtime/per-frame animation owner.

## Motion backbone

The retained motion infrastructure remains valid:

- G2 CMU `105_34 NormalWalk`;
- `G2_CANONICAL_RIG`;
- G3V-R `DIRECTION_SPACE_FK` retarget approval;
- `G3V_CMU_RIG` may be retained as a convenient character-proportioned hidden armature.

The retained `G3V_BODY` mesh is historical G3V evidence only and is no longer required for the animation guide path.

## Closed routes

- direct visible 3D -> final pixel art;
- single B3B still -> cutout/warp/cage -> full gait;
- skinned MPFB body -> rendered anatomy/silhouette/depth package as mandatory animation guide.

## First walk implementation

Target events remain:

1. left contact;
2. left down/loading;
3. left passing;
4. left up;
5. right contact;
6. right down/loading;
7. right passing;
8. right up.

For the first proof, export **one left-contact skeleton guide** first. Only after that spatial guide is validated should C1B author one complete persistent native-2D left-contact body pose.

## Runtime

Once the pose family exists, gameplay animation is ordinary sprite animation driven by motion-derived timing/contact/root metadata.

The current authored body family faces screen-left and therefore its travel preview must move screen-left.
