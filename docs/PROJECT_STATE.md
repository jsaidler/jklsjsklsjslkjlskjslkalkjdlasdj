# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
7. `docs/PIXEL_ART_PRODUCTION.md`
8. `docs/ANIMATION_PIPELINE.md`
9. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
10. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
11. `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`
12. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
13. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
14. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

After every material step: update the relevant thematic document + this file and make a focused commit.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical design master:

`assets/source/characters/exilada/reference/exilada_master.png`

Adult woman, approximately 162 cm, lean/functional/resilient anatomy, natural adult feminine proportions, olive-brown skin, severe mature face, very long heavy black hair, degraded beige cloth in the initial equipped state, captivity history, bare feet, weaponless base identity.

Do **not** reinterpret “compact” as short, squat or flattened anatomy. The approved body direction is natural adult proportion at ~162 cm, lean/functional/resilient.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell remain explicit visual references. Mature sensuality, erotic charge and adult nudity are legitimate parts of the visual language and are not automatically sanitized.

## Body-first rule — LOCKED

The production character owns a **complete adult body base independent of hair, clothing and restraints**.

- body base is hairless;
- hair is a separate persistent 2D layer family;
- clothing/bindings are separate overlays;
- cuffs/shackles/chains are accessories/equipment;
- the body remains complete under removable layers;
- nudity is a normal supported state;
- no censor garment is structurally required.

## Hard operator constraint

The user does not perform routine Blender/Aseprite/rigging work and does not repaint frames manually. Normal production remains scriptable/headless.

Normal operator loop once a runner is approved:

`git pull -> one documented PowerShell command -> inspect/share output`

## Visible-ownership invariant — CRITICAL

G3V rejected hidden 3D as visible-image owner.

Hidden 3D may own motion, topology/left-right identity, sockets/contacts/root data, physics, depth/occlusion metadata and structural guides. It **must not own final visible RGB, alpha or final sprite silhouette**.

Final character art is owned by persistent 2D pixel assets. Runtime/export remains sprite-based.

## Locked gameplay baseline

- scene canvas: `640×360`;
- orthographic camera;
- pitch: `26°`;
- protagonist **visible standing height**: approximately `128 px`.

### 128 px clarification — LOCKED

`128 px` is the target **on-screen standing height** of the protagonist at native `640×360`. It is **not** a universal sprite-frame dimension and does not require production frames to be `128×128`.

G1 compared `112 / 128 / 144 px`; `128 px` was selected as the best compromise between character identity/equipment/gore readability and combat/walkable-screen composition.

Animation frames, hair, weapons and extreme actions may require larger transparent bounds while preserving the same native body scale.

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
  - G3S-A1 facial/anatomy lock attempts — FAIL/CLOSED
  - G3S-B persistent part decomposition V1 — FAIL/CLOSED
  - G3S-B2 layer-stack preflight — PASS/CLOSED DIAGNOSTIC
  - **G3S-B3 complete body base** ← CURRENT
    - B3A V1 — FAIL/CLOSED REVISION: wrong MPFB gender polarity
    - B3A V2 — PASS/CLOSED structural adult-female guide
    - B3B V1 — FAIL/CLOSED ROUTE: 3D-mask-owned silhouette
    - B3B V2 — FAIL/CLOSED VISUAL ROUTE: procedural/mannequin look
    - covered Grok body turnaround — PASS historical reference / SUPERSEDED
    - **fully nude Grok body turnaround — PASS / APPROVED PRIMARY BODY REFERENCE / NOT PRODUCTION ART**
    - **B3B V3 nude-reference native-grid review spike** ← CURRENT / READY TO RERUN
  - B4 hair — BLOCKED UNTIL B3B PASS
  - B5 clothing/restraints/accessories — BLOCKED UNTIL B3B PASS
  - G3S-C layered walk proof — BLOCKED UNTIL B3/B4/B5

## Approved high-resolution nude body reference — PASS

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical expected local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

Source facts:

- SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`;
- dimensions `2048×1401`;
- views: front, back, profile, front-three-quarter;
- adult female, bald/hairless for body-reference purposes, barefoot;
- lean / functional / resilient;
- mature, severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell;
- full pelvic anatomy visible;
- no occluding garment.

It supersedes the previous covered turnaround SHA `2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474` as primary anatomy reference.

This eliminates the previous reference-stage pelvic occlusion problem. V3 must not synthesize or patch that region.

## B3B visual PASS rule

A candidate must read immediately as the Exilada's adult sword-and-sorcery body: attractive, sensual, strong, dangerous, severe and lived-in — **beauty + hardness + survival**.

Automatic FAIL: procedural mannequin, generic fitness/character-creator body, superhero exaggeration, shortened/squat body, weak chest/pelvis/thigh anatomy, bad hands/feet at 1×, pseudo-3D/filtered render, sanitized body language or absent Exilada identity.

## B3B V3 — current bounded visual spike

Runner:

`tools/structured-2d-character-pipeline/13_run_g3s_b3b_v3_reference_guided_translation.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_reference_guided_translation.py`

V3 now pins the approved nude **2D** turnaround by SHA256 and canonical repo-local path. It uses the front-three-quarter panel for a native-scale review abstraction, performs no synthetic pelvic repair and does not read B3A/hidden-3D RGB or mask for visible translation.

### V3 authority boundary

**V3 output is not automatically a production B3B source.**

The existing rule rejecting simple high-resolution resize/quantize as final Production Pixel Master remains locked. V3 is only a bounded test of whether the approved body survives native-scale abstraction well enough to inform authored pixel art.

If the contact sheet reads as reduced illustration/filtering, procedural art or mannequin anatomy, V3 is FAIL/CLOSED and nothing is promoted. No model cleanup applies because V3 downloads no model weights.

If V3 is visually useful, the accepted native cluster/silhouette language must then be established as an independently owned persistent B3B production asset and validated.

## Current exact action

One-time prerequisite: save the exact approved nude turnaround at:

`D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_body_turnaround_nude_approved.jpg`

Expected SHA256:

`1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`

Then run exactly:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\13_run_g3s_b3b_v3_reference_guided_translation.ps1"
```

Then STOP and inspect/share only:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

or the complete console error.

B4/B5/G3S-C remain blocked.

## Workspaces

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- shared embedded Python runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
