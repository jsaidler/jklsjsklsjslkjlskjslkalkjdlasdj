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

- canvas `640×360`;
- orthographic camera;
- pitch `26°`;
- protagonist reference height `128 px`.

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
    - high-resolution Grok body turnaround — **PASS / APPROVED BODY REFERENCE / NOT PRODUCTION ART**
    - **B3B V3 reference-guided native-grid translation spike** ← CURRENT / READY FOR RUN / REVIEW ONLY
  - B4 hair — BLOCKED UNTIL B3B PASS
  - B5 clothing/restraints/accessories — BLOCKED UNTIL B3B PASS
  - G3S-C layered walk proof — BLOCKED UNTIL B3/B4/B5

## Approved high-resolution body reference — PASS

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Source facts:

- SHA256 `2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474`;
- dimensions `1168×784`;
- views: front, back, profile, front-three-quarter;
- adult female, bald/hairless for body-reference purposes, barefoot;
- lean / functional / resilient;
- mature, severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell.

The reference contains a minimal dark loincloth/tapa-sexo. It is only an occluder in the high-resolution reference. It is **not body geometry**, must not be baked into B3B and later belongs to B5 if used as clothing.

This reference resolves the intended body. The remaining problem is translation into production-quality modern pixel art.

## B3B visual PASS rule

A candidate must read immediately as the Exilada's adult sword-and-sorcery body: attractive, sensual, strong, dangerous, severe and lived-in — **beauty + hardness + survival**.

Automatic FAIL: procedural mannequin, generic fitness/character-creator body, superhero exaggeration, shortened/squat body, weak chest/pelvis/thigh anatomy, bad hands/feet at 1×, pseudo-3D/filtered render, sanitized body language or absent Exilada identity.

## B3B V3 — current bounded visual spike

Ready marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_spike_ready.json`

Runner:

`tools/structured-2d-character-pipeline/13_run_g3s_b3b_v3_reference_guided_translation.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_reference_guided_translation.py`

V3 uses the approved **2D** turnaround only. It does not read B3A/hidden-3D RGB or mask for visible translation.

It automatically locates the exact approved image by SHA256 in common user image folders, isolates the three-quarter view, normalizes the visual study to the locked `128 px` body height, produces a deterministic native-grid palette/cluster abstraction, reconstructs the pelvis without assigning garment ownership, and emits a contact sheet plus gameplay preview.

### V3 authority boundary

**V3 output is not automatically a production B3B source.**

The existing rule rejecting simple high-resolution resize/quantize as final Production Pixel Master remains locked. V3 is a bounded test of whether a deterministic **2D-reference-guided** abstraction can cross the visual threshold into intentional modern pixel art.

If the contact sheet still reads as reduced illustration/filtering, procedural art or mannequin anatomy, V3 is FAIL/CLOSED and nothing is promoted. No model cleanup applies because V3 downloads no model weights.

If V3 visually passes, the accepted native cluster language must then be frozen/re-authored as the persistent B3B production source and independently validated.

## Current exact action

The V3 runner is approved for this bounded **review-only** spike.

Run exactly:

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
