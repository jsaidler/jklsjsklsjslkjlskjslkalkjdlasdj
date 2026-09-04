# Character Animation Production — Living Decision Record

Status: **FLUX.2 Klein Base 4B FP8 + RefControl Pose is the strongest animation/re-posing route tested so far. The V1 four-pose one-shot inference completed successfully on the target RTX 3060 machine. Visual QA is promising but not production-ready: one foot shows reversed toe orientation, the left arm is inconsistent, body proportions drift slightly and chain/shackle topology changes between frames. The immediate next gate is a controlled V2 correction run of the same four walk phases.**

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

It defines the stable identity anchors:

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

The useful decomposition remains:

`motion/key poses -> explicit skeletons -> controlled character renderer -> gameplay-scale/native-raster translation -> temporal completion if needed -> QA`

Motion generation and character re-posing are separate problems.

### Character re-posing

Input:

- canonical character reference;
- explicit target pose skeleton.

Output:

- the same character in the requested pose.

FLUX.2 Klein + RefControl Pose currently owns this layer.

### Motion / pose-sequence generation

This remains downstream. MoMask remains the preferred first numeric text-to-motion candidate if a generated pose sequence is needed later. Do not introduce it until the re-posing and gameplay-raster representation are stable.

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

The RefControl model card explicitly requires an **OpenPose-style COCO-18** skeleton. COCO-18 contains ankle joints but no toe/heel joints. Therefore foot/toe errors cannot be corrected by adding extra foot keypoints without leaving the supported control format. The supported correction strategy is:

1. reduce ambiguity/crossing in hip-knee-ankle geometry;
2. keep gait phases clean and readable;
3. constrain foot orientation textually;
4. judge whether the renderer obeys the correction.

## V1 — four walk key poses

### Fixed V1 contract

- `pose_00_contact_L`
- `pose_01_passing_L`
- `pose_02_contact_R`
- `pose_03_passing_R`
- COCO-18 skeleton PNGs at `768 × 1024`;
- seed `20260904`;
- one generation per pose;
- no retry;
- no inpainting;
- no parameter change;
- no interpolation/video generation.

### Steps 1–5

Validated before inference:

1. target machine/runtime preflight — PASS;
2. ComfyUI Portable / CUDA runtime — PASS;
3. four required weights — PASS;
4. canonical reference and deterministic pose inputs — PASS;
5. runtime/workflow schema — sufficient to execute the production spike.

### STEP 6 — one-shot inference: PASS technically

The user executed:

`tools/flux2-refcontrol-spike/05_run_spike.ps1`

Observed run:

- isolated ComfyUI on `127.0.0.1:8199`;
- exactly four `/prompt` submissions;
- same seed for every pose;
- no fallback/retry/parameter change.

Outputs:

- `pose_00_contact_L_00001_.png` — 242.18 s — SHA256 `12c03f5ca96b8eef474c384de6b1ed8d8e6f9adbb40db691484476f4f04df5a8`
- `pose_01_passing_L_00001_.png` — 234.84 s — SHA256 `d314bb7255d883c8dbf71872a3778911ebcf1a2ddeeebacc8ac13aa3ebe0a1c0`
- `pose_02_contact_R_00001_.png` — 235.10 s — SHA256 `e0a37bc15c8e72cdbf71c890cc0fa486db3a2c8297ff1266e0f7daa53c8efa9c`
- `pose_03_passing_R_00001_.png` — 235.15 s — SHA256 `987780837414b91838924073a4508b893bd7b9022bcec6b16339020fbc58022b`

Run manifest:

`D:\AI\Flux2RefControlSpike\run\step6_run_manifest.json`

### V1 visual QA — CONDITIONAL PASS

Strong findings:

- best identity preservation of every route tested so far;
- all four images are recognizably the same Exilada;
- hair mass, face, clothing language and body type are substantially more stable than prior pipelines;
- the four requested gait phases are distinct enough to continue testing.

Blocking defects:

1. **foot anatomy:** at least one right foot has toe orientation reversed / mirrored;
2. **left arm:** anatomy/placement is inconsistent in at least part of the set;
3. **body drift:** subtle changes in torso/limb volume between frames;
4. **restraint continuity:** chains/shackles move or swap side/orientation between frames.

Decision:

**PASS as the lead upstream re-posing/reference route.**

**FAIL as a production-ready final walk cycle.**

## V2 — controlled correction gate

The V2 is deliberately a comparison experiment, not an unrestricted optimization pass.

### Unchanged from V1

- canonical `exilada_master.png`;
- FLUX.2 Klein Base 4B FP8;
- RefControl Pose LoRA;
- LoRA strength `1.0`;
- seed `20260904`;
- canvas `768 × 1024`;
- `20` steps;
- CFG `5.0`;
- Euler sampler;
- image order: skeleton first, identity reference second;
- exactly one `/prompt` submission per pose;
- no retry, fallback, inpainting or seed search.

### Controlled changes

Only these variables change:

1. **COCO-18 pose geometry**
   - remove the V1 arm-crossing geometry through the torso;
   - keep elbows/wrists visually separated from the body centerline;
   - remove the crossed-leg X geometry present in the old opposite-contact pose;
   - use clean non-crossing screen-space leg trajectories;
   - use COCO left/right joint colors to assign which anatomical leg occupies each trajectory.

2. **Prompt correction contract**
   - both feet/toes point toward screen-right;
   - no reversed/mirrored foot;
   - anatomically coherent left and right arms;
   - same body proportions/limb thickness across all frames;
   - exact restraint/chain topology from reference image 2;
   - never swap loose chains to the opposite anatomical wrist/ankle;
   - preserve scars and torn-cloth layout as closely as possible.

### New V2 pose names

- `pose_00_contact_L_v2`
- `pose_01_passing_L_v2`
- `pose_02_contact_R_v2`
- `pose_03_passing_R_v2`

### V2 tooling

`tools/flux2-refcontrol-spike/06_prepare_v2_inputs.ps1`

Creates:

- `ComfyUI\input\refcontrol_poses_v2\`
- `D:\AI\Flux2RefControlSpike\pose_specs_v2\`
- `D:\AI\Flux2RefControlSpike\input_manifest_v2.json`

No inference.

`tools/flux2-refcontrol-spike/07_run_v2.ps1`

Runs exactly four V2 one-shot generations and writes:

- outputs under `ComfyUI\output\flux2_refcontrol_v2\`;
- request/history evidence under `D:\AI\Flux2RefControlSpike\run_v2\`;
- `step7_v2_started.json` sentinel before the first possible prompt submission;
- `step7_v2_run_manifest.json` on successful completion.

The sentinel prevents accidental artistic reruns after any submission may have occurred.

## V2 acceptance criteria

Compare V1 and V2 frame-for-frame.

V2 passes the correction gate only if:

- foot orientation is anatomically correct in all four outputs;
- no catastrophic hand/arm anatomy appears;
- left-arm consistency materially improves;
- body proportions drift less than V1;
- chain/shackle topology is more stable than V1;
- Exilada identity remains at least as strong as V1;
- four gait phases remain clearly distinct.

A regression in identity is not acceptable merely to improve feet/props.

## Next gate

Run V2 exactly once, then upload/share the four V2 images and `step7_v2_run_manifest.json` for V1-vs-V2 QA.

Only after that comparison do we decide whether:

1. RefControl is reliable enough as the upstream re-posing generator;
2. another controlled V3 is justified;
3. or the route should be frozen as an upstream reference generator and the final walk solved downstream at native gameplay raster.
