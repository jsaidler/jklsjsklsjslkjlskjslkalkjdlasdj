# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/PIXEL_ART_PRODUCTION.md`
7. `docs/ANIMATION_PIPELINE.md`
8. current tooling under `tools/`

After every material step: update thematic docs + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity

The game is a **systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a living world**.

Immediate gameplay baseline: **elevated 2D belt-scroller / false 3D**.

Character-art/animation feasibility remains the current priority because it is the largest production risk; code capability is not the current unknown.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite. Final visible art remains true modern pixel art; simple high-resolution generation followed by resize/quantization is not accepted as the final-sprite route.

## Direct per-frame diffusion route — CLOSED AS PRIMARY ARCHITECTURE

RefControl was tested through V1/V2/V3.

- V1: strong identity retention but foot/arm/body/chain inconsistencies.
- V2: anatomy improved but opposite gait phases collapsed into near duplicates.
- V3: distinct controls restored phase alternation but `pose_01_passing_L_v3` generated **three visible legs / three feet** and accessories still drifted.

Final decision:

**RefControl is rejected as the production direct-frame generator. No V4.**

The problem is broader than extra limbs: independently synthesized frames do not guarantee stable proportions, natural locomotion, stable clothing/hair/accessories, anatomical side identity or scalable consistency across many actions.

Qwen-Image-Edit-2509 tooling remains preserved under `tools/qwen-image-edit-2509-spike/`, but that spike is **PAUSED** as the active next step. A perfect isolated pose would not prove the full animation-system requirements.

## Important correction — tested walk-pose provenance

The old `contact_L / passing_L / contact_R / passing_R` controls were manually parameterized project test poses, not motion capture or a validated locomotion solver.

They were valid only as pose-control experiments. They are **not** the canonical gait source.

Future motion comes from real captured motion, recorded performance or deterministic locomotion solving.

## Active production architecture — RISK-FIRST DETERMINISTIC PIPELINE

Canonical end-to-end roadmap:

`docs/CHARACTER_PRODUCTION_PIPELINE.md`

Production decomposition:

`gameplay scale/camera -> real motion -> deterministic rig -> persistent secondary systems -> native-raster semantic passes -> pixel-specific renderer -> modular equipment/state composition -> sprite/runtime export -> automated QA`

A hidden 3D rig is currently the preferred topology/motion backbone because it scales to motion capture, equipment sockets and many characters/actions. This **does not** mean the visible game becomes conventional 3D.

## Hard user-operation constraint — LOCKED

The user will not learn or manually operate Blender/rigging/animation/pixel-production software and will not hire an external art/animation team.

Therefore recurring production work must be executable by ChatGPT-authored tooling through command line/headless operation.

Acceptable pattern:

`PowerShell -> blender.exe --background --python ... -> deterministic outputs/reports`

Any proposed pipeline that requires routine specialist GUI work or frame-by-frame repair by the user is invalid.

## Key planning correction — visual translation is tested EARLY

We will **not** spend days building a complete rig and animation library before discovering whether hidden 3D can produce the required pixel-art language.

The first four gates deliberately cross-check downstream risk early:

### G0 — headless automation

Prove Blender/toolchain can create/render/export a known result with no GUI/manual operation.

### G1 — camera/native scale

Before final art, use primitive gameplay composition to determine:

- native scene raster (provisional `640×360` only until tested);
- camera pitch/elevation;
- pixels-per-world-unit;
- protagonist visible height;
- safe action bounds;
- likely facing-family requirements.

Candidate heights such as 112/128/144 px remain comparison points only.

### G2 — real motion/topology

Use a generic humanoid + real locomotion BVH, retargeted/baked headlessly.

PASS requires the full cycle to preserve normal topology, natural gait, acceptable foot contact, left/right identity and stable wrist/ankle/weapon sockets.

### G3 — native pixel-translation feasibility

**Before building the Exilada model**, prove that a simple stylized rig proxy can be translated into intentional modern pixel art at the exact G1 raster.

The primary candidate is not a conventional beauty render + pixel filter. Blender supplies deterministic native-density semantic passes such as silhouette, part/material IDs, normals, depth and stable detail masks; a purpose-built pixel renderer constructs indexed palette/value clusters directly on the final pixel grid.

If G3 reads as filtered/low-resolution 3D rather than intentional pixel art, that visible rendering route is rejected immediately. The rig may still survive as motion/reference infrastructure, but we do not invest in a detailed Exilada 3D model.

## Gates after G3

Only after G0–G3 all PASS:

- **G4 identity mapping:** low-detail Exilada production proxy + first approved native Production Pixel Master;
- **G5 temporal stress pack:** walk + high-energy/extreme action + compressed/impact/recovery motion before any animation library;
- **G6 equipment/attachments:** hair, shackles, chains and one representative weapon remain persistent and modular across motions;
- **G7 systemic visual state:** representative blood/dirt/wetness/injury/material states use stable semantic masks/palette rules;
- **G8 production scaling:** several clips/items process automatically end-to-end with deterministic export and QA.

The exact definitions, kill switches and outputs live in `docs/CHARACTER_PRODUCTION_PIPELINE.md`.

## Planned visual translation — current primary candidate

The hidden rig will output machine-readable passes at the **final target pixel density**, not a final high-resolution illustration:

- silhouette/coverage;
- body-part ID;
- material ID;
- normals;
- depth;
- persistent UV/detail masks;
- attachment metadata.

A deterministic pixel-specific renderer then applies:

- material-specific discrete palette ramps;
- large connected value clusters;
- controlled silhouette/edge rules;
- no smooth gradients as the primary language;
- no bilinear filtering;
- no automatic dithering/noise;
- stable UV-anchored details for scars/tears;
- temporal QA/cleanup limited to deterministic pixel noise, never anatomy/motion rewriting.

This is the current route to test because it lets 3D own topology/motion while the raster system owns the visible pixel language.

## Persistent accessories/equipment plan

These are not redrawn independently per frame.

- hair: persistent rigged large-mass geometry with deterministic secondary motion;
- cloth: persistent rig/secondary structures before considering free simulation;
- shackles: separate rigid objects on named wrist/ankle sockets;
- chains: persistent endpoint-connected structures;
- weapons/gear: named sockets on the canonical rig.

Equipment scalability is planned as modular rendering with depth/occlusion metadata, so we do not pre-render every body×weapon×armor combination. G6 must prove this before equipment content expands.

## Systemic visual-state plan

Semantic/material/body masks are planned from the start so causal state can change without redrawing animation:

- blood/injury;
- dirt/mud;
- wetness;
- frost/burn;
- material wear;
- selected persistent scars;
- discrete-palette lighting/weather changes.

## Production precedent / feasibility evidence

Motion Twin publicly documented a `Dead Cells` character workflow using simple 3D models/animation plus a custom small-size pixel-art rendering tool to avoid redrawing every frame and to reuse animation across models. This is evidence that a hidden 3D motion backbone plus purpose-built 2D pixel output is a credible production class, not evidence that our final look is already solved.

Blender supports background/headless Python execution, so this class of production work can be automated rather than requiring GUI operation.

## Exact next implementation sequence — LOCKED

Do **not** run the paused Qwen spike and do **not** build a detailed Exilada rig yet.

Next implementation sequence:

`G0 headless probe -> G1 gameplay camera/scale blockout -> G2 real-mocap generic walk -> G3 generic native-pixel renderer proof`

Only if all four pass do we construct the Exilada production proxy.

## Workspace state

Frozen RefControl evidence:

`Z:\AI\Flux2RefControlSpike`

Paused Qwen spike:

`Z:\AI\QwenImageEditSpike`

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`

A separate deterministic character-pipeline workspace will be created by the G0 tooling; its exact path will be locked in that implementation step.
