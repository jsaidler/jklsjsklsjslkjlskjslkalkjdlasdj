# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **READY TO RERUN WITH BINARY OCCLUSION-AWARE SEMANTIC MASKS.**

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

`runpy.run_path()` returned a dictionary separate from the globals actually referenced by target functions. The fix now binds runtime patches directly through `target_main.__globals__` and asserts that binding before execution.

### 7 — bound classifier proves a real visible-layer problem

The next run confirmed the patch was genuinely active. Stdout included:

- `G3V_RUNTIME_PATCH_GLOBALS=BOUND_TO_MAIN`
- `G3V_SEMANTIC_CLASSIFIER=NEAREST_VS_BACKGROUND`
- `G3V_ID_COLOR_TRANSFORM=RAW`

Frame `1563` then produced:

`{'foreground_pixels': 10148, 'bbox': [274, 115, 365, 241], 'bbox_height_px': 127, 'semantic_pixels': {'skin': 0, 'hair': 667, 'cloth': 9481, 'metal': 0}}`

This is materially different from the earlier 143-pixel artifact. It proves:

- MPFB bootstrap works;
- the representative asset is on camera;
- the projected height is correct;
- substantial geometry is genuinely rendering;
- hair and cloth are visible;
- skin and metal are absent from the visible semantic result.

At this point color classification is no longer an acceptable diagnostic dependency. The remaining possibilities include actual occlusion by representative proxy geometry, MPFB body renderability/modifier state, or shackle placement/subpixel visibility.

## Binary semantic-mask mode — CURRENT

`g3v_semantic_masks.py` now replaces the multi-color semantic diagnostic with four independent binary renders per sampled frame:

- skin: target white, all other representative geometry black;
- hair: target white, all other representative geometry black;
- cloth: target white, all other representative geometry black;
- metal: target white, all other representative geometry black.

Black non-target geometry remains renderable, so normal depth/occlusion is preserved. The four masks are composited in Python into the canonical semantic-ID image. No RGB classification is required to discover layer ownership.

For any semantic with zero visible pixels, G3V immediately renders an additional **unoccluded diagnostic mask** with all non-target semantic geometry hidden:

- `visible=0, unoccluded>0` => the target exists and renders, but is fully occluded by representative proxy geometry;
- `visible=0, unoccluded=0` => the target itself does not render or is offscreen; object/mesh/modifier diagnostics are included.

Console diagnostics use explicit records such as:

- `G3V_MASK_SKIN_FRAME_1563_VISIBLE=...`
- `G3V_MASK_METAL_FRAME_1563_VISIBLE=0 UNOCCLUDED=...`
- `G3V_MASK_SEQUENCE_TOTALS=skin:...,hair:...,cloth:...,metal:...`

Semantic completeness is validated across the sampled sequence rather than requiring every small attachment to occupy a pixel in every single phase.

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

Four approved real-walk frames use the locked `640×360 / 26 deg / 128 px` presentation.

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
2. weighted deformation remains coherent across the sampled walk;
3. hair/cloth/shackle side ownership remains structurally stable;
4. all representative semantic layers are genuinely visible somewhere in the sampled sequence;
5. the native-grid result has a credible path toward intentional modern pixel art;
6. it does not merely read as conventional 3D made blocky;
7. the complete dependency/body/rig/motion/render process remains headless.

If a validated representative human still reads only as filtered/low-resolution 3D, hidden 3D is rejected as owner of the final visible character but remains the motion/topology/socket/physics backbone.

G4 remains blocked until a validated G3V contact sheet is visually reviewed.
