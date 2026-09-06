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

## Living-document invariant — LOCKED

Every project action that changes state must update the living documents before that action is reported complete.

Required sequence: perform/inspect -> update thematic docs -> update `PROJECT_STATE` -> update active handoff when applicable -> commit -> only then report completion/next action.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical design master:

`assets/source/characters/exilada/reference/exilada_master.png`

Adult woman, approximately 162 cm, lean/functional/resilient anatomy, natural adult feminine proportions, olive-brown skin, severe mature face, very long heavy black hair, degraded beige cloth in the initial equipped state, captivity history, bare feet, weaponless base identity.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell remain explicit visual references. Mature sensuality, erotic charge and adult nudity are legitimate parts of the visual language and are not automatically sanitized.

## Body-first rule — LOCKED

The production character owns a complete adult body base independent of hair, clothing and restraints.

## Hard operator constraint

The user does not perform routine Blender/Aseprite/rigging work and does not repaint frames manually. Normal production remains scriptable/headless.

Normal operator loop once a runner is approved:

`git pull -> one documented PowerShell command -> inspect/share output`

## Visible-ownership invariant — CRITICAL

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides but not final visible RGB/alpha/silhouette. Final visible art is owned by persistent native 2D pixel assets.

High-resolution render/reference art may not be mechanically pixelated into production art.

A separate case is now explicitly recognized for the user-locked **pixel-art** turnaround: a bounded review candidate may extract an existing pixel-art view and normalize scale using nearest-neighbor only, provided no anatomy/silhouette repair, palette synthesis, smoothing or render-to-pixel conversion is performed. Visual approval is still mandatory before promotion.

## Locked gameplay baseline

- native scene: `640×360`;
- orthographic camera;
- pitch: `26°`;
- protagonist visible standing height: approximately `128 px`.

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
    - B3A V1 — FAIL/CLOSED REVISION
    - B3A V2 — PASS/CLOSED structural adult-female guide
    - B3B V1 — FAIL/CLOSED ROUTE: 3D-mask-owned silhouette
    - B3B V2 — FAIL/CLOSED VISUAL ROUTE: procedural/mannequin look
    - fully nude Grok high-resolution turnaround — PASS / SUPPORTING ANATOMY REFERENCE / NOT PRODUCTION ART
    - B3B V3 reduced-reference spike — FAIL/CLOSED VISUAL AND METHOD ROUTE
    - final user-supplied four-view pixel-art visual reference — PASS / LOCKED / NO FURTHER USER GENERATION
    - **B3B V4 locked pixel-reference normalization** ← CURRENT / RUNNER READY / REVIEW NEXT
  - B4 hair — BLOCKED UNTIL B3B PASS
  - B5 clothing/restraints/accessories — BLOCKED UNTIL B3B PASS
  - G3S-C layered walk proof — BLOCKED UNTIL B3/B4/B5

## Locked B3B references

### Supporting high-resolution nude anatomy reference

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`.

Role: anatomy/proportion support only; never visible sprite source.

### Final user-supplied pixel-art visual reference — LOCKED

Marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Source facts:

- SHA256 `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`;
- dimensions `1168×784`;
- JPEG;
- front/back/profile/front-three-quarter;
- adult nude/hairless body;
- pixel-art imagery on flat dark background.

Hard interaction lock: do not ask the user for another body image, turnaround, Grok prompt or reference-generation attempt.

## B3B V3 — FAIL/CLOSED

V3 reduced/quantized a high-resolution render and therefore produced a reduced render, not authored pixel art.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

No model cleanup applies.

## B3B V4 — CURRENT

Spec:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_direct_pixel_authoring_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_extract_pixel_reference_candidate.py`

Approved review runner:

`tools/structured-2d-character-pipeline/14_run_g3s_b3b_v4_pixel_reference_candidate.ps1`

V4 uses only the locked pixel-art turnaround as visible source. It selects the existing front-three-quarter figure, removes the flat presentation background, normalizes visible height to `128 px` using nearest-neighbor only, and produces native/enlarged/gameplay review outputs. It does not use the high-resolution anatomy render as visible source and does not invent/repair anatomy.

Automatic promotion is forbidden.

## Current exact action

Run exactly:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\14_run_g3s_b3b_v4_pixel_reference_candidate.ps1"
```

The runner searches the exact locked reference by SHA in the canonical repo path and common user image folders (`Downloads`, `Desktop`, `Pictures`).

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference\g3s_b3b_v4_contact_sheet.png`

or the complete console error.

B4/B5/G3S-C remain blocked.

## Actual local AI disk/runtime state — LOCKED 2026-09-06

- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable` (folder name historical; Qwen weights removed);
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- repository-only old spike code does not imply local model installation;
- Wan-Animate-2 must not be assumed installed without fresh verification;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed;
- Blender/MPFB may remain only as hidden structural infrastructure.
