# Character Animation Production — Living Decision Record

Status: **No production animation pipeline accepted. Sprite Sheet Diffusion hybrid and Wan-Animate-2 Base INT8 were tested and rejected. Generic video-diffusion is no longer an approved research direction. Paid/proprietary hosted generation services are not valid candidates unless the user explicitly authorizes a paid dependency in advance.**

## Hard production constraints

The animation pipeline must satisfy all of the following:

- start from the approved canonical character reference rather than requiring a redesigned source image;
- preserve character identity, adult anatomy, hair, clothing, captivity markers and equipment state;
- provide explicit, inspectable gameplay motion control;
- preserve authentic modern pixel-art structure natively rather than generating smooth painted imagery and pixelating it afterward;
- work without manual frame-by-frame repainting or hand animation;
- be reproducible through project tooling and CLI automation;
- be viable on the project's Windows 11 machine with RTX 3060 12 GB and 48 GB RAM, or otherwise be lightweight enough to run locally without a larger paid compute dependency;
- **not depend on a paid API, subscription tier, per-generation credits or proprietary hosted renderer unless the user explicitly approves that cost model before the candidate is selected or tested.**

The user will not manually animate production characters and will not hire an animation/art team.

## Canonical character reference

The Exilada production master is the approved weaponless modern-pixel-art full-body reference:

`assets/source/characters/exilada/reference/exilada_master.png`

Weapons are gameplay-variable equipment and are not permanent character identity.

## Rejected approaches

The following are rejected as production foundations:

- independent frame generation with a general-purpose image generator;
- one-shot general-purpose sprite-sheet generation;
- rigid cut-out/segmented 2D puppetry from a flattened PNG;
- conventional rendered/painted animation followed by a pixel filter;
- manual frame-by-frame repainting as part of the production workflow;
- Sprite Sheet Diffusion hybrid public-weight reconstruction;
- Wan-Animate-2 Base INT8 ConvRot motion transfer;
- continuing through generic video-diffusion models that do not natively target pixel-art sprite animation;
- **paid/proprietary hosted sprite-generation APIs as the default production path.**

## Sprite Sheet Diffusion hybrid — TESTED AND REJECTED

The public SSD experiment combined the released SSD denoising/reference UNets with baseline AnimateAnyone pose guider and motion module components because the paper's trained custom multi-scale pose guider was not released.

The pipeline successfully ran locally on Windows 11 / RTX 3060 12 GB / 48 GB RAM. Rejection was therefore visual rather than infrastructural.

Observed failures on the Exilada walk included:

- identity drift;
- face changes;
- leg/foot/lower-body collapse;
- unstable hair mass;
- clothing and chain drift;
- malformed residual anatomy/objects;
- incoherent walk biomechanics;
- output dramatically below the approved master.

Do not rescue SSD with a new master, seed search, CFG tuning, extra steps or cosmetic cleanup.

Tooling under `tools/sprite-animation/` remains research history only.

## Wan-Animate-2 Base INT8 — TESTED AND REJECTED

Validated local route:

- Windows 11;
- RTX 3060 12 GB;
- 48 GB RAM;
- ComfyUI native `WanAnimate2ToVideo`;
- official `wan_animate_2_int8_convrot.safetensors` Base model;
- UMT5 FP8 text encoder;
- CLIP Vision H;
- Wan VAE;
- no LightX2V distillation LoRA;
- 384×576;
- 17 frames;
- 16 fps driver;
- seed 42;
- Euler;
- 20 steps;
- CPU cache/offload.

The workflow completed successfully. The initial `comfy-cli` WebSocket timeout did not stop the server-side generation.

Wan preserved coarse Exilada identity much better than SSD, but failed two hard gates:

1. **Motion adherence:** the driver performed clear locomotion while the generated Exilada remained mostly planted with only weak weight/limb changes.
2. **Pixel-art preservation:** output became smooth painted/diffusion illustration rather than intentional modern pixel art.

Wan-Animate-2 is therefore rejected as a production foundation. Do not rescue it with seed fishing, reference-strength sweeps, prompt cosmetics or post-generation pixel filters.

Tooling under `tools/wan-animate2-spike/` remains reproducible research history only.

## Post-Wan architectural conclusion

The useful conclusion from the failed diffusion approaches remains valid:

> **Motion representation and sprite rendering should be separated.**

A promising architecture should look more like:

`explicit skeleton/key poses -> pixel-native renderer -> temporal completion/inbetweening -> automatic QA`

rather than asking one generic video model to infer motion, identity and visual language simultaneously.

However, every component in that chain must satisfy the free/self-hostable constraint unless the user explicitly authorizes otherwise.

## PixelLab / Pixel Engine hosted route — RESEARCHED, NOW DISQUALIFIED BY COST MODEL

PixelLab was investigated because it exposes explicit skeleton-conditioned pixel-art generation and an `estimate-skeleton` API. A CLI spike was implemented under `tools/pixellab-skeleton-spike/` and successfully reached:

- canonical Exilada normalization;
- deterministic 24-color palette extraction;
- automatic skeleton estimation;
- automatic construction of four walk key poses;
- saved target-pose artifacts.

The account trial exposed limited hosted quota and the actual animation endpoint is tied to PixelLab's hosted service/tier model. This violates the project's cost constraint because the candidate was selected without first obtaining explicit authorization for a paid or metered external dependency.

**Decision:** PixelLab is not a valid production candidate under the current project rules. Stop the spike; do not purchase credits or a subscription for it.

Pixel Engine and Retro Diffusion are likewise not valid default candidates because their useful animation models are proprietary hosted services rather than freely self-hostable production components.

The `tools/pixellab-skeleton-spike/` directory remains research history. It must not be treated as the current production path.

## Free/self-hostable research candidates still relevant

### MDIGAN / differentiable palette research

The open MDIGAN/UFMG-CEFET work is scientifically relevant because it treats pixel art as a structured discrete-color domain and provides public code. Its available models focus on directional pose/view imputation rather than arbitrary locomotion or action animation, so it is not immediately usable for Exilada gameplay animation without new training/data work.

### Skeleton-driven bitmap inbetweening

The open research direction represented by `Skeleton-Driven Inbetweening of Bitmap Character Drawings` is relevant because it separates explicit skeleton motion from raster deformation/inbetweening. The released approach requires multiple drawn keyframes and topology/occlusion information, so it does not yet solve the single-reference key-pose-generation problem.

### Local SDXL/OpenPose/IP-Adapter-style stacks

A local pose-conditioned SDXL stack is technically plausible on a 12 GB GPU with aggressive memory management, but it remains unapproved because there is insufficient evidence that it will preserve the Exilada's identity and native pixel-art structure across frames. Pixel-art LoRAs that rely on high-resolution smooth generation followed by nearest-neighbor reduction do not satisfy the hard visual requirement by themselves.

## Current research rule

Before installing or testing the next candidate, verify **all** of these first:

1. source code and required model weights are freely obtainable for local/self-hosted use;
2. no subscription, per-generation credit or proprietary hosted inference is required;
3. license permits the intended project use;
4. there is concrete evidence of explicit pose/action control rather than only prompt animation;
5. there is concrete evidence of stylized/pixel-art character preservation;
6. the RTX 3060 12 GB target is credible, or there is a small controlled technical spike that can prove it without building a production stack;
7. failure criteria are defined before installation.

Do not recommend another candidate merely because it is technically installable or because a demo looks attractive.

## General production gate

Any future pipeline passes only if it can preserve:

- character identity;
- adult anatomy and stable proportions;
- hair, clothing and persistent markers;
- explicitly requested equipment/weapon state;
- coherent motion and ground contact;
- temporal consistency without morphing;
- authentic modern-pixel-art readability at gameplay scale;
- reproducibility without manual frame-by-frame repainting;
- free/local/self-hostable operation under the current project constraint.

A model being installable, runnable or capable of producing a video is not evidence that it passes this gate.

## Repository tooling status

- `tools/sprite-animation/` — rejected SSD experiment; research history only.
- `tools/wan-animate2-spike/` — rejected Wan-Animate-2 experiment; research history only.
- `tools/pixellab-skeleton-spike/` — hosted PixelLab experiment; research history only and stopped due cost-model incompatibility.

Model checkpoints, dependency checkouts, build products and temporary generated files remain excluded from git.
