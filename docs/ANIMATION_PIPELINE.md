# Character Animation Production — Living Decision Record

Status: **Sprite Sheet Diffusion hybrid officially rejected; no production animation pipeline accepted; Wan-Animate-2 selected only as the next controlled validation candidate.**

## Production constraint

The user will not manually animate production characters and will not hire an animation/art team. A valid character-animation pipeline must therefore be reproducible by project tooling and scale beyond a single hand-corrected demo.

The visible game style is **modern pixel art**. Animation output must preserve that language natively rather than looking like conventional painted/video AI output with a pixel filter applied afterward.

Manual frame-by-frame repainting to repair identity, anatomy, clothing or timing is outside the accepted production workflow.

## Canonical character reference

Each production character has one approved master reference that anchors identity. For the Exilada, the current master is a full-body, weaponless, modern-pixel-art image with adult anatomy, long heavy black hair, minimal deteriorated clothing and captivity markers.

Recommended repository-side source layout:

`assets/source/characters/exilada/reference/exilada_master.png`

Weapons are gameplay-variable equipment, not part of the Exilada's permanent identity.

## Rejected approaches

The following approaches are rejected as production foundations:

- generating independent frames with a general-purpose image generator;
- asking a general image generator for a complete sprite sheet in one generation;
- cutting a flattened PNG into rigid body parts and rotating them as a 2D puppet;
- accepting conventional rendered/painted animation and applying a pixel filter afterward;
- relying on manual frame-by-frame repainting;
- **Sprite Sheet Diffusion hybrid public-weight reconstruction**.

## Sprite Sheet Diffusion hybrid — OFFICIALLY REJECTED

### Why it was tested

Sprite Sheet Diffusion (SSD) was specifically designed for game-character animation from a reference image plus driving poses. The public release is incomplete because the trained custom multi-scale pose guider used by the paper was not released. The reproducible local experiment therefore used:

- SSD finetuned `denoising_unet.pth`;
- SSD finetuned `reference_unet.pth`;
- baseline AnimateAnyone `pose_guider.pth`;
- baseline AnimateAnyone `motion_module.pth`;
- CLIP vision image encoder;
- SD VAE.

This was a hybrid reconstruction, not the exact unreleased paper checkpoint set.

### Hardware and execution result

The hybrid pipeline was successfully compiled and executed locally on:

- Windows 11;
- RTX 3060 12 GB;
- 48 GB RAM.

Both smoke and quality walk generations completed and produced animated output, sprite sheets and metadata. Therefore the rejection is not an installation or execution failure.

### Visual rejection evidence — Exilada walk, 2026-09-04

The generated walk failed the production gate by a large margin:

- character identity was not preserved;
- face changed materially between frames;
- legs, feet and lower-body anatomy collapsed or changed shape;
- hair became an unstable dark mass that swallowed body structure;
- clothing, chains and persistent details drifted;
- several frames contained malformed or residual anatomy/objects;
- the sequence did not read as a biomechanically coherent walk cycle;
- the quality profile increased resolution but did not solve the structural failures;
- output quality was dramatically below the approved master reference.

The pipeline is **not to be rescued** with a new master, seed search, CFG tuning, additional steps or cosmetic cleanup. It is rejected as a production foundation.

The tooling under `tools/sprite-animation/` remains as experimental/research history and must not be treated as the current production path.

## 2026-09-04 alternative-pipeline research

The next search is constrained by the exact failure mode observed above. A candidate must address identity and detail preservation under motion, not merely execute video generation.

### Wan-Animate-2 — NEXT VALIDATION CANDIDATE, NOT ACCEPTED

Wan-Animate-2 (August 2026) is currently the strongest next experiment because its architecture directly targets a failure class relevant to the SSD result: it consumes the raw driving video inside a redesigned dual-branch Diffusion Transformer rather than depending on an intermediate skeleton/motion extractor. Its paper explicitly identifies extraction errors and cross-identity drift as shortcomings of explicit-pose pipelines. Training/evaluation includes diverse characters, including humans, anthropomorphic cartoon animals, robots and animals.

For the RTX 3060 12 GB target, the official BF16 implementation is not viable as-is: official defaults target multi-A800 configurations. A community GGUF path exists for 8–12 GB GPUs, with Q4_K_M around 9.8 GB and ComfyUI chunking guidance of 33 frames for 12 GB. This makes a controlled local spike plausible, not proven on this exact machine.

Critical caveats before any production acceptance:

- it is a general character-video model, not a sprite-native model;
- authentic modern-pixel-art preservation is unproven;
- it uses a driving video rather than the project's deterministic BODY_18 pose sequence;
- cycle seam quality is not guaranteed;
- the reference should roughly match the opening pose of the driver;
- GGUF must be loaded with an Animate-2-aware custom loader; a stock GGUF loader can silently load it as ordinary Wan I2V and ignore the driving video.

Therefore Wan-Animate-2 is approved only for a **small identity/motion/style validation spike using the existing Exilada master**. It is not a production pipeline until it passes the same visual gate that SSD failed.

### One-to-All Animation — high relevance, hardware not yet proven

One-to-All Animation (CVPR 2026) is highly relevant because it introduces identity-robust pose control that decouples appearance from skeletal structure, supports direct/retargeted pose input, includes self-collected cartoon data and has a 1.3B model. However, the authors' documented low-resource example uses a 16 GB T4, and a ComfyUI-WanVideoWrapper report documented broken memory optimization/OOM behavior for the 1.3B integration. No sufficiently strong current RTX 3060 12 GB proof has been found. It remains a research candidate, not the next local install.

### SteadyDancer — viable 12 GB fallback, weaker style fit

SteadyDancer explicitly targets first-frame/identity preservation and spatio-temporal misalignment. A community ComfyUI implementation reports testing on 12 GB VRAM with CPU offload. It remains a viable fallback. Its main weakness for this project is domain fit: it is built around human-image animation and pose preprocessing rather than native stylized/pixel-art production.

### SCAIL-2 — not preferred for the Exilada

SCAIL-2 has genuine 8–12 GB GGUF workflows and direct driving-video conditioning, but current public evidence includes an open issue where identity becomes unrecognizable after roughly two seconds even in FP16 on an RTX 5090, plus documented instability with loose clothing. Those are too close to the Exilada's actual risk factors to make it the next candidate.

### MikuDance — stylized-character fit, insufficient hardware evidence

MikuDance was designed specifically for stylized character art and addresses reference/motion misalignment, but it is an older explicit-pose/scene-motion architecture based on SD1.5-era components. Its released weights total roughly 6.2 GB before base-model components, but no strong current RTX 3060 12 GB production evidence was found. It remains interesting as a style-domain reference rather than the next recommendation.

### StableAnimator — local VRAM feasible, domain mismatch

StableAnimator provides explicit pose control and reports 8 GB VRAM for its 16-frame 512×512 basic model; its pro U-Net requires about 10 GB while VAE decode can be moved to CPU. Its identity system is strongly face/human oriented and there is no strong evidence for preserving modern pixel-art character construction. It remains a fallback experiment, not the primary candidate.

## Next validation gate: Wan-Animate-2

Do not install a large production stack before a minimal proof is defined. The first Wan-Animate-2 test must use the **existing Exilada master**, not a redesigned reference created to accommodate the model.

The first test must be deliberately short and answer only four questions:

1. Does the Exilada remain recognizably the same character through motion?
2. Are adult anatomy, long hair, clothing and captivity markers stable rather than morphing?
3. Does the driving motion transfer coherently without limb collapse?
4. Does the output still read as intentional modern pixel art rather than generic painted/video diffusion imagery?

If any of these fail by a large margin, Wan-Animate-2 is rejected without seed fishing or manual repair.

Only after that identity/motion/style gate passes may the project test loopability, exact gameplay direction, equipment/weapon conditioning and sprite-sheet extraction.

## General production gate

Any future pipeline passes only if it can preserve:

- character identity;
- adult anatomy and stable proportions;
- hair, clothing and persistent character markers;
- explicitly requested equipment/weapon state;
- coherent motion and ground contact;
- temporal consistency without morphing;
- authentic modern-pixel-art readability at gameplay scale;
- reproducibility without manual frame-by-frame repainting.

A model being installable, runnable or capable of producing a video is not evidence that it passes this gate.

## Repository tooling

`tools/sprite-animation/` contains the rejected SSD experiment and remains useful only as research history unless explicitly repurposed.

Model checkpoints, dependency checkouts, build products and temporary generated files remain excluded from git.