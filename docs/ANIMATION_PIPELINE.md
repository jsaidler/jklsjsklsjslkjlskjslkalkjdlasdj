# Character Animation Production — Living Decision Record

Status: **No production animation pipeline is accepted yet. Sprite Sheet Diffusion and Wan-Animate-2 were tested and rejected. Paid/proprietary hosted generation is disqualified unless explicitly authorized. The current active experiment is a free/local four-key-pose spike using FLUX.2 Klein Base 4B FP8 + RefControl Pose on the canonical Exilada reference. Steps 1–4 have passed: hardware/runtime, required weights, canonical reference copy and four deterministic COCO-18 poses are prepared. No FLUX inference has been executed yet.**

## Process rule — living documentation

All material animation decisions, test results, constraints, accepted/rejected directions and current execution state must be recorded here as they occur. This document is canonical across chats. When a decision changes, edit this document instead of creating a parallel version or relying on conversation history.

## Hard production constraints

The animation pipeline must:

- start from the approved canonical character design/reference rather than requiring the user to redraw production art manually;
- preserve character identity, adult anatomy, hair mass, clothing state, captivity markers and equipment state;
- provide explicit, inspectable gameplay motion control;
- be reproducible through project tooling and command-line automation;
- avoid manual frame-by-frame repainting, seed fishing and hand animation as normal production steps;
- be credible on Windows 11 / RTX 3060 12 GB / 48 GB RAM;
- use source code and required weights that are freely obtainable for local/self-hosted use;
- not require subscriptions, per-generation credits or proprietary hosted inference unless explicitly approved in advance;
- use licenses compatible with intended project use.

The user will not manually animate production characters and will not hire an animation/art team.

## Canonical Exilada reference — important clarification

Canonical file:

`assets/source/characters/exilada/reference/exilada_master.png`

The reference remains the approved source of the Exilada's design identity: adult anatomy, proportions, face, long black hair mass, minimal degraded clothing, broken restraints, bare feet and weaponless base state.

**2026-09-04 clarification:** the current master is too detailed to be treated as proof of strict production pixel-art construction. It is now classified as a **high-detail canonical design/identity reference**, not as evidence that every visible pixel already satisfies the final gameplay raster language.

Therefore the current FLUX + RefControl spike must not be rejected merely because the output reproduces the same high-detail/illustrative density present in the source. For this spike, the model is judged primarily on **source fidelity and pose control**.

The separate question — how to derive the final gameplay-scale modern-pixel-art asset language from the approved design without manual art labor — remains a downstream production problem. It must be solved explicitly rather than blamed on the pose model.

Weapons are gameplay-variable equipment and are not part of permanent character identity.

## Rejected approaches

Rejected as production foundations:

- independent generic frame generation;
- one-shot generic sprite-sheet generation;
- rigid cut-out / segmented 2D puppetry from a flattened PNG;
- conventional rendered animation followed by a pixel filter;
- manual frame-by-frame repainting;
- Sprite Sheet Diffusion hybrid public-weight reconstruction;
- Wan-Animate-2 Base INT8 motion transfer;
- generic video-diffusion as the primary architecture for this problem;
- paid/proprietary hosted sprite-generation or interpolation APIs as the default production path.

### Sprite Sheet Diffusion — tested and rejected

The public-weight reconstruction ran locally on the target RTX 3060 12 GB machine. Rejection was visual/structural rather than infrastructural: identity drift, lower-body collapse, unstable hair/clothing/chains, malformed anatomy and incoherent walk mechanics.

Do not rescue SSD through seed search, CFG sweeps, new masters or manual repair. `tools/sprite-animation/` is research history only.

### Wan-Animate-2 Base INT8 — tested and rejected

The local workflow completed. It preserved coarse Exilada identity better than SSD but failed explicit motion adherence: the driver locomotion was not transferred strongly enough, while output remained mostly planted. It also changed the visual treatment substantially from the supplied source.

Do not rescue the tested Wan route with seed fishing, prompt cosmetics or post-generation filters. `tools/wan-animate2-spike/` is research history only.

## Architectural conclusion

The useful decomposition remains:

`motion / key-pose generation -> explicit skeleton / key poses -> controlled character renderer -> temporal completion / inbetweening -> automatic QA`

Motion generation, motion representation and character rendering are separate problems. A generic video model should not be asked to infer choreography, identity, visual treatment and temporal structure simultaneously.

## Pose generation vs. character re-posing — locked research distinction

**2026-09-04:** the project now explicitly distinguishes two AI tasks that must be evaluated independently.

### A. Character re-posing

Input: one canonical character reference + one explicit target skeleton.

Output: the same character rendered in that target pose.

The current FLUX.2 Klein + RefControl spike tests only this layer. Its four COCO-18 walk poses are deterministic and were generated by project tooling, not by an AI motion generator. This prevents choreography quality from contaminating the first renderer test.

### B. Motion / pose-sequence generation

Input: an action description, optional constraints/key poses and desired duration.

Output: a time sequence of body joints/poses, ideally as 3D joints or a format convertible deterministically to the project's 2D COCO-18 driving skeletons.

This layer will be evaluated only after the controlled character renderer demonstrates adequate source fidelity and pose adherence. The preferred architecture is to generate motion numerically first and rasterize OpenPose/COCO controls afterward, rather than asking an image/video generator to invent motion implicitly.

## Current pose-sequence generator research — 2026-09-04

No pose-sequence AI is approved for production yet. Current ranking for a future local spike:

### 1. MoMask — strongest practical baseline candidate

Why it is relevant:

- text-to-motion from natural-language actions;
- outputs per-frame 3D joints (`nframe × 22 × 3`) at 20 fps;
- also exports BVH;
- supports specifying motion length;
- official implementation and pretrained models are public;
- code license is MIT;
- inference is substantially lighter than image/video diffusion and is plausible on the RTX 3060 target.

Risks:

- HumanML3D motion vocabulary is generic human motion, not gameplay animation authored for combat timing;
- supplied naive foot IK is acknowledged by the project to sometimes fail;
- generated sequences still require deterministic retargeting/down-projection to the COCO-18 driver representation and game-specific timing cleanup.

**Status:** preferred first AI motion-generator spike if/when the renderer stage passes.

### 2. MotionGPT3 — newer research candidate

Why it is relevant:

- released pretrained models in late 2025;
- supports text-to-motion, motion prediction and motion inbetweening;
- outputs HumanML3D motion sequences and therefore fits the numeric-motion-first architecture;
- code repository is MIT licensed;
- official checkpoint is approximately 1.2 GB and public but gated on Hugging Face.

Risks / unresolved production issues:

- the official Hugging Face checkpoint metadata currently reports a generic `cc` license rather than a production-clear software/model license, so model-weight licensing must be resolved before production use;
- more complex runtime than MoMask;
- quality advantage for the project's short game-action key-pose use case is not yet demonstrated.

**Status:** second research candidate; do not install for production until weight license is clarified.

### 3. MotionLCM — technically attractive, licensing disqualifies current production use

Why it is technically interesting:

- very fast text-to-motion;
- explicit motion control facilities;
- per-frame 3D joint output;
- well suited conceptually to generating short motion candidates.

Blocking issue:

- the official repository explicitly states that its MotionLCM license does not allow commercial usage.

**Status:** research reference only unless licensing changes or a clearly compatible independently licensed checkpoint/runtime is established.

### 4. MotionStreamer — not production eligible

It provides modern streaming text-to-motion research and joint/rotation representations, but the official repository states academic-only usage.

**Status:** disqualified for production licensing; useful only as architectural research.

### Not pose generators

The following should not be confused with the motion-generation layer:

- **RefControl Pose:** controlled still-image character renderer from supplied skeleton + reference;
- **One-to-All Animation:** character animation/video renderer driven by pose/video; it consumes motion rather than being the preferred source of game choreography;
- **Wan-Animate-2:** video/motion-transfer renderer already rejected in this project;
- **OpenPose/DWPose-style extractors:** pose estimators/extractors, useful for converting existing footage into skeletons but not generative motion models.

## Free/open/local rule

Before installing any new candidate, verify:

1. required code and weights are freely obtainable locally;
2. no mandatory subscription, per-generation credit or proprietary hosted inference exists;
3. license is compatible with intended use;
4. explicit pose/action control exists;
5. RTX 3060 12 GB operation is credible;
6. failure criteria are defined before installation.

PixelLab, Pixel Engine and Retro Diffusion were stopped because their relevant production route depended on hosted/tiered services. `tools/pixellab-skeleton-spike/` is research history only.

## Current active spike — FLUX.2 Klein Base 4B FP8 + RefControl Pose

This is **not** a video-generation test and not a motion-generation test. It tests one narrow capability first: can one canonical Exilada reference be re-posed into four explicit walk key poses while maintaining the same character?

### Components

- base: `black-forest-labs/FLUX.2-klein-base-4B` family, Apache 2.0;
- local runtime: ComfyUI Portable NVIDIA;
- diffusion weight: `flux-2-klein-base-4b-fp8.safetensors`;
- text encoder: `qwen_3_4b.safetensors`;
- VAE: `flux2-vae.safetensors`;
- pose adapter: `xocialize/refcontrol-FLUX.2-klein-4B-pose-lora`, `refcontrol-pose-klein-4b.safetensors`, Apache 2.0;
- RefControl contract: image 1 = OpenPose-style COCO-18 target skeleton; image 2 = reference subject; prompt trigger includes `refcontrol` and the instruction to apply pose from image 1 with reference from image 2.

Current external verification:

- BFL lists FLUX.2 Klein 4B Base as Apache 2.0 and approximately 9.2 GB VRAM in its standard local configuration;
- an official FP8 single-file variant is available at approximately 4.09 GB;
- the current RefControl 4B pose LoRA is approximately 92 MB, Apache 2.0, and specifically trained for the two-input COCO-18 skeleton/reference contract;
- a 9B RefControl pose variant also exists, but the corresponding BFL 9B Base is substantially above the target VRAM and uses the FLUX non-commercial license, so the 9B route is not a production candidate for this project.

No Pixel Art LoRA is part of the current spike. Adding one now would confound whether RefControl itself preserves the supplied design.

### Fixed spike contract

- canonical `exilada_master.png` only;
- four deterministic walk poses: `contact_L`, `passing_L`, `contact_R`, `passing_R`;
- OpenPose-style COCO-18 skeletons on black;
- one fixed seed: `20260904`;
- one fixed model/adapter configuration;
- one render per pose;
- no seed fishing;
- no inpainting;
- no frame repair;
- no video generation;
- no interpolation;
- no artistic retry.

### Current execution state — 2026-09-04

Passed:

1. **Preflight:** Windows 11, 47.7 GB RAM, RTX 3060 12 GB, sufficient disk space, canonical master present.
2. **ComfyUI runtime:** Python 3.13.14, PyTorch 2.13.0+cu130, CUDA 13.0, GPU visible with 12.00 GB VRAM.
3. **Weights:** exactly the four required model files installed and hash-validated; no generation performed.
4. **Inputs:** canonical master copied byte-for-byte; four deterministic 768×1024 COCO-18 skeleton PNGs and JSON specifications generated; manifest written; no inference performed.

Current next gate:

5. **Runtime schema/workflow validation without inference.** Start ComfyUI headless on localhost, confirm the installed runtime exposes every core node required for two-reference FLUX.2 editing, confirm all four model filenames are visible to the correct loaders, save the relevant `/object_info` schema and stop the server. Only after this passes will an executable workflow be built/queued.

## Acceptance criteria for the four-key-pose spike

For this stage, evaluate the model against what the source actually contains.

Pass requires all four poses to maintain, within reasonable generative variance:

- recognizably the same Exilada;
- adult body proportions and coherent anatomy;
- long black hair as the dominant silhouette mass;
- minimal degraded clothing and broken restraint markers;
- plausible limb/foot placement matching the requested skeleton;
- clear distinction between the four requested walk phases;
- no catastrophic extra limbs, missing limbs or object/anatomy fusion;
- reproducibility under the fixed configuration.

**Do not fail this spike solely because the result is not stricter pixel art than the high-detail reference itself.** The model is expected to be coherent with its source. Final production pixel-art compliance is a separate downstream gate.

Fail this route if explicit pose control is materially weak, identity changes across poses, anatomy becomes unstable, or critical design anchors disappear unpredictably. A failure is not to be rescued with manual corrections or seed searching.

## Downstream problem if RefControl passes

If all four key poses pass, the next research task is not immediately video interpolation. First determine a scalable **production-raster translation** that turns the approved high-detail design language into actual gameplay-scale modern pixel art while preserving identity and allowing repeated animation/equipment variation without manual frame work.

After the production-resolution representation is defined, the next motion step is to test a numeric pose-sequence generator — currently MoMask is the preferred first candidate — and then select temporal completion/inbetweening only if needed.

## Other researched candidates

Not currently approved for installation:

- **One-to-All 1.3B:** explicit pose-driven animation and cartoon relevance, but official low-resource route targets a 16 GB T4 and it belongs to the renderer/video layer rather than the pose-generator layer.
- **StableAnimator:** fits VRAM but is a human-video framework in the wrong domain.
- **SteadyDancer:** 12 GB community route exists but remains continuous human-video diffusion.
- **MikuDance:** stylized-character relevance, insufficient 12 GB/pixel evidence.
- **SCAIL-2:** large Wan-family video renderer, wrong current direction.
- **See-through:** potentially useful semantic-layer decomposition research, but not an accepted animation foundation.
- **Animated Drawings:** deterministic and open, but visually/structurally incompatible with the Exilada.
- **AniGen:** fails the 12 GB hardware constraint.
- **MDIGAN / bitmap inbetweening research:** useful principles/components, not a complete single-reference production route.

## Repository tooling status

- `tools/sprite-animation/` — rejected SSD experiment; research history.
- `tools/wan-animate2-spike/` — rejected Wan experiment; research history.
- `tools/pixellab-skeleton-spike/` — stopped hosted PixelLab experiment; research history.
- `tools/flux2-refcontrol-spike/` — **active current local spike**.

Model checkpoints, dependency checkouts, generated outputs and temporary runtime files remain excluded from git unless a specific artifact is intentionally promoted as canonical project evidence.
