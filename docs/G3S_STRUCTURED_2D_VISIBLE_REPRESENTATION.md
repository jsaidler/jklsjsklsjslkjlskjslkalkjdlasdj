# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A1 FACIAL / ANATOMY LOCK V2 READY**

## Why G3S exists

G3V-R proved deterministic transfer of real CMU motion into the humanoid control rig. G3V then proved that hidden 3D is useful as motion/topology infrastructure but fails as owner of final visible pixel art.

Locked production architecture:

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D may own motion, topology, left/right identity, sockets, contacts, depth/occlusion, physics and semantic guides. It may not own final visible color pixels.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI operation by the user;
- no generic beauty-render shrink/pixel-filter route as final production method;
- no bilinear filtering;
- recurring production remains scriptable/headless;
- one-time native source authoring may use explicit deterministic pixel edits;
- future animation must consume persistent structured assets rather than regenerate frames;
- anatomical details are gate-critical: a feature must read semantically, not merely exist as pixels.

## Model-discard cleanup rule — LOCKED

Whenever a model/route is declared **FAIL/CLOSED/REJECTED** and no longer required, the same response must include exact PowerShell cleanup commands for its model-specific files. Shared runtimes still in use are preserved; small result/log evidence remains unless explicitly removed.

### Alucard

```powershell
Remove-Item -LiteralPath "Z:\AI\AlucardSpike" -Recurse -Force -ErrorAction SilentlyContinue
```

### PixelLock

```powershell
Remove-Item -LiteralPath "Z:\AI\PixelLockSpike" -Recurse -Force -ErrorAction SilentlyContinue
```

### SD1.5 native re-author

```powershell
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\checkpoints\v1-5-pruned-emaonly.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\loras\pixel-art-sd15.safetensors" -Force -ErrorAction SilentlyContinue
```

### Qwen-Image-Edit-2509 direct sprite route

The fixed control is retained; the shared embedded Python/ComfyUI runtime remains because authored tooling still uses that Python.

```powershell
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\unet\Qwen-Image-Edit-2509-Q4_0.gguf" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\ComfyUI\models\vae\qwen_image_vae.safetensors" -Force -ErrorAction SilentlyContinue
```

# G3S-A — static source sprite gate

Goal: obtain one approved Exilada source image for the locked presentation:

- native asset canvas `128×128` RGBA;
- gameplay canvas `640×360`;
- visible character height about `128 px`;
- lateral/slight-3/4 presentation facing screen-right;
- lean adult female anatomy;
- very long heavy black hair;
- degraded asymmetric beige cloth;
- wrist/ankle restraints and broken chain remnants;
- bare feet;
- no weapon;
- intentional modern pixel clusters at native 1×;
- recognizable Exilada identity derived from the canonical master.

## Automated source search — CLOSED

Bounded architecture probes were completed and closed:

- Qwen direct-native — FAIL;
- Qwen preferred-resolution control — PASS only as design/scaffold provenance;
- SD1.5 + pixel LoRA native re-author — FAIL;
- PixelLock initial-source authoring — FAIL;
- Alucard external-reference attempt — INVALID;
- Alucard text-only native-128 control — FAIL.

Do not start another source-model search.

The retained Qwen control is:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Pinned SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

It is provenance/design scaffold only; it never owns animation frames.

# Authored native source V1 — FAIL / CLOSED

V1 method:

`fixed design scaffold -> native 128×128 base -> explicit mouth/restraint/chain patch`

Visual review showed that the overall body remained coherent but the **mouth still did not read**. The old helper only checked that nominal mouth pixels were opaque, so it incorrectly treated pixel presence as feature readability.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_authored_v1_failure.json`

Lesson: a native anatomical feature must be judged semantically at 1× and in explicit nearest-neighbor diagnostics.

# G3S-A1 — Facial / Anatomy Lock — CURRENT

Detailed canonical log:

`docs/G3S_A1_FACIAL_ANATOMY_LOCK_LOG.md`

## Purpose

Lock static anatomy before any decomposition or animation.

V2 is still deterministic/headless and invokes no image model. It uses the same pinned Qwen scaffold and explicit native-grid authoring data.

## V2 facial changes

Patch:

`tools/structured-2d-character-pipeline/g3s_a_anatomy_patch_v2.json`

Changes include:

- nose/lower-plane separation;
- explicit five-pixel dark mouth opening;
- separate lower-lip row;
- lower-lip center highlight;
- chin separation below the mouth;
- preservation of both wrist cuffs, both ankle cuffs and broken-chain remnants.

## Stronger technical guard

The alpha-only V1 guard is permanently rejected.

V2 checks:

- mouth occupies two distinct semantic rows;
- mouth core has local RGB contrast against surrounding face skin;
- face diagnostic region is present;
- both hand regions are present;
- both foot regions are present;
- candidate remains native `128×128`;
- visual review remains authoritative.

## Diagnostic output

The contact sheet now exposes six views:

1. Qwen design provenance;
2. pre-lock native scaffold;
3. V2 candidate;
4. large nearest-neighbor face diagnostic;
5. separate hands/feet diagnostic;
6. 1:1 gameplay preview.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_a_anatomy_patch_v2.json`
- `tools/structured-2d-character-pipeline/g3s_a1_facial_anatomy_lock.py`
- `tools/structured-2d-character-pipeline/08_run_g3s_a1_facial_anatomy_lock.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a1_anatomy_lock`

## PASS criteria

Review order:

1. one head/torso, two arms/hands, two legs/feet;
2. mouth visibly reads at native 1×;
3. face reads as human rather than undifferentiated skin pixels;
4. hands and feet remain identifiable and plausible;
5. restraints remain on the correct wrists/ankles;
6. Exilada identity remains coherent;
7. gameplay preview remains readable at `640×360`.

If any anatomy item fails, revise the explicit native patch. Do **not** begin animation and do **not** search another image model.

# G3S-B — persistent part decomposition

Blocked until G3S-A1/static source approval. The approved source will be decomposed into stable side-aware parts: head/face, torso/pelvis, upper/lower limbs, hands/feet, hair masses, cloth pieces and restraints. Parts own IDs, side, pivots, depth rules, palette/material families and attachment inheritance.

# G3S-C — four-phase walk proof

Blocked until G3S-B. Persistent parts will be driven by validated motion frames `1568,1588,1608,1628` using deterministic pixel-aware transforms/deformation and depth ordering. No frame may be independently regenerated by diffusion.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\08_run_g3s_a1_facial_anatomy_lock.ps1"
```

Then STOP. If it reaches `G3S-A1: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a1_anatomy_lock\g3s_a1_contact_sheet.png`

Do not start G3S-B, G3S-C or G4 until static anatomy is visually approved.
