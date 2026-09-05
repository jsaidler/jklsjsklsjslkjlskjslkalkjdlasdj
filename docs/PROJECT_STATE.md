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

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical design master:

`assets/source/characters/exilada/reference/exilada_master.png`

Adult woman, approximately 162 cm, lean/functional/resilient anatomy, olive-brown skin, severe mature face, very long heavy black hair, degraded beige cloth in the initial equipped state, scars/wounds, captivity history, bare feet, canonical base weaponless.

The master defines identity/design, not hidden-body pixels and not final gameplay pixels.

### Body-first rule — LOCKED

The production character owns a **complete nude adult body base independent of hair, clothing and restraints**.

- body base is hairless;
- hair is a separate persistent 2D asset/layer family;
- clothing/bindings are separate overlays;
- cuffs/shackles/chains are accessories/equipment;
- the body remains complete under all removable layers;
- nudity is a normal supported state produced by omitting garment/equipment layers;
- the composite master cannot recover hidden anatomy by subtraction.

### Erotic charge — LOCKED

The project does **not** impose blanket desexualization of adult bodies or nudity.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell remain explicit visual references. Adult nudity may be neutral, sensual, erotic, heroic, brutal or vulnerable according to scene intent. No censor garment or anti-erotic framing is structurally required.

## Hard operator constraint

Normal production remains scriptable/headless. The user must not need routine Blender/Aseprite/rigging work, frame-by-frame repainting or a hired specialist.

Normal operator loop:

`git pull -> one documented PowerShell command -> inspect/share output`

## Model-discard cleanup rule — LOCKED

Whenever a model or model route is declared **FAIL/CLOSED/REJECTED** and is no longer active, the same response must include the exact PowerShell command to remove its downloaded model-specific files.

Preserve small evidence outputs and shared runtimes still used elsewhere.

## Locked gameplay baseline

- canvas `640×360`;
- orthographic camera;
- pitch `26 deg`;
- protagonist reference height `128 px`.

## Active production architecture — LOCKED

`camera/scale -> real motion -> deterministic hidden topology -> DIRECTION_SPACE_FK -> projected joints/depth/sockets/guides -> persistent 2D pixel assets -> deterministic 2D deformation/composition -> sprite/runtime export -> QA`

### Visible-ownership invariant — CRITICAL

G3V explicitly rejected hidden 3D as visible-image owner.

Hidden 3D may own only:

- motion;
- topology/left-right identity;
- sockets/contacts/root data;
- physics;
- depth/occlusion metadata;
- semantic/anatomical guides;
- secondary-motion driving data.

Hidden 3D **must not own final visible RGB or final sprite silhouette**. Final visible character art is owned by persistent 2D pixel assets. Runtime/export remains sprite-based.

This means a 3D render or mask may be inspected as a reference/guide, but it may not simply be cropped, recolored, downsampled, quantized or otherwise promoted into the final sprite geometry.

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
  - G3V-R retarget preflight — PASS/CLOSED using `DIRECTION_SPACE_FK`
- **G3S structured 2D visible representation** ← ACTIVE
  - G3S-A source-model search — CLOSED
  - authored native source V1 — FAIL/CLOSED
  - G3S-A1 Facial / Anatomy Lock V2 — FAIL/CLOSED
  - G3S-B persistent part decomposition V1 — FAIL/CLOSED
  - G3S-B2 layer-stack preflight — PASS/CLOSED DIAGNOSTIC
  - **G3S-B3 complete nude body base** ← CURRENT
    - G3S-B3A V1 — FAIL/CLOSED REVISION: wrong MPFB gender polarity
    - G3S-B3A V2 corrected adult-female anatomy guide — PASS/CLOSED
    - G3S-B3B V1 3D-mask-derived authoring route — **FAIL/CLOSED ROUTE**
    - **G3S-B3B genuine native 2D body source method** ← CURRENT / NOT YET IMPLEMENTED
  - G3S-B4 hair asset — BLOCKED UNTIL B3B PASS
  - G3S-B5 clothing/restraints/accessories — BLOCKED UNTIL B3B PASS
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

Marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

### G3V — FAIL / CLOSED

The continuous MPFB human animated coherently after validated retarget, but both conventional 3D and palette/semantic translation still read as low-resolution 3D rather than authored pixel art.

Canonical consequence: hidden 3D is retained as motion/topology infrastructure only and is demoted from visible-image ownership.

Marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

## G3S source-model search — CLOSED

Qwen native, SD1.5, PixelLock and Alucard were bounded probes. None produced an acceptable native production sprite. Do not restart source-model search.

Retained Qwen preferred-resolution control is design/scaffold provenance only:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## G3S-B2 — PASS/CLOSED DIAGNOSTIC

Measured:

- source alpha pixels: `2974`;
- body visible: `1538`;
- hair: `826`;
- clothing: `610`;
- unresolved hidden body: `1205`;
- exact recomposition: PASS.

Conclusion: subtraction from the master is not a body-authoring method.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

## G3S-B3 Nude Body Base — CURRENT

Canonical log:

`docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

Required production order:

1. complete nude/hairless **2D body sprite source**;
2. separate hair asset;
3. separate clothing/bindings/restraints/chains;
4. layered motion proof.

### B3-A V2 — PASS/CLOSED

B3A is a structural guide only. It validated:

- adult female phenotype;
- complete body geometry;
- zero hair/clothing/restraint/chain objects;
- visible height `128 px`;
- locked gameplay camera/scale.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

The MPFB render/mask is **not** a production sprite source.

### B3-B V1 route — FAIL/CLOSED

The first B3B implementation was rejected before user execution after repository review.

It copied the B3A projected body mask directly into the native alpha/silhouette and then procedurally colored that mask. Although it did not copy lit RGB, this still left hidden 3D as the final visible silhouette owner and revived the previously rejected procedural mannequin/Pillow authoring route.

That contradicts both:

- the G3V kill switch, which demoted hidden 3D from visible-image ownership;
- the G3S architecture, where persistent 2D pixel assets own final visible art.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

The invalid V1 script and runner were removed from `main` so they cannot be run accidentally.

No model was downloaded or discarded by this correction, so no model-file cleanup command applies.

### B3-B — CURRENT CORRECT REQUIREMENT

B3B must create a **genuinely authored native 2D `128×128` body sprite source**.

Allowed use of B3A:

- anatomy/proportion reference;
- joint/topology reference;
- camera/scale reference;
- sanity-check comparison.

Forbidden use of B3A for final visible ownership:

- copying its lit RGB;
- copying its binary mask as final sprite alpha;
- treating its projected 3D silhouette as final sprite silhouette;
- recoloring/quantizing/downsampling a 3D raster and calling it authored 2D art.

The final body sprite must have independently authored 2D silhouette, pixel clusters, palette/value structure and anatomical readability. After that source is approved, hidden 3D may drive animation/deformation guides while exported/runtime visuals remain sprites.

## Exact next action

**Do not run a B3B command yet.**

The next step is to design and review the corrected B3B authoring method itself against the canonical sprite-ownership invariant before any new runner is committed.

Do not start B3S-B4 hair, B5 clothing/accessories or G3S-C animation before B3B passes.

## Workspaces

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- shared embedded Python runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
