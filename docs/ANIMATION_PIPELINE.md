# Character Animation Production — Living Decision Record

Status: **No production animation pipeline accepted. Sprite Sheet Diffusion hybrid and Wan-Animate-2 Base INT8 were tested and rejected. Generic video-diffusion is no longer an approved research direction. Paid/proprietary hosted generation services are disqualified unless explicitly authorized in advance. The only new local spike currently justified is a four-key-pose renderer based on FLUX.2 Klein 4B + RefControl Pose + a pixel-art LoRA; it is not production-approved.**

## Hard production constraints

The animation pipeline must:

- start from the approved canonical character reference rather than requiring a redesigned source image;
- preserve character identity, adult anatomy, hair, clothing, captivity markers and equipment state;
- provide explicit, inspectable gameplay motion control;
- preserve authentic modern pixel-art structure rather than generating smooth painted imagery and pixelating it afterward;
- work without manual frame-by-frame repainting or hand animation;
- be reproducible through project tooling and CLI automation;
- be credible on Windows 11 / RTX 3060 12 GB / 48 GB RAM;
- use source code and required model weights that are freely obtainable for local/self-hosted use;
- not require subscriptions, per-generation credits or proprietary hosted inference unless the user explicitly authorizes that cost model before research or testing;
- have a license compatible with intended project use, preferably permissive/commercial-compatible.

The user will not manually animate production characters and will not hire an animation/art team.

## Canonical character reference

The Exilada production master is the approved weaponless modern-pixel-art full-body reference:

`assets/source/characters/exilada/reference/exilada_master.png`

Weapons are gameplay-variable equipment and are not permanent character identity.

## Rejected approaches

Rejected as production foundations:

- independent frame generation with a general-purpose image generator;
- one-shot general-purpose sprite-sheet generation;
- rigid cut-out/segmented 2D puppetry from a flattened PNG;
- conventional rendered/painted animation followed by a pixel filter;
- manual frame-by-frame repainting;
- Sprite Sheet Diffusion hybrid public-weight reconstruction;
- Wan-Animate-2 Base INT8 ConvRot motion transfer;
- generic video-diffusion models that do not natively target pixel-art sprite animation;
- paid/proprietary hosted sprite-generation APIs as the default production path.

## Sprite Sheet Diffusion hybrid — TESTED AND REJECTED

The public SSD experiment combined the released SSD denoising/reference UNets with baseline AnimateAnyone pose guider and motion module components because the paper's trained custom multi-scale pose guider was not released.

The pipeline successfully ran locally on Windows 11 / RTX 3060 12 GB / 48 GB RAM. Rejection was visual rather than infrastructural.

Observed Exilada failures included identity drift, face changes, leg/foot/lower-body collapse, unstable hair mass, clothing and chain drift, malformed residual anatomy/objects, incoherent walk biomechanics and output dramatically below the approved master.

Do not rescue SSD with a new master, seed search, CFG tuning, extra steps or cosmetic cleanup. `tools/sprite-animation/` remains research history only.

## Wan-Animate-2 Base INT8 — TESTED AND REJECTED

Validated local route: Windows 11, RTX 3060 12 GB, 48 GB RAM, ComfyUI native `WanAnimate2ToVideo`, official Base INT8 ConvRot model, UMT5 FP8, CLIP Vision H, Wan VAE, no LightX2V LoRA, 384×576, 17 frames, 16 fps driver, seed 42, Euler, 20 steps and CPU cache/offload.

The workflow completed successfully; the initial `comfy-cli` WebSocket timeout did not stop server-side generation.

Wan preserved coarse Exilada identity much better than SSD but failed two hard gates:

1. **Motion adherence:** the driver performed clear locomotion while the generated Exilada remained mostly planted with weak weight/limb changes.
2. **Pixel-art preservation:** output became smooth painted/diffusion illustration rather than intentional modern pixel art.

Wan-Animate-2 is rejected as a production foundation. Do not rescue it with seed fishing, reference-strength sweeps, prompt cosmetics or post-generation pixel filters. `tools/wan-animate2-spike/` remains research history only.

## Architectural conclusion after SSD and Wan

The useful direction is still:

`explicit skeleton/key poses -> pixel-oriented renderer -> temporal completion/inbetweening -> automatic QA`

Motion representation and sprite rendering should be separated. Asking one generic video model to infer motion, identity and visual language simultaneously has failed for materially different reasons.

## Hosted route — RESEARCHED, DISQUALIFIED BY COST MODEL

PixelLab was investigated because it exposes explicit skeleton-conditioned pixel-art generation. A CLI spike reached canonical Exilada normalization, deterministic palette extraction, automatic skeleton estimation and automatic construction of four walk key poses. The useful animation endpoint is a hosted/tiered service, which violates the project constraint because no paid dependency had been authorized.

**Decision:** stop PixelLab; do not buy credits/subscription. Pixel Engine and Retro Diffusion are likewise disqualified because their relevant animation models are proprietary hosted services. `tools/pixellab-skeleton-spike/` remains research history only.

## 2026-09-04 free/open/local-only research

The search was repeated with a hard filter: public local weights, local execution, compatible license, explicit pose/motion control, evidence relevant to stylized/pixel rendering and credible RTX 3060 12 GB operation. No candidate was accepted merely because it can technically run.

### FLUX.2 Klein 4B + RefControl Pose + pixel-art LoRA — ONLY NEW SPIKE CURRENTLY JUSTIFIED

This is not a video-animation model. It is a proposed **four-key-pose renderer** intended to answer one narrow question first: can the same Exilada survive four explicitly prescribed walk poses while retaining a convincing modern-pixel-art language?

Base model:

- `black-forest-labs/FLUX.2-klein-base-4B` / 4B family;
- public local weights;
- Apache 2.0;
- Black Forest Labs explicitly documents the 4B model as local/commercial-capable and gives RTX 3060 12 GB as an example hardware target for 4B local fine-tuning;
- official/current memory figures put 4B inference around the 9–13 GB class depending on variant/runtime, with CPU offload available;
- public Apache-2.0 GGUF quantizations of the Base 4B exist (Q4_0 roughly 2.46 GB, Q8_0 roughly 4.3 GB), although LoRA compatibility must be validated in the chosen runtime rather than assumed.

Explicit pose/reference control:

- `xocialize/refcontrol-FLUX.2-klein-4B-pose-lora`;
- Apache 2.0;
- rank-32 LoRA, roughly 88 MB;
- trained on `FLUX.2-klein-base-4B`;
- input 1 is an OpenPose-style COCO-18 skeleton and input 2 is the character reference;
- its stated purpose is to render the referenced subject in the skeleton pose while retaining identity/appearance;
- model card reports bf16/int4 loading and data across human motion identities/activities, with claimed stylized-subject generalization.

Pixel-art conditioning candidates:

- `adirik/pixel-art-lora-flux.2-klein-4B`: Apache 2.0, roughly 370 MB, trained on the same Base 4B family. Compatibility is cleanest, but its 64×64 training images were upsampled to 512×512 specifically to create a pixelated style/easier downsampling. This is a material warning because pseudo-pixel rendering followed by reduction is not the project's target.
- `Limbicnation/pixel-art-lora`: Apache 2.0, roughly 308 MB, trained on distilled `FLUX.2-klein-4B`, explicitly targeted at game sprites/transparent RGBA and trained on a CC0/provenance-tracked pixel-art dataset. Its domain fit is stronger, but combining it with the Base-trained RefControl Pose adapter on one runtime is not yet empirically proven.

Diffusers supports activating/weighting multiple LoRA adapters in general, so a pose LoRA + style LoRA combination is technically plausible. **That does not prove that these two specific adapters cooperate correctly on FLUX.2 Klein.** This interaction is part of the spike, not an established fact.

Why installation is justified for a minimal spike:

- all required base/adapter weights are publicly downloadable;
- relevant components are Apache 2.0;
- the pose adapter provides explicit skeleton + reference conditioning rather than prompt-only motion;
- pixel-art-specific 4B adapters exist in the same model family;
- FLUX.2 Klein 4B has credible 12 GB-class local execution/offload evidence, including explicit RTX 3060 12 GB documentation from BFL for the 4B family.

What it does **not** solve yet:

- temporal consistency between independently rendered key poses;
- true native modern-pixel-art structure at the Exilada's desired detail level;
- exact hair/chain/clothing persistence across pose changes;
- inbetweening or a full animation loop.

Therefore it is approved only as a **single fixed four-key-pose validation spike**. No temporal model is to be added until those four frames pass.

Proposed spike gate:

- fixed four walk key poses generated from one deterministic COCO-18 skeleton template/sequence;
- canonical Exilada master as reference;
- one fixed seed and one fixed adapter configuration;
- no seed fishing, character redesign, manual frame repair or inpainting;
- compare face, silhouette/anatomy, hair, clothing, chains, feet/ground contact and deliberate pixel-cluster structure;
- reject immediately if the frames become smooth/painterly, pseudo-pixel after downsampling, materially different characters or anatomically unstable;
- if and only if all four pass, research a free/local temporal completion method separately.

### One-to-All Animation 1.3B — OPEN, NOT APPROVED FOR INSTALLATION

Official repository and checkpoints are public under Apache 2.0. The method accepts a single reference and explicit/direct/retargeted pose control and includes cartoon-oriented data. This makes it architecturally relevant.

However, the authors' own low-resource example targets a 16 GB T4 for the 1.3B model. No sufficiently strong RTX 3060 12 GB proof was found, and there is no convincing evidence of preserving deliberate modern pixel-art structure. It also returns to the video-diffusion family already shown to be problematic for this project.

Decision: do not install now.

### StableAnimator — OPEN/HARDWARE-FEASIBLE, WRONG DOMAIN

Public model weights are Apache 2.0 and the implementation supports a reference image plus pose sequence. The authors report 8 GB VRAM for the 16-frame 512×512 basic model; the pro U-Net needs about 10 GB while VAE decode can be moved to CPU.

This satisfies the hardware test but is explicitly a human-animation/video framework with identity machinery centered on human faces and no evidence of preserving real pixel-art raster structure.

Decision: do not install.

### SteadyDancer — OPEN/12-GB COMMUNITY PROOF, WRONG DOMAIN

Open Apache-2.0 implementations/weights and a community ComfyUI route report testing at 12 GB VRAM with offload and GGUF support. It is pose-driven and targets first-frame preservation.

There is no material evidence that it preserves modern pixel-art structure; it remains a continuous human-video renderer closely related to a direction already rejected.

Decision: do not install.

### MikuDance — OPEN/STYLIZED, INSUFFICIENT 12-GB + PIXEL EVIDENCE

Public Apache-2.0 project/weights exist and the method is explicitly aimed at stylized character art with pose/motion conditioning. This is better domain alignment than human-only systems.

No strong RTX 3060 12 GB evidence was found, and its stylized examples do not establish native modern-pixel-art preservation.

Decision: do not install.

### SCAIL-2 — OPEN, NOT A PIXEL-ART CANDIDATE

Public code/checkpoints are available and the method supports end-to-end and pose-driven character animation at 512p/704p. It remains a large Wan-family video renderer with no convincing pixel-art preservation evidence; earlier research also found identity/loose-clothing risks close to the Exilada's failure modes.

Decision: do not install.

### AniGen — OPEN RESEARCH, FAILS HARDWARE CONSTRAINT

AniGen can turn a single image into a rigged 3D asset and then use external motion, but the authors require an NVIDIA GPU with at least 18 GB VRAM and test on A800/RTX 3090. It also introduces third-party dependency/license complexity.

Decision: reject for the RTX 3060 12 GB target.

### See-through layer decomposition — OPEN/12-GB PLAUSIBLE, RESEARCH COMPONENT ONLY

`shitagaki-lab/see-through` (Apache 2.0) decomposes a single anime illustration into up to 23 inpainted semantic layers. The official project documents roughly 10 GB peak at 1280 with group offload on a 12 GB GPU and an ~8 GB NF4 route.

This is interesting because it can preserve a source character through explicit layered deformation rather than independently redrawing every frame. It is not accepted as an animation foundation because:

- it is trained for anime/VTuber illustrations, not pixel art;
- occluded regions are diffusion-inpainted;
- downstream mesh/layer deformation risks resampling/mixels unless a pixel-preserving renderer is designed;
- it returns toward the deformable-rig family, which may reproduce the visual stiffness/artifact problems already rejected.

Decision: research reference only; no installation yet.

### Animated Drawings — FREE/DETERMINISTIC, VISUALLY INCOMPATIBLE

Meta's archived MIT project automatically rigs/deforms a single drawing and can apply motion data while preserving the source bitmap more directly than generative rendering. It was designed for simple children's drawings with separated limbs and uses deformable 2D character animation. The Exilada's hair, clothing, occlusion and mature detailed pixel-art silhouette fall far outside its intended domain, and the project has already rejected puppet-like deformation as a visual foundation.

Decision: do not install.

### MDIGAN / differentiable palette work — PIXEL-NATIVE RESEARCH, WRONG ACTION SPACE

Open local research treats pixel art as a structured discrete-color domain and is valuable scientifically. Available models focus on directional pose/view imputation (front/back/left/right), not arbitrary locomotion or combat actions from a single reference.

Decision: research principle only; not a current production candidate without a project-specific training program.

### Skeleton-driven bitmap inbetweening — OPEN COMPONENT, NOT SINGLE-REFERENCE AUTOMATION

The released bitmap inbetweening research separates skeleton motion from raster deformation but requires multiple drawn keyframes plus topology/occlusion information. It may become relevant only after a reliable automatic key-pose renderer exists.

Decision: no installation yet.

## Current technical ranking under the free/local rule

1. **FLUX.2 Klein 4B + RefControl Pose + one pixel-art LoRA** — only candidate with enough combined evidence to justify a minimal local four-key-pose spike; not production-approved.
2. **See-through + a future pixel-preserving deformation renderer** — interesting non-generative identity-preservation research, but currently conflicts with style/rig constraints.
3. **One-to-All 1.3B** — explicit pose + cartoon relevance, but official low-resource target is 16 GB and pixel-art evidence is absent.
4. **MikuDance** — stylized-character relevance, but no good 12 GB or pixel-art evidence.
5. **StableAnimator / SteadyDancer / SCAIL-2** — runnable or nearly runnable, but wrong continuous-video domain.
6. **MDIGAN / bitmap inbetweening / Animated Drawings** — useful technical components or principles, not a complete solution to the single-reference requirement.
7. **AniGen** — fails the 12 GB hardware gate.

## Current research rule

Before installing/testing any candidate, verify:

1. source code and required weights are freely obtainable locally;
2. no subscription, per-generation credit or proprietary hosted inference is required;
3. license permits intended use;
4. explicit pose/action control exists rather than only prompt animation;
5. there is relevant evidence for stylized/pixel-art preservation;
6. RTX 3060 12 GB operation is credible;
7. failure criteria are defined before installation.

Do not recommend a candidate merely because it is installable or because a demo looks attractive.

## General production gate

A future pipeline passes only if it preserves character identity, adult anatomy/proportions, hair/clothing/markers, requested equipment state, coherent motion/ground contact, temporal consistency, authentic modern-pixel-art readability at gameplay scale, reproducibility without manual repainting and free/local/self-hostable operation.

A model being installable, runnable or capable of producing a video is not evidence that it passes this gate.

## Repository tooling status

- `tools/sprite-animation/` — rejected SSD experiment; research history only.
- `tools/wan-animate2-spike/` — rejected Wan-Animate-2 experiment; research history only.
- `tools/pixellab-skeleton-spike/` — hosted PixelLab experiment; research history only and stopped due cost-model incompatibility.

Model checkpoints, dependency checkouts, build products and temporary generated files remain excluded from git.
