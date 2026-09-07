# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
6. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
7. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`
8. `docs/ANIMATION_PIPELINE.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Do not reconstruct a candidate route from memory when a prior test exists in Git history or canonical docs.

## Model exhaustion protocol — LOCKED 2026-09-07

A bad output from one configuration is **not** sufficient to declare the underlying model/model family incapable.

Before switching models, classify the result correctly:

- **INFRASTRUCTURE FAIL** — install/runtime/loader/OOM/path/dependency problem; fix infrastructure and rerun;
- **INTEGRATION FAIL** — wrong graph, incompatible checkpoint, preprocessing, pose registration, loader semantics or input contract; fix integration and rerun;
- **CONFIGURATION FAIL** — one validated configuration does not meet quality/motion/style requirements; continue controlled testing;
- **BLOCKED** — exact intended route cannot currently be reproduced because a required checkpoint/component is unavailable or hardware makes it impractical;
- **MODEL/TASK FAIL** — only after a reference/official baseline is reproduced where possible, the task input contract is validated, meaningful parameters are tested systematically with fixed seeds, and the same decisive failure persists across multiple valid configurations.

Rules:

1. Prefer one model/route at a time until its meaningful options are exhausted.
2. First reproduce an official/reference baseline in the same local integration whenever practical.
3. Then test the project task with the easiest valid matched input before adding the full Exilada complexity.
4. Change one meaningful variable at a time and keep seed/input fixed when comparing settings; controlled sweeps are diagnostics, not seed fishing.
5. Separate body/motion adherence, identity, topology, secondary motion and art-language failures so one class is not blamed on the wrong component.
6. Do not delete a model workspace merely because one configuration failed. Cleanup occurs only after a genuine MODEL/TASK FAIL, an explicit abandonment decision, or a BLOCKED route whose files are no longer useful.

This protocol supersedes earlier project wording that prematurely promoted configuration-level failures to model-level rejection.

## Model-discard cleanup rule — LOCKED / CLARIFIED

Whenever a model or model route is **genuinely abandoned after the exhaustion protocol** and is no longer required as an active dependency, the same response must include an exact PowerShell command that removes its downloaded model-specific files.

- Preserve small result images, JSON markers and logs as evidence unless explicitly asked to remove them.
- If the model shares a runtime that is still used elsewhere, delete only that model's weights/model-specific dependency files.
- If the model has an isolated dependency workspace and nothing else depends on it, the workspace may be removed recursively.
- A single visual/configuration failure is not sufficient grounds for cleanup.

## Game / presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first canonical locomotion family is screen-left / mostly lateral-three-quarter;
- `72 deg` azimuth from travel heading is locked as the first locomotion-facing baseline (`90 deg` = pure side).

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

Offline authoring may still be modular; runtime composition may not be silently reintroduced.

## Canonical Exilada initial-state master

`assets/source/characters/exilada/reference/exilada_master.png`

The master is the **complete initial-state appearance reference** for current animation work.

## Motion state

C1A remains mechanical gait/control infrastructure using `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk` and eight contact/down/passing/up states.

- runner 31 locked `72 deg` facing;
- runner 32 V1 remained too generic;
- runner 33 V2 was not approved as final locomotion but remains usable as a provisional body-motion driver for route diagnostics.

## Runner 34 — complete-character playable proof

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Result:

- technical/export **PASS**;
- complete-character spritesheet architecture **PASS**;
- this particular Moore-compatible SSD configuration: **CONFIGURATION/INTEGRATION QUALITY FAIL**, not proof that SSD as a model family cannot do the task.

Observed output failures:

- hair mostly frozen/warped;
- cloth morphing without convincing controlled lag;
- jiggle not deliberately readable;
- wrist chain mostly static;
- ankle chain/restraint detaches/mutates;
- lower legs/feet degrade in displaced phases;
- loop/phase differentiation weak.

Important evidence against premature model rejection: runner 30 fixed a `1.7778×` pose-registration distortion in our own preprocessing and materially improved pose response/lower-limb reconstruction. Therefore integration correctness has already been proven to be a first-order variable in this branch.

## SSD status — MODEL CAPABILITY UNRESOLVED / PUBLIC EXACT ROUTE BLOCKED

Exact upstream Sprite Sheet Diffusion has **not** been reproduced locally because the public release does not include the custom SSD pose-guider checkpoint required by the exact published graph.

Our current route is a compatibility reconstruction:

`Moore AnimateAnyone graph + Moore baseline pose guider/motion module + released SSD reference/denoising UNets`

Therefore:

- do **not** say “SSD cannot do it” based on runner 34;
- do say “the current public-weight Moore-compatible reconstruction is not yet good enough in its tested configuration”;
- exact published SSD remains **BLOCKED**, not visually disproven;
- before switching models, exhaust the diagnostically meaningful Moore/SSD compatibility options that do not depend on the missing checkpoint.

## Wan-Animate-2 historical test — CONFIGURATION FAILED; MODEL FAMILY NOT EXHAUSTIVELY DISPROVEN

A real local Wan-Animate-2 Base INT8 ConvRot test was performed on 2026-09-04. The tested configuration produced recognizable Exilada identity but weak locomotor transfer and a smooth painted/video-diffusion appearance.

That result remains valid evidence against **that configuration**. It is no longer classified as proof that the entire Wan-Animate-2 model family is incapable of the task.

Reasons the earlier verdict was too strong:

- the project test was deliberately tiny (`17` frames, `384×576`) rather than the upstream reference regime;
- we did not first establish a documented successful official/reference motion-transfer baseline in the exact local runtime and then move to Exilada;
- we did not systematically isolate motion/reference conditioning strength and input-compatibility effects before closing the model;
- project history itself warned that a strongly mismatched first pose in the official-demo driver would make an artistic failure non-diagnostic.

The isolated Wan workspace was nevertheless deleted under the earlier premature cleanup decision. Do not assume `D:\AI\WanAnimate2` exists. Rebuilding it is **not the current next step** because the SSD/Moore workspace is still present and should be exhausted first.

## Erroneous 2026-09-07 runner-35 proposal — WITHDRAWN

The previously-created Wan runner 35 remains withdrawn and deleted. Its mistake was not merely that Wan had been tested before; it also attempted another model switch before the current Moore/SSD branch had been properly exhausted.

No runner 35 is active.

## CURRENT GATE — MOORE/SSD EXHAUSTION AUDIT BEFORE ANY MODEL SWITCH

Do not install or download another large animation model yet.

The next work is an **integration/exhaustion audit** of the retained Moore/SSD environment. It should answer, in order:

1. Can the pure Moore baseline reproduce its expected/reference behavior with our exact reference/pose preprocessing?
2. With identical inputs/settings, what changes when only the released SSD reference/denoising UNets replace the Moore baseline weights?
3. Are our pose images exactly in the domain/registration expected by the actual Moore pipeline rather than merely visually plausible skeleton maps?
4. Is the Moore baseline pose guider the dominant bottleneck when paired with SSD-finetuned UNets?
5. Which failures are intrinsic to body-only pose conditioning and which are artifacts of our compatibility reconstruction?
6. If the fallback reaches a repeatable ceiling, is recovering/retraining a compatible SSD pose guider practical enough to justify before declaring the public SSD recreation BLOCKED for production?

Only after this audit may the project choose between continuing SSD reconstruction, rebuilding Wan for a properly controlled exhaustion pass, or selecting another model family.

## Historical / closed assumptions

- runtime visible-character layer assembly — ABOLISHED/CLOSED;
- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- exact-upstream SSD runner 28 — BLOCKED by missing public pose-guider checkpoint.

Wan-Animate-2 is **not currently active**, but is no longer globally classified as model-level CLOSED; its old tested configuration remains failed evidence.

## Retention / cleanup

Retain runner-34 outputs, the SSD environment/models, motion evidence and diagnostics until the Moore/SSD exhaustion audit is explicitly complete.
