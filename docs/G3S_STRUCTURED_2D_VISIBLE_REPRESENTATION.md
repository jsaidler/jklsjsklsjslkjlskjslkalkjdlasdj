# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-B2 LAYER STACK PREFLIGHT READY**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets -> complete 2D body base -> separate hair -> separate clothing/equipment/accessories -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character color pixels.

## Canonical layer ownership — LOCKED

This must match `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`:

1. complete persistent unclothed body base;
2. hair / body-attached secondary masses;
3. underlayers / soft clothing;
4. outer clothing;
5. armor;
6. restraints/accessories;
7. weapons/tools;
8. surface-state overlays;
9. transient VFX.

Consequences:

- clothing may visually exist in the initial state but is never baked into body ownership;
- hair is never part of torso/head/body pixels; it is a separate persistent secondary-motion family;
- the body must exist underneath removable clothing and underneath hair;
- chains/restraints are separate socketed accessories/state;
- animation cannot begin from an incomplete body underlayer.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI operation by the user;
- no beauty-render shrink/pixel-filter route as final art;
- no bilinear filtering;
- recurring work remains scriptable/headless;
- one-time source construction may use deterministic native-grid edits;
- animation consumes persistent semantic owners rather than independently generated frames.

## Model-discard cleanup rule — LOCKED

Whenever a model/route is declared **FAIL/CLOSED/REJECTED** and no longer required, the same response must include exact PowerShell cleanup commands for its model-specific files. Shared runtimes still in use are preserved; small result/log evidence remains unless explicitly removed.

Closed-model cleanup commands remain documented in project history. No model is being discarded by G3S-B/B2.

# G3S-A source history — CLOSED AS MODEL SEARCH

Bounded source experiments were completed and closed: Qwen direct-native, SD1.5 native re-author, PixelLock and Alucard did not produce an acceptable native source sprite.

Do not restart source-model search.

Retained design/provenance control:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## Face state

Authored V1 mouth was unreadable. G3S-A1 V2 mouth became an artificial block. The face remains unresolved/replacement-ready, but this localized defect no longer blocks architecture work.

Markers:

- `tools/structured-2d-character-pipeline/g3s_a_authored_v1_failure.json`
- `tools/structured-2d-character-pipeline/g3s_a1_v2_failure.json`

# G3S-B V1 — FAIL / CLOSED

Canonical log:

`docs/G3S_B_PERSISTENT_PART_DECOMPOSITION_LOG.md`

V1 technically achieved exact recomposition, but visual review exposed invalid semantic ownership:

- body/limb parts still contained garment/binding pixels;
- hair masks contained non-hair pixels;
- no complete body existed under hair/clothing.

This is a production-architecture failure even though the pixels recomposed exactly.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b_v1_failure.json`

Locked lesson: **pixel-exact reconstruction does not prove correct semantic ownership.**

# G3S-B2 — Layer Stack Preflight — CURRENT

Canonical log:

`docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`

Purpose: correct ownership before any animation.

B2 rebuilds the same pinned provisional source and diagnostically partitions it into:

- currently visible body pixels — explicitly marked incomplete;
- hair-only persistent layer family;
- clothing-only overlay family.

It then:

- requires exact recomposition of those visible families;
- generates a magenta diagnostic of body regions currently hidden by hair/clothing;
- reports exactly how many native body pixels still require real underlayer authoring;
- refuses to treat the current visible-body extraction as a complete body base.

B2 deliberately does **not** fill missing body regions with generic skin colors. That would only create another fake technical solution.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b2_layer_stack_spec_v1.json`
- `tools/structured-2d-character-pipeline/g3s_b2_layer_stack_preflight.py`
- `tools/structured-2d-character-pipeline/10_run_g3s_b2_layer_stack_preflight.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b2_layer_stack`

Review artifact:

`g3s_b2_contact_sheet.png`

## PASS meaning

B2 PASS means the ownership split is credible and the hidden-body problem is bounded. It does **not** mean the body base is complete.

Next gate after B2 review:

**G3S-B3 — Body Base Completion**

B3 must provide the complete persistent unclothed body under all removable layers.

# G3S-C — Four-phase walk proof

Blocked until B3 completes the body base and layer ownership is approved.

Persistent owners will then bind to validated motion frames `1568,1588,1608,1628`. No frame may be independently regenerated by diffusion.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\10_run_g3s_b2_layer_stack_preflight.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b2_layer_stack\g3s_b2_contact_sheet.png`

Do not run G3S-C.
