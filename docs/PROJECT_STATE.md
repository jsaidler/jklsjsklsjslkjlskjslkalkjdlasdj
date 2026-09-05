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
- **Qwen-Image-Edit-2509 direct native `640×360` source generation — REJECTED after G3S-A V2 flat-collapse.**

Qwen remains forbidden as independent animation-frame generator. Its official-resolution control has now completed and proved that the model/runtime functions when allowed to operate at its preferred high-resolution raster. That high-resolution output is reference/provenance only and is never eligible as final sprite art.

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
    - **SD1.5 native pixel re-author** ← READY TO RUN
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

Canonical design: `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`.

Goal: final pixels come from persistent 2D assets while hidden motion/topology supplies deterministic control.

## Qwen source experiment — CLOSED

Provisioned runtime remains under:

`Z:\AI\QwenImageEditSpike`

### Qwen V1 — INVALID

Harness graph was wrong relative to official ComfyUI Qwen 2509 workflow. Not a model-quality verdict.

### Qwen V2 native `640×360` — FAIL

Corrected graph completed normally but produced a genuinely flat native output:

- raw SHA256 `a5ecaf9db68fbb8370280c4b6c61a727aa5cd191134d6f508a34207f4c8d157e`;
- mean luma `70.3017`;
- p99 `71`;
- target stddev `0.4336`.

No seed/prompt/threshold rescue attempts are allowed.

### Qwen official-resolution control — PASS AS CONTROL / CLOSED

Restoring the official `FluxKontextImageScale` produced a coherent output rather than collapse.

Uploaded artifact facts:

- raster `1392×752`;
- coherent full-body adult woman;
- long dark hair, degraded beige cloth and bare feet readable;
- visually conventional high-resolution illustration/pseudo-pixel styling rather than native gameplay pixel art.

Conclusion: **Qwen/model/runtime are functional, but Qwen is unsuitable as the direct native sprite generator.** The working high-resolution Qwen image is retained only as a one-time identity/composition reference. It must not be simply shrunk/quantized into final art.

# G3S-A SD1.5 native pixel re-author — CURRENT

New tooling:

- `tools/structured-2d-character-pipeline/g3s_a_sd15_native_reauthor.py`
- `tools/structured-2d-character-pipeline/03_bootstrap_and_run_g3s_a_sd15_native.ps1`

Purpose: use the coherent Qwen control **only as conditioning**, then have Stable Diffusion 1.5 re-author the final image through diffusion directly at native `640×360` with a dedicated pixel-art LoRA.

This is not the rejected high-res-shrink route: the high-res source is reduced only to create an img2img conditioning/latent guide; the final generated pixels are newly sampled at `640×360` and are never resized after inference.

Input:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Output:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_sd15`

Pinned first test:

- Stable Diffusion 1.5 `v1-5-pruned-emaonly.safetensors`, SHA256 `6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa`;
- SD1.5 pixel-art LoRA, SHA256 `ad5034703699e910d5f9525ea5db64abcbd8d7396ff8f771c09403f3adb048ad`;
- guide figure automatically normalized to `128 px` height on `640×360`;
- seed `20260905`;
- `30` steps;
- CFG `6.0`;
- DPM++ 2M / Karras;
- denoise `0.72`;
- no final resize;
- one candidate only.

First run downloads about `4.27 GB` plus a ~`3.23 MB` LoRA. Existing isolated ComfyUI is reused.

Kill rule: if the candidate still reads as smooth/pseudo-pixel diffusion art rather than deliberate native pixel clusters, reject this route without seed fishing or parameter sweeps.

## Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\03_bootstrap_and_run_g3s_a_sd15_native.ps1"
```

Then STOP. If it reaches `G3S-A SD15: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_sd15\g3s_a_sd15_contact_sheet.png`

If it fails, share the complete console output. Do not run G3S-B or G4.

## Workspace

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- hidden deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- Qwen runtime: `Z:\AI\QwenImageEditSpike`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
