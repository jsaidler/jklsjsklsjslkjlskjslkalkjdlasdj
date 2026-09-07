# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`

## Runtime lock

- final runtime = ordinary playback of **complete-character spritesheets**;
- no runtime body/hair/clothing/equipment layer assembly;
- every frame already contains body, hair, clothing, restraints/accessories and all secondary motion/occlusion.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

This is the complete initial-state appearance reference.

## New complete-character model contract — LOCKED

Production animation must use **two distinct references**:

1. Exilada master for appearance;
2. a real driving video for movement/performance.

The driving video may be found on the Internet. The performer does **not** need to wear matching clothes or resemble the Exilada.

The final production model must consume richer motion information than a body skeleton and automatically infer:

- locomotion/weight transfer;
- body jiggle/soft response;
- long-hair inertia/follow-through;
- cloth deformation/lag/material behavior;
- wind response where appropriate;
- chains/restraints/accessories motion.

No manual production work is allowed: no manual rigging, keyframing, cloth/hair simulation, frame repainting, per-frame cleanup, hand compositing or manual mask correction. Automatic preprocessing is allowed.

## Runner 34 result

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 remains:

- complete-character export/packing **PASS**;
- current Moore+SSD visible result **not good enough**.

The Moore/AnimateAnyone route is now research-only for the final production contract because it receives body pose rather than raw driving-video dynamics. It cannot be the primary final authoring foundation when the required signal includes hair, cloth, jiggle, wind and accessory dynamics.

Exact public SSD reconstruction remains independently BLOCKED by the missing custom SSD pose-guider checkpoint.

## Model exhaustion rule

Do not switch models after one ugly output.

Before declaring a model dead:

1. reproduce an official/reference baseline where practical;
2. validate the exact local integration;
3. change one meaningful variable at a time;
4. keep seed/input fixed for comparisons;
5. separate infrastructure/integration/configuration failures from model/task failures;
6. never use manual cleanup to rescue a route;
7. only classify `EXHAUSTED_FAIL` after a finite documented test matrix.

## Candidate ranking

### 1 — Wan-Animate-2 — EXHAUST FIRST

Wan-Animate-2 is in the correct class: reference image + **raw driving video**, no intermediate body-skeleton requirement.

The 2026-09-04 test is now classified as **configuration failure evidence**, not model-family exhaustion.

Important audit finding:

- old project run: about `384×576`, `17` frames, seed `42`;
- upstream Base config: `640×800`, `37` frames, `16 fps`, `20` steps, base seed `0`.

Therefore the old test materially differed from upstream defaults and was done through a constrained 12 GB route.

The old isolated Wan workspace was deleted; rebuilding it is required for the new exhaustion pass.

### 2 — SCAIL-2 — NEXT OPEN/LOCAL CANDIDATE

Only after Wan reaches `EXHAUSTED_FAIL`.

Why it is relevant:

- reference image + end-to-end raw driving video;
- explicitly bypasses skeleton intermediates;
- open model/code;
- native ComfyUI support;
- automatic SAM3 masks compatible with no-manual rule;
- official 512p/704p end-to-end driving;
- community Q4_K_M GGUF ≈10.9 GB makes a 12 GB proof plausible.

Do not install SCAIL-2 yet.

### External benchmarks

- DreamActor-M2: excellent end-to-end RGB architecture/benchmark, but no public self-hostable weights currently available.
- Kling Video 3.0 Motion Control: relevant closed hosted comparator, not current local production dependency.

## CURRENT GATE — Wan-Animate-2 exhaustion protocol

Canonical details:

`docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

Order:

### W0 — official baseline

Official Wan reference + official Wan driving video through our local implementation, as close as hardware permits to upstream Base semantics.

Target reference semantics:

- `640×800`;
- `37` frames;
- `16 fps`;
- Base model;
- upstream-compatible steps/settings;
- seed/base seed `0`;
- no post-generation pixel filter.

### W1 — Exilada cross-identity

Same known-good driver/settings. Change only the appearance reference to `exilada_master.png`.

### W2 — target walking driver

Use a clean real full-body Internet walking clip. No costume match required.

### W3 — secondary-motion stress

Use a real clip with visible soft-body response and non-rigid dynamics such as hair, loose cloth or wind.

### W4 — finite high-leverage variants

Only documented hypothesis-driven variants:

- Base vs Distilled;
- upstream vs hardware-safe resolution/frame window;
- one justified higher-quality quantization if feasible;
- documented viewpoint control;
- prompt/caption correction only when tied to a known condition.

No seed fishing. No manual rescue.

After W4: `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Exact next action

Do **not** run the withdrawn old runner 35 and do **not** install SCAIL-2 yet.

First pull this canonical correction:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only
```

The next implementation task is to prepare the Wan-Animate-2 exhaustion preflight/rebuild and W0 official-baseline runner, enumerating model files, disk footprint and hardware deviations **before downloading anything**.
