# Next-chat handoff — G3S-B3 Body Base

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Mandatory source of truth

Before acting, read:

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/CHARACTERS.md`
4. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
5. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
6. `docs/PIXEL_ART_PRODUCTION.md`
7. `docs/ANIMATION_PIPELINE.md`
8. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
9. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
10. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
11. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`

Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant — MANDATORY

Every state-changing project action must update thematic docs, `PROJECT_STATE`, this handoff when continuation changes, and commit before reporting completion.

## Locked architecture

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides, but persistent 2D pixel assets own final visible RGB/alpha/silhouette.

High-resolution render/reference art may not be mechanically pixelated into production art.

The final user-supplied body reference is different: it is already pixel-art imagery. A review candidate may therefore select one existing pixel-art view and normalize scale with nearest-neighbor only, without anatomy/silhouette repair or palette synthesis. This still requires visual approval before production promotion.

## Build order

1. complete adult hairless body base;
2. separate hair;
3. separate clothing/bindings;
4. separate cuffs/shackles/chains/accessories;
5. layered sprite animation driven by hidden-rig guides.

## Gate history

- B3A V1 — FAIL/CLOSED REVISION.
- B3A V2 — PASS/CLOSED structural guide.
- B3B V1 — FAIL/CLOSED 3D-mask-owned silhouette.
- B3B V2 — FAIL/CLOSED procedural/mannequin visual route.
- high-resolution nude turnaround — supporting anatomy reference only.
- B3B V3 — FAIL/CLOSED: reduced/quantized high-resolution render.
- final user-supplied four-view pixel-art visual reference — PASS / LOCKED / no more user generation.
- **B3B V4 locked pixel-reference normalization — CURRENT / RUNNER READY / REVIEW NEXT.**

## Fixed references

Supporting anatomy reference:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`.

Final user-supplied pixel-art reference marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Source:

- SHA256 `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`;
- `1168×784` JPEG;
- front/back/profile/front-three-quarter;
- adult nude/hairless body;
- flat dark presentation background.

Hard interaction lock: do not ask the user for another body image, another Grok prompt or another turnaround.

## 128 px clarification

`128 px` is the visible standing body height in the locked `640×360` gameplay raster, not a universal frame-canvas size.

## V4 implementation

Specification:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_direct_pixel_authoring_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_extract_pixel_reference_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/14_run_g3s_b3b_v4_pixel_reference_candidate.ps1`

Output:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference`

Method:

- locate exact locked reference by SHA;
- verify `1168×784`;
- select the existing rightmost front-three-quarter pixel-art body;
- remove only the flat dark presentation background;
- normalize standing height to `128 px` with nearest-neighbor only;
- no hidden-3D visible source;
- no high-resolution anatomy-render visible source;
- no palette synthesis;
- no anatomy repair;
- no silhouette morphing;
- no automatic production promotion.

## Exact next operator action

Run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\14_run_g3s_b3b_v4_pixel_reference_candidate.ps1"
```

The runner searches for the exact locked reference by SHA in the canonical repo path and common user image folders (`Downloads`, `Desktop`, `Pictures`).

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference\g3s_b3b_v4_contact_sheet.png`

or the complete console error.

B4/B5/G3S-C remain blocked.

## Actual local AI state

- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable` (historical folder name; Qwen weights removed);
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- old Git tool directories do not prove installed models;
- do not assume Wan-Animate-2 installed;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed.

## Operator/process rules

- read canonical docs before every project action;
- update docs before reporting state changes;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no additional body-reference requests;
- no new sprite-model search unless explicitly reopened;
- no B4/B5/G3S-C before B3B PASS;
- include exact cleanup commands when a model route is closed and no longer needed;
- verify actual local runtime/disk state before naming installed tools.
