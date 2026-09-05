# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-B3B NATIVE 128×128 NUDE BODY SOURCE NEXT**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel assets -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB pixels.

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

Consequences:

- no censor garment is structurally required;
- no hidden body reconstruction is allowed when clothing is removed/damaged;
- chest and pelvic anatomy must be coherent at native gameplay scale;
- presentation may be neutral, sensual, erotic, heroic, brutal or vulnerable according to scene intent; no blanket anti-erotic framing is imposed;
- body wounds/scars/blood/wetness remain attached to body regions;
- sever/dismemberment operates on the same complete body while clothing/equipment inherits or detaches by state rules.

# G3S-B3 — Nude Body Base — CURRENT

Canonical log:

`docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

The master/Qwen composite is reference only. B3 creates a dedicated body asset rather than removing hair/clothes from a composite.

## G3S-B3A V1 — FAIL/CLOSED REVISION

The first guide run produced valid layer/scale mechanics but used `MPFB gender = 1.0`, which resolves male in the pinned MPFB semantics. This was a revision error, not a route/model rejection.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3a_v1_failure.json`

MPFB `2.0.17` remains active; no cleanup command applies.

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

B3A is closed. Its lit RGB is never promoted to final art.

## G3S-B3B — ACTIVE

B3B owns the actual native visible body source.

V1 implementation rules:

- native canvas `128×128`;
- body stays at approximately the locked `128 px` gameplay height;
- B3A binary mask and projected joints are structural guides only;
- no B3A lit RGB/shading is sampled or transferred;
- visible RGB is authored by explicit native palette and pixel-cluster rules;
- binary alpha;
- no hair, clothing, binding, restraint or chain pixels;
- deterministic source, mask, gameplay preview, manifest and contact sheet;
- visual review at 1× is mandatory before promotion.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_b3b_native_body_source.py`
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_native_body_source.ps1`

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_native_body_source\g3s_b3b_contact_sheet.png`

# G3S-B4 — Hair

Blocked until B3B body approval.

# G3S-B5 — Clothing / restraints / chains

Blocked until B3B body approval.

# G3S-C — Four-phase walk proof

Blocked until B3/B4/B5 are structurally correct.
