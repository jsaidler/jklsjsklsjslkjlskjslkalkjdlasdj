# Next-chat handoff — G3S-B3 Nude Body Base

Status date: **2026-09-05**

Purpose: exact continuation state for opening a new chat without losing project decisions.

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
10. `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`
11. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

GitHub living documents are canonical. Do not reconstruct project state from chat memory when the documents disagree. Update the relevant thematic document + `docs/PROJECT_STATE.md` after every material step.

## Current production state

Validated backbone remains:

- G0 automation — PASS;
- G1 camera/native scale — PASS: `640×360`, orthographic, `26 deg`, protagonist ~`128 px`;
- G2 real motion/topology — PASS using CMU `105_34 NormalWalk`;
- G3V-R retarget — PASS using `DIRECTION_SPACE_FK`;
- G3V visible 3D/pixel translation — FAIL/CLOSED;
- hidden 3D is infrastructure only, not final visible character art.

G3S state:

- source-model search — CLOSED;
- G3S-B V1 decomposition — FAIL/CLOSED;
- G3S-B2 layer-stack preflight — PASS/CLOSED diagnostic;
- G3S-B3 complete nude body base — CURRENT;
- G3S-B3A V1 — FAIL/CLOSED REVISION because of wrong MPFB gender polarity;
- G3S-B3A V2 corrected adult-female anatomy guide — PASS/CLOSED;
- G3S-B3B V1 mask-derived authoring route — **FAIL/CLOSED ROUTE**;
- **G3S-B3B corrected genuine native-2D body-source method — CURRENT / NOT YET IMPLEMENTED**.

## Locked visible-ownership invariant

The G3V kill switch is authoritative.

Hidden 3D may own:

- real motion;
- topology/left-right identity;
- sockets/contacts;
- depth/occlusion metadata;
- physics;
- anatomy/proportion guides;
- secondary-motion driving data.

Hidden 3D may **not** own final visible RGB or final sprite silhouette.

Final visible art is owned by persistent 2D pixel assets. Runtime/export remains sprite-based.

Therefore:

- a 3D render may be inspected as a guide;
- a 3D binary mask may be inspected as a guide;
- neither may be cropped/recolored/quantized and promoted mechanically into the final sprite alpha/silhouette;
- the native 2D source itself must own silhouette, clusters, palette/value structure, edge treatment and final alpha.

## Locked build order

1. complete adult nude/hairless native 2D body base;
2. separate persistent hair asset/layer family;
3. separate clothing/bindings overlays;
4. separate cuffs/shackles/chains/accessories/equipment;
5. layered sprite animation proof driven by hidden rig guides.

Do not extract hidden anatomy from the composite master. It is identity/proportion reference only.

## Nudity and erotic charge — LOCKED

Nudity is a normal supported state. The complete body base always exists and garments/equipment are optional layers.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell remain explicit references. Sensuality, erotic charge, idealized adult bodies and nudity are legitimate parts of the mature visual vocabulary. Do not impose automatic desexualization or automatic sexualization; framing is intentional to scene/state.

## B3A result — PASS/CLOSED

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

B3A remains useful only as anatomy/proportion/joint/scale guidance.

## B3B V1 route — FAIL/CLOSED

The rejected implementation used the B3A projected mask directly as the final native body alpha/silhouette and then procedurally colored it.

That violates the visible-ownership invariant even though it did not copy the lit-guide RGB.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

The invalid files were removed from `main`:

- `tools/structured-2d-character-pipeline/g3s_b3b_native_body_source.py`;
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_native_body_source.ps1`.

No model was downloaded/discarded by this correction; no model cleanup command applies.

## Current exact gate: G3S-B3B METHOD DESIGN

Do **not** give the user a runner yet.

First design a method that produces one genuine native `128×128` 2D nude body sprite source where:

- B3A is reference only;
- final alpha/silhouette are independently authored in 2D;
- final RGB/pixel clusters are independently authored in 2D;
- no procedural mannequin renderer is treated as final art;
- no new sprite-model search is opened;
- no user manual pixel editing is required;
- the result can later be decomposed/animated as persistent 2D parts driven by hidden rig guides.

Only after this method is reviewed against the canonical documents should new tooling be committed.

## Operator/process rules

- before every material action, read the current project documents first;
- normal loop after a runner is actually approved: `git pull -> one documented PowerShell command -> inspect/share output`;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no unrequested image generation;
- no new sprite-model search;
- topology/anatomy-first visual QA;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact PowerShell cleanup commands for its model-specific files in the same response;
- preserve small evidence outputs and shared runtimes still in use;
- after every material step update relevant living docs + `docs/PROJECT_STATE.md` and commit.

## Prompt to paste into the next chat

> Continue o projeto Roguelite exatamente do estado canônico no GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`. Antes de qualquer ação, leia `docs/PROJECT_STATE.md`, `docs/VISUAL_DIRECTION.md`, `docs/CHARACTERS.md`, `docs/CHARACTER_PRODUCTION_PIPELINE.md`, `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`, `docs/PIXEL_ART_PRODUCTION.md`, `docs/ANIMATION_PIPELINE.md`, `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`, `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`, `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`, `docs/G3S_B3_NUDE_BODY_BASE_LOG.md` e este handoff. Não reconstrua decisões pela memória.
>
> Estado atual: G3V rejeitou 3D como dono da imagem visível. O 3D oculto pode fornecer motion/topology/sockets/depth/anatomy guides, mas os sprites 2D persistentes devem possuir silhouette, alpha e RGB finais. B3A V2 passou apenas como guia anatômico estrutural. O primeiro B3B V1 foi rejeitado porque copiou a máscara projetada do 3D como silhouette/alpha final e depois a coloriu proceduralmente. O marker é `g3s_b3b_v1_route_failure.json`; o script e runner foram removidos. O gate atual é desenhar o método correto para um body source 128x128 genuinamente 2D, sem reabrir busca por modelos e sem exigir edição manual do usuário. Não entregue runner antes de verificar essa arquitetura contra os documentos.
