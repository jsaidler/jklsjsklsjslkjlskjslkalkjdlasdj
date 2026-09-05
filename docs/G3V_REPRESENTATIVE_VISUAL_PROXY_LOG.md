# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **READY TO RERUN AFTER BLANK-RENDER FIX.**

## Why this gate exists

G3/G3R proved that renderer tuning on a primitive capsule/mannequin cannot answer the production-art question. Post-processing cannot invent human form, authored silhouette, long-hair structure, clothing structure or identity-bearing shape absent from the source geometry.

G3R is therefore canonically **FAIL / CLOSED**. Marker:

`tools/deterministic-character-pipeline/g3r_failure.json`

G3V tests the real visible hypothesis before any finished Exilada model is built:

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

## MPFB dependency — current locked loading mode

G3V pins **MPFB 2.0.17**.

The runner deliberately does **not depend on Blender extension repositories, add-on activation state or GUI preferences**.

Current sequence:

1. query the official Blender Extensions API for exactly MPFB `2.0.17` compatible with Blender 5.1.1;
2. download the official archive only when the verified cached copy is absent;
3. verify the SHA256 advertised by the Blender Extensions API;
4. extract the pinned archive to the project dependency workspace;
5. locate the actual MPFB Python package root by requiring `__init__.py + services/ + data/`;
6. start **one** Blender process with `--background`;
7. `g3v_mpfb_bootstrap.py` loads MPFB directly from that verified package root and initializes only its service layer required by G3V;
8. MPFB user-writable paths are redirected to a deterministic project-local directory;
9. the bootstrap then runs the G3V representative proxy script in the same Blender process.

Expected MPFB archive SHA256 from the successful local download:

`4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87`

The runner refuses silently substituting a newer MPFB version.

## Runtime incidents

### Incident 1 — PowerShell parser error

The initial runner contained an interpolated string with `$code:`. Windows PowerShell interpreted the colon as part of a scoped/drive-style variable reference and rejected the file before execution.

Fix: delimit the variable as `${code}:`.

### Incident 2 — extension installed but unavailable to project script

MPFB downloaded and validated, but no MPFB module was present in the fresh render process.

The first attempted fix used explicit Blender extension activation. It still failed in a fresh background process.

### Incident 3 — extension activation path caused useless Blender process churn

Decision:

- stop managing a custom Blender extension repository for G3V;
- stop opening multiple Blender processes for repo-list/repo-add/install/probe;
- load the verified MPFB package directly in Python;
- normal G3V execution now launches one Blender background process only.

### Incident 4 — generated contact sheet was blank / all background

Observed review artifact:

`g3v_contact_sheet.png`

The label layer was present, but all eight image cells contained only the background. Therefore this run was **invalid and must not be visually judged**.

The original script accepted any non-empty PNG file as a successful render. That was insufficient: a valid file could still contain zero character pixels.

Fix now implemented:

1. stop depending on Workbench object-color rendering for the semantic pass;
2. create an explicit root-visible `G3V_RENDER` collection and move the representative body, rig, hair/cloth/shackle geometry, camera and light into it;
3. render through **Blender Eevee**;
4. semantic ID pass uses explicit emissive materials for `skin / hair / cloth / metal`;
5. neutral-light pass uses an explicit diffuse material plus deterministic sun/world lighting;
6. after every semantic render, reload the PNG and count classified foreground pixels;
7. reject a frame if it contains fewer than 200 foreground pixels;
8. reject a frame if its visible semantic bounding-box height is outside `80..180 px` around the locked `128 px` target;
9. refuse to build the contact sheet if the complete sampled sequence contains zero semantic foreground.

This means a blank/offscreen render can no longer silently become `REVIEW_REQUIRED`.

## Representative body / rig

The script uses MPFB's public service API headlessly:

- `HumanService.create_human(...)` for a continuous basemesh;
- `TargetService.get_default_macro_info_dict()` for macro body parameters;
- `HumanService.add_builtin_rig(..., "cmu_mb")` for MPFB's built-in CMU MotionBuilder-compatible weighted rig.

The representative body is deliberately not the finished Exilada. Initial macro values create an adult female, relatively lean/resilient proxy. The exact macro dictionary is written to the manifest.

The `cmu_mb` rig is important because its naming/topology is designed for the same MotionBuilder-friendly CMU motion family already validated in G2. G3V copies the approved G2 action onto this compatible weighted human rig and verifies required major bone names before rendering.

## Representative identity-bearing structures

G3V adds only enough deterministic structure to make visual judgement meaningful:

- continuous female human body;
- long dark hair represented by three persistent overlapping geometry masses attached to head/neck/spine bones;
- simple asymmetric degraded-beige chest/waist/drape masses;
- separate wrist and ankle metal shackles attached to named left/right bones;
- bare body feet from the continuous human mesh;
- semantic IDs for skin / hair / cloth / metal.

These are not production assets. They are a visual kill-switch proxy.

## Visual translation test

Four approved real-walk frames are rendered at the locked `640×360 / 26 deg / 128 px` presentation.

For each frame Blender now creates:

1. **semantic ID pass** — exact skin/hair/cloth/metal ownership using emissive Eevee materials;
2. **neutral light pass** — deterministic Eevee lighting with neutral geometry.

The visible outputs are then constructed at the same native raster.

### A — representative continuous geometry

Semantic body/hair/cloth/metal structure displayed with fixed material colors. This row exists to judge whether the actual representative source structure is coherent.

### B — native semantic 4-band pixel

Semantic ownership comes from the ID pass; lighting value comes from the neutral-light pass. A global set of four luminance bands is computed across all four sampled frames and mapped into material-specific pixel palettes.

No high-resolution beauty render is shrunk. No bilinear scaling, diffusion, generative repainting or manual frame repaint is used.

## Output / review artifact

Expected contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_contact_sheet.png`

Layout:

- 4 columns = four approved real walk phases;
- top row = representative continuous geometry;
- bottom row = native semantic 4-band pixel result.

Other outputs:

- `g3v_representative_proxy.blend`;
- `g3v_manifest.json`;
- `g3v_result.json`;
- semantic ID/light debug passes;
- foreground statistics per sampled frame;
- SHA256 hashes for visible outputs and dependency provenance.

## PASS / FAIL

G3V can PASS only if:

1. anatomy/silhouette reads as a coherent human rather than a primitive technical mannequin;
2. real weighted deformation remains coherent across walk phases;
3. hair/cloth/shackle side ownership remains structurally stable;
4. the native-grid result has a credible path toward intentional modern pixel art;
5. it does not merely read as a conventional 3D character made blocky;
6. the entire dependency/body/rig/motion/render process runs headlessly;
7. there is enough visual headroom to justify building the Exilada identity proxy next.

If the representative continuous human still reads only as filtered/low-resolution 3D, hidden 3D is rejected as owner of the final visible character. It remains useful for motion/topology/sockets/physics, and final character art moves to a structured 2D representation.

G4 remains blocked until a **non-blank, validated G3V contact sheet** is visually reviewed.
