# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-B3 NUDE BODY BASE NEXT**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel assets -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible color pixels.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI operation by the user;
- no beauty-render shrink/pixel-filter route as final art;
- no bilinear filtering;
- recurring work remains scriptable/headless;
- animation consumes persistent parts rather than independently generated frames;
- body, hair, clothing and accessories must have separate ownership;
- a complete body must exist under every removable layer.

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

Qwen native, SD1.5, PixelLock and Alucard were bounded source experiments. None produced an acceptable native production sprite. Do not reopen the local source-model search.

The coherent Qwen preferred-resolution control remains design/scaffold provenance only:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## G3S-A / G3S-A1 history

- authored native V1 — FAIL/CLOSED: mouth not visually readable;
- Facial/Anatomy Lock V2 — FAIL/CLOSED: mouth became an artificial block;
- macro source retained only as provisional design/scale evidence;
- head/face remains a replaceable asset problem rather than a reason to redraw the whole character.

## G3S-B V1 — FAIL/CLOSED

The first persistent-part decomposition was pixel-lossless but architecturally wrong. It carved body/hair/clothing pieces directly from a composite source, so production ownership was contaminated.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b_v1_failure.json`

## G3S-B2 — PASS/CLOSED DIAGNOSTIC

Canonical log:

`docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`

B2 successfully demonstrated the problem instead of solving it by fake subtraction.

Measured facts:

- exact recomposition: PASS;
- source opaque pixels: `2974`;
- visible body pixels: `1538`;
- hair pixels: `826`;
- clothing pixels: `610`;
- hidden/unknown body pixels: **`1205`**.

Conclusion: **the complete body cannot be recovered by subtracting hair/clothing from the master.**

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

# Correct staged character build — LOCKED

The structured character is now authored in this order:

1. **G3S-B3 — complete nude body base**
   - adult female body;
   - hairless;
   - no clothing/bindings;
   - no cuffs/shackles/chains;
   - complete scalp/head/neck/torso/limbs under all future layers.

2. **G3S-B4 — hair**
   - independent persistent asset/layer family;
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
   - no independently regenerated animation frame.

# Nudity — LOCKED SYSTEMIC STATE

Nudity is a normal supported state, not a special variant and not a runtime generation task.

Runtime composition:

`complete body base + optional hair + body-state overlays + zero or more garment/equipment/accessory layers`

A nude state therefore means garment/equipment layers are absent. The complete adult body already exists underneath.

Consequences:

- no censor garment is structurally required;
- no hidden body reconstruction is allowed when clothing is removed/damaged;
- chest and pelvic anatomy must be coherent at native gameplay scale;
- presentation remains matter-of-fact and non-erotic;
- body wounds/scars/blood/wetness remain attached to body regions;
- sever/dismemberment operates on the same complete body while clothing/equipment inherits or detaches by state rules.

# G3S-B3 — Nude Body Base — CURRENT

Canonical log:

`docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

The master/Qwen composite is reference only. B3 must create a dedicated body asset rather than remove hair/clothes from a composite.

B3 internal bounded sequence:

- **B3-A deterministic anatomy guide** from the existing hidden-rig/MPFB infrastructure; guide only, not final art;
- **B3-B native `128×128` body source**, visually reviewed as standalone intentional pixel art.

No hair, clothing or restraint asset is authored before B3-B passes.

# G3S-B4 — Hair

Blocked until B3 body approval.

# G3S-B5 — Clothing / restraints / chains

Blocked until B3 body approval; hair may be validated before or alongside these overlays, but all remain independent assets.

# G3S-C — Four-phase walk proof

Blocked until the layered base is structurally correct.
