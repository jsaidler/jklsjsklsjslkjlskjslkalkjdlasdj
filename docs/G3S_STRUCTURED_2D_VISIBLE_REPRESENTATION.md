# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-B3B GENUINE NATIVE 2D BODY SOURCE METHOD NEXT**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets/guides -> persistent 2D pixel assets -> deterministic 2D transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB or final sprite silhouette.

## Visible-ownership invariant — LOCKED

G3V is authoritative: the direct visible-3D route failed and was closed.

Therefore:

- 3D may guide anatomy, motion, topology, sockets, contacts, depth and occlusion;
- 3D may not be mechanically promoted into final visible sprite geometry;
- a 3D render or mask is not a sprite template;
- cropping/recoloring/quantizing a projected 3D mask or render is still a 3D-owned visible route;
- final character pixels are owned by persistent structured 2D assets;
- runtime/export uses sprites.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI operation by the user;
- no beauty-render shrink/pixel-filter route as final art;
- no bilinear filtering;
- recurring work remains scriptable/headless;
- animation consumes persistent 2D parts rather than independently generated frames;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer.

## Model-discard cleanup rule — LOCKED

Whenever a model/route is declared **FAIL/CLOSED/REJECTED** and no longer required, the same response must include exact PowerShell cleanup commands for its model-specific files. Shared runtimes still in use are preserved; small evidence outputs remain unless explicitly removed.

### Current closed-model cleanup commands

```powershell
# Alucard
Remove-Item -LiteralPath "Z:\AI\AlucardSpike" -Recurse -Force -ErrorAction SilentlyContinue

# PixelLock
Remove-Item -LiteralPath "Z:\AI\PixelLockSpike" -Recurse -Force -ErrorAction SilentlyContinue

# SD1.5 native re-author
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\checkpoints\v1-5-pruned-emaonly.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\loras\pixel-art-sd15.safetensors" -Force -ErrorAction SilentlyContinue

# Qwen weights — fixed control retained; shared embedded Python runtime remains
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\unet\Qwen-Image-Edit-2509-Q4_0.gguf" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\vae\qwen_image_vae.safetensors" -Force -ErrorAction SilentlyContinue
```

## Closed source-model search

Qwen native, SD1.5, PixelLock and Alucard were bounded source experiments. None produced an acceptable native production sprite. Do not reopen local model hunting.

The coherent Qwen preferred-resolution control remains design/scaffold provenance only:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## G3S-A / A1 history

- authored native V1 — FAIL/CLOSED: mouth not visually readable;
- Facial/Anatomy Lock V2 — FAIL/CLOSED: mouth became an artificial block;
- macro source retained only as provisional design/scale evidence;
- head/face remains a replaceable asset problem rather than a reason to redraw the whole character.

## G3S-B V1 — FAIL/CLOSED

The first persistent-part decomposition was pixel-lossless but architecturally wrong. It carved body/hair/clothing pieces directly from a composite source, so production ownership was contaminated.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b_v1_failure.json`

## G3S-B2 — PASS/CLOSED DIAGNOSTIC

Measured facts:

- exact recomposition: PASS;
- source opaque pixels: `2974`;
- visible body pixels: `1538`;
- hair pixels: `826`;
- clothing pixels: `610`;
- hidden/unknown body pixels: `1205`.

Conclusion: **the complete body cannot be recovered by subtracting hair/clothing from the master.**

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

# Correct staged character build — LOCKED

1. **G3S-B3 — complete nude body base**
   - adult female body;
   - hairless;
   - no clothing/bindings;
   - no cuffs/shackles/chains;
   - complete scalp/head/neck/torso/limbs under all future layers;
   - owned as a native 2D sprite asset.

2. **G3S-B4 — hair**
   - independent persistent 2D asset/layer family;
   - later separable into back/front/submasses for wind and secondary motion;
   - never part of body pixels.

3. **G3S-B5 — clothing and accessories**
   - chest wrap;
   - hip cloth;
   - arm/leg bindings;
   - cuffs/shackles;
   - chain segments;
   - each owns coverage, sockets, depth and state independently.

4. **G3S-C — four-phase walk proof**
   - only after B3/B4/B5 assets are layered correctly;
   - validated motion frames `1568,1588,1608,1628`;
   - hidden rig drives 2D deformation/ordering guides;
   - no independently regenerated animation frame;
   - exported/runtime result is sprite-based.

# Nudity — LOCKED SYSTEMIC STATE

Nudity is a normal supported state, not a special variant and not a runtime generation task.

Runtime composition:

`complete body base + optional hair + body-state overlays + zero or more garment/equipment/accessory layers`

Consequences:

- no censor garment is structurally required;
- no hidden body reconstruction is allowed when clothing is removed/damaged;
- chest and pelvic anatomy must be coherent at native gameplay scale;
- presentation may be neutral, sensual, erotic, heroic, brutal or vulnerable according to scene intent;
- body wounds/scars/blood/wetness remain attached to body regions;
- sever/dismemberment operates on the same complete body while clothing/equipment inherits or detaches by state rules.

# G3S-B3 — Nude Body Base — CURRENT

Canonical log:

`docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

The master/Qwen composite is reference only. B3 creates a dedicated body asset rather than removing hair/clothes from a composite.

## G3S-B3A V1 — FAIL/CLOSED REVISION

The first guide run used the wrong MPFB gender polarity. This was a revision failure only.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3a_v1_failure.json`

## G3S-B3A V2 — PASS/CLOSED

The corrected V2 guide passes structural review:

- resolved gender `female`;
- resolved life stage `adult`;
- female targets `21`, male targets `0`;
- adult targets `21`, minor targets `0`;
- complete body geometry;
- zero hair/clothing/restraint/chain objects;
- visible height `128 px`;
- locked G1 camera/scale;
- guide-only art authority.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3A is closed. Its RGB, mask and projected silhouette are reference/guide data only.

## G3S-B3B V1 — FAIL/CLOSED ROUTE

The first B3B implementation copied the B3A binary projected mask directly into final native alpha/silhouette and procedurally colored that shape.

This was rejected because it still made hidden 3D the final visible silhouette owner and revived procedural mannequin-style authoring.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

The invalid V1 script and runner were removed from `main` before user execution.

No model was downloaded/discarded by this route correction, so no model cleanup command applies.

## G3S-B3B — CURRENT

B3B must produce a genuinely authored native `128×128` 2D body sprite source.

B3A may guide:

- anatomy;
- proportions;
- joints/topology;
- scale/camera;
- sanity checks.

B3A may not own:

- final alpha;
- final silhouette;
- final RGB;
- final pixel clusters/edge treatment.

The approved 2D body source must itself own those decisions. Only after that source passes may hidden rig data be used to animate/deform persistent 2D parts.

# G3S-B4 — Hair

Blocked until B3B body approval.

# G3S-B5 — Clothing / restraints / chains

Blocked until B3B body approval.

# G3S-C — Four-phase walk proof

Blocked until B3/B4/B5 are structurally correct.

## Exact next action

**No B3B runner is approved. Do not run one yet.**

First define the corrected native-2D B3B authoring method and verify that it preserves sprite ownership instead of mechanically promoting 3D guide pixels into final art.
