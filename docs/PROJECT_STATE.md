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
- SD1.5 + pixel-art LoRA direct native `640×360` re-author — REJECTED after block/mannequin identity collapse;
- **PixelLock as initial G3S-A source generator — REJECTED after a footprint-perfect but single-color 128×128 silhouette.**

Qwen official-resolution generation is retained only as a one-time design/pose reference. It cannot be resized/quantized into final art and remains forbidden as independent animation-frame owner.

PixelLock may return only later as a footprint-safe recolor/restyle tool after a good canonical sprite already exists.

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
    - PixelLock native-grid source — FAIL/CLOSED
    - **Alucard purpose-built native `128×128 RGBA` proof** ← READY TO RUN / RESEARCH ONLY
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

## Qwen direct-native — FAIL / CLOSED

The corrected native Qwen run completed but produced a flat raster. The official-resolution control at `1392×752` is coherent and proves Qwen works, but remains reference-only because high-res shrink/quantization is forbidden.

## SD1.5 native re-author — FAIL / CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_sd15_failure.json`

The one native `640×360` SD1.5 + pixel-LoRA run produced a block/mannequin and lost identity-bearing detail. No further SD1.5 tuning is allowed.

## PixelLock native-grid — FAIL / CLOSED

Failure marker:

`tools/structured-2d-character-pipeline/g3s_a_pixellock_failure.json`

The model completed normally and `footprint_perfect == true`, but the native output had:

- `128×128` raster;
- visible height `124 px`;
- `3416` opaque pixels;
- **exactly one opaque RGB value `[99,9,25]`**;
- raw SHA256 `a77348f93b795eff1371d3960a9c23693b1667f20aa5c621ef795916e861858b`.

This is a monochrome silhouette, not a viable Exilada source. The failure is architectural: PixelLock's hard footprint grammar preserves an existing silhouette; it does not solve initial sprite authorship. Do not tune it for G3S-A.

# G3S-A Alucard native-128 proof — CURRENT

Next runner:

- `tools/structured-2d-character-pipeline/g3s_a_alucard_native.py`
- `tools/structured-2d-character-pipeline/05_bootstrap_and_run_g3s_a_alucard.ps1`

Pinned upstream code commit:

`02d1c60a16142015f7838a6a033da5e6ac9ce4f7`

Alucard is a purpose-built ~32M parameter sprite model whose native input/output is `128×128 RGBA`. Unlike PixelLock it is allowed to change the footprint and generate a new sprite. The coherent Qwen control is converted only into a transparent `128×128` conditioning reference; final Alucard output is independently sampled at `128×128` with no post-generation resize.

Fixed test:

- one candidate only;
- seed `20260905`;
- 20 Euler ODE steps;
- text CFG `5.0`;
- reference CFG `2.0`;
- output exactly `128×128 RGBA`;
- gameplay preview composites it 1:1 into `640×360`.

Dependency workspace:

`Z:\AI\AlucardSpike`

Output:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_alucard`

### Harness correction

The first invocation stopped before model download or inference during the expected first-pass dependency probe. This was a runner bug: Windows PowerShell 5.1 promoted Python stderr to a terminating `NativeCommandError` under `$ErrorActionPreference='Stop'`, so the intended install branch never ran. Commit `5d65039e406a4d3c01ce0dad37e51578cffa4a4e` routes every Python probe/pip/helper call through `Invoke-PythonSafe` and treats the native exit code as authoritative. If imports still fail after installation, the exact traceback is printed deliberately. Sampling parameters are unchanged.

## Alucard license boundary

This is **research-only** until licensing is resolved. Alucard uses FAIR License 1.0.0: published terms permit non-commercial personal/research use; commercial use requires visible attribution; Business Use requires a separate signed commercial agreement with the author. A visual PASS therefore does not automatically authorize production adoption.

Kill rule: if this one purpose-built native-128 candidate still cannot produce credible Exilada pixel art, close the automated local generative-source search rather than tuning endlessly. G3S-A would then need to be re-scoped as an authored canonical-source problem.

## Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\05_bootstrap_and_run_g3s_a_alucard.ps1"
```

Then STOP. If it reaches `G3S-A ALUCARD: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_alucard\g3s_a_alucard_contact_sheet.png`

If it fails, share the complete console output. Do not run G3S-B or G4.

## Workspace

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- hidden deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- Qwen runtime/reference: `Z:\AI\QwenImageEditSpike`
- PixelLock evidence/dependencies: `Z:\AI\PixelLockSpike`
- Alucard research dependency workspace: `Z:\AI\AlucardSpike`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`