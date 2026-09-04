# Character Animation Production — Living Decision Record

Status: **FLUX.2 Klein Base 4B FP8 + RefControl Pose remains the strongest character re-posing route tested so far. V1 preserved identity strongly but had anatomy/continuity defects. V2 improved feet, arms and body consistency, but failed as a walk because left/right phase pairs collapsed into nearly repeated poses. The immediate gate is V3 pose-control preparation with genuinely different screen-space geometry and an automatic color-independent silhouette-uniqueness check.**

This document is canonical across chats. Update it after every material animation test, PASS/FAIL decision or pipeline change.

## Hard production constraints

The animation pipeline must:

- start from the approved Exilada identity reference;
- preserve adult anatomy, face, long black hair mass, clothing state, scars/restraints and equipment state;
- provide explicit inspectable pose/motion control;
- run reproducibly on Windows 11 / RTX 3060 12 GB / ~48 GB RAM;
- avoid routine manual frame-by-frame repainting, seed fishing and artistic retry loops;
- use free/local/self-hosted code and weights unless explicitly approved otherwise;
- scale to many characters, equipment states and actions.

## Canonical Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

This is the **high-detail identity/design master**, not the final gameplay pixel sprite.

Stable identity anchors:

- adult woman;
- lean functional anatomy;
- severe face;
- very long heavy black hair;
- minimal degraded beige cloth;
- wounds/scars;
- wrist and ankle restraints / broken chains;
- barefoot base state;
- no permanent weapon.

## Architecture

`motion/key poses -> explicit skeletons -> controlled character renderer -> gameplay-scale/native-raster translation -> temporal completion if needed -> QA`

Motion generation and character re-posing are separate problems.

FLUX.2 Klein + RefControl Pose currently owns the **character re-posing** layer. MoMask remains a possible later numeric motion/pose-sequence generator only after the renderer and gameplay-raster representation are stable.

## Rejected routes

Do not revive casually:

- Sprite Sheet Diffusion — tested locally; identity/anatomy/motion coherence failed;
- Wan-Animate-2 Base INT8 — tested locally; motion adherence failed;
- generic video diffusion as primary animation architecture;
- manual frame-by-frame repainting;
- paid hosted sprite/interpolation APIs as the default production path;
- one-shot generic sprite-sheet generation.

## RefControl contract

Current local route:

- base: FLUX.2 Klein Base 4B FP8;
- LoRA: `refcontrol-pose-klein-4b.safetensors`;
- text encoder: `qwen_3_4b.safetensors`;
- VAE: `flux2-vae.safetensors`;
- image 1: target OpenPose-style skeleton;
- image 2: Exilada identity reference;
- trigger: `refcontrol`;
- fixed seed: `20260904`.

RefControl expects an **OpenPose-style COCO-18** skeleton. COCO-18 has ankle joints but no toe/heel joints. Therefore foot/toe errors are attacked by cleaner hip-knee-ankle geometry plus textual orientation constraints, not unsupported extra foot joints.

## V1 — four walk key poses

Fixed V1 contract:

- `pose_00_contact_L`
- `pose_01_passing_L`
- `pose_02_contact_R`
- `pose_03_passing_R`
- `768 × 1024` COCO-18 controls;
- seed `20260904`;
- one generation per pose;
- no retry/inpainting/seed search/interpolation.

### V1 result

Runtime: **PASS**.

Visual verdict: **CONDITIONAL PASS / not production-ready**.

Strengths:

- best identity preservation of every route tested so far;
- all four images recognizably the same Exilada;
- gait phases visibly distinct.

Blocking defects:

1. right-foot / toe orientation error;
2. left-arm inconsistency;
3. subtle body-proportion drift;
4. chain/shackle topology drift.

Decision:

**PASS as lead upstream re-posing/reference route.**

**FAIL as final production-ready walk cycle.**

## V2 — anatomy correction experiment

V2 was a controlled comparison, not unrestricted optimization.

Unchanged:

- canonical `exilada_master.png`;
- FLUX.2 Klein Base 4B FP8;
- RefControl Pose LoRA strength `1.0`;
- seed `20260904`;
- canvas `768 × 1024`;
- `20` steps;
- CFG `5.0`;
- Euler;
- one artistic generation per pose;
- no retry/fallback/inpainting/seed search.

Changed:

- cleaner limb separation;
- no arm crossing through torso centerline;
- no crossed-leg X in the control set;
- stricter anatomy/feet/continuity prompt.

### STEP 7A — V2 controls: PASS to inference

The deterministic V2 controls were generated successfully in the SSD workspace.

### V2 visual result — FAIL as walk cycle

The V2 outputs materially improved:

- foot anatomy;
- arm anatomy;
- body stability;
- overall Exilada identity retention remained strong.

However the core motion result regressed:

- `pose_00_contact_L_v2` ≈ `pose_02_contact_R_v2`;
- `pose_01_passing_L_v2` ≈ `pose_03_passing_R_v2`.

The four requested phases therefore collapsed into effectively two repeated pose geometries.

### V2 root cause — LOCKED

The left/right pairs used nearly identical **screen-space geometry** and differed mainly through COCO anatomical side colors/labels.

Observed model behavior:

**RefControl followed the visible skeleton geometry more strongly than the intended semantic left/right reassignment.**

Therefore future gait controls must not depend on COCO colors alone to distinguish opposite phases.

Secondary unresolved defect:

- chain/shackle topology remains inconsistent between generated frames.

V2 verdict:

**FAIL as a usable walk cycle.**

**Do not expand V2 to eight frames.**

## V3 — structural left/right phase correction

V3 exists solely to correct the V2 phase-collapse failure while preserving the useful anatomy gains.

### V3 control names

- `pose_00_contact_L_v3`
- `pose_01_passing_L_v3`
- `pose_02_contact_R_v3`
- `pose_03_passing_R_v3`

### V3 geometry rules

- each phase has genuinely different screen-space limb geometry;
- `contact_L` and `contact_R` differ in stride extent, support/trailing geometry and arm opposition;
- `passing_L` and `passing_R` differ in support-leg and swing-leg geometry, not merely color labels;
- no leg-crossing X shapes;
- support vs swing leg must be readable in silhouette;
- arms change geometry with the opposite gait phase;
- slight 3/4 side-facing-right asymmetry is retained.

### New hard QA rule — silhouette uniqueness

The four V3 controls must remain distinct **with all COCO colors removed**.

Tooling:

`tools/flux2-refcontrol-spike/08_prepare_v3_inputs.ps1`

The script renders a binary white-on-black skeleton internally for each pose and records a silhouette SHA256. STEP 8A fails unless all four hashes are unique.

This automatic gate directly prevents the V2 mistake from recurring.

### STEP 8A contract

STEP 8A performs no model loading and no inference.

It writes:

- `Z:\AI\Flux2RefControlSpike\ComfyUI_windows_portable\ComfyUI\input\refcontrol_poses_v3\`
- `Z:\AI\Flux2RefControlSpike\pose_specs_v3\`
- `Z:\AI\Flux2RefControlSpike\input_manifest_v3.json`

After STEP 8A, stop and visually inspect/share the four skeleton PNGs before any V3 inference runner is created or executed.

## Workspace relocation — LOCKED

Current canonical FLUX workspace:

`Z:\AI\Flux2RefControlSpike`

Old path:

`D:\AI\Flux2RefControlSpike` — superseded.

Repository remains:

`D:\GOOGLE DRIVE\DEV\Roguelite`

## Exact next gate

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\flux2-refcontrol-spike\08_prepare_v3_inputs.ps1" -Workspace "Z:\AI\Flux2RefControlSpike"
```

Then share the four V3 skeleton PNGs.

**Do not run another FLUX inference yet.**
