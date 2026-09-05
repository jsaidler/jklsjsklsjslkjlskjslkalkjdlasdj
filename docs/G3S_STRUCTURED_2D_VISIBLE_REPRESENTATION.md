# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A NATIVE SD1.5 PIXEL REAUTHOR READY**

## Why G3S exists

G3V-R proved deterministic transfer of real CMU motion into the MPFB humanoid. G3V then proved that hidden 3D is useful as motion/topology infrastructure but failed the visible-art kill switch: direct native-raster/palette translation still read as coarse 3D rather than intentional modern pixel art.

Therefore final character pixels must come from persistent structured 2D assets.

Locked target architecture:

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D may own motion, topology, left/right identity, sockets, contacts, depth/occlusion, physics and semantic guides. It may not own final visible color pixels.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting;
- no generic high-resolution beauty render followed by shrink/quantization as final art;
- no bilinear filtering;
- no required Blender/Aseprite/Spine GUI operation by the user;
- recurring production remains scriptable/headless.

# G3S-A — static source sprite gate

Goal: obtain one approved Exilada source image at the locked gameplay presentation:

- canvas `640×360`;
- visible character height about `128 px`;
- lateral/slight-3/4 view facing screen-right;
- lean adult female anatomy;
- very long heavy black hair;
- degraded asymmetric beige cloth;
- wrist/ankle restraints;
- bare feet;
- no weapon;
- intentional modern pixel clusters at native 1×;
- recognizably derived from `assets/source/characters/exilada/reference/exilada_master.png`.

# Qwen source experiment — CLOSED

Qwen-Image-Edit-2509 was tested only as a bounded static-source experiment. It remains forbidden as independent animation-frame generator.

## V1 — INVALID / HARNESS FAIL

The first completed Qwen run produced an almost-black result. Inspection found the API graph differed materially from the official ComfyUI Qwen 2509 blueprint: primary conditioning image and sampled latent did not match, `CFGNorm` was missing, negative conditioning was wired differently and sampling settings mixed separate official presets.

V1 is therefore not a model-quality verdict.

## V2 — DIRECT NATIVE 640×360 FAIL

Workflow revision:

`QWEN2509_OFFICIAL_ALIGNED_NATIVE_V2`

V2 corrected the graph and completed inference normally, but the saved native `640×360` output genuinely collapsed to a near-uniform image.

Measured evidence:

- size: `640×360`;
- SHA256: `a5ecaf9db68fbb8370280c4b6c61a727aa5cd191134d6f508a34207f4c8d157e`;
- mean luma: `70.3017`;
- p99 luma: `71`;
- target mean luma: `70.2322`;
- target p95 luma: `71`;
- target stddev: `0.4336`.

Therefore the direct native Qwen route is rejected. No seed/prompt/threshold rescue is permitted.

## Official-resolution control — PASS AS MODEL-FUNCTION CONTROL / NOT ART ELIGIBLE

The final control restored `FluxKontextImageScale`, matching the official preferred-resolution behavior. It produced a coherent full-body Exilada-like woman rather than collapse.

Uploaded control facts:

- output size: **`1392×752`**;
- coherent adult female anatomy with two arms/two legs;
- long dark hair, degraded beige cloth and bare feet are readable;
- the image is conventional high-resolution illustration/pseudo-pixel styling, not native gameplay pixel art;
- it is **not eligible as final sprite art and must never be promoted by simple shrink/quantization**.

Conclusion:

**Qwen itself works, but Qwen is rejected as the direct native G3S-A sprite generator.** The native route collapsed; the working route requires a high-resolution raster outside the locked production representation.

Qwen may remain only as a provenance/reference source for a later native re-authoring stage. No additional Qwen generation will be attempted for this gate.

# G3S-A native re-author — CURRENT

The next bounded test separates the two problems:

1. Qwen has already supplied a coherent high-resolution identity/composition reference;
2. a second model must actually author the final pixels **directly at `640×360`**, rather than shrink the Qwen pixels.

Chosen spike: **Stable Diffusion 1.5 + a dedicated SD1.5 pixel-art LoRA, img2img at native raster**.

Why this is materially different from the rejected high-res-shrink route:

- the Qwen control image is resized only to create a conditioning/latent guide;
- the guide is not final art;
- SD1.5 resamples/re-authors the image through diffusion at exactly `640×360`;
- the final generated image is never post-resized;
- a 32-color same-raster version exists only for inspection.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_a_sd15_native_reauthor.py`
- `tools/structured-2d-character-pipeline/03_bootstrap_and_run_g3s_a_sd15_native.ps1`

Input control source:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_sd15`

Pinned new model payload:

- Stable Diffusion 1.5 `v1-5-pruned-emaonly.safetensors` — about `4.27 GB`, SHA256 `6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa`;
- SedatAl SD1.5 pixel-art LoRA — about `3.23 MB`, SHA256 `ad5034703699e910d5f9525ea5db64abcbd8d7396ff8f771c09403f3adb048ad`.

The existing isolated ComfyUI runtime is reused. No new runtime is installed.

Locked first test:

- source figure automatically isolated from the Qwen control;
- conditioning-only guide placed at approximately `128 px` visible height on `640×360`;
- SD1.5 img2img generation directly at `640×360`;
- pixel-art LoRA strength `1.0`;
- fixed seed `20260905`;
- `30` steps;
- CFG `6.0`;
- DPM++ 2M / Karras;
- denoise `0.72`;
- no final resize.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_sd15\g3s_a_sd15_contact_sheet.png`

Review order:

1. topology integrity: one head/torso, two arms/hands, two legs/feet;
2. Exilada identity/design continuity;
3. approximately 128 px gameplay scale;
4. intentional native 1× pixel cluster language rather than a tiny smooth illustration;
5. long hair / degraded cloth / restraints / bare-foot readability.

Kill rule:

If this single native re-author candidate still reads as smooth/pseudo-pixel diffusion art rather than intentional pixel clusters, reject this SD1.5 source route too. Do not start seed fishing or parameter sweeps.

# G3S-B — persistent part decomposition

Blocked until one static native source is approved. The future source is decomposed into stable side-aware 2D parts: head/face, torso/pelvis, upper/lower limbs and hands/feet, hair masses, cloth pieces and wrist/ankle restraints. Parts own IDs, side, pivots, depth rules, palette/material families and attachment inheritance.

# G3S-C — four-phase walk proof

Blocked until G3S-B. Persistent parts will be driven by validated motion frames `1568,1588,1608,1628` using deterministic pixel-aware transforms/deformation and depth ordering. No frame may be independently regenerated by diffusion.

## G3S PASS criteria

- static source reads as intentional modern pixel art at 1×;
- major topology and left/right ownership remain stable;
- motion/grounding matches G2/G3V-R;
- hair/cloth/restraints remain persistent;
- joints avoid puppet gaps/rubbery collapse;
- authored clusters survive movement;
- recurring production remains headless/reproducible.

## G4 rescope

After G3S passes, G4 becomes the Exilada production 2D identity system: canonical sprite parts, palette/material families, hair/cloth/restraint variants, sockets/occlusion metadata and damage-ready layers.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\03_bootstrap_and_run_g3s_a_sd15_native.ps1"
```

The first run downloads about `4.27 GB` plus a small LoRA, then executes one native candidate.

Then STOP. If it reaches `G3S-A SD15: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_sd15\g3s_a_sd15_contact_sheet.png`

If it fails, share the complete console output. Do not start G3S-B or G4.
