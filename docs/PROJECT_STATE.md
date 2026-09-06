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

**Every project action that changes state must update the living documents before that action is reported as complete.**

This includes, without exception: decisions, approvals/rejections, generated or reviewed artifacts, PASS/FAIL/CLOSED results, runner/tool creation or removal, runtime/install/cleanup state, architecture changes, visual-direction changes, next-step changes and operator instructions.

Required sequence for every such action:

1. perform/inspect the action;
2. update the relevant thematic living document(s);
3. update `docs/PROJECT_STATE.md` with the current gate/state when the action affects project state;
4. update the active cross-chat handoff when continuation instructions or local runtime/tool state changed;
5. make the focused Git commit(s);
6. only then tell the user the action is complete and give the next command/action.

Do **not** leave the canonical state only in chat. Do **not** postpone documentation until the end of a batch. Cross-chat continuation must be possible from GitHub alone.

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

The same principle now explicitly applies to high-resolution 2D reference art: reference images may guide design/anatomy but may not be mechanically resized, quantized, traced or filtered into final production sprite geometry.

Final character art is owned by persistent native 2D pixel assets. Runtime/export remains sprite-based.

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
    - fully nude Grok body turnaround — **PASS / APPROVED PRIMARY BODY REFERENCE / NOT PRODUCTION ART**
    - B3B V3 reduced-reference native-grid spike — **FAIL/CLOSED VISUAL AND METHOD ROUTE**
    - **B3B authored native-pixel body candidate** ← CURRENT
  - B4 hair — BLOCKED UNTIL B3B PASS
  - B5 clothing/restraints/accessories — BLOCKED UNTIL B3B PASS
  - G3S-C layered walk proof — BLOCKED UNTIL B3/B4/B5

## Approved high-resolution nude body reference — PASS

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical local path:

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

This reference resolves the intended body but remains design/anatomy reference only.

## B3B V3 — FAIL/CLOSED

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

SHA256:

`ded6e53cd5c36b106a7d7729534cd2f12241862a6f3b0e3a27b6e706ded08047`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

V3 mechanically isolated the three-quarter reference, downscaled it to `128 px`, retained the reduced reference silhouette/mask, quantized colors and applied cleanup. The result reads as a **tiny reduced render**, not authored modern pixel art.

Observed failure:

- no deliberate pixel-art silhouette authoring;
- face/hands/feet collapse at native scale;
- render-like/noisy value structure survives reduction;
- anatomy is inherited mechanically rather than redesigned for the pixel grid;
- the route proves no usable production pixel-language solution.

V3 is closed and must not be promoted or rerun. No model cleanup applies because V3 downloaded no model weights.

## B3B visual PASS rule

A candidate must read immediately as the Exilada's adult sword-and-sorcery body: attractive, sensual, strong, dangerous, severe and lived-in — **beauty + hardness + survival**.

Automatic FAIL: procedural mannequin, generic fitness/character-creator body, superhero exaggeration, shortened/squat body, weak chest/pelvis/thigh anatomy, bad hands/feet at 1×, pseudo-3D/filtered render, reduced-illustration look, sanitized body language or absent Exilada identity.

## Current exact action

**No B3B runner is approved.**

The next artifact must be an **actually authored native-pixel body candidate**, not another conversion script. It should be one gameplay-view body sprite at approximately `128 px` visible standing height, using the approved nude turnaround only as anatomy/design reference.

Do not resize, quantize, mechanically trace or filter the high-resolution turnaround into the final candidate.

Only after that authored candidate visually passes should deterministic import/validation/export tooling be committed.

B4/B5/G3S-C remain blocked.

## Actual local AI disk/runtime state — LOCKED 2026-09-06

User visually verified the contents of `Z:\AI` after the cleanup work. The relevant retained directories are:

- `Z:\AI\QwenImageEditSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\Flux2RefControlSpike`

Interpret them correctly:

- **`QwenImageEditSpike\ComfyUI_windows_portable` is the only retained general local AI application/runtime currently used by this project.** The directory name is historical. The Qwen image-edit model weights themselves were removed when that route was closed. Do not infer that Qwen is still installed merely from the directory name.
- **`RogueliteCharacterPipeline` is the deterministic project workspace/output area**, not a generative model or a second AI application.
- **`Flux2RefControlSpike` is frozen spike evidence/workspace from the closed RefControl investigation**, not the current B3B authoring tool and not a reason to reopen that route.
- Repository directories such as `tools/wan-animate2-spike`, `tools/sprite-animation`, `tools/qwen-image-edit-2509-spike`, etc. are historical/experimental code in Git. Their presence in the repository **does not prove corresponding models/runtimes are installed on `Z:\AI`**.
- **Wan-Animate-2 is not to be assumed installed locally.** Do not tell the user it is the current local tool unless a fresh local inspection proves it.
- Closed model routes Qwen-native, SD1.5, PixelLock and Alucard remain closed and their model-specific weights must not be treated as present merely because code/logs remain in Git.
- Blender/MPFB may remain installed as hidden structural infrastructure outside this `Z:\AI` inventory, but they are not a competing local pixel-art authoring stack.

Cross-chat rule: before naming any local model/tool as installed or active, read this section and distinguish **runtime**, **workspace/evidence**, and **repository-only historical tooling**.

## Workspaces

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`
- deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
