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

**Every project action that changes project state must be documented before it is reported complete.**

For every decision, approval/rejection, artifact review, PASS/FAIL/CLOSED result, runner/tool change, install/cleanup/runtime change, architecture change, visual-direction change, gate change or next-action change:

1. update the relevant thematic living document(s);
2. update `docs/PROJECT_STATE.md` whenever the current state/gate/next action is affected;
3. update this active handoff whenever continuation instructions or local runtime/tool state changes;
4. commit those updates;
5. only then report completion or give the next operator command.

Never leave authoritative project state only in chat. Never defer documentation to a later batch.

## Locked architecture

Hidden 3D may own motion/topology/joints/sockets/depth/physics/reference guides, but persistent 2D pixel assets own final visible RGB, alpha and silhouette. Runtime/export remains sprite-based.

Reference art is guidance only: do not mechanically resize/quantize/trace/filter it into final production pixel geometry.

Build order:

1. complete adult hairless body base;
2. separate hair;
3. separate clothing/bindings;
4. separate cuffs/shackles/chains/accessories;
5. layered sprite animation driven by hidden-rig guides.

Nudity is a normal supported state. The project does not impose blanket desexualization.

## Gate history

- B3A V1 — FAIL/CLOSED REVISION: wrong MPFB gender polarity.
- B3A V2 — PASS/CLOSED: adult-female structural guide at locked ~`128 px` visible standing scale.
- B3B V1 — FAIL/CLOSED ROUTE: copied B3A projected mask into final silhouette.
- B3B V2 — FAIL/CLOSED VISUAL ROUTE: procedural/mannequin body and poor pixel-art quality.
- covered Grok body turnaround — PASS historical reference / SUPERSEDED.
- fully nude Grok high-resolution turnaround — PASS / SUPPORTING ANATOMY REFERENCE / NOT PRODUCTION ART.
- B3B V3 reduced-reference native-grid spike — **FAIL/CLOSED VISUAL AND METHOD ROUTE**.
- final user-supplied four-view visual reference — **PASS / LOCKED / NO FURTHER USER GENERATION.**
- **B3B V4 native-pixel authoring from fixed references — CURRENT / IMPLEMENTATION NEXT.**

## Fixed references

### Supporting high-resolution nude anatomy reference

Marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256:

`1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`

Role: anatomy/proportion support only.

### Final user-supplied visual reference — LOCKED

Marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Source facts:

- SHA256 `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`;
- dimensions `1168×784`;
- JPEG;
- front/back/profile/front-three-quarter views;
- adult nude/hairless body reference.

**Hard interaction lock:** do not ask the user for another body image, turnaround, Grok prompt or reference-generation attempt. The assistant/pipeline must proceed from what already exists.

## 128 px clarification

`128 px` is the **visible standing body height** in the locked `640×360` gameplay view with orthographic `26°` camera. It is not a universal `128×128` frame limit.

## V3 closure — DO NOT RERUN

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

V3 produced a mechanically reduced/quantized render, not authored pixel art. It is closed and must not be promoted or rerun. No model cleanup applies because V3 downloaded no model weights.

## V4 — current method

Specification:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_direct_pixel_authoring_spec.json`

Core rule: **author the production body for the native pixel grid from the fixed references; do not convert the references into the sprite.**

The earlier V4 dependency on the user generating another Grok candidate is superseded.

Target:

- front-three-quarter elevated gameplay view approximating `26°` pitch;
- adult nude hairless body;
- approximately `128 px` visible standing height;
- intentional native pixel clusters/value groups;
- no high-res resize/quantize/trace route;
- no procedural mannequin final art;
- no routine manual repainting burden on the user.

## Current exact action

**Reference acquisition is closed. No B3B runner is currently approved.**

The assistant/pipeline must now **select/implement a valid native-pixel authoring path from the fixed references and produce the first real B3B body candidate.**

Do not ask the user for another image or prompt. Do not create another mechanical conversion runner. Do not reopen closed local model routes automatically.

B4/B5/G3S-C remain blocked until B3B passes.

## Actual local AI state — USER-VERIFIED 2026-09-06

Retained relevant `Z:\AI` directories:

- `Z:\AI\QwenImageEditSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\Flux2RefControlSpike`

Interpretation:

1. **Only retained general local AI application/runtime:** `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`. Folder name is historical; Qwen model weights were removed.
2. `RogueliteCharacterPipeline` is workspace/output/deterministic tooling, not another AI application.
3. `Flux2RefControlSpike` is frozen evidence from the closed RefControl spike, not active B3B authoring.
4. Repository-only historical tool folders do not imply local model installation.
5. Do not assume Wan-Animate-2 is installed locally without fresh verification.
6. Qwen-native, SD1.5, PixelLock and Alucard remain closed.
7. Blender/MPFB may remain only as hidden structural infrastructure.

## Operator/process rules

- read canonical docs before every project action;
- update living docs before reporting every state-changing action complete;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no new sprite-model search unless explicitly reopened in canonical state;
- no additional body-reference requests to the user;
- no B4/B5/G3S-C before B3B PASS;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact cleanup commands;
- verify actual local runtime/disk state before naming a tool/model as installed.
