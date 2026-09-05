# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **READY TO RERUN AFTER CONFIRMED BONE-PARENT SCALE FIX.**

## Why this gate exists

G3/G3R proved that renderer tuning on a primitive capsule/mannequin cannot answer the production-art question. Post-processing cannot invent human form, authored silhouette, long-hair structure, clothing structure or identity-bearing shape absent from the source geometry.

G3R is canonically **FAIL / CLOSED**. Marker:

`tools/deterministic-character-pipeline/g3r_failure.json`

G3V asks:

**Can a coherent continuous adult female human asset with representative hair/cloth/metal structure, driven by the approved real motion backbone, survive deterministic native-grid pixel translation convincingly enough to justify Exilada identity mapping?**

## Locked upstream baseline

- G0 headless automation: PASS;
- G1: `640×360`, orthographic pitch `26 deg`, protagonist reference height `128 px`;
- G2: CMU `105_34 NormalWalk`, deterministic persistent motion/topology PASS;
- G3: technical native-raster translation PASS, look not approved;
- G3R: renderer-only mannequin refinement FAIL.

## Tooling

- `tools/deterministic-character-pipeline/03c_run_g3v.ps1`
- `tools/deterministic-character-pipeline/g3v_mpfb_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_bone_attachment_patch.py`
- `tools/deterministic-character-pipeline/g3v_geometry_phase_patch.py`
- `tools/deterministic-character-pipeline/g3v_semantic_masks.py`
- `tools/deterministic-character-pipeline/g3v_representative_visual_proxy.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3v`

The user performs no Blender/MPFB GUI work.

## MPFB dependency — locked loading mode

G3V pins **MPFB 2.0.17** and loads it directly from the verified archive in one background Blender process. Blender extension repository/add-on preference state is not part of the production path.

Validated archive SHA256:

`4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87`

## Runtime incidents and decisions

### 1 — PowerShell parser error

Initial `$code:` interpolation was parsed as a scoped/drive-style variable reference. Fixed as `${code}:`.

### 2–3 — extension activation failure and process churn

The Blender-extension activation route was abandoned. G3V now loads the pinned verified MPFB package directly in the single background Blender process.

### 4 — blank contact sheet accepted as review artifact

The first one-process G3V completed but all eight cells contained only background. This was invalid. G3V now validates rendered foreground and visible height before review.

### 5 — first semantic validator recognized only cloth

Frame `1563` initially reported only 143 recognized pixels, all cloth. Camera projection itself was correct at 127 px.

### 6 — first classifier patch was bound to the wrong `runpy` namespace

`runpy.run_path()` returned a dictionary separate from the globals actually referenced by target functions. Runtime patches now bind through `target_main.__globals__`.

### 7 — correctly bound classifier proved a real visible-layer problem

A bound run produced frame `1563` with substantial foreground but `skin=0` and `metal=0`, proving the remaining problem was not stale classification.

### 8 — binary masks isolated true occlusion

The binary mask run reported:

- skin: `visible=0`, `unoccluded=507`;
- hair: `visible=709`;
- cloth: `visible=9679`;
- metal: `visible=0`, `unoccluded=75`.

Therefore skin and metal existed and rendered, but were fully occluded by representative geometry.

### 9 — old four-frame subset aliased the gait cycle

Frames `1563, 1612, 1661, 1710` repeatedly landed on the same gait phase. G3V now derives a gait period from G2 contact metadata and samples quarter-cycle phases. G2's full 12-frame motion/topology approval remains valid; G3/G3R do not independently prove four-phase temporal diversity.

### 10 — skeleton calibration exposed Blender bone-parent scale inflation

After switching to contact-derived phases and skeleton-based scale/camera, the next run produced:

- `G3V_DERIVED_GAIT_PERIOD_FRAMES=80.000`;
- `G3V_PHASE_FRAMES=1568,1588,1608,1628`;
- `G3V_BODY_GEOMETRY_HEIGHT=1.713562`;
- `G3V_SKELETON_HEIGHT=1.647693`;
- camera calibration from skeleton head-to-foot;
- but composite visible height **285 px**;
- skin: `visible=0`, `unoccluded=2314`;
- hair: `visible=3426`;
- cloth: `visible=47692`;
- metal: `visible=0`, `unoccluded=501`.

The body and skeleton physical heights are sane and close to each other, while cloth occupied almost the entire 206×285 px visible bbox. At a 128 px skeleton height, the authored cloth dimensions should occupy only a small fraction of that area. This identifies the remaining blocker as **transform inflation from Blender BONE parenting of the proxy attachments**, not camera scale or MPFB body scale.

Current fix: `g3v_bone_attachment_patch.py` replaces Blender bone parenting for representative hair/cloth/cuffs with explicit rigid bone-relative matrices:

1. capture each proxy object's world matrix at creation;
2. capture the owning pose bone's world translation+rotation only;
3. store the object's relative transform to that rigid bone frame;
4. keep the proxy object unparented;
5. after every frame change, reconstruct `object_world = rigid_bone_world × relative`;
6. deliberately ignore parent/bone scale inheritance.

This keeps physical proxy dimensions fixed while preserving deterministic attachment to animated bones. The patch installs **before** the geometry-phase shackle replacement so all representative attachments use the same safe transform owner.

Expected markers:

- `G3V_ATTACHMENT_MODE=RIGID_RELATIVE_MATRIX`
- `G3V_ATTACHMENT_SCALE_INHERITANCE=DISABLED`
- `G3V_GEOMETRY_SCALE=SKELETON_DERIVED`
- `G3V_PHASE_SELECTION=CONTACT_DERIVED_QUARTER_CYCLE`
- `G3V_CAMERA_CALIBRATION=SKELETON_HEAD_FOOT`

## Binary semantic-mask mode

`g3v_semantic_masks.py` renders four independent binary masks per sampled frame with non-target geometry still present as black occluders. If a semantic has zero visible pixels, an additional unoccluded mask distinguishes true occlusion from offscreen/non-renderable geometry.

## Representative body / rig

The script uses MPFB public services headlessly:

- `HumanService.create_human(...)` for a continuous adult female basemesh;
- `TargetService.get_default_macro_info_dict()` for macro body parameters;
- `HumanService.add_builtin_rig(..., "cmu_mb")` for the weighted CMU-compatible rig.

The proxy is not the finished Exilada. It adds only enough persistent structure to make the visual kill switch meaningful:

- continuous female body;
- long dark hair masses;
- asymmetric degraded-beige cloth;
- left/right wrist and ankle shackles;
- bare feet;
- semantic ownership for skin / hair / cloth / metal.

## Visual translation test

Four **contact-derived quarter-cycle walk phases** use the locked `640×360 / 26 deg / 128 px` presentation.

For each frame:

1. four binary occlusion-aware semantic masks;
2. Python-composited semantic ID pass;
3. neutral-light pass;
4. representative continuous-geometry row;
5. native semantic 4-band pixel row.

No high-resolution beauty render is shrunk. No bilinear scaling, diffusion, generative repainting or manual frame repaint is used.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_contact_sheet.png`

## PASS / FAIL

G3V can PASS only if:

1. anatomy/silhouette reads as a coherent human rather than a primitive technical mannequin;
2. weighted deformation remains coherent across genuinely distinct sampled walk phases;
3. hair/cloth/shackle side ownership remains structurally stable;
4. all representative semantic layers are genuinely visible somewhere in the sampled sequence;
5. the native-grid result has a credible path toward intentional modern pixel art;
6. it does not merely read as conventional 3D made blocky;
7. the complete dependency/body/rig/motion/render process remains headless.

If a validated representative human still reads only as filtered/low-resolution 3D, hidden 3D is rejected as owner of the final visible character but remains the motion/topology/socket/physics backbone.

G4 remains blocked until a validated G3V contact sheet is visually reviewed.
