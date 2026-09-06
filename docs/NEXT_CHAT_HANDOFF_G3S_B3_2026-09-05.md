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

The final user-supplied body reference is already pixel-art imagery. One existing view may therefore be extracted and scale-normalized with nearest-neighbor only, provided no anatomy/silhouette repair, palette synthesis, smoothing or render-to-pixel conversion is performed.

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
- **B3B V4 locked pixel-reference candidate — VISUAL PASS / CORRECTED PROMOTION READY.**

## Fixed references

Supporting anatomy reference:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`.

Final user-supplied pixel-art reference marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Source SHA256:

`f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`

Hard interaction lock: do not ask the user for another body image, another Grok prompt or another turnaround.

## B3B V4 review — PASS

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference\g3s_b3b_v4_contact_sheet.png`

Recorded SHA256:

`2b3ad85e956fdd432fe6cd52ac94d71afd30b5603b071681f81d2dbd8788a182`

Approved native body candidate:

- `37×128` RGBA;
- `128 px` visible standing height;
- **authoritative local raw RGBA SHA256:** `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The older `bd4a78e...` digest was measured from an assistant-side reconstructed candidate and is superseded for promotion.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_visual_approval.json`

This passes the nude/hairless body-base visual gate only.

## First promotion attempt — implementation bug

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_promotion_hash_mismatch.json`

The first promotion attempt refused correctly because the promoter expected the wrong raw digest. Observed local candidate: `818f0538...`; hardcoded assistant-side reconstruction: `bd4a78e...`.

No art decision changed. No model cleanup applies.

## Corrected promotion implementation

Promotion helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_promote_body_base.py`

Promotion runner:

`tools/structured-2d-character-pipeline/15_promote_g3s_b3b_v4_body_base.ps1`

The corrected runner:

- does **not** rerun V4 generation;
- uses the existing local candidate already present in `Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference`;
- verifies `37×128`, exact authoritative raw RGBA digest and 128 px visible alpha height;
- copies exact pixels to the canonical asset tree;
- writes provenance JSON;
- commits/pushes only the canonical body PNG + metadata JSON.

Canonical targets:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

## Exact next operator action

Run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\15_promote_g3s_b3b_v4_body_base.ps1"
```

**Do not run runner 14 first.** The existing candidate from the failed promotion attempt is the artifact to promote.

Then send the final console output.

If promotion/push succeeds, immediately update living docs to **G3S-B3B PASS/CLOSED** and open **G3S-B4 hair**.

## Actual local AI state

- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable` (historical folder name; Qwen weights removed);
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- PixelLab is historical external paid spike code only and is not active/authorized;
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
- no B4/B5/G3S-C before B3B promotion is confirmed;
- include exact cleanup commands when a model route is closed and no longer needed;
- verify actual local runtime/disk state before naming installed tools.
