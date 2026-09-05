# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **ACTIVE — G3S-A READY TO RUN**

## Why G3S exists

G3V-R proved that real CMU motion can be transferred deterministically into the MPFB humanoid without topology collapse. The final G3V body rerun then proved that this technical backbone is stable enough to animate a representative human.

However the G3V visual kill switch failed: the native semantic/palette output still read as conventional 3D made coarse/blocky rather than intentional modern pixel art.

Therefore hidden 3D remains infrastructure only. Ownership of final visible character pixels moves to a persistent structured 2D representation.

Canonical failure marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

## Locked architecture

Hidden 3D may own:

- real motion;
- persistent topology and left/right identity;
- attachment sockets;
- root/contact data;
- physics proxies;
- depth/occlusion guides;
- semantic/body-part guides;
- secondary-motion driving data.

Hidden 3D may **not** own final visible color pixels by direct render/palette translation.

Target architecture:

`real motion -> validated hidden rig -> projected 2D joints/depth -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

The visible representation is a 2D asset system, not a frame generator.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting;
- no generic high-resolution render followed by shrink/quantization;
- no bilinear filtering;
- no arbitrary bitmap rotations without pixel-aware rules;
- one-time source-art creation/decomposition is acceptable if recurring production becomes deterministic;
- no required Blender/Aseprite/Spine GUI operation by the user;
- recurring production remains scriptable/headless.

# G3S-A — static source sprite gate

Before attempting animation, create **one approved gameplay-scale Exilada source image** in the locked G1 presentation family.

Required characteristics:

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
- true intentional modern pixel clusters at native 1×;
- no anti-aliased pseudo-pixel edges or smooth 3D shading logic;
- recognizably derived from `exilada_master.png`.

## G3S-A source route — LOCKED FOR THIS SPIKE

Qwen-Image-Edit-2509 returns **only as a constrained one-time static source-art candidate**. The temporal-consistency objection that paused Qwen no longer applies to this specific test because it generates no animation frames.

Runtime reused from:

`Z:\AI\QwenImageEditSpike`

Pinned local model set already expected there:

- `Qwen-Image-Edit-2509-Q4_0.gguf`;
- `qwen_2.5_vl_7b_fp8_scaled.safetensors`;
- `qwen_image_vae.safetensors`.

The G3S-A runner downloads **nothing**. If these existing files are absent it fails rather than silently downloading ~large model dependencies.

Tooling:

- `tools/structured-2d-character-pipeline/01_run_g3s_a.ps1`
- `tools/structured-2d-character-pipeline/g3s_a_static_source.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_a`

## G3S-A deterministic test contract

The one-shot test uses:

- canonical `exilada_master.png` as Picture 1 / identity-design source;
- a generated `640×360` abstract pose/scale guide as Picture 2;
- fixed seed `20260905`;
- Qwen edit canvas driven directly at `640×360`;
- target figure envelope ≈`128 px`;
- `20` steps, CFG `4.0`, Euler/simple, denoise `1.0`;
- explicit topology instruction: exactly one head/torso, two arms/hands, two legs/feet;
- explicit visual instruction for modern native pixel-art clusters rather than blocky 3D;
- no post-inference resize.

A 32-color quantized version is generated **at the same 640×360 raster for inspection only**. It is not automatically promoted as production art and does not resize or repair anatomy.

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_a\g3s_a_contact_sheet.png`

The contact sheet contains:

1. pose/scale guide — control only, not art;
2. raw Qwen output at native `640×360`;
3. same-raster 32-color inspection image;
4. nearest-neighbor zoom of the target gameplay area for pixel-cluster inspection.

## G3S-A review order

1. topology integrity: one head/torso, two arms/hands, two legs/feet;
2. Exilada identity/design continuity;
3. gameplay angle and approximately 128 px scale;
4. native 1× pixel-art shape/value cluster language;
5. hair / cloth / restraint readability.

A candidate does not pass merely because it is attractive at enlarged zoom.

## G3S-A kill rule

If the fixed static candidate still reads as conventional high-resolution/soft illustration, blocky 3D, or pseudo-pixel art after same-raster inspection, do not animate it and do not decompose it. Reassess the static visible-source method first.

Qwen remains forbidden as independent per-frame animation generator regardless of G3S-A result.

# G3S-B — persistent part decomposition

Only after one static source is approved, decompose it into persistent 2D pieces, for example:

- head/face;
- torso/pelvis;
- upper/lower arms and hands per side;
- upper/lower legs and feet per side;
- large hair masses;
- degraded cloth pieces;
- wrist/ankle metal restraints.

Each part owns stable ID, anatomical side, pivots, depth rules, material/palette family and attachment inheritance.

# G3S-C — four-phase walk proof

Drive persistent parts from validated motion frames:

`1568, 1588, 1608, 1628`

Allowed operations include integer translation, constrained pixel-aware rotation/warp, deterministic local mesh deformation, authored joint-cover patches and deterministic depth ordering.

No frame may be independently regenerated by diffusion.

## G3S PASS criteria

G3S passes only if:

1. static source reads as intentional modern pixel art at 1×;
2. major topology remains stable across the four gait phases;
3. left/right ownership remains stable;
4. motion/grounding corresponds to G2/G3V-R;
5. hair, cloth and restraints remain persistent;
6. joints avoid obvious cutout gaps or rubbery deformation;
7. authored pixel clusters survive movement;
8. production after source approval remains headless/reproducible.

## G4 rescope

After G3S passes, G4 becomes **Exilada production 2D identity system**: approved source sprite/parts, palette/material families, hair/cloth/restraint variants, sockets/occlusion metadata and damage-ready layering.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\01_run_g3s_a.ps1"
```

Then STOP. If the runner reaches `G3S-A: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a\g3s_a_contact_sheet.png`

If it fails, share the complete console output. Do not start G3S-B or G4 yet.
