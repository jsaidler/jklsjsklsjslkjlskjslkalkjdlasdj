# Character Animation Production — Living Decision Record

Status: **Sprite Sheet Diffusion hybrid rejected; Wan-Animate-2 Base INT8 spike rejected for production; no production animation pipeline accepted.**

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
- **Sprite Sheet Diffusion hybrid public-weight reconstruction**;
- **Wan-Animate-2 Base INT8 ConvRot local motion-transfer spike**.

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

### Wan-Animate-2 — TESTED AND REJECTED FOR PRODUCTION

Wan-Animate-2 (August 2026) was selected as the strongest next experiment because its architecture directly targets a failure class relevant to the SSD result: it consumes the raw driving video inside a redesigned dual-branch Diffusion Transformer rather than depending on an intermediate skeleton/motion extractor. Its paper explicitly identifies extraction errors and cross-identity drift as shortcomings of explicit-pose pipelines.

For the local RTX 3060 12 GB target, the public Base GGUF route became unavailable during setup. The controlled fallback used the official `Comfy-Org/Wan-Animate-2` **Base INT8 ConvRot** checkpoint rather than substituting the Distilled/Turbo model.

Validated local route:

- Windows 11;
- RTX 3060 12 GB;
- 48 GB RAM;
- ComfyUI native `WanAnimate2ToVideo`;
- `wan_animate_2_int8_convrot.safetensors`;
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`;
- `clip_vision_h.safetensors`;
- `Wan2_1_VAE_bf16.safetensors`;
- no LightX2V distillation LoRA;
- 384×576;
- 17 frames;
- 16 fps driver;
- seed 42;
- Euler;
- 20 steps;
- cache on CPU.

The local workflow executed successfully. The `comfy-cli` client initially timed out while waiting on the WebSocket, but the ComfyUI generation itself continued and produced two 17-frame MP4 outputs: the generated animation and the side-by-side comparison with the driver. Therefore the visual rejection is not an installation, OOM or execution failure.

### Visual rejection evidence — Exilada motion-transfer spike, 2026-09-04

The produced animation preserved several coarse character traits better than the rejected SSD hybrid:

- the Exilada remained recognizably the same adult character;
- face and body proportions stayed relatively stable across the 17 frames;
- long black hair remained coherent rather than collapsing into gross anatomy errors;
- worn beige clothing and captivity chains remained substantially present;
- no major extra limbs or catastrophic anatomical corruption appeared.

However, it still failed the production gate for two decisive reasons:

1. **Driving motion transfer was too weak.** The comparison video shows the real driver clearly walking across the 17-frame interval, while the generated Exilada remains largely planted in place with only a modest weight/limb shift. The requested locomotor action is not transferred with sufficient amplitude or fidelity to serve as a gameplay animation source.
2. **The canonical modern-pixel-art language was not preserved.** The output reads as smooth painted/diffusion illustration, with continuous tonal rendering and soft contour treatment, rather than intentional modern pixel art with designed pixel clusters. This is a hard project requirement, not a cosmetic preference.

Additional observed drift exists at the face and small costume details between the first and last frames, but those are secondary to the two failures above.

Result: **Wan-Animate-2 Base INT8 is rejected as the production animation foundation for the Exilada.**

Do not attempt to rescue this result with seed fishing, stronger reference strength, prompt cosmetics, post-generation pixel filters or manual repainting. A future revisit is justified only if a materially different model/checkpoint/integration specifically demonstrates both stronger raw-video motion adherence and native stylized/pixel-art preservation.

The tooling under `tools/wan-animate2-spike/` remains as reproducible research history and must not be treated as the current production path.

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

## Next animation-pipeline search

The Wan-Animate-2 spike clarified the search target further. The next candidate must not merely preserve identity. It must demonstrate all three of the following before local installation is justified:

1. strong adherence to explicit locomotor motion or pose control;
2. stable stylized-character identity and anatomy;
3. native preservation of deliberate pixel-art or similarly discrete game-art structure.

Candidates that only solve the first two while producing smooth painted/video output do not meet the project requirement.

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

`tools/wan-animate2-spike/` contains the rejected Wan-Animate-2 Base INT8 validation tooling and remains useful as reproducible research history unless explicitly repurposed.

Model checkpoints, dependency checkouts, build products and temporary generated files remain excluded from git.
