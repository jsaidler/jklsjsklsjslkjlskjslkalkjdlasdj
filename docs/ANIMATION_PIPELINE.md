# Character Animation Production — Living Decision Record

Status: **FLUX.2 Klein Base 4B FP8 + RefControl Pose remains the strongest character re-posing route tested so far. V1 completed with strong identity retention but visible anatomy/continuity defects. V2 deterministic skeletons passed visual QA. The first V2 runner attempt hit a Windows PowerShell JSON-depth bug; the runner has been fixed to preserve any already-generated output and safely continue only with remaining poses.**

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

RefControl expects an **OpenPose-style COCO-18** skeleton. COCO-18 has ankle joints but no toe/heel joints. Therefore foot/toe errors are attacked by cleaner hip-knee-ankle geometry plus textual orientation constraints, not by unsupported extra foot joints.

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

### STEP 6 — one-shot inference: PASS technically

Observed outputs:

- `pose_00_contact_L_00001_.png` — 242.18 s — SHA256 `12c03f5ca96b8eef474c384de6b1ed8d8e6f9adbb40db691484476f4f04df5a8`
- `pose_01_passing_L_00001_.png` — 234.84 s — SHA256 `d314bb7255d883c8dbf71872a3778911ebcf1a2ddeeebacc8ac13aa3ebe0a1c0`
- `pose_02_contact_R_00001_.png` — 235.10 s — SHA256 `e0a37bc15c8e72cdbf71c890cc0fa486db3a2c8297ff1266e0f7daa53c8efa9c`
- `pose_03_passing_R_00001_.png` — 235.15 s — SHA256 `987780837414b91838924073a4508b893bd7b9022bcec6b16339020fbc58022b`

V1 visual verdict: **CONDITIONAL PASS / not production-ready**.

Strong findings:

- best identity preservation of every route tested so far;
- all four images recognizably the same Exilada;
- gait phases distinct enough to continue testing.

Blocking defects:

1. right-foot / toe orientation error;
2. left-arm inconsistency;
3. subtle body-proportion drift;
4. chain/shackle topology drift.

Decision:

**PASS as lead upstream re-posing/reference route.**

**FAIL as final production-ready walk cycle.**

## V2 — controlled correction gate

V2 is a controlled comparison, not unrestricted optimization.

### Unchanged from V1

- canonical `exilada_master.png`;
- FLUX.2 Klein Base 4B FP8;
- RefControl Pose LoRA strength `1.0`;
- seed `20260904`;
- canvas `768 × 1024`;
- `20` steps;
- CFG `5.0`;
- Euler sampler;
- image order: skeleton first, identity second;
- one artistic generation per pose;
- no retry/fallback/inpainting/seed search.

### Controlled changes

1. **COCO-18 geometry**
   - arms no longer cross through torso centerline;
   - elbows/wrists separated from body center;
   - crossed-leg X removed;
   - cleaner non-crossing screen-space leg trajectories;
   - larger knee/ankle separation.

2. **Prompt correction contract**
   - anatomically correct feet/toes toward screen-right;
   - coherent left/right arms;
   - stable body dimensions/limb thickness;
   - exact restraint/chain topology from image 2;
   - preserve scars/torn-cloth layout as closely as possible.

### STEP 7A — V2 pose preparation: PASS

The user generated and visually reviewed the V2 skeletons in the SSD workspace.

Hashes:

- `pose_00_contact_L_v2` — `5867506c9c7e16116fd2eb5e40f60dc0ba9b528d4ecedc4e2d53372e33fd5755`
- `pose_01_passing_L_v2` — `cb8e2ea801e4002e1b8b0ca8d6286e94ee3ba760f689aa1ae15e235c9d960518`
- `pose_02_contact_R_v2` — `31497ed42506faf9d12ad9978fdc6769640250369d6b60d69c4ec36501a82f87`
- `pose_03_passing_R_v2` — `1ecf40680f6baba73f5924f327795b7c85ce45edb53a8419d29a97b7f6ac4e24`

Visual skeleton verdict: **PASS to inference**.

## STEP 7B — first V2 runner attempt: TOOLING FAIL

Observed error:

`ConvertTo-Json : A profundidade máxima permitida de serialização é 100.`

Root cause:

- initial runner used `ConvertTo-Json` depths `100` / `120`;
- Windows PowerShell hard-limits serialization depth to 100;
- critically, the `history` save used depth `120`, so the failure could occur **after a pose had already completed and written a PNG**.

Therefore this incident is not automatically classified as pre-submission.

### Corrected runner behavior

Current runner:

`tools/flux2-refcontrol-spike/07_run_v2.ps1`

Fix commits:

- `08eaab0d2541bc656515a04dc393ed60881be422`
- `74c05a39b5f2048d837adc7ad1922e4e144e61f3`

Correction rules:

- JSON depth capped at safe `32/64`;
- request fully serializes before any `POST /prompt`;
- future accepted prompts write explicit `*_accepted.json` with `prompt_id`;
- recovery scans the V2 output directory before any submission;
- existing outputs must be a unique contiguous prefix of the four intended poses;
- any existing completed output is preserved and **never resubmitted**;
- only remaining poses are submitted;
- submission/history evidence without a corresponding PNG is treated as ambiguous and stops recovery;
- unexpected/duplicate/non-contiguous outputs also stop recovery.

This preserves the one-shot artistic contract even if the old runner failed during bookkeeping after an already-completed first image.

## Workspace relocation — LOCKED

Current canonical FLUX workspace:

`Z:\AI\Flux2RefControlSpike`

Old path:

`D:\AI\Flux2RefControlSpike` — superseded after moving the workspace to SSD.

Repository remains:

`D:\GOOGLE DRIVE\DEV\Roguelite`

The active V2 runner defaults to `Z:\AI\Flux2RefControlSpike`. Historical scripts with legacy defaults must receive `-Workspace "Z:\AI\Flux2RefControlSpike"` explicitly if reused.

## V2 acceptance criteria

Compare V1 and V2 frame-for-frame.

V2 passes only if:

- foot orientation is anatomically correct in all four outputs;
- no catastrophic hand/arm anatomy appears;
- left-arm consistency materially improves;
- body proportions drift less than V1;
- chain/shackle topology is more stable than V1;
- Exilada identity remains at least as strong as V1;
- four gait phases remain distinct.

A regression in identity is not acceptable merely to improve feet/props.

## Exact next gate

Pull the corrected runner and resume the interrupted V2 sequence with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\flux2-refcontrol-spike\07_run_v2.ps1" -Workspace "Z:\AI\Flux2RefControlSpike" -RecoverSerializationFailure
```

The runner must report any existing V2 PNG it is preserving before it submits a remaining pose.

After four V2 outputs exist, upload/share them plus `Z:\AI\Flux2RefControlSpike\run_v2\step7_v2_run_manifest.json` for V1-vs-V2 QA.

Only after that comparison do we decide whether:

1. RefControl is reliable enough as the upstream re-posing generator;
2. another controlled V3 is justified;
3. or the route should be frozen as an upstream reference generator and the final walk solved downstream at native gameplay raster.
