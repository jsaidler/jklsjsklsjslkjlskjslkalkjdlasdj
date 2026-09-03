# Character Animation Production — Living Decision Record

Status: **local generative sprite-animation spike prepared; not yet visually validated**

## Production constraint

The user will not manually animate production characters and will not hire an animation/art team. A valid 2D character pipeline must therefore be reproducible by the project tooling and must scale beyond a single hand-corrected demo.

## Rejected approaches

The following approaches have been tested and are rejected as production foundations:

- generating independent animation frames with a general-purpose image generator and hoping identity remains stable;
- asking a general image generator for a complete sprite sheet in one generation;
- cutting an already-flattened character PNG into rigid body parts and rotating those parts as a 2D puppet.

Observed failures included character drift, biomechanically incoherent cycles, inconsistent equipment, changing proportions, and obvious paper-doll articulation.

## Current experiment: Sprite Sheet Diffusion hybrid

Sprite Sheet Diffusion (SSD) is specifically aimed at generating game-character animation from a reference character and driving poses. It is therefore materially more relevant than general image generation.

However, the public SSD release is incomplete: its trained custom multi-scale pose guider was never released. The public release contains the sprite-finetuned denoising UNet and ReferenceNet, while the motion module is byte-equivalent to the AnimateAnyone baseline.

For a reproducible local test, this project uses the runnable configuration documented by the `fszontagh/stable-diffusion.cpp` port:

- SSD finetuned `denoising_unet.pth`;
- SSD finetuned `reference_unet.pth`;
- baseline AnimateAnyone `pose_guider.pth`;
- baseline AnimateAnyone `motion_module.pth`;
- CLIP vision image encoder;
- SD VAE.

This is a **hybrid public-weight reconstruction**, not the exact unreleased paper checkpoint set.

## Hardware target

The first target is the user's Windows 11 machine with RTX 3060 12 GB and 48 GB RAM.

The chosen C++ port explicitly documents an RTX 3060 recipe:

- FP16 model loading;
- CPU parameter offload;
- flash attention for multi-frame generation;
- VAE tiling at 512x768 and above.

The port measured approximately 7.4 GB peak VRAM for an 8-frame 512x640 / 25-step video generation test. The project will use 512x768 for the quality profile because the approved Exilada reference is tall and detail retention matters.

## Deterministic walk test

The project does not ask the model to invent motion. A deterministic BODY_18/OpenPose-style walk skeleton sequence is generated locally.

The base cycle has eight conventional phases:

1. contact A;
2. down A;
3. passing A;
4. up A;
5. contact B;
6. down B;
7. passing B;
8. up B.

This cycle is repeated three times to create a 24-frame driving window. The motion module performs more reliably in its native context length than on an isolated 8-frame sequence. The output tool extracts the middle eight frames as the candidate production cycle.

## Decision gate

The pipeline is not accepted because it installs or executes successfully. The first generated Exilada walk cycle must be inspected.

Pass criteria:

- identity preservation;
- stable adult anatomy and proportions;
- stable clothing/hair/weapon design;
- coherent gait;
- no hallucinated anatomy or extra props;
- temporal consistency sufficient that any remaining post-processing can be automated.

Fail condition:

If acceptable quality requires manual frame-by-frame repainting, the pipeline is rejected because it violates the project's production constraint.

## Repository tooling

Implementation lives under:

`tools/sprite-animation/`

The repository versions scripts, configuration and documentation only. Model checkpoints, dependency checkouts, build products and generated animation files are explicitly excluded from git.
