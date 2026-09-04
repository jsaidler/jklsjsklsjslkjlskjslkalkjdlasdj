# Character Production Pipeline — End-to-End Living Plan

Status: **canonical production roadmap.** The project will not build a complete rig, animation library, equipment catalog or Exilada production model before the downstream visual-translation risks have been proven in small gates. All recurring production operations must be scriptable/headless; the user is not expected to learn Blender, rigging, animation, pixel editing or asset-pipeline tools.

## Non-negotiable production contract

The complete character pipeline must satisfy all of the following:

- final visible language: true modern pixel art at native gameplay raster;
- gameplay presentation: elevated 2D belt-scroller / false 3D;
- normal body topology is owned by deterministic structure, never by per-frame diffusion;
- motion is sourced from real capture, recorded performance or deterministic solving, not guessed stick-figure key poses;
- anatomy, proportions, left/right side identity and attachment sockets persist through every frame;
- clothing, hair, restraints and equipment have persistent structure and cannot arbitrarily migrate between sides;
- no routine manual frame-by-frame repainting;
- no required Blender GUI work or specialist tool operation by the user;
- local/free/self-hosted tooling unless explicitly approved otherwise;
- production must scale to many actions, NPCs, races, equipment states and systemic visual conditions;
- every stage must have an explicit PASS/FAIL gate before the next expensive stage begins.

Canonical identity reference:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines identity/design, not final gameplay pixels.

## Planned production architecture

`gameplay scale/camera -> real motion -> deterministic rig -> persistent secondary systems -> native-raster semantic passes -> pixel-specific renderer -> modular equipment/state composition -> sprite/runtime export -> automated QA`

The hidden 3D structure is production infrastructure. It does not imply conventional visible 3D graphics.

## Risk-first validation order

The project must validate the following risks in this order. A later stage may not be started simply because an earlier technical demo looked attractive.

| Gate | What is proved | Minimal artifact | Hard failure consequence |
| --- | --- | --- | --- |
| G0 — automation | The toolchain can be operated headlessly by scripts | Blender CLI probe + scripted render + manifest | Reject any tool that requires recurring GUI/manual operation |
| G1 — camera/scale | The belt-scroller camera and actual pixel density are viable | primitive gameplay composition at native 1× | Change raster/camera before any character art is built |
| G2 — motion/topology | Real motion can drive a persistent humanoid rig with stable contacts/sockets | generic rig + real walk + diagnostic render | Change motion/retarget strategy; do not touch final art |
| G3 — pixel-translation feasibility | Hidden 3D structure can become intentional native-grid pixel art rather than filtered 3D | stylized generic proxy rendered through the planned pixel renderer | Reject this visual translation before building Exilada model |
| G4 — identity mapping | Exilada's silhouette/material identity survives the same deterministic renderer | low-detail Exilada production proxy + one approved still | Rework model/material abstraction; do not build animation library |
| G5 — temporal visual stability | The visual language survives actual movement, not only a still | short walk + one high-energy action at native 1× | Rework raster/renderer/temporal rules before content multiplication |
| G6 — equipment/attachments | Modular equipment and restraints remain correctly attached/occluded without combinatorial redraw | one weapon + shackles/chains across G5 motions | Rework layer/depth composition before equipment catalog creation |
| G7 — systemic state | Dirt/blood/wetness/injury/material state can vary causally without destroying pixel readability | two representative dynamic state overlays | Rework state-mask/palette system before broad simulation integration |
| G8 — production library | New clips/items can be converted automatically and reproduce accepted quality | batch of several actions + automated export/QA | Pipeline is not production-ready; stop content expansion |

## G0 — headless automation gate

Primary orchestration is PowerShell calling command-line tools.

Blender must run through commands equivalent to:

`blender.exe --background --python <script.py> -- <arguments>`

Scripts must own scene creation/loading, BVH/FBX import, retargeting, baking, camera, materials, rendering, export and manifests.

The pipeline may use Python for deterministic raster processing, palette application, masks, temporal QA, packing and metadata. This does not revive the rejected primitive-Pillow character-authoring route: Python is not inventing anatomy or drawing a mannequin; it processes deterministic semantic geometry/raster data.

Aseprite is not a mandatory dependency. If later useful, its batch/Lua interface may be used for inspection/export/structured pixel operations, but the production pipeline must not depend on the user opening it.

### G0 PASS

One command creates a known scene, renders a diagnostic PNG, writes machine-readable metadata and exits without GUI interaction.

## G1 — camera and native gameplay scale BEFORE final art

The exact pixel density must be determined before designing the final character renderer.

First composition test:

- provisional scene raster: `640×360`;
- representative belt-scroller ground/depth band;
- one protagonist proxy;
- 3–5 enemy proxies;
- attack reach/spacing overlays;
- candidate protagonist visible heights such as 112 / 128 / 144 px used only as comparison points.

The test is viewed at native 1×. It determines:

- scene raster;
- camera pitch/elevation;
- orthographic or near-orthographic treatment;
- pixels-per-world-unit;
- protagonist screen height;
- safe animation bounds;
- whether left/right-only body families are enough or a limited 3/4 family is required.

### G1 hard rule

No Production Pixel Master, detailed Exilada model, palette tuning or animation atlas is approved before this scale is known.

## G2 — deterministic motion/topology backbone

Use a generic humanoid first, not Exilada art.

Initial motion source: a real locomotion BVH from a permissively usable mocap source (current first candidate: CMU Graphics Lab Motion Capture Database).

Processing must be scripted:

1. import source motion;
2. map/retarget to canonical rig;
3. normalize orientation/scale;
4. identify foot-contact intervals;
5. separate locomotion root translation from local body motion when needed;
6. calculate stride length and natural clip speed;
7. bake the result;
8. expose stable attachment sockets on wrists, ankles, hands, back/head as required;
9. export diagnostic sequence + metrics.

Locomotion playback speed in the game must be derived from stride/root-motion metadata so animation and actual travel do not create systematic foot sliding.

### G2 PASS

Across the complete cycle:

- normal topology persists;
- measured gait reads naturally;
- foot contacts are acceptable;
- pelvis/shoulder motion survives retargeting;
- left/right identity is stable;
- wrist/ankle/weapon sockets remain attached;
- the same result is reproducible headlessly.

## G3 — visual translation is tested EARLY, not at the end

This is the critical safeguard against spending days building a rig only to discover that the final look reads as filtered 3D.

The primary visual-translation candidate is a **native-raster semantic pixel renderer**, not a high-resolution beauty render followed by resize/quantization.

### Blender outputs at exact target pixel density

The hidden model is rendered/exported into machine-readable passes rather than a conventional finished 3D image:

- silhouette/coverage;
- body-part ID;
- material ID;
- view-space normals;
- depth;
- stable UV/detail masks;
- attachment/socket metadata;
- optional flat unlit diagnostic color.

These passes are produced at the final character pixel density derived from G1. No antialiased high-resolution color render is treated as final art.

### Pixel-specific renderer

A deterministic renderer then constructs the visible native-grid sprite from semantic passes:

- material-specific indexed palette ramps;
- discrete lighting bands, not smooth gradients;
- deliberate silhouette/edge rules rather than uniform black outlines;
- large connected value clusters before accents;
- material-specific cluster language for hair / skin / cloth / metal;
- fixed UV-anchored details for scars, tears and other persistent marks;
- no automatic dithering by default;
- no random texture/speckling;
- no bilinear filtering;
- no arbitrary bitmap rotation;
- target approximately 24–32 visible base colors for Exilada unless validation proves a different count is needed.

The renderer may use normals/depth mathematically, but the visible output is built directly as pixel-grid material/value decisions. This is intentionally different from applying a generic pixel filter to a conventional 3D render.

### Temporal raster stability

The renderer must be sequence-aware enough to detect/avoid pathological one-frame pixel noise while preserving legitimate motion.

Automated checks include:

- isolated single-pixel births/deaths;
- abrupt silhouette-area spikes;
- material-ID discontinuities unrelated to occlusion;
- attachment jumps;
- palette violations;
- frame-to-frame body-area anomalies.

Any temporal cleanup must be deterministic and cannot repaint anatomy or change motion.

### G3 test asset

Do not build the Exilada yet. Use a deliberately simple stylized humanoid proxy with:

- skin region;
- large dark hair-like mass;
- cloth region;
- small metal region;
- clear hands/feet.

Test one static pose plus a few frames of the G2 walk at final 1× scale.

### G3 PASS

The output must read as intentional modern pixel art, not low-resolution 3D, while remaining temporally coherent. If it fails, the hidden-3D motion rig can still be retained as motion reference, but this visible rendering route is rejected before detailed character work begins.

## G4 — Exilada identity mapping

Only after G3 passes is a production proxy of Exilada constructed.

Because the final sprite is small, the hidden model should be optimized for **projected pixel silhouette and material masses**, not photorealistic 3D detail.

Identity-bearing structure to encode mechanically:

- lean adult proportions;
- severe head/face silhouette appropriate to gameplay scale;
- very long heavy black hair as a dominant geometry mass;
- degraded asymmetric beige cloth as persistent meshes/material regions;
- barefoot feet;
- wrist and ankle shackles as separate socketed objects;
- scars/wounds that need persistence as UV/material masks or geometry where scale justifies it;
- no permanent weapon.

The low-detail model can be crude in conventional 3D terms if its native-raster projection is correct. This follows the principle that geometry exists to support the pixel result, not to be shown as a normal 3D asset.

### Production Pixel Master redefinition

The first approved static Exilada result produced by the accepted deterministic rig + pixel renderer at the locked gameplay scale becomes the **Production Pixel Master**.

It is judged at 1× on:

- silhouette;
- hair mass;
- anatomy;
- skin/hair/cloth/metal separation;
- palette/cluster quality;
- recognizability against `exilada_master.png`;
- absence of filtered-3D appearance.

## G5 — motion stress pack BEFORE an animation library

Do not create dozens of clips after only a walk works.

The first visual stress pack must include at least three motion classes:

- locomotion with repeated foot contacts;
- one high-energy/extreme-silhouette action such as attack or evasive motion;
- one compressed/impact/recovery motion.

Motion should come from real/captured/deterministic sources, not manually guessed final poses.

The stress pack tests:

- silhouette deformation;
- limb separation;
- pixel-edge stability;
- hair/cloth secondary motion;
- contact readability;
- action arcs;
- sprite bounds;
- whether the chosen frame sampling rate preserves physicality without smooth 3D-looking interpolation.

Mocap may be sampled/baked into a lower sprite-frame cadence. Frame selection is derived from motion/contact/error metrics, not arbitrary `every Nth frame` only.

## G6 — persistent hair, restraints, chains and equipment

These must never be regenerated as arbitrary image details.

### Hair

Represented as persistent rigged geometry/large masses with secondary bones or a deterministic damped-spring solver. Fine hair strands are not modeled because they are not a gameplay-scale identity requirement.

### Cloth

Persistent cloth pieces are geometry/rigged secondary structures. Full free cloth simulation is not required initially; deterministic secondary bones/constraints are preferred until a simulation proves reproducible and visually necessary.

### Shackles/chains

- shackles are separate rigid objects attached to named wrist/ankle sockets;
- chain endpoints are fixed to known objects/sockets;
- visible chain motion is solved from persistent geometry/curve/segment structures;
- no system is permitted to reinterpret which anatomical side owns the chain.

### Equipment

Weapons/gear use named sockets and the same canonical rig.

The production target is **modular rendering**, not pre-rendering every possible equipment combination.

Preferred scalable export:

- base-character pixel layer/pass;
- equipment pixel layer/pass;
- per-pixel or per-part depth/occlusion information generated from the same 3D scene;
- frame metadata describing attachment and ordering.

The runtime or offline compositor uses deterministic depth/occlusion so one item can be rendered across animation clips independently instead of multiplying every body×weapon×armor combination.

If depth-aware modular composition proves impractical in the target game engine, this must be discovered in G6 and the alternative (slot-specific front/back layers or controlled offline composite families) chosen before an equipment catalog is authored.

## G7 — systemic visual-state architecture

The living-world design requires visual state to be causal and maintainable.

Plan from the start to export stable semantic/material/body-part masks so runtime or offline tools can apply state without redrawing animation:

- blood/injury overlays tied to anatomical regions;
- dirt/mud;
- wetness;
- frost/burn states;
- material wear;
- selected persistent scars;
- palette changes caused by lighting/weather/status.

Dynamic lighting should not introduce smooth non-pixel gradients. If per-frame normal information is retained, runtime lighting must map into discrete palette/value ramps or other pixel-consistent rules.

G7 is tested with only a few representative states before broad simulation integration.

## G8 — production automation and content scaling

After all earlier gates pass, a new animation clip should require only source selection/configuration, not manual animation work.

Expected automated clip pipeline:

`source motion -> retarget/bake -> contact/root metadata -> secondary motion -> native semantic passes -> pixel render -> equipment/state passes -> QA -> PNG/spritesheet + metadata`

Expected outputs per animation may include:

- indexed-color sprite sequence/sheet;
- alpha;
- optional normal/material/body/depth metadata textures if runtime systems need them;
- pivot/root anchors;
- foot-contact events;
- attack/event markers;
- attachment points;
- clip natural speed/stride;
- collision/hitbox helper data;
- provenance/version manifest.

## Automated QA / CI contract

Every production batch must automatically validate at least:

- exact frame dimensions/raster;
- palette limits;
- transparent background integrity;
- topology proxy/body-part presence from semantic passes;
- stable left/right part IDs;
- socket continuity;
- foot-contact/ground metrics;
- root/pivot stability;
- sprite bound overflow;
- no unexpected color/AA pixels;
- no singleton-noise threshold violations;
- loop closure metrics where applicable;
- deterministic output hashes for unchanged inputs.

The batch also generates visual review artifacts automatically:

- contact sheet;
- native-1× looping preview/video;
- silhouette-only preview;
- part-ID/depth debug preview;
- QA report.

The user's role is approval/critique of visible results, not operating production software.

## Early kill switches

The project must not continue a route merely because sunk cost exists.

- If G1 cannot find a readable gameplay scale, revise presentation before character production.
- If G2 cannot produce a natural stable rigged walk, change motion/retarget source before visual work.
- If G3 cannot produce convincing intentional pixel art, reject the hidden-3D visible renderer before building Exilada geometry; retain the rig only as motion/reference infrastructure and evaluate the deterministic 2D mesh/structured-pixel fallback.
- If G4 cannot preserve Exilada identity at the chosen gameplay scale, revisit scale/model abstraction before animation multiplication.
- If G5 reveals temporal pixel instability in extreme actions, fix the renderer/frame-sampling rules before creating an action library.
- If G6 modular equipment fails, solve composition architecture before creating equipment content.
- If G7 state overlays destroy readability, solve material/mask rules before simulation-driven art expansion.

## Why this route is considered credible enough to test

A 3D-to-2D production backbone is not unprecedented: Motion Twin documented using simple 3D models/animation plus a custom small-size pixel-art rendering pipeline for `Dead Cells`, specifically to avoid redrawing every frame and to reuse animation across models. The relevant lesson for this project is not to copy its exact look, but that **3D may own motion/topology while a purpose-built raster pipeline owns the final 2D pixel language**.

Blender officially supports non-interactive execution with `--background --python`, so the planned production operations can be driven by scripts rather than requiring the user to operate its GUI.

## Immediate next implementation sequence

The first implementation is intentionally small and cross-validates downstream risk early:

`G0 headless probe -> G1 camera/scale blockout -> G2 real-mocap generic walk -> G3 generic native-pixel renderer proof`

Only if **all four** pass do we begin the Exilada production proxy.

This is the key anti-waste rule: **we will test the final visual translation before investing in the final character model or animation library.**
