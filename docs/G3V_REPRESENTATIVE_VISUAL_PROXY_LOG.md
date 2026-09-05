# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **READY TO RERUN AFTER RUNPY FUNCTION-GLOBALS FIX.**

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

Initial `$code:` interpolation was parsed as a scoped/drive-style variable reference.

Fix: `${code}:`.

### 2 — Blender extension installed but unavailable headlessly

MPFB installed successfully but a fresh background process did not expose the expected extension module.

### 3 — extension activation caused useless process churn

Decision: stop managing Blender extension repositories for G3V and load the verified MPFB package directly in Python. Normal G3V execution launches one Blender background process only.

### 4 — blank contact sheet accepted as review artifact

The first one-process G3V completed but all eight cells contained only background. This was an invalid artifact.

Fixes:

- explicit `G3V_RENDER` collection;
- Eevee render path;
- explicit semantic materials;
- post-render foreground validation;
- visible-height sanity check around the locked `128 px` target;
- blank output can no longer become `REVIEW_REQUIRED`.

### 5 — semantic validator recognized only cloth

A later run proved:

- MPFB bootstrap: PASS;
- `base.obj` imported;
- projected representative geometry height: **127 px**;
- Eevee semantic PNG written;
- validator recognized only `143` pixels, all `cloth`;
- `skin=0`, `hair=0`, `metal=0`.

Observed frame `1563` stats:

`{'foreground_pixels': 143, 'bbox': [274, 115, 365, 241], 'bbox_height_px': 127, 'semantic_pixels': {'skin': 0, 'hair': 0, 'cloth': 143, 'metal': 0}}`

The intended fix was:

- nearest semantic vs. background classification;
- no absolute `0.12` color-distance cutoff;
- `Raw` transform for semantic IDs;
- all four semantic classes required before review.

### 6 — intended semantic fix printed as active but was not actually bound

The next run produced **the exact same 143-cloth-only stats**, despite stdout reporting:

- `G3V_SEMANTIC_CLASSIFIER=NEAREST_VS_BACKGROUND`
- `G3V_ID_COLOR_TRANSFORM=RAW`
- `G3V_REQUIRED_SEMANTICS=skin,hair,cloth,metal`

Root cause is now exact: `runpy.run_path()` returns a copied namespace. The bootstrap patched that returned dictionary, while the target functions continued to resolve globals through their original `function.__globals__` dictionary. Therefore the console advertised the patch but `id_foreground_stats()` and `build_visible_outputs()` still executed the old classifier.

Fix committed in `g3v_mpfb_bootstrap.py`:

- obtain the target callable from the returned namespace;
- obtain `target_main.__globals__`;
- install `classify_id`, `render_pass` and strict semantic validator into **that actual globals dictionary**;
- assert identity of the bound replacements;
- invoke `main()` from the same globals dictionary;
- print `G3V_RUNTIME_PATCH_GLOBALS=BOUND_TO_MAIN` only after successful binding.

This rerun is now diagnostic: if semantic layers are still missing, that will be a real render/visibility issue rather than an inert runtime patch.

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

1. semantic ID pass;
2. neutral-light pass;
3. representative continuous-geometry row;
4. native semantic 4-band pixel row.

No high-resolution beauty render is shrunk. No bilinear scaling, diffusion, generative repainting or manual frame repaint is used.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_contact_sheet.png`

## PASS / FAIL

G3V can PASS only if:

1. anatomy/silhouette reads as a coherent human rather than a primitive technical mannequin;
2. weighted deformation remains coherent across the sampled walk;
3. hair/cloth/shackle side ownership remains structurally stable;
4. all representative semantic layers are genuinely visible;
5. the native-grid result has a credible path toward intentional modern pixel art;
6. it does not merely read as conventional 3D made blocky;
7. the complete dependency/body/rig/motion/render process remains headless.

If a validated representative human still reads only as filtered/low-resolution 3D, hidden 3D is rejected as owner of the final visible character but remains the motion/topology/socket/physics backbone.

G4 remains blocked until a **validated non-blank G3V contact sheet containing all representative semantic layers** is visually reviewed.
