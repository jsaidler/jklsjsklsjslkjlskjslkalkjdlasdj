# Roguelite — Current Project State

Status date: **2026-09-05**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

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
11. `docs/G0_AUTOMATION_LOG.md`
12. `docs/G1_CAMERA_SCALE_LOG.md`
13. `docs/G2_MOTION_TOPOLOGY_LOG.md`
14. `docs/G3_PIXEL_TRANSLATION_LOG.md`
15. `docs/G3R_RENDERER_REFINEMENT_LOG.md`
16. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
17. `docs/G3V_RETARGET_PREFLIGHT_LOG.md`
18. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
19. `docs/G3S_A1_FACIAL_ANATOMY_LOCK_LOG.md`
20. `docs/G3S_B_PERSISTENT_PART_DECOMPOSITION_LOG.md`
21. `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`
22. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
23. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

After every material step: update the relevant thematic document + this file and make a focused commit.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: elevated 2D belt-scroller / false 3D.

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical design master:

`assets/source/characters/exilada/reference/exilada_master.png`

Adult woman, lean/resilient anatomy, olive-brown skin, severe face, very long heavy black hair, degraded beige cloth in the initial equipped state, scars/wounds, captivity history, bare feet, canonical base weaponless.

The master defines design/identity, not hidden-body pixels and not final gameplay pixels.

### Body-first clarification — LOCKED 2026-09-05

The production character owns a **complete nude adult body base independent of hair, clothing and restraints**.

- body base is hairless;
- hair is a separate persistent asset/layer family;
- clothing/bindings are separate overlays;
- cuffs/shackles/chains are accessories/equipment;
- the body remains complete under all removable layers;
- nudity is a normal supported state, produced by omitting garment/equipment layers rather than generating a separate nude sprite;
- the composite master cannot be used to recover hidden anatomy by subtraction.

### Erotic charge — LOCKED 2026-09-05

The project does **not** impose blanket desexualization of adult bodies or nudity.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell are explicit visual references, and their sensual/erotic adult-body vocabulary is considered part of the intended mature direction.

- adult nudity may be neutral, sensual, erotic, heroic, brutal or vulnerable according to scene intent;
- the Exilada may remain beautiful/sexually charged while also severe, dangerous, dirty, wounded, exhausted or deprived;
- erotic charge is allowed but not mandatory in every scene;
- no censor garment or anti-erotic framing is structurally required;
- framing must be intentional rather than automatically sanitized or automatically sexualized.

Canonical detail is in `docs/VISUAL_DIRECTION.md` and `docs/CHARACTERS.md`.

## Hard operator constraint

Normal production remains scriptable/headless. The user must not need routine Blender/Aseprite/rigging work, frame-by-frame repainting or a hired specialist.

Normal operator loop:

`git pull -> one documented PowerShell command -> inspect/share output`

## Model-discard cleanup rule — LOCKED

Whenever a model or model route is declared **FAIL/CLOSED/REJECTED** and is no longer active, the same response must include an exact PowerShell command to remove its downloaded model-specific files.

Preserve small evidence outputs and shared runtimes still used elsewhere.

## Locked gameplay baseline

- canvas `640×360`;
- orthographic camera;
- pitch `26 deg`;
- protagonist reference height `128 px`.

## Active production architecture — LOCKED

`camera/scale -> real motion -> deterministic hidden topology -> DIRECTION_SPACE_FK -> projected joints/depth/sockets -> complete 2D body base -> separate hair -> separate clothing/equipment/accessories -> deterministic 2D composition/deformation -> sprite/runtime export -> QA`

Hidden 3D owns infrastructure only: motion, topology/left-right identity, sockets, contacts/root data, physics, depth/occlusion, semantic guides and secondary-motion drivers. It does **not** own final visible character color pixels.

## Canonical character layer stack — LOCKED

1. complete unclothed body base;
2. hair / body-attached secondary masses;
3. underlayers / soft clothing;
4. outer clothing;
5. armor;
6. restraints/accessories;
7. weapons/tools;
8. persistent surface overlays;
9. transient VFX.

The body must exist under removable/damageable clothing and under hair. Hair and garments are never baked into body ownership.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3 first native translation — TECHNICAL PASS / LOOK NOT APPROVED
- G3R primitive renderer refinement — FAIL/CLOSED
- G3V representative continuous human visual proxy — FAIL/CLOSED
  - G3V-R retarget preflight — PASS/CLOSED
- **G3S structured 2D visible representation** ← ACTIVE
  - G3S-A source-model search — CLOSED
  - authored native source V1 — FAIL/CLOSED
  - G3S-A1 Facial / Anatomy Lock V2 — FAIL/CLOSED
  - G3S-B persistent part decomposition V1 — FAIL/CLOSED
  - G3S-B2 layer-stack preflight — **PASS/CLOSED DIAGNOSTIC**
  - **G3S-B3 complete nude body base** ← CURRENT
    - **G3S-B3A deterministic nude anatomy guide** ← READY TO RUN
    - G3S-B3B native `128×128` body source — BLOCKED UNTIL B3A REVIEW
  - G3S-B4 hair asset — BLOCKED UNTIL B3
  - G3S-B5 clothing/restraints/accessories — BLOCKED UNTIL B3
  - G3S-C four-phase walk proof — BLOCKED UNTIL B3/B4/B5
- G4 Exilada production 2D identity system — BLOCKED UNTIL G3S PASS
- G5 temporal stress pack
- G6 equipment/attachments
- G6A wind/secondary motion
- G6B liquid/contact VFX
- G6C gore topology
- G6D clothing/armor damage
- G7 systemic state/dynamic lighting
- G8 production scaling

## Validated deterministic backbone

### G0 — PASS

Windows 11 + Blender 5.1.1 headless automation validated.

### G1 — PASS

Locked `640×360`, orthographic `26 deg`, protagonist `128 px`.

### G2 — PASS

Real motion source: CMU `105_34 NormalWalk`, 120 fps. Major-limb topology, left/right alternation and deterministic structure validated.

### G3V-R — PASS

Accepted retarget: **`DIRECTION_SPACE_FK`**.

Measured facts: `0` parent mismatches; mean rest-orientation difference `83.1874 deg`, max `180.0289 deg`; 4 unique target poses; mean elbow/knee error `0.0000 deg`, max `0.0001 deg`; rest-independent chain-shape metric passed; source/target skeleton comparison visually passed.

Marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

### G3V — FAIL

Representative MPFB body animated coherently after validated retarget, but direct visible translation still read as coarse 3D rather than deliberate modern pixel art. Hidden 3D remains control/infrastructure only.

Marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

## G3S source-model search — CLOSED

Qwen native, SD1.5, PixelLock and Alucard were bounded probes. None produced an acceptable native source sprite. Do not restart source-model search.

Retained Qwen preferred-resolution control is design/scaffold provenance only:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## G3S-A / A1 — face state

The provisional 128×128 scaffold has acceptable macro body readability but its face is unresolved.

V1 mouth patch was unreadable. V2 stronger mouth patch became an artificial block. The face remains a replaceable future component rather than blocking all architecture work.

Markers:

- `tools/structured-2d-character-pipeline/g3s_a_authored_v1_failure.json`
- `tools/structured-2d-character-pipeline/g3s_a1_v2_failure.json`

## G3S-B V1 — FAIL/CLOSED

The V1 decomposition technically passed exact reconstruction, but visual review showed semantic ownership was wrong: body/limb parts retained garment/binding pixels, hair masks retained non-hair pixels, and the body did not exist independently underneath hair/clothing.

Marker:

`tools/structured-2d-character-pipeline/g3s_b_v1_failure.json`

Critical lesson: **pixel-exact reconstruction does not validate semantic ownership.**

## G3S-B2 — PASS/CLOSED DIAGNOSTIC

B2 correctly proved the body-under-occluders problem rather than trying to fake the missing body.

Measured:

- source alpha pixels: `2974`;
- body visible: `1538`;
- hair: `826`;
- clothing: `610`;
- unresolved hidden body: **`1205`**;
- exact recomposition: PASS.

Conclusion: subtraction from the master is not a body-authoring method.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

Canonical log:

`docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`

## G3S-B3 Nude Body Base — CURRENT

Canonical log:

`docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

Required production order:

1. complete nude/hairless body base;
2. separate hair asset;
3. separate clothing/bindings/restraints/chains;
4. layered motion proof.

Nudity is a normal runtime state: the body base is always complete and garments/equipment are simply absent.

B3 must not recover hidden anatomy by subtracting hair/clothing.

### B3-A — ready

The first bounded step creates a deterministic complete adult female nude/hairless **anatomy guide** from the existing MPFB/hidden-rig infrastructure. It creates zero hair, clothing, cuff/shackle or chain objects.

This guide is structural data only and explicitly does **not** become final visible pixel art.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b3_mpfb_bootstrap.py`
- `tools/structured-2d-character-pipeline/g3s_b3a_nude_anatomy_guide.py`
- `tools/structured-2d-character-pipeline/g3s_b3a_contact_sheet.py`
- `tools/structured-2d-character-pipeline/11_run_g3s_b3a_nude_anatomy_guide.ps1`

Output:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3a_nude_guide\g3s_b3a_contact_sheet.png`

### B3-B — blocked

After B3-A structural review, author the actual native `128×128` nude body-base pixel source. Only B3-B can pass visible body art.

No hair, clothing or animation starts before B3-B passes.

## Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\11_run_g3s_b3a_nude_anatomy_guide.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3a_nude_guide\g3s_b3a_contact_sheet.png`

Do not run G3S-C.

## Next-chat handoff

Canonical continuation prompt/state:

`docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Workspaces

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- shared embedded Python runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
