# Roguelite — Current Project State

Status date: **2026-09-05**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
7. `docs/ANIMATION_SOURCE_LIBRARY.md`
8. `docs/PHYSICAL_INTERACTION_VFX_GORE.md`
9. `docs/PIXEL_ART_PRODUCTION.md`
10. `docs/ANIMATION_PIPELINE.md`
11. `docs/G0_AUTOMATION_LOG.md`
12. `docs/G1_CAMERA_SCALE_LOG.md`
13. `docs/G2_MOTION_TOPOLOGY_LOG.md`
14. `docs/G3_PIXEL_TRANSLATION_LOG.md`
15. `docs/G3R_RENDERER_REFINEMENT_LOG.md`
16. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
17. `docs/G3V_RETARGET_PREFLIGHT_LOG.md`
18. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`

After every material step: update relevant thematic docs + this file and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: elevated 2D belt-scroller / false 3D.

Final visible language remains **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines identity/design, not final gameplay pixels.

## Hard operator constraint

Normal production must remain scriptable/headless. The user must not need routine Blender/Aseprite/rigging operation, frame-by-frame repainting or a hired specialist.

## Rejected / closed routes

- FLUX.2 Klein + RefControl direct-frame animation — REJECTED/FROZEN after topology drift and a three-leg frame;
- direct per-frame diffusion as animation owner — REJECTED;
- high-resolution beauty render + generic shrink/pixel filter — REJECTED as final-art route;
- primitive mannequin renderer tuning — REJECTED after G3R;
- hidden 3D as owner of final visible character color pixels — REJECTED after G3V kill switch;
- raw Blender `Action` copy G2 -> MPFB — REJECTED;
- raw per-frame `matrix_basis` copy — REJECTED;
- local-axis `REST_COMPENSATED_FK` — REJECTED;
- MPFB pose API for this source/target pair — REJECTED;
- Qwen-Image-Edit-2509 direct native `640×360` generation — REJECTED after flat collapse;
- **SD1.5 + pixel-art LoRA direct native `640×360` re-author — REJECTED after block/mannequin identity collapse.**

Qwen official-resolution generation is retained only as a one-time design/pose reference. It cannot be resized/quantized into final art and remains forbidden as independent animation-frame owner.

## Active architecture — LOCKED

`camera/scale -> real motion -> deterministic hidden topology -> DIRECTION_SPACE_FK -> projected joints/depth/sockets -> persistent structured 2D pixel assets -> deterministic 2D composition/deformation -> sprite/runtime export -> QA`

Hidden 3D owns control/infrastructure only: motion, topology/left-right identity, sockets, contacts/root data, physics, depth/occlusion, semantic guides and secondary-motion drivers.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3 first native translation — TECHNICAL PASS / LOOK NOT APPROVED
- G3R primitive renderer refinement — FAIL/CLOSED
- G3V representative continuous human visual proxy — FAIL/CLOSED
  - G3V-R retarget preflight — PASS/CLOSED
- **G3S structured 2D visible representation** ← ACTIVE
  - G3S-A static source — ACTIVE
    - Qwen V1 harness — INVALID/CLOSED
    - Qwen V2 native `640×360` — FAIL/CLOSED
    - Qwen official-resolution control — PASS AS MODEL-FUNCTION CONTROL / CLOSED
    - SD1.5 native re-author — FAIL/CLOSED
    - **PixelLock native pixel-grid source** ← READY TO RUN
  - G3S-B persistent part decomposition — BLOCKED
  - G3S-C four-phase walk proof — BLOCKED
- G4 Exilada production 2D identity system — BLOCKED UNTIL G3S PASS
- G5 temporal stress pack
- G6 equipment/attachments
- G6A wind/secondary motion
- G6B liquid/contact VFX
- G6C gore topology
- G6D clothing/armor damage
- G7 systemic state/dynamic lighting
- G8 production scaling

# Validated history

## G0 — PASS

Windows 11 + Blender 5.1.1 headless automation validated.

## G1 — PASS

Locked `640×360`, orthographic pitch `26 deg`, protagonist visible reference height `128 px`.

## G2 — PASS

CMU `105_34 NormalWalk`, 120 fps. Real locomotion basis, major-limb topology, left/right alternation and deterministic structure validated.

## G3 / G3R

G3 proved deterministic native-grid processing technically possible but not production-looking. G3R proved renderer-only refinement cannot invent authored 2D form from a primitive source.

## G3V-R — PASS

Accepted retarget: **`DIRECTION_SPACE_FK`**.

Measured facts: `0` parent mismatches; mean rest-orientation difference `83.1874 deg`, max `180.0289 deg`; 4 unique target poses; mean elbow/knee error `0.0000 deg`, max `0.0001 deg`; rest-independent chain-shape metric passed; source/target skeleton sheet visually passed.

Marker: `tools/deterministic-character-pipeline/g3v_retarget_approval.json`.

## G3V — FAIL

Representative MPFB body animated coherently after validated retarget, but native semantic/palette output still read as coarse 3D rather than deliberate modern pixel art. Hidden 3D therefore remains infrastructure only.

Failure marker: `tools/deterministic-character-pipeline/g3v_failure.json`.

# G3S — current

Canonical design:

`docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`

Goal: final pixels come from persistent 2D assets while hidden motion/topology supplies deterministic control.

## Qwen source experiment — CLOSED

### Direct native `640×360` — FAIL

The corrected Qwen graph completed normally but produced a flat native output:

- SHA256 `a5ecaf9db68fbb8370280c4b6c61a727aa5cd191134d6f508a34207f4c8d157e`;
- mean luma `70.3017`;
- p99 `71`;
- target stddev `0.4336`.

### Official-resolution control — PASS AS CONTROL / CLOSED

Restoring Qwen's preferred-resolution preprocessing produced a coherent `1392×752` Exilada-like woman. That proves the model/runtime functions, but the result is high-resolution illustration/pseudo-pixel styling and is not final-art eligible.

The Qwen control remains at:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

It may supply one-time pose/design conditioning only.

## SD1.5 native re-author — FAIL / CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_sd15_failure.json`

The bounded native run sampled final pixels directly at `640×360` using SD1.5 + pixel-art LoRA, seed `20260905`, 30 steps, CFG 6, DPM++ 2M/Karras, denoise 0.72, no final resize.

Evidence:

- conditioning subject `48×128`;
- raw SHA256 `294a412ffc0aa859c7fdf4128b13755e1e89fec4f3ea1d96c63e735a10ed92b0`;
- result was a coarse block/mannequin;
- Exilada identity, long hair, degraded cloth, restraints, hands and feet did not survive at production quality.

Conclusion: do not tune SD1.5, LoRA, seed or prompt further. Standard image-latent diffusion at the full gameplay canvas is rejected for this tiny identity-rich sprite source problem.

# G3S-A PixelLock native-grid — CURRENT

This test changes representation rather than diffusion parameters.

PixelLock serializes small pixel sprites as palette-indexed text grids and uses a per-sprite llama.cpp GBNF grammar to lock the silhouette/alpha footprint. The model authors discrete grid cells instead of an 8×-compressed image latent.

Pinned components:

- PixelLock code commit `bb682f9919fcd302eaa5226b7e6965dfdf151beb` (MIT code);
- PixelLock Gemma-4 12B pixel-art GGUF Q4_K_M, ~7.38 GB;
- model revision `d35e3bcc3c8651603393042df4dbf2a1d37173ea`;
- llama.cpp `b10516`, Windows CUDA 12.4;
- llama main ZIP SHA256 `96d64faeb5b8e655341f32b26ad3e51fbea8bff0bc8120ad3dbffdc0b05b8ad3`;
- CUDA runtime ZIP SHA256 `8c79a9b226de4b3cacfd1f83d24f962d0773be79f1e7b75c6af4ded7e32ae1d6`.

Representation test:

`Qwen control -> 64×64 transparent conditioning scaffold (~62 px person) -> PixelLock grammar-constrained 2× generation -> 128×128 pixel asset -> 640×360 gameplay preview`

The generated 128×128 grid is **not a post-generation resize**. PixelLock's 2× mode samples the output cells while grammar guarantees the exact scaled footprint. Hard checks require `footprint_perfect`, exact `128×128` output, visible height `116–128 px`, and no post-generation resize.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_a_pixellock_native.py`
- `tools/structured-2d-character-pipeline/04_bootstrap_and_run_g3s_a_pixellock.ps1`

Dependency workspace:

`Z:\AI\PixelLockSpike`

Output:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_pixellock`

First run downloads approximately `7.4 GB` for the PixelLock model plus the pinned llama.cpp CUDA runtime. The runner automatically retries lower GPU-layer offload if full offload does not start on the RTX 3060 12 GB.

Kill rule: one candidate only. If the footprint-locked model merely recolors a coarse scaffold and cannot make an identity-bearing Exilada sprite with intentional clusters, close this source route without prompt/temperature fishing.

## Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\04_bootstrap_and_run_g3s_a_pixellock.ps1"
```

Then STOP. If it reaches `G3S-A PIXELLOCK: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_pixellock\g3s_a_pixellock_contact_sheet.png`

If it fails, share the complete console output. Do not run G3S-B or G4.

## Workspace

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- hidden deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- Qwen runtime/reference: `Z:\AI\QwenImageEditSpike`
- PixelLock dependency workspace: `Z:\AI\PixelLockSpike`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
