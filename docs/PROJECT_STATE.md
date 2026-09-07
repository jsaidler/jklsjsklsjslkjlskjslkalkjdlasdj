# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
5. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
6. `docs/ANIMATION_PIPELINE.md`
7. `docs/CHARACTERS.md`
8. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Do not reconstruct a candidate route from memory when a prior test exists in Git history or canonical docs.

## Model exhaustion protocol — LOCKED 2026-09-07

A bad output from one configuration is **not** sufficient to declare the underlying model/model family incapable.

Before switching models, classify the result correctly:

- **INFRASTRUCTURE FAIL** — install/runtime/loader/OOM/path/dependency problem; fix infrastructure and rerun;
- **INTEGRATION FAIL** — wrong graph, incompatible checkpoint, preprocessing, registration, loader semantics or input contract; fix integration and rerun;
- **CONFIGURATION FAIL** — one validated configuration does not meet quality/motion/style requirements; continue controlled testing;
- **BLOCKED** — exact intended route cannot currently be reproduced because a required checkpoint/component is unavailable or hardware makes it impractical;
- **MODEL/TASK FAIL** — only after an official/reference baseline is reproduced where possible, the task input contract is validated, meaningful parameters are tested systematically with fixed seeds, and the same decisive failure persists across multiple valid configurations.

Rules:

1. Prefer one model/route at a time until its meaningful options are exhausted.
2. First reproduce an official/reference baseline in the same local integration whenever practical.
3. Then test the project task with the easiest valid matched input before adding the full Exilada complexity.
4. Change one meaningful variable at a time and keep seed/input fixed when comparing settings; controlled sweeps are diagnostics, not seed fishing.
5. Separate motion adherence, identity, topology, secondary motion and art-language failures so one class is not blamed on the wrong component.
6. Do not delete a model workspace merely because one configuration failed. Cleanup occurs only after a genuine MODEL/TASK FAIL, an explicit abandonment decision, or a BLOCKED route whose files are no longer useful.

This supersedes earlier premature model-level rejection language.

## Game / presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first canonical locomotion family is screen-left / mostly lateral-three-quarter;
- `72 deg` azimuth from travel heading remains the current facing baseline (`90 deg` = pure side), but a raw-video model may use its own viewpoint control to preserve that game-facing intent.

## Runtime animation architecture — LOCKED

The runtime plays **complete precomposed character frames**:

`complete frames -> complete-character spritesheet PNG(s) + metadata -> ordinary sprite playback`

Runtime construction of the visible character from body/hair/clothing/equipment layers is **ABOLISHED/CLOSED**.

Every exported frame must already contain the whole visible state and all baked motion, including where present:

- body locomotion;
- soft-tissue/jiggle;
- hair motion;
- base clothing/bindings motion;
- shackles/chains/restraints/accessories motion;
- final occlusion.

## Canonical Exilada initial-state master

`assets/source/characters/exilada/reference/exilada_master.png`

The master is the **complete initial-state appearance reference** for current animation work.

## Complete-character generation contract — LOCKED 2026-09-07

The final production model must use **two distinct references**:

1. `exilada_master.png` for the target character's complete appearance/state;
2. a real driving video for motion/performance.

The driving performer may come from arbitrary Internet video and does **not** need to wear matching clothing or resemble the Exilada.

The production model must go beyond a body skeleton and automatically infer convincing:

- body weight transfer and locomotion;
- soft-body/jiggle response;
- long-hair inertia/follow-through;
- cloth lag/deformation/material behavior;
- wind response where appropriate;
- chain/restraint/accessory dynamics.

**Manual animation work is outside the production contract.** No manual keyframing, rigging, cloth/hair simulation, frame repainting, per-frame cleanup, hand compositing or manual mask correction may be required. Fully automatic preprocessing is allowed.

Canonical screening/protocol:

`docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

## Moore / SSD status — RESEARCH ONLY FOR THIS FINAL CONTRACT

Runner 34 proved that complete-character spritesheet generation/packing works, and also showed that the current Moore-compatible SSD route preserves Exilada identity reasonably while following body pose to a degree.

However the current Moore/AnimateAnyone conditioning path receives body pose information rather than the full raw driving video. Under the newly locked production contract this makes it **structurally insufficient as the final complete-motion author**, because the conditioning signal discards the non-rigid motion classes we explicitly require: hair, cloth, jiggle, wind and accessory dynamics.

Therefore:

- do not call Moore/SSD a useless model;
- do not spend the next production gate on further body-pose tuning;
- retain it as appearance/pose-transfer evidence and historical research;
- exact public SSD remains separately BLOCKED by the missing custom pose-guider checkpoint.

## Wan-Animate-2 historical test — CONFIGURATION FAIL, NOT EXHAUSTED

Wan-Animate-2 is in the **correct architectural class** because it directly consumes a reference image plus the raw driving video and was specifically designed to avoid intermediate motion extractors.

The 2026-09-04 local test remains valid evidence that the tested setup was poor for the project: weak motion transfer and a painted/smoothed visual result.

But the previous global rejection was premature. A new audit found a material mismatch between that test and upstream Base defaults:

- historical project test: approximately `384×576`, `17` frames, seed `42`;
- current upstream Base config: `640×800`, `37` frames, `16 fps`, `20` steps, base seed `0`;
- upstream Base Diffusers example also uses `640×800` and 40 inference steps.

The model therefore was **not exhausted** under a controlled protocol.

The isolated Wan workspace was deleted under the earlier premature cleanup decision and must be rebuilt if/when the exhaustion run begins.

## SCAIL-2 — SELECTED FALLBACK CANDIDATE, NOT YET INSTALLED

SCAIL-2 is the strongest currently identified open/local alternative if Wan reaches a documented `EXHAUSTED_FAIL`.

Why it qualifies:

- reference image + end-to-end raw driving video;
- explicitly bypasses pose/skeleton intermediates;
- open weights/code;
- native ComfyUI integration exists;
- automatic SAM3 mask generation is compatible with the no-manual-work rule;
- official end-to-end driving supports 512p/704p;
- community GGUF Q4_K_M around 10.9 GB makes a 12 GB local proof plausible.

Do not install it yet. First exhaust Wan-Animate-2 because switching before a finite Wan exhaustion pass would repeat the workflow error the user explicitly rejected.

## External benchmarks, not current production dependencies

- **DreamActor-M2**: excellent architectural match and strong reported end-to-end RGB-driven results, but no public self-hostable weights currently available; hosted/closed access only.
- **Kling Video 3.0 Motion Control**: architecturally relevant reference-image + motion-video system, but closed/hosted and outside the current local/free/self-hosted constraint.

## CURRENT GATE — WAN-ANIMATE-2 MODEL EXHAUSTION, NO MANUAL RESCUE

Do not switch to another model before completing the finite Wan protocol documented in `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`.

Required order:

1. **W0 official baseline** — official Wan reference + official Wan driving video in our local implementation, as close to upstream Base semantics as hardware permits.
2. **W1 Exilada cross-identity** — same driver/settings; only replace the reference with `exilada_master.png`.
3. **W2 target walking video** — use a clean real Internet walking clip; no costume match required.
4. **W3 secondary-motion stress** — use a raw video with visible body bounce and non-rigid dynamics such as hair, loose cloth or wind.
5. **W4 finite high-leverage variants** — Base vs Distilled, upstream vs hardware-safe resolution/frame window, one justified quantization tier, documented viewpoint/reference controls. Fixed seed unless stochasticity is explicitly under test.

No manual alignment, manual masks, rigging, keyframes, cloth/hair animation, repainting, compositing or frame repair is permitted.

After W4 classify Wan as either:

- `PASS_CANDIDATE`, or
- `EXHAUSTED_FAIL`.

Only then move to SCAIL-2.

## Historical / closed assumptions

- runtime visible-character layer assembly — ABOLISHED/CLOSED;
- visible 3D -> final pixel art — CLOSED;
- manual hidden-3D secondary animation as production requirement — CLOSED by no-manual contract;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- body-pose-only diffusion as final complete-motion production foundation — CLOSED;
- exact-upstream SSD public recreation — BLOCKED by missing pose-guider checkpoint.

## Retention / cleanup

Retain runner-34 outputs and SSD evidence as research history. Do not clean up a currently tested raw-video model merely because one configuration fails; apply the exhaustion protocol first.
