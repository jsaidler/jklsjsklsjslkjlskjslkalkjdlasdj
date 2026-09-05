# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
7. `docs/ANIMATION_SOURCE_LIBRARY.md`
8. `docs/PHYSICAL_INTERACTION_VFX_GORE.md`
9. `docs/PIXEL_ART_PRODUCTION.md`
10. `docs/ANIMATION_PIPELINE.md`
11. current tooling under `tools/`

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

## Animation-source strategy — CANONICAL LIBRARY PLAN

Canonical source/ingestion catalog:

`docs/ANIMATION_SOURCE_LIBRARY.md`

Blender is the deterministic processing/retargeting backbone, not the sole source of motions.

Primary permissive sources already identified:

- **Quaternius Universal Animation Library** — 120+ CC0 humanoid animations including locomotion, crawl, swim, death and combat;
- **Quaternius Universal Animation Library 2** — 130+ additional CC0 actions including armed/melee combos and parkour;
- **CMU Graphics Lab Motion Capture Database** — thousands of recorded trials, including walking, limping, get-up/recovery, swordplay and many natural motions, commercially usable in products under its stated terms;
- **Quaternius animal/monster/dinosaur packs** — CC0 animated sources for quadruped/creature rig-family validation.

Adobe Mixamo remains supplemental rather than a required automated dependency because acquisition normally requires account/web interaction.

The library is normalized by canonical **rig families** rather than forcing all species through one skeleton.

## Character layer / clothing / armor damage architecture — LOCKED

Canonical document:

`docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`

Character body, clothing, armor, restraints, equipment, surface state and structural damage are persistent modular systems. They are **not** baked independently into every animation frame.

Canonical logical layers:

1. complete body base;
2. hair/body-attached secondary masses;
3. underlayers/soft clothing;
4. outer clothing;
5. armor;
6. restraints/accessories;
7. weapons/tools;
8. persistent surface-state overlays;
9. transient VFX.

Every persistent item owns stable semantic identity, equipment slot/layer, material class, body-region/socket ownership, anatomical side, coverage/occlusion rules, damage zones, detach/drop rules, sever inheritance and serialized state.

### Damage model

Damage has two independent axes:

- **surface damage:** scratches, wear, blood, dirt, wetness, soot/scorch and similar state that does not alter topology;
- **structural damage:** tears, holes, broken straps, missing cloth sections, dented/broken/missing armor components, detached panels and other silhouette/coverage changes.

Structural damage uses a finite deterministic set of geometry/state transitions rather than per-frame generative reconstruction.

The complete body always exists under clothing. Damaged/removed layers reveal the correct underlayer or body region, preserving scars, wounds and body state across every animation.

Material-specific rules are defined for cloth, leather/hide, metal armor and wood/bone/rigid organic equipment.

### G6D — clothing/armor damage gate

Before broad equipment production, one representative soft garment and one representative rigid armor piece must prove:

- intact state;
- surface damage;
- structural damage changing silhouette/coverage;
- detach/broken-fastener event;
- correct body/underlayer exposure;
- persistence through locomotion and one high-energy action;
- blood/wetness interaction;
- one wind interaction on damaged soft cloth;
- deterministic headless rebuild/export from saved state;
- no body×item×damage×animation combinatorial sprite explosion.

## Physical interaction / VFX / gore / body-state architecture — LOCKED PLAN

Canonical document:

`docs/PHYSICAL_INTERACTION_VFX_GORE.md`

These are **not** deferred polish items. Wind, liquids, gore, dynamic lighting and optional unclothed body states affect how the rig, materials, semantic passes and runtime composition are designed.

### Wind

- Blender force fields / deterministic secondary systems may drive hair, cloth, foliage, dust, smoke-reference motion and similar assets;
- character hair/cloth remain persistent modular structures, not per-frame redraws;
- wind must not create full-body animation×wind combinatorial explosion if separate depth-aware hair/cloth layers can solve it;
- if continuous bitmap deformation damages pixel clusters, use discrete wind-state families instead.

### Liquids

Separate **surface state** from **free fluid motion**.

- wetness/blood/mud on characters use persistent semantic/material/body masks;
- blood spray, splashes, drips and ordinary water interaction are event-driven pixel VFX at runtime;
- Blender fluid simulation is useful for reference, hero effects and atlas generation, but ordinary gameplay liquid interaction must not require an offline bake per event;
- environment water may use runtime 2D wave/height-field logic, contact splashes and depth-aware pixel particles where needed.

### Gore

Gore is a production requirement.

The deterministic body must include named anatomical damage/sever zones from the start.

A sever event uses:

- known body-part hide/removal;
- persistent wound-cap/gore socket;
- detached limb/head object from the same body identity;
- blood emitter at the correct socket;
- collision/velocity/depth behavior;
- deterministic equipment/clothing inheritance rules.

Do not begin with arbitrary mesh slicing. Controlled anatomical cut zones are the scalable first architecture.

### Dynamic lighting

Hidden per-frame normal/material/depth information may drive runtime lighting, but visible pixel sprites must use **discrete material palette bands/LUTs**, not smooth photoreal gradients.

### Nude/unclothed body support

The body exists **independently under clothing** because clothing is modular and may be removed/damaged/changed.

This does not require generative nude imagery.

A current deterministic base-body candidate is **MakeHuman/MPFB or their CC0 core assets**. Any third-party downloaded asset must be license-checked separately.

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
- **G6A wind/secondary motion:** calm + wind-state response without manual repair or pixel corruption;
- **G6B liquid/contact VFX:** one water/wetness interaction + one blood impact;
- **G6C gore topology:** one deterministic sever-zone test before Exilada gore content is multiplied;
- **G6D clothing/armor damage:** one soft garment + one rigid armor piece through structural/surface damage, detachment and exposure;
- **G7 systemic visual state/dynamic lighting:** blood/dirt/wetness plus one dynamic light and wind-driven state;
- **G8 production scaling:** several clips/items process automatically end-to-end with deterministic export and QA.

The exact definitions, kill switches and outputs live in `docs/CHARACTER_PRODUCTION_PIPELINE.md`, `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md` and `docs/PHYSICAL_INTERACTION_VFX_GORE.md`.

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

## Persistent accessories/equipment plan

These are not redrawn independently per frame.

- hair: persistent rigged large-mass geometry with deterministic secondary motion;
- cloth: persistent rig/secondary structures before considering free simulation;
- shackles: separate rigid objects on named wrist/ankle sockets;
- chains: persistent endpoint-connected structures;
- weapons/gear: named sockets on the canonical rig;
- clothing/armor: modular persistent objects with localized surface + structural damage state.

Equipment scalability is planned as modular rendering with depth/occlusion metadata, so we do not pre-render every body×weapon×armor×damage combination.

## Systemic visual-state plan

Semantic/material/body masks are planned from the start so causal state can change without redrawing animation:

- blood/injury;
- dirt/mud;
- wetness;
- frost/burn;
- material wear;
- selected persistent scars;
- clothing/armor surface damage;
- discrete-palette lighting/weather changes.

## G0 implementation — READY TO RUN

Tooling:

- `tools/deterministic-character-pipeline/00_run_g0.ps1`
- `tools/deterministic-character-pipeline/g0_headless_probe.py`

Canonical deterministic pipeline workspace is now:

`Z:\AI\RogueliteCharacterPipeline`

`00_run_g0.ps1` is a one-command gate. It:

1. validates Windows/repository/workspace drive;
2. locates Blender if already installed;
3. if Blender is absent, installs the official `BlenderFoundation.Blender` package through `winget` unless `-SkipInstall` is explicitly used;
4. launches Blender with `--background --factory-startup --python`;
5. creates a known diagnostic 3D scene entirely through Python;
6. creates an orthographic camera and a named semantic socket marker;
7. saves `g0_probe.blend`;
8. renders `g0_probe.png`;
9. writes `g0_manifest.json` including Blender version, engine, semantic objects and PNG SHA256;
10. independently verifies outputs/hash in PowerShell and writes `g0_result.json`.

This render is **automation evidence only**, not a visual-direction or pixel-art test.

### Exact next action — DO ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\00_run_g0.ps1"
```

Then **STOP** and share:

- `Z:\AI\RogueliteCharacterPipeline\g0\g0_probe.png`
- `Z:\AI\RogueliteCharacterPipeline\g0\g0_result.json`

Do not start G1 until G0 is reviewed and recorded.

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

Active deterministic character pipeline:

`Z:\AI\RogueliteCharacterPipeline`

Repository:

`D:\GOOGLE DRIVE\DEV\Roguelite`
