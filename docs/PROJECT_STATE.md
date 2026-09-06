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
11. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
12. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
13. `docs/G3S_B4_HAIR_LOG.md`
14. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every project action that changes state must update the living documents before that action is reported complete.

Required sequence: perform/inspect -> update thematic docs -> update `PROJECT_STATE` -> update active handoff when applicable -> commit -> only then report completion/next action.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical design master: `assets/source/characters/exilada/reference/exilada_master.png`.

Adult woman, approximately 162 cm, lean/functional/resilient, natural adult feminine proportions, olive-brown skin, severe mature face, very long heavy messy black hair, captivity history, bare feet, weaponless base.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell remain explicit visual references.

## Hard operator constraint

The user does not perform routine Blender/Aseprite/rigging work and does not repaint frames manually. Normal production remains scriptable/headless.

Normal operator loop once a runner is approved:

`git pull -> one documented PowerShell command -> inspect/share output`

## Visible-ownership invariant — CRITICAL

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides but not final visible RGB/alpha/silhouette. Final visible art is owned by persistent native 2D pixel assets.

## Locked gameplay baseline

- native scene: `640×360`;
- orthographic camera;
- pitch: `26°`;
- protagonist visible standing body height: approximately `128 px`.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3 first native translation — TECHNICAL PASS / LOOK NOT APPROVED
- G3R primitive renderer refinement — FAIL/CLOSED
- G3V representative continuous human visual proxy — FAIL/CLOSED
- **G3S structured 2D visible representation** ← ACTIVE
  - G3S-B3 complete body base — **PASS/CLOSED**
    - B3B V4 — **PASS/CLOSED / PRODUCTION BODY BASE PROMOTED**
  - **G3S-B4 hair** ← CURRENT / OPEN
    - B4A preflight — **PASS/CLOSED DIAGNOSTIC**
    - B4B V1 master extraction — **FAIL/CLOSED PRE-RUN METHOD**
    - B4B V2 authored two-layer — **FAIL/CLOSED VISUAL / STRUCTURAL PASS**
    - B4B V3 authored two-layer — **FAIL/CLOSED VISUAL AND ALIGNMENT METHOD**
    - B4B V4 pose-anchored authored two-layer — **FAIL/CLOSED VISUAL AND METHOD**
    - **procedural Pillow/heuristic-anchor hair authoring route — CLOSED**
    - **no approved B4 runner currently exists**
  - G3S-B5 clothing/restraints/accessories — BLOCKED UNTIL B4 PASS
  - G3S-C layered walk proof — BLOCKED UNTIL B3/B4/B5

## Canonical production body base — LOCKED

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- dimensions `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body remains byte/pixel unchanged under B4/B5 composition.

## G3S-B4 hair — CURRENT / OPEN

Canonical hair direction: black/nearly black, very long, heavy, voluminous, messy, wild, primary silhouette anchor.

Mandatory composition:

`rear_hair -> body -> front_hair`

### B4B V4 — FAIL/CLOSED VISUAL AND METHOD

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

SHA256:

`50dd663cbbeb0bb1a9865f2ac95daedc7990ceaf7a98ae6a968c8b7eacb4a8a5`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchor_failure.json`

Root cause:

- the pose detector itself is invalid for this task; the reviewed sheet reports `shoulder_span=6.36 px` for a `37 px`-wide body, proving it is not measuring the real shoulder span;
- head center + shoulder row/span + torso center + binary facing bias do not encode enough of the actual 3/4 pose;
- they omit head tilt, shoulder slope, torso rotation, arm occlusion, back contour and local depth;
- hard-coded Pillow polygons/lines therefore cannot visually wrap the hair around the actual body pose.

### Route closure — LOCKED

Do not create another B4 hair candidate by:

- extracting master pixels;
- fixed master-pose coordinates;
- heuristic body anchors plus hard-coded Pillow polygons/lines;
- primitive procedural lock generation.

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1` is intentionally disabled to prevent accidental reruns of the closed route.

No model/API was used by V4; no cleanup command applies.

## Current exact action

**No B4 runner is approved.**

The next B4 solution must be **real visual 2D authoring/adaptation to the actual canonical B3B pose**, while preserving separate `rear_hair` and `front_hair` ownership. Do not start B5 or G3S-C before B4 passes.

## Actual local AI state — LOCKED 2026-09-06

- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`;
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- PixelLab is historical external paid spike only and is not active/authorized;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed;
- do not assume Wan-Animate-2 installed without fresh verification.
