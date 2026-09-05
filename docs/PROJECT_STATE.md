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

After every material step: update the relevant thematic document + this file and make a focused commit.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: elevated 2D belt-scroller / false 3D.

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical design master:

`assets/source/characters/exilada/reference/exilada_master.png`

Adult woman, lean/resilient anatomy, olive-brown skin, severe face, very long heavy black hair, degraded beige cloth, scars/wounds, broken restraints at wrists/ankles, bare feet, canonical base weaponless.

The master defines identity/design, not final gameplay pixels.

## Hard operator constraint

Normal production remains scriptable/headless. The user must not need routine Blender/Aseprite/rigging work, frame-by-frame repainting or a hired specialist.

Normal operator loop:

`git pull -> one documented PowerShell command -> inspect/share output`

## Model-discard cleanup rule — LOCKED

Whenever a model or model route is declared **FAIL/CLOSED/REJECTED** and is no longer an active dependency, the same response must include an exact PowerShell command to remove its downloaded model-specific files.

- preserve small result images/JSON/logs as evidence unless asked otherwise;
- preserve shared runtimes still used elsewhere;
- isolated dead dependency workspaces may be removed recursively.

## Locked gameplay camera baseline

- `640×360`;
- orthographic;
- pitch `26 deg`;
- protagonist reference visible height `128 px`.

## Active production architecture — LOCKED

`camera/scale -> real motion -> deterministic hidden topology -> DIRECTION_SPACE_FK -> projected joints/depth/sockets -> persistent structured 2D pixel assets -> deterministic 2D composition/deformation -> sprite/runtime export -> QA`

Hidden 3D owns infrastructure only: motion, topology/left-right identity, sockets, contacts/root data, physics, depth/occlusion, semantic guides and secondary-motion drivers. It does **not** own final visible character color pixels.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3 first native translation — TECHNICAL PASS / LOOK NOT APPROVED
- G3R primitive renderer refinement — FAIL/CLOSED
- G3V representative continuous human visual proxy — FAIL/CLOSED
  - G3V-R retarget preflight — PASS/CLOSED
- **G3S structured 2D visible representation** ← ACTIVE
  - G3S-A static source — ACTIVE
    - Qwen V1 harness — INVALID/CLOSED
    - Qwen V2 native `640×360` — FAIL/CLOSED
    - Qwen official-resolution control — PASS AS MODEL-FUNCTION CONTROL / CLOSED
    - SD1.5 native re-author — FAIL/CLOSED
    - PixelLock native-grid source — FAIL/CLOSED
    - Alucard external-reference test — INVALID/CLOSED
    - Alucard text-only native-128 control — FAIL/CLOSED
    - automated local generative-source search — CLOSED
    - authored native source V1 — **FAIL/CLOSED: mouth not visually readable**
    - **G3S-A1 Facial / Anatomy Lock V2** ← READY TO RERUN AFTER HARNESS FIX
  - G3S-B persistent part decomposition — BLOCKED
  - G3S-C four-phase walk proof — BLOCKED
- G4 Exilada production 2D identity system — BLOCKED UNTIL G3S PASS
- G5 temporal stress pack
- G6 equipment/attachments
- G6A wind/secondary motion
- G6B liquid/contact VFX
- G6C gore topology
- G6D clothing/armor damage
- G7 systemic state/dynamic lighting
- G8 production scaling

## Validated backbone

### G0 — PASS

Windows 11 + Blender 5.1.1 headless automation validated.

### G1 — PASS

Locked `640×360`, orthographic `26 deg`, protagonist `128 px`.

### G2 — PASS

Real motion source: CMU `105_34 NormalWalk`, 120 fps. Major-limb topology, left/right alternation and deterministic structure validated.

### G3V-R — PASS

Accepted retarget: **`DIRECTION_SPACE_FK`**.

Measured facts: `0` parent mismatches; mean rest-orientation difference `83.1874 deg`, max `180.0289 deg`; 4 unique target poses; mean elbow/knee error `0.0000 deg`, max `0.0001 deg`; rest-independent chain-shape metric passed; source/target skeleton sheet visually passed.

Marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

### G3V — FAIL

Representative MPFB body animated coherently after validated retarget, but native visible translation still read as coarse 3D rather than deliberate modern pixel art. Hidden 3D remains control/infrastructure only.

Marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

## G3S-A source-search history — CLOSED

Qwen native, SD1.5, PixelLock and Alucard were bounded architecture probes. None produced an acceptable native source sprite. The automated local generative-source search is closed; do not start another model search.

A coherent Qwen preferred-resolution control is retained only as design/scaffold provenance:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Pinned SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## Authored native source V1 — FAIL/CLOSED

Method:

`fixed Qwen design scaffold -> deterministic 128×128 base -> explicit native pixel patch`

V1 added/restored nominal mouth pixels, wrist cuffs, ankle restraints and chain remnants. Visual review found that the mouth still did **not** read as a mouth. The old automated guard merely checked alpha presence and therefore produced a false technical pass.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_authored_v1_failure.json`

Critical lesson: **anatomical details are gate-critical and semantic readability is authoritative; pixel existence alone is insufficient.**

## G3S-A1 Facial / Anatomy Lock — CURRENT

Canonical log:

`docs/G3S_A1_FACIAL_ANATOMY_LOCK_LOG.md`

V2 remains deterministic/headless and does not invoke an image model. It strengthens the facial cluster with an explicit two-row mouth, lip contrast and chin separation while preserving the canonical restraint patches.

It also changes review tooling: the contact sheet exposes explicit nearest-neighbor diagnostics for face, both hands and both feet.

### Harness incident fixed

The first G3S-A1 run stopped before anatomy processing with `ModuleNotFoundError: No module named 'g3s_a_authored_native_v1'`.

Root cause: the helper used a bare sibling-module import under ComfyUI's embeddable Python, whose `sys.path` does not guarantee the script directory.

Fix: `g3s_a1_facial_anatomy_lock.py` now loads `g3s_a_authored_native_v1.py` by absolute sibling file path through `importlib.util.spec_from_file_location`. This does not change pixel patch data or gate criteria.

Fix commit: `bf5fe174165ee9cd08ed2f50a09e3ca7563f8658`.

Incident marker:

`tools/structured-2d-character-pipeline/g3s_a1_import_failure.json`

Tooling:

- `tools/structured-2d-character-pipeline/g3s_a_anatomy_patch_v2.json`
- `tools/structured-2d-character-pipeline/g3s_a1_facial_anatomy_lock.py`
- `tools/structured-2d-character-pipeline/08_run_g3s_a1_facial_anatomy_lock.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a1_anatomy_lock`

Do **not** begin G3S-B, G3S-C or G4 until static anatomy is visually approved.

## Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\08_run_g3s_a1_facial_anatomy_lock.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a1_anatomy_lock\g3s_a1_contact_sheet.png`

## Workspaces

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- shared embedded Python runtime retained under: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
