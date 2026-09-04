# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/PIXEL_ART_PRODUCTION.md`
6. `docs/ANIMATION_PIPELINE.md`
7. current tooling under `tools/`

After every material step: update thematic docs + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity

The game is a **systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a living world**.

Immediate gameplay baseline is an **elevated 2D belt-scroller / false 3D** rather than rigid isometric/top-down 360° presentation.

Character-art/animation feasibility is the current priority because it is the largest production risk; code capability is not the current unknown.

## Exilada visual state

Canonical identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It is a high-detail identity/design reference, not the final gameplay sprite.

Final visible art remains true modern pixel art. Simple high-resolution generation followed by resize/quantization is not an accepted final-sprite route.

Old provisional production values such as ~64 px visible height / `96×96` idle canvas / eight mandatory directions are superseded after the belt-scroller decision.

## Current animation checkpoint

### FLUX.2 Klein + RefControl Pose V1

This is the strongest route tested so far.

STEP 6 executed successfully:

- four one-shot generations;
- fixed seed `20260904`;
- `768×1024`;
- no retry, fallback, inpainting, interpolation or seed fishing.

Runtime result: **PASS**.

Visual result: **CONDITIONAL PASS / not production-ready**.

Blocking defects:

1. right-foot/toe orientation error in at least one frame;
2. left-arm inconsistency;
3. small inter-frame body-proportion drift;
4. chain/shackle side/topology drift.

Decision:

**Keep RefControl as the lead upstream re-posing route and run one controlled correction round.**

## V2 correction run

### STEP 7A — V2 inputs: PASS

The user executed `06_prepare_v2_inputs.ps1` against the relocated workspace and generated four deterministic V2 COCO-18 controls:

- `pose_00_contact_L_v2` — SHA256 `5867506c9c7e16116fd2eb5e40f60dc0ba9b528d4ecedc4e2d53372e33fd5755`
- `pose_01_passing_L_v2` — SHA256 `cb8e2ea801e4002e1b8b0ca8d6286e94ee3ba760f689aa1ae15e235c9d960518`
- `pose_02_contact_R_v2` — SHA256 `31497ed42506faf9d12ad9978fdc6769640250369d6b60d69c4ec36501a82f87`
- `pose_03_passing_R_v2` — SHA256 `1ecf40680f6baba73f5924f327795b7c85ce45edb53a8419d29a97b7f6ac4e24`

Visual skeleton QA: **PASS to inference**.

Observed improvements in controls:

- arms no longer cross through torso centerline;
- crossed-leg X ambiguity removed;
- larger leg/ankle screen-space separation;
- four gait phases remain clearly distinguishable.

### STEP 7B — first execution attempt: TOOLING FAIL, artistic status preserved

The initial `07_run_v2.ps1` execution stopped with:

`ConvertTo-Json : A profundidade máxima permitida de serialização é 100.`

Root cause:

- the runner used JSON serialization depths `100` and `120`;
- Windows PowerShell enforces a maximum serialization depth of 100;
- the `history` save at depth `120` could fail after an artistic prompt had already completed.

Therefore the incident must **not** be treated automatically as a pre-submission failure.

Corrected runner:

`tools/flux2-refcontrol-spike/07_run_v2.ps1`

Fix commits:

- `08eaab0d2541bc656515a04dc393ed60881be422` — safe JSON depth and recovery guard;
- `74c05a39b5f2048d837adc7ad1922e4e144e61f3` — safe resume that preserves any already-generated contiguous V2 output and submits only remaining poses.

New recovery behavior:

- JSON serialization is capped at safe depth `32/64`;
- request JSON is fully serialized before `POST /prompt`;
- accepted prompts now get explicit `*_accepted.json` evidence with `prompt_id`;
- if the old failed run produced no V2 PNG, recovery treats it as pre-submission;
- if it produced `pose_00` (or another contiguous prefix), those images are preserved and never resubmitted;
- evidence for a pose without a corresponding PNG is treated as ambiguous and recovery stops;
- unexpected, duplicate or non-contiguous outputs cause FAIL rather than an artistic retry.

## V2 fixed comparison contract

Unchanged from V1:

- Exilada reference;
- FLUX.2 Klein Base 4B FP8;
- RefControl Pose LoRA strength 1.0;
- seed `20260904`;
- `768×1024`;
- 20 steps;
- CFG 5.0;
- Euler;
- one artistic generation per pose.

Changed variables only:

1. cleaner COCO-18 skeleton geometry;
2. stricter prompt for feet/toes, left/right arms, fixed body dimensions and exact restraint topology.

RefControl expects COCO-18; toe/heel joints cannot simply be added. Foot correction is being tested through less ambiguous hip/knee/ankle geometry plus text constraints.

## Workspace relocation — LOCKED

The FLUX/RefControl workspace was moved to an SSD.

Current canonical workspace:

`Z:\AI\Flux2RefControlSpike`

Old workspace:

`D:\AI\Flux2RefControlSpike` — **superseded**.

Repository remains:

`D:\GOOGLE DRIVE\DEV\Roguelite`

Active V2 runner now defaults to `Z:\AI\Flux2RefControlSpike`. Older historical scripts may still contain the legacy default; when they are ever reused, pass `-Workspace "Z:\AI\Flux2RefControlSpike"` explicitly unless their defaults have also been migrated.

## Exact next gate

Resume STEP 7B with the corrected runner in recovery mode:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\flux2-refcontrol-spike\07_run_v2.ps1" -Workspace "Z:\AI\Flux2RefControlSpike" -RecoverSerializationFailure
```

The runner must first inspect the existing V2 evidence and report what it is preserving before any new `/prompt` submission.

After four V2 images exist, compare V1 vs V2 on:

- foot correctness;
- left-arm correctness;
- body-proportion stability;
- chain/shackle continuity;
- Exilada identity retention;
- gait-phase readability.

Do not proceed to eight frames, inbetweening or final gameplay sprite authoring before this comparison.

## Gameplay-scale / Production Pixel Master gate — queued after V2

After the upstream re-poser is judged, test accepted motion/reference frames in an elevated belt-scroller gameplay composition to establish:

- real Exilada on-screen height;
- native gameplay raster suitability (provisional `640×360`);
- safe action bounds;
- Production Pixel Master dimensions;
- required facing families.

High-resolution RefControl outputs are motion/identity references; they are not automatically final pixel sprites.

## Rejected/stopped routes

- Sprite Sheet Diffusion — rejected;
- Wan-Animate-2 — rejected;
- paid hosted PixelLab/Pixel Engine/Retro Diffusion routes — stopped/disqualified;
- generic video diffusion as primary animation architecture — rejected;
- direct high-resolution generation as final pixel master — rejected;
- primitive Python/Pillow geometry as final artistic authoring — rejected.

## Target machine

- Windows 11;
- RTX 3060 12 GB;
- ~48 GB RAM;
- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`;
- workspace: `Z:\AI\Flux2RefControlSpike`.
