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

High-resolution 2D reference art is also reference only: do not mechanically resize/quantize/trace/filter it and call the result production pixel art.

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
- **fully nude Grok four-view turnaround — PASS / APPROVED PRIMARY BODY REFERENCE / NOT PRODUCTION ART.**
- B3B V3 reduced-reference native-grid spike — **FAIL/CLOSED VISUAL AND METHOD ROUTE**: it produced a reduced/quantized render, not authored pixel art.
- **B3B authored native-pixel body candidate — CURRENT.**

## Approved nude body reference

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

Source identity:

- SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`;
- `2048×1401`;
- four views: front/back/profile/front-three-quarter;
- adult woman, ~162 cm identity;
- natural adult feminine proportions, lean/functional/resilient;
- olive/brown skin, bald/hairless for body-reference purposes, barefoot;
- mature, severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell;
- fully nude with pelvic anatomy visible and no occluding garment.

## 128 px clarification

`128 px` is the **visible standing body height** in the locked `640×360` gameplay view with orthographic `26°` camera. It is not a universal `128×128` frame limit. Animation frames may have larger transparent bounds while preserving the same body scale.

## V3 closure — DO NOT RERUN

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

V3 mechanically reduced the high-resolution reference to native scale, inherited its silhouette/value structure and quantized it. The result was a tiny reduced render / photo-like image with large pixels, not pixel art. It is closed and must not be promoted or rerun. No model cleanup applies because V3 downloaded no model weights.

## Current exact gate

**No B3B runner is currently approved.**

The next visual artifact must be an **actually authored native-pixel Exilada body candidate** at approximately `128 px` visible standing height. The approved nude turnaround is anatomy/design reference only.

Do not create another resize/quantize/filter conversion runner.

Do not start B4/B5/G3S-C before B3B passes.

## Actual local AI state — USER-VERIFIED 2026-09-06

The user showed the current `Z:\AI` contents after cleanup. Retained relevant directories:

- `Z:\AI\QwenImageEditSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\Flux2RefControlSpike`

Interpretation is locked:

1. **Only retained general local AI application/runtime for the current project:**
   `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`

   The folder name is historical. Qwen model weights were removed when the Qwen route closed. Do not say “Qwen is installed” merely because this directory remains; what remains is the shared ComfyUI/embedded-Python runtime.

2. `Z:\AI\RogueliteCharacterPipeline` is **workspace/output/deterministic tooling**, not another AI model/application.

3. `Z:\AI\Flux2RefControlSpike` is **frozen evidence/workspace from the closed RefControl spike**, not the active B3B visual author and not a route to reopen automatically.

4. Git repository folders such as `tools/wan-animate2-spike`, `tools/sprite-animation` and old model-spike code are **repository history/tooling only**. Their existence in Git does not mean those models are installed locally.

5. **Do not assume Wan-Animate-2 is installed locally.** A future chat must verify disk/runtime state before naming it as present.

6. Closed local sprite-model routes remain closed: Qwen-native, SD1.5, PixelLock and Alucard. Do not reopen them or speak of their model weights as still present without fresh evidence.

7. Blender/MPFB may remain as hidden structural infrastructure outside this `Z:\AI` inventory, but that is not a second local pixel-art authoring stack.

This section exists specifically to prevent cross-chat confusion between **installed runtime**, **workspace/evidence**, and **historical repository tooling**.

## Operator/process rules

- read canonical docs before every project action;
- **after every action that changes state, update the relevant living document(s), `docs/PROJECT_STATE.md`, and this handoff when applicable before reporting completion**;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no new sprite-model search unless the canonical decision is explicitly reopened;
- no B4/B5/G3S-C before B3B PASS;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact cleanup commands in the same response;
- before naming a local tool/model as installed, verify the actual current runtime/disk state instead of inferring from old code or folder names.
