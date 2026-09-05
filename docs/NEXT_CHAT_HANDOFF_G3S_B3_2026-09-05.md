# Next-chat handoff — G3S-B3 Nude Body Base

Status date: **2026-09-05**

Purpose: exact continuation state for opening a new chat without losing project decisions.

## Mandatory source of truth

Before acting, read:

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/CHARACTERS.md`
4. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
5. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
6. `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`
7. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

GitHub living documents are canonical. Update the relevant thematic document + `docs/PROJECT_STATE.md` after every material step.

## Current production state

The direct visible-art model search is closed. Qwen-native, SD1.5, PixelLock and Alucard did not produce an acceptable native source sprite. Do not reopen model hunting.

Validated backbone remains:

- G0 automation — PASS;
- G1 camera/native scale — PASS: `640×360`, orthographic, `26 deg`, protagonist ~`128 px`;
- G2 real motion/topology — PASS using CMU `105_34 NormalWalk`;
- G3V-R retarget — PASS using `DIRECTION_SPACE_FK`;
- hidden 3D is infrastructure only, not final visible character RGB.

G3S state:

- G3S-A/A1 source/face attempts — closed/fail;
- G3S-B V1 decomposition — FAIL because exact recomposition did not imply correct semantic ownership;
- G3S-B2 layer-stack preflight — PASS/CLOSED diagnostic;
- B2 measured `1205` hidden/unknown body pixels and proved the composite master cannot be converted into a complete body by subtraction;
- G3S-B3 complete nude body base — CURRENT;
- G3S-B3A V1 — FAIL/CLOSED REVISION because of wrong MPFB gender polarity;
- **G3S-B3A V2 corrected adult-female anatomy guide — PASS/CLOSED**;
- **G3S-B3B native `128×128` nude body source V1 — ACTIVE / READY TO RUN**.

## Locked build order

1. complete adult nude/hairless body base;
2. separate persistent hair asset/layer family;
3. separate clothing/bindings overlays;
4. separate cuffs/shackles/chains/accessories/equipment;
5. layered motion proof.

Do not extract hidden anatomy from the composite master. It is identity/proportion reference only.

## Nudity and erotic charge — LOCKED

Nudity is a normal supported state. The complete body base always exists and garments/equipment are optional layers.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell remain explicit references. Sensuality, erotic charge, idealized adult bodies and nudity are legitimate parts of the mature visual vocabulary. Do not impose automatic desexualization or automatic sexualization; framing is intentional to scene/state.

## B3A result

B3A V2 passes structurally:

- revision `G3S_B3A_NUDE_ANATOMY_GUIDE_V2`;
- resolved gender `female`;
- resolved life stage `adult`;
- female targets `21`, male targets `0`;
- adult targets `21`, minor targets `0`;
- complete body geometry;
- zero hair/clothing/restraint/chain objects;
- visible height `128 px`;
- pitch `26 deg`, guide yaw `8 deg`;
- guide-only art authority.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3A is closed. Do not use its lit RGB as final body art.

## Current exact gate: G3S-B3B

B3B owns final visible body RGB pixels.

The V1 implementation:

- consumes the approved B3A binary mask and projected joints as structural guides only;
- preserves 1:1 gameplay scale into a native `128×128` asset;
- does not sample/transfer B3A lit RGB/shading;
- authors RGB from an explicit native palette and deterministic pixel-cluster rules;
- creates zero hair/clothing/binding/restraint/chain pixels;
- writes a binary-alpha body source, mask, gameplay preview, manifest and contact sheet;
- requires native 1× visual review before B3B can pass.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b3b_native_body_source.py`
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_native_body_source.ps1`

## Exact next operator action

Verify the runner exists in GitHub, then give only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\12_run_g3s_b3b_native_body_source.ps1"
```

Then STOP and request only:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_native_body_source\g3s_b3b_contact_sheet.png`

or the complete console error if the runner fails.

Do not start B3S-B4 hair, B5 clothing/accessories or G3S-C animation before B3B passes.

## Operator/process rules

- normal loop: `git pull -> one documented PowerShell command -> inspect/share output`;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no unrequested image generation;
- no new sprite-model search;
- topology/anatomy-first visual QA;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact PowerShell cleanup commands for its model-specific files in the same response;
- preserve small evidence outputs and shared runtimes still in use;
- after every material step update relevant living docs + `docs/PROJECT_STATE.md` and commit.
