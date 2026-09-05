# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A ALUCARD NATIVE-128 RESEARCH PROOF READY**

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

- gameplay canvas `640×360`;
- visible character height about `128 px`;
- lateral/slight-3/4 presentation facing screen-right;
- lean adult female anatomy;
- very long heavy black hair;
- degraded asymmetric beige cloth;
- wrist/ankle restraints;
- bare feet;
- no weapon;
- intentional modern pixel clusters at native 1×;
- recognizably derived from `assets/source/characters/exilada/reference/exilada_master.png`.

# Closed source experiments

## Qwen direct-native — FAIL / CLOSED

Corrected Qwen-Image-Edit-2509 inference at native `640×360` completed normally but produced a genuinely flat raster. The official-resolution control at `1392×752` produced a coherent Exilada-like woman and therefore proved the model/runtime works, but that high-resolution illustration/pseudo-pixel result is **reference only** and may never be promoted by simple shrink/quantization.

Qwen remains forbidden as independent animation-frame generator.

## SD1.5 native latent re-author — FAIL / CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_sd15_failure.json`

The bounded SD1.5 + pixel-art LoRA run sampled final pixels directly at `640×360` with no post-inference resize. It produced a coarse vertical block/mannequin and lost Exilada identity, long hair, degraded cloth, restraints, hands and feet. Do not seed-fish or tune this route further.

## PixelLock native-grid source — FAIL / CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_pixellock_failure.json`

Recorded run:

- upstream code commit `bb682f9919fcd302eaa5226b7e6965dfdf151beb`;
- model revision `d35e3bcc3c8651603393042df4dbf2a1d37173ea`;
- `64×64` conditioning scaffold -> grammar-constrained `128×128` output;
- completion tokens `16695`;
- latency `626.5 s`;
- parser PASS;
- `footprint_perfect == true`;
- raw SHA256 `a77348f93b795eff1371d3960a9c23693b1667f20aa5c621ef795916e861858b`;
- visible height `124 px`;
- opaque pixels `3416`;
- **unique opaque RGB colors: `1`**;
- only opaque RGB value: `[99, 9, 25]`.

Visual verdict: a monochrome silhouette, not an authored character.

Architectural lesson: PixelLock's hard GBNF footprint lock is useful only **after** a good canonical sprite footprint exists. In the tested 2× mode every transparent/opaque location is inherited from the scaffold by construction; it cannot repair or invent the source silhouette. It is therefore rejected as G3S-A source generator, but may return later as a footprint-safe recolor/restyle tool after canonical assets exist.

No PixelLock prompt, palette, temperature, seed or upscale tuning is permitted for G3S-A.

# Alucard native-128 sprite proof — CURRENT

This next test changes the model class and native representation instead of tuning another failed route.

Alucard is a small purpose-built text-to-sprite flow-matching model whose **native input/output is `128×128 RGBA`**. It has an optional `128×128 RGBA` reference input and generates a new sprite rather than locking the reference footprint. This directly addresses the structural failure of PixelLock while remaining on the target sprite raster.

Pinned code:

- upstream: `evilsocket/alucard`;
- code commit: `02d1c60a16142015f7838a6a033da5e6ac9ce4f7`;
- architecture: ~32M-param U-Net / rectified flow;
- output: native `128×128 RGBA`;
- default bounded sampling used here: 20 Euler ODE steps, text CFG `5.0`, reference CFG `2.0`;
- fixed seed: `20260905`.

Model reference:

- Hugging Face `evilsocket/alucard`;
- weight file `alucard_model.safetensors`, about `128 MB`;
- pinned weight revision used by the runner: `b8e7602`;
- the runner records the downloaded weight SHA256 on first provisioning and requires it on reuse.

Conditioning contract:

1. The coherent high-resolution Qwen control remains **design/pose conditioning only**.
2. It is background-isolated and normalized to a transparent `128×128 RGBA` reference.
3. That reference is not final art and is allowed to use nearest-neighbor normalization because only the Alucard output can become candidate art.
4. Alucard samples a brand-new `128×128 RGBA` sprite directly at the target asset raster.
5. There is **no post-generation resize**.
6. The native sprite is composited 1:1 into the `640×360` gameplay preview.
7. Only one fixed-seed candidate is generated.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_a_alucard_native.py`
- `tools/structured-2d-character-pipeline/05_bootstrap_and_run_g3s_a_alucard.ps1`

Dependency workspace:

`Z:\AI\AlucardSpike`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_alucard`

## Harness correction — 2026-09-05

The first invocation stopped during the dependency import probe **before model download or Alucard inference**. This was a runner bug, not an Alucard/model failure: Windows PowerShell 5.1 converted the expected Python stderr from a failed first-pass import probe into a terminating `NativeCommandError` because `$ErrorActionPreference='Stop'`, so the script never reached its intended dependency-install branch.

Fixed in commit `5d65039e406a4d3c01ce0dad37e51578cffa4a4e`: all Python probe/pip/helper calls now go through `Invoke-PythonSafe`, which temporarily disables stderr-to-terminating-error behavior and uses the native process exit code as the authority. If the post-install import still fails, the exact Python traceback is printed deliberately.

This correction does **not** alter Alucard sampling parameters or gate criteria.

## License boundary — HARD

Alucard uses FAIR License 1.0.0, not a permissive MIT/Apache production license. The published license permits non-commercial personal/research use; commercial use requires visible attribution, and Business Use requires a separate signed commercial agreement with the author.

Therefore this gate is **research/architecture proof only**. A visually successful result does **not** automatically approve Alucard for shipping. Before any Alucard-generated production asset is adopted, the project's intended distribution/entity status must be checked against that license and, if Business Use applies, a written commercial agreement is required.

## Review order

1. topology: exactly one head/torso, two arms/hands, two legs/feet;
2. Exilada identity: dominant long black hair, olive-brown skin, degraded beige cloth, wrist/ankle restraints, bare feet;
3. native pixel language: deliberate 1× clusters rather than smooth/pseudo-pixel rendering;
4. gameplay readability when composited 1:1 on `640×360`;
5. only after visual PASS: resolve licensing before adoption.

## Kill rule

One candidate only. If this purpose-built native `128×128` model cannot produce a credible identity-bearing Exilada sprite from the fixed reference/prompt, close the automated local generative-source route rather than tuning seeds/CFG/prompts indefinitely. At that point G3S-A must be re-scoped as an authored canonical-source problem rather than another model search.

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
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\05_bootstrap_and_run_g3s_a_alucard.ps1"
```

Then STOP. If it reaches `G3S-A ALUCARD: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_alucard\g3s_a_alucard_contact_sheet.png`

If it fails, share the complete console output. Do not start G3S-B or G4.