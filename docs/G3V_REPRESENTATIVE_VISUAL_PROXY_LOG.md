# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **READY TO RERUN AFTER LOCAL-SCALE BAKE + DIMENSION AUDIT.**

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
- `tools/deterministic-character-pipeline/g3v_geometry_phase_patch.py`
- `tools/deterministic-character-pipeline/g3v_bone_attachment_patch.py`
- `tools/deterministic-character-pipeline/g3v_semantic_masks.py`
- `tools/deterministic-character-pipeline/g3v_representative_visual_proxy.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3v`

The user performs no Blender/MPFB GUI work.

## MPFB dependency — locked loading mode

G3V pins **MPFB 2.0.17**. The runner:

1. queries the official Blender Extensions API for exactly MPFB `2.0.17` compatible with Blender 5.1.1;
2. downloads only when the verified cached copy is absent;
3. verifies the advertised SHA256;
4. extracts the pinned archive to the project dependency workspace;
5. locates the MPFB Python package root;
6. starts **one** Blender background process;
7. bootstraps the MPFB service layer directly from the verified package, bypassing extension repository/add-on preference state;
8. redirects MPFB writable paths to the project workspace;
9. loads and executes the G3V target in the same Blender process.

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

`runpy.run_path()` returned a dictionary separate from the globals actually referenced by target functions. The fix binds runtime patches directly through `target_main.__globals__` and asserts that binding before execution.

### 7 — bound classifier proves a real visible-layer problem

A correctly bound run produced frame `1563`:

`{'foreground_pixels': 10148, 'bbox': [274, 115, 365, 241], 'bbox_height_px': 127, 'semantic_pixels': {'skin': 0, 'hair': 667, 'cloth': 9481, 'metal': 0}}`

This proved that substantial representative geometry really rendered and that skin/metal absence was not a stale classifier artifact.

### 8 — binary masks isolate the exact blocker

The binary occlusion-aware rerun completed all four sampled frames and reported identical per-frame values:

- skin: `visible=0`, `unoccluded=507`;
- hair: `visible=709`;
- cloth: `visible=9679`;
- metal: `visible=0`, `unoccluded=75`.

Sequence totals:

`skin:0, hair:2836, cloth:38716, metal:0`

Therefore body and shackles existed and rendered when isolated, while skin/metal were fully occluded by representative geometry.

### 9 — old G3V four-frame subset aliased the gait cycle

Frames `1563,1612,1661,1710` repeatedly sampled the same phase. This does not invalidate G2's full 12-frame motion review, but it invalidates any claim that G3/G3R independently proved four distinct gait phases.

G3V now derives a gait period from G2 foot contacts and uses quarter-cycle phases. Current measured selection:

- gait period: `80` frames at 120 fps;
- phases: `1568,1588,1608,1628`.

### 10 — skeleton camera fix exposed persistent attachment inflation

After switching to skeleton-derived scale, contact-derived phases and rigid relative attachments, the first frame still produced:

- body geometry height: `1.713562`;
- skeleton height: `1.647693`;
- skin: `visible=0`, `unoccluded=2314`;
- hair: `3426` visible pixels;
- cloth: `47692` visible pixels;
- metal: `visible=0`, `unoccluded=501`;
- rendered semantic bbox height: **285 px** despite skeleton camera calibration to 128 px.

This contradiction is decisive: the MPFB body and skeleton are physically sane, but one or more representative proxy primitives are still carrying inflated transform scale. Replacing Blender `BONE` parenting alone was insufficient because the proxy primitives themselves retained authored `obj.scale` inside their world matrices.

Current fix in `g3v_bone_attachment_patch.py`:

1. bake each proxy primitive's authored local scale directly into mesh vertices before attachment;
2. reset `obj.scale` to exactly `(1,1,1)`;
3. store only rigid translation/rotation relative to the owning bone;
4. emit per-object authored-scale and world-dimension diagnostics;
5. run a hard attachment-dimension audit once all 10 representative attachments exist;
6. fail with the exact object name/dimensions if any attachment's largest world dimension exceeds 80% of skeleton height.

Expected new markers:

- `G3V_ATTACHMENT_LOCAL_SCALE=BAKED_TO_MESH`
- `G3V_ATTACHMENT_CREATED=... world_dims=(...)`
- `G3V_ATTACHMENT_AUDIT=... largest_over_skeleton=...`
- `G3V_ATTACHMENT_DIMENSION_AUDIT=PASS`

This next run is no longer allowed to reach semantic rendering with an unidentified 285 px oversized proxy.

## Geometry / phase corrections

`g3v_geometry_phase_patch.py` provides:

1. skeleton-derived representative scale;
2. skeleton head-to-foot camera calibration;
3. oriented surface-visible wrist/ankle shackles;
4. contact-derived quarter-cycle frame selection.

## Binary semantic-mask mode

`g3v_semantic_masks.py` renders four independent binary masks per sampled frame:

- skin target white / all other representative geometry black;
- hair target white / all other representative geometry black;
- cloth target white / all other representative geometry black;
- metal target white / all other representative geometry black.

Black non-target geometry remains renderable, preserving actual depth/occlusion. Zero-visible layers are rerendered unoccluded so the pipeline distinguishes full occlusion from non-renderable/offscreen objects.

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
