# Next-chat handoff — G3S-B3 Nude Body Base

Status date: **2026-09-05**

Purpose: exact continuation prompt/state for opening a new chat without losing project decisions.

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
- hidden 3D is infrastructure only, not final visible character art.

G3S state:

- G3S-A/A1 source/face attempts — closed/fail;
- G3S-B V1 decomposition — FAIL because exact recomposition did not imply correct semantic ownership;
- G3S-B2 layer-stack preflight — PASS/CLOSED diagnostic;
- B2 measured `1205` hidden/unknown body pixels under hair/clothing and proved the composite master cannot be converted into a complete body by subtraction;
- **G3S-B3 complete nude body base is CURRENT**.

## Locked build order

The production character must now be built in this exact order:

1. complete adult nude/hairless body base;
2. separate persistent hair asset/layer family;
3. separate clothing/bindings overlays;
4. separate cuffs/shackles/chains/accessories/equipment;
5. layered motion proof.

Do not extract hair/clothing/body ownership from the composite master as if hidden anatomy were recoverable. The master is identity/proportion reference only.

## Nudity and erotic charge — LOCKED

Nudity is a normal supported state in the game. The complete body base always exists and garments/equipment are optional layers.

The visual direction does **not** impose anti-erotic framing. Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell are explicit references; sensuality, erotic charge, idealized adult bodies and nudity are legitimate parts of the mature visual vocabulary.

The Exilada may be beautiful, sexualized, nude or minimally clothed while remaining severe, dangerous, wounded, dirty, vulnerable or brutal. Do not sanitize adult nudity by default. Framing should be intentional to scene/character rather than automatically neutral or automatically erotic.

## Current exact gate: G3S-B3A

B3A is a deterministic **anatomy guide only** using the already-present MPFB/hidden-rig infrastructure.

It must create:

- one complete adult female body;
- hairless scalp/body;
- no hair objects;
- no clothing/bindings;
- no cuffs, shackles or chains;
- complete chest/pelvis/limbs/hands/feet;
- Exilada-compatible proportions;
- locked G1 camera/scale reference.

It must **not** be accepted as final visible art merely because it renders successfully. A 3D-looking guide is acceptable at B3A because final pixels belong to B3B.

Tooling already exists:

- `tools/structured-2d-character-pipeline/g3s_b3_mpfb_bootstrap.py`
- `tools/structured-2d-character-pipeline/g3s_b3a_nude_anatomy_guide.py`
- `tools/structured-2d-character-pipeline/g3s_b3a_contact_sheet.py`
- `tools/structured-2d-character-pipeline/11_run_g3s_b3a_nude_anatomy_guide.ps1`

## Exact next operator action

Give the user only this run command unless repository inspection reveals the runner is missing/broken. Never tell the user to run a file before verifying it exists.

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\11_run_g3s_b3a_nude_anatomy_guide.ps1"
```

Then STOP and request only:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3a_nude_guide\g3s_b3a_contact_sheet.png`

or the complete console error if the runner fails.

## Next gate after B3A review

If B3A structurally passes, implement **G3S-B3B native `128×128` nude body-base source**. B3B owns final visible body pixels; the MPFB guide does not.

Do not start hair, clothing or animation before B3B passes.

## Operator/process rules

- normal loop: `git pull -> one documented PowerShell command -> inspect/share output`;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no unrequested `image_gen` calls;
- no new sprite-model search;
- topology/anatomy-first visual QA;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact PowerShell cleanup commands for its model-specific files in the same response;
- preserve small evidence outputs and shared runtimes still in use;
- after every material step update relevant living docs + `docs/PROJECT_STATE.md` and commit.

## Prompt to paste into the next chat

> Continue o projeto Roguelite exatamente do estado canônico no GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`. Antes de responder, leia `docs/PROJECT_STATE.md`, `docs/VISUAL_DIRECTION.md`, `docs/CHARACTERS.md`, `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`, `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`, `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`, `docs/G3S_B3_NUDE_BODY_BASE_LOG.md` e `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`. Não reconstrua decisões pela memória se os documentos disserem algo diferente.
>
> Estado atual: G3S-B2 passou como diagnóstico e provou que o master composto não serve para recuperar corpo oculto por subtração. A ordem agora está travada: **corpo adulto nu completo e sem cabelo -> cabelo separado -> roupas/bindings separados -> grilhões/correntes/acessórios separados -> animação em camadas**. Nudez é estado normal do jogo. A carga erótica também é permitida e faz parte da linhagem visual Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell; não imponha dessexualização automática. O corpo pode ser sensual/erótico, heroico, brutal, vulnerável ou neutro conforme a cena.
>
> O gate atual é **G3S-B3A deterministic nude anatomy guide**. O runner já deve existir em `tools/structured-2d-character-pipeline/11_run_g3s_b3a_nude_anatomy_guide.ps1`. Verifique no repositório antes de me mandar executar. Se estiver correto, me dê apenas um bloco PowerShell com `git pull --ff-only` e esse runner. Depois pare e peça somente o contact sheet ou o erro completo. Não gere imagem sem eu pedir. Não reabra busca por modelos. Atualize a documentação canônica a cada etapa e, sempre que descartar um modelo, inclua o comando exato para apagar seus arquivos.
