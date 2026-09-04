# Character Animation Production — Living Decision Record

Status: **Sprite Sheet Diffusion hybrid rejected; Wan-Animate-2 Base INT8 spike rejected for production; no production animation pipeline accepted. The next validation must be pixel-native and explicitly motion-controlled; no further generic video-diffusion spike is approved.**

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
- **Wan-Animate-2 Base INT8 ConvRot local motion-transfer spike**;
- continuing through generic video-diffusion models that do not natively target pixel-art sprite animation.

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

## Wan-Animate-2 — TESTED AND REJECTED FOR PRODUCTION

Wan-Animate-2 (August 2026) was selected because its architecture directly targets a failure class relevant to the SSD result: it consumes the raw driving video inside a redesigned dual-branch Diffusion Transformer rather than depending on an intermediate skeleton/motion extractor.

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

## 2026-09-04 post-Wan research — pixel-native and explicit-control routes

The search was restarted from the production constraints rather than from the current video-model leaderboard. The key conclusion is that **motion representation and sprite rendering should be separated**. A game pipeline benefits from deterministic or inspectable motion (skeleton/keyframes) and a renderer trained for actual pixel art; asking one generic video model to infer both simultaneously has now failed twice for different reasons.

### PixelLab raw skeleton animation — strongest explicit-control renderer found, hosted only

PixelLab exposes a public `animate-with-skeleton` API that accepts a character reference image plus explicit skeleton keypoints, camera view/direction, seed, forced palette, init images, inpainting images and masks. Its `estimate-skeleton` endpoint can estimate the source character rig from a single image. Current API/docs support pixel-art canvases up to 256×256, although one pricing page still describes the skeleton product as up to 128×128; the API schema is the more specific current contract.

Why it is relevant:

- motion is an explicit skeleton sequence rather than a text/video guess;
- output is generated as pixel art at the target raster scale;
- palette can be forced;
- the same skeleton sequence can be reused across characters;
- the API is scriptable and therefore compatible with a CLI-only project pipeline;
- a driver video, BVH/motion library or procedural walk can be converted to 2D keypoints before rendering, so the renderer does not need to infer motion from raw video.

Critical caveat: PixelLab's own recommended workflow still expects occasional skeleton correction, rough frame fixes and iterative inpainting. That conflicts with the project's no-manual-production constraint. Therefore PixelLab is **not accepted as production**, but it is the strongest candidate for a small controlled remote validation of explicit pose adherence + pixel-native rendering.

### Pixel Engine 1.5 and Keyframes — strongest temporal pixel-native candidate found, hosted only

Pixel Engine is explicitly trained for pixel-art animation rather than still-image generation. Its current `pixel-engine-v1.5` API accepts a starting PNG up to 320×320, 3–16 output frames, deterministic seed and a pixel mode with either color-count quantization or an explicit palette. The service states that pixel mode produces real pixel art rather than mixels.

More important for this project, its separate `/keyframes` endpoint accepts one or more reference images at exact frame indices, each with independent conditioning strength and placement, then interpolates them into a full 3–20-frame animation. Pixel-mode keyframes support images up to 256×256. This is materially different from asking a video model to invent motion: a small set of approved/generated action poses can become hard temporal anchors.

Why it is relevant:

- native pixel mode and palette control;
- temporal model specialized for sprite animation;
- exact frame count;
- keyframes can be pinned to exact indices;
- output can be a spritesheet directly;
- current v1.5 supports more detailed/higher-resolution pixel sprites than most older sprite models.

Caveats:

- architecture/weights are proprietary and no public local checkpoint was found;
- direct `/animate` remains prompt-driven and the official guide recommends rerolling some difficult actions, which cannot become the production reliability strategy;
- `/keyframes` solves temporal control only after suitable keyframe images exist.

Result: Pixel Engine is **not production-approved**, but its keyframe mode is the best temporal-completion stage found for a hybrid pipeline.

### Retro Diffusion RD Animation — pixel-native benchmark candidate, hosted only

Retro Diffusion's current RD Animation API is specialized for grid-aligned, limited-color pixel-art sprites. Advanced animation takes an existing pixel-art start frame, supports 32–256px frames, 4/6/8/10/12/16-frame durations, palette input and direct spritesheet output. RD Pro also supports multiple reference images for consistent character/style generation.

Strength: the service has the clearest explicit commitment to true grid-aligned pixel art among the surveyed production tools.

Weakness: motion control is primarily preset/action text (`walking`, `idle`, `jump`, `crouch`, `attack`, `custom_action`, etc.), not raw skeleton or exact joint trajectories. It is therefore useful as a pixel-art quality benchmark but ranks below a skeleton→keyframe pipeline for gameplay animation control.

No current public local weights for the advanced animation model were found; current integrations use the hosted API/Replicate.

### MDIGAN / differentiable-palette-quantization research — pixel-native but wrong motion domain

The UFMG/CEFET line of work (`mdigan-characters`, SBGames 2024; extended differentiable palette quantization work in 2025) is highly relevant scientifically because it treats pixel art as a structured discrete-color domain instead of as a visual effect. The official MDIGAN code is available and trains 64×64 TensorFlow models that impute missing front/back/left/right character poses from one or more other views. The 2025 extension adds differentiable palette quantization and palette-coverage losses.

This is evidence that pixel-native generative constraints are technically effective, but the available models solve **directional pose imputation**, not arbitrary locomotion/action animation. They are not a production candidate for the Exilada's walk/attack system without a new project-specific dataset and training program.

### SDXL + OpenPose ControlNet + IP-Adapter + Pixel Art XL — locally feasible but not recommended

A local frame-by-frame architecture can combine:

- SDXL;
- OpenPoseXL ControlNet for exact pose;
- IP-Adapter Plus for the Exilada reference;
- Pixel Art XL LoRA for style;
- fixed seed and one pose per frame.

There is concrete evidence that SDXL/IP-Adapter workflows run on RTX 3060 12 GB, and current memory guidance puts SDXL + one ControlNet + one IP-Adapter near the 12 GB limit with offload/tiling. Therefore this route is technically installable on the target machine.

It is **not recommended for installation now** because the stronger requirement is visual/domain evidence, not mere VRAM feasibility. Pixel Art XL explicitly recommends generating at SDXL resolution and downscaling by 8× to obtain pixel-perfect output, which is too close to the already rejected 'painted image then pixel treatment' family. Frame-by-frame SDXL also provides no intrinsic temporal identity guarantee. A recent 16 GB deployment design using exactly SDXL + OpenPose + IP-Adapter + Pixel Art XL exists, but that is not evidence that it will preserve the Exilada at the required quality on 12 GB.

### Skeleton-driven bitmap inbetweening — useful research component, not single-reference automation

The 2024 ACM `Skeleton-Driven Inbetweening of Bitmap Character Drawings` project uses explicit skeleton animation, 2.5D layering, deformation optimization and learned blending to interpolate raster keyframes while handling occlusions. It is closer to animation engineering than prompt generation and gives strong motion control.

However, it requires two drawn bitmap keyframes plus topology/occlusion annotations, has a Linux-oriented monolithic implementation, and does not create new action poses from a single reference. It may become useful only after a reliable automated key-pose generator exists. It is not a standalone production solution for the current constraint.

### Other current sprite products researched but deprioritized

- **AutoSprite / FrameSprite**: both ultimately create AI video and extract frames/spritesheets; this is the generic-video-derived family we are no longer pursuing.
- **PerfectPixel / agent-driven sprite-sheet pipelines**: orchestration around general image/video models; consistency still depends on regeneration/curation.
- **Animator2D / pose-sprite-diffusion learning projects**: useful research demonstrations but their own authors describe incoherent output or explicitly state that they are educational rather than production systems.
- **traditional/cut-out 2D auto-rigging**: deterministic and cheap but visually belongs to the rigid-puppet approach already rejected for the game.

## Current technical ranking

Ranked by fit to the actual project requirement, not by general image quality:

1. **Hybrid explicit-motion pipeline: PixelLab skeleton key poses → Pixel Engine keyframe interpolation** — strongest architecture found; hosted; unproven on Exilada; next controlled validation candidate.
2. **PixelLab skeleton animation alone** — strongest direct explicit-pose control and true pixel-art target, but official workflow still anticipates manual correction.
3. **Pixel Engine 1.5 / keyframes alone** — strongest temporal pixel-native renderer, but needs keyframe poses for hard motion control.
4. **Retro Diffusion RD Animation** — strongest hosted pixel-art benchmark with start-frame/palette/spritesheet support, weaker explicit motion control.
5. **MDIGAN / differentiable-palette-quantization research** — excellent domain principles, insufficient action space.
6. **SDXL + OpenPose + IP-Adapter + Pixel Art XL** — locally feasible on 12 GB only with tight memory management; not recommended because pixel/temporal quality evidence is insufficient.
7. **Skeleton-driven bitmap inbetweening** — strong inbetweening research, but not single-reference generation and requires annotation/keyframes.

## Local-install decision after research

**No new local model stack is approved for installation at this point.**

The target RTX 3060 12 GB can technically run some SDXL pose/reference stacks, and the small GAN research models would trivially fit, but neither class currently has concrete evidence of simultaneously satisfying:

- Exilada identity;
- explicit gameplay motion;
- stable temporal anatomy/details;
- native modern pixel-art structure;
- no manual frame repair.

Installing another multi-gigabyte local stack before testing the stronger pixel-native hosted candidates would repeat the previous mistake of treating hardware feasibility as pipeline evidence.

## Next controlled validation

The recommended next experiment is **not another video model**. It is a two-stage, CLI/API-controlled spike:

1. derive an explicit 4-pose walk cycle skeleton from a deterministic source (procedural/BVH/template or pose extraction from a driver) and retarget it to the Exilada's estimated skeleton;
2. ask PixelLab `animate-with-skeleton` for four 256×256 pixel-art key poses using the Exilada reference and a fixed/derived palette;
3. if and only if those four key poses preserve identity, anatomy, hair, clothing, chains and pixel-art structure, feed them at fixed indices into Pixel Engine `/keyframes` to create an 8-frame loop;
4. automatically measure palette drift, alpha, baseline/foot contact, silhouette-area variance, frame-to-frame structural change and loop seam;
5. reject immediately on strong identity/style/anatomy failure — no reroll farming or manual repainting.

Retro Diffusion RD Animation may be run once as a benchmark against the same normalized reference, but it is not the primary control architecture because its motion is prompt/preset driven rather than joint-explicit.

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
