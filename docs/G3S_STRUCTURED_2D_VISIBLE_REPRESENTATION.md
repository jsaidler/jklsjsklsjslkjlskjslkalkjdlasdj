# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A V2 READY TO RUN**

## Why G3S exists

G3V-R proved that real CMU motion can be transferred deterministically into the MPFB humanoid without topology collapse. The final G3V body rerun then proved that this technical backbone is stable enough to animate a representative human.

However the G3V visual kill switch failed: the native semantic/palette output still read as conventional 3D made coarse/blocky rather than intentional modern pixel art.

Therefore hidden 3D remains infrastructure only. Ownership of final visible character pixels moves to a persistent structured 2D representation.

Canonical G3V failure marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

## Locked architecture

Hidden 3D may own real motion, persistent topology/left-right identity, sockets, root/contact data, physics proxies, depth/occlusion guides, semantic/body-part guides and secondary-motion driving data.

Hidden 3D may **not** own final visible color pixels by direct render/palette translation.

Target architecture:

`real motion -> validated hidden rig -> projected 2D joints/depth -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

The visible representation is a 2D asset system, not a frame generator.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting;
- no generic high-resolution beauty render followed by shrink/quantization as final art;
- no bilinear filtering;
- no arbitrary bitmap rotations without pixel-aware rules;
- one-time source-art creation/decomposition is acceptable if recurring production becomes deterministic;
- no required Blender/Aseprite/Spine GUI operation by the user;
- recurring production remains scriptable/headless.

# G3S-A — static source sprite gate

Before attempting animation, create **one approved gameplay-scale Exilada source image**.

Requirements:

- native canvas `640×360`;
- visible character height approximately `128 px`;
- lateral/slight-3/4 gameplay presentation facing screen-right;
- lean adult female anatomy;
- severe readable head silhouette;
- dominant very long black hair mass;
- degraded asymmetric beige cloth;
- wrist and ankle restraints;
- bare feet;
- no weapon;
- intentional modern pixel clusters at native 1×;
- recognizably derived from `assets/source/characters/exilada/reference/exilada_master.png`.

Qwen-Image-Edit-2509 is permitted here **only as a one-time static source-art candidate**. It remains forbidden as independent per-frame animation owner.

Runtime workspace:

`Z:\AI\QwenImageEditSpike`

Pinned model set:

- `Qwen-Image-Edit-2509-Q4_0.gguf` — ~11.9 GB;
- `qwen_2.5_vl_7b_fp8_scaled.safetensors` — ~9.38 GB;
- `qwen_image_vae.safetensors` — ~0.25 GB.

One-command provisioning/runner:

`tools/structured-2d-character-pipeline/00_bootstrap_and_run_g3s_a.ps1`

Inference-only runner:

`tools/structured-2d-character-pipeline/01_run_g3s_a.ps1`

## G3S-A V1 — INVALID INFERENCE / NOT A VISUAL VERDICT

The first completed inference produced an almost-black frame and therefore was not a meaningful Exilada candidate. The uploaded contact sheet showed the raw and 32-color panels essentially collapsed to black with only faint structure.

This is **not** recorded as a Qwen visual FAIL because inspection of the API graph found implementation errors in the test harness.

V1 graph errors relative to the official ComfyUI Qwen 2509 blueprint:

1. conditioning `image1` was the Exilada master while `latent_image` was encoded from the layout guide; the official graph uses the same primary image for both;
2. the model path omitted `CFGNorm` after `ModelSamplingAuraFlow`;
3. negative conditioning did not receive the same image references/VAE structure as positive conditioning;
4. V1 used `20 steps / CFG 4.0`; the official ComfyUI blueprint documents non-Lightning "Comfy Original" settings as `20 / 2.5` (Qwen Team reference `50 / 4.0`, Lightning `4 / 1.0`).

Relevant upstream evidence:

- official ComfyUI blueprint `blueprints/Image Edit (Qwen 2509).json` at commit `250b2e9551a7bc7a8ebb5beb07e0fecd2983e04a`;
- official `TextEncodeQwenImageEditPlus` implementation in `comfy_extras/nodes_qwen.py`;
- official `CFGNorm` node in `comfy_extras/nodes_cfg.py`.

## G3S-A V2 — CURRENT

New helper:

`tools/structured-2d-character-pipeline/g3s_a_static_source_v2.py`

Locked workflow revision:

`QWEN2509_OFFICIAL_ALIGNED_NATIVE_V2`

V2 uses:

- Picture 1 = generated `640×360` pose/placement/scale guide;
- **the same Picture 1 is VAE-encoded as `latent_image`**;
- Picture 2 = exact canonical `exilada_master.png` identity/design reference;
- positive and negative `TextEncodeQwenImageEditPlus` both receive Picture 1, Picture 2 and the VAE;
- `UnetLoaderGGUF -> ModelSamplingAuraFlow(shift=3.0) -> CFGNorm(strength=1.0) -> KSampler`;
- `20` steps, CFG `2.5`, Euler/simple, denoise `1.0`;
- fixed seed `20260905`;
- no post-inference resize.

The official blueprint normally passes the primary image through `FluxKontextImageScale`, which maps it to a preferred ~1MP raster. G3S-A V2 intentionally omits only that scaling node because this gate specifically tests whether a true `640×360` output can exist without later shrinking. The Qwen conditioning node may still internally resize references for vision/reference-latent encoding, but the output latent itself remains the native `640×360` guide.

### Invalid-output guard

V2 now performs a loose automatic luma/dynamic-range sanity check on the raw `640×360` inference before producing `REVIEW_REQUIRED`.

A near-black/flat output is saved for diagnosis and marked `FAIL_INVALID_INFERENCE`; it is **not** presented again as a visual-review candidate.

Only a non-collapsed raw output proceeds to:

- `g3s_a_qwen_raw.png`;
- `g3s_a_same_raster_32color.png` — inspection only, no resize;
- `g3s_a_contact_sheet.png`;
- `g3s_a_result.json` with status `REVIEW_REQUIRED`.

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a`

## G3S-A review order

1. topology integrity: one head/torso, two arms/hands, two legs/feet;
2. Exilada identity/design continuity;
3. gameplay angle and approximately 128 px scale;
4. native 1× pixel-art shape/value cluster language;
5. hair / cloth / restraint / bare-foot readability.

A candidate does not pass merely because an enlarged zoom looks attractive.

## G3S-A kill rule

If a technically valid V2 output still reads as conventional illustration, blocky 3D, or pseudo-pixel art at native 1×, do not decompose or animate it. Reassess the static visible-source method first.

# G3S-B — persistent part decomposition

Only after one static source is approved, decompose it into persistent side-aware 2D parts: head/face, torso/pelvis, upper/lower limbs and hands/feet per side, large hair masses, cloth pieces and wrist/ankle restraints.

Each part owns stable ID, anatomical side, pivots, depth rules, material/palette family and attachment inheritance.

# G3S-C — four-phase walk proof

Drive persistent parts from validated motion frames:

`1568, 1588, 1608, 1628`

Allowed operations include integer translation, constrained pixel-aware rotation/warp, deterministic local mesh deformation, authored joint-cover patches and deterministic depth ordering. No frame may be independently regenerated by diffusion.

## G3S PASS criteria

G3S passes only if the static source reads as intentional modern pixel art at 1×, major topology and side ownership remain stable through the four gait phases, motion/grounding corresponds to G2/G3V-R, hair/cloth/restraints remain persistent, joints avoid obvious puppet gaps/rubbery deformation, authored pixel clusters survive motion and recurring production remains headless/reproducible.

## G4 rescope

After G3S passes, G4 becomes **Exilada production 2D identity system**: canonical sprite parts, palette/material families, hair/cloth/restraint variants, sockets/occlusion metadata and damage-ready layers.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\00_bootstrap_and_run_g3s_a.ps1"
```

The runtime/models are already provisioned, so this should reuse them and go directly to the V2 inference.

Then STOP. If it reaches `G3S-A: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a\g3s_a_contact_sheet.png`

If it fails, share the complete console output. Do not start G3S-B or G4 yet.
