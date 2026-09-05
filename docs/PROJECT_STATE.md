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

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines identity/design, not final gameplay pixels.

Adult woman, lean/resilient anatomy, olive-brown skin, severe face, very long heavy black hair, degraded beige cloth, scars/wounds, broken restraints at wrists/ankles, bare feet, canonical base weaponless.

## Hard operator constraint

Normal production must remain scriptable/headless. The user must not need routine Blender/Aseprite/rigging operation, frame-by-frame repainting or a hired specialist.

Normal operator loop:

`git pull -> one documented PowerShell command -> inspect/share output`

## Locked gameplay camera baseline

- `640×360`;
- orthographic;
- pitch `26 deg`;
- protagonist reference visible height `128 px`.

## Active architecture — LOCKED

`camera/scale -> real motion -> deterministic hidden topology -> DIRECTION_SPACE_FK -> projected joints/depth/sockets -> persistent structured 2D pixel assets -> deterministic 2D composition/deformation -> sprite/runtime export -> QA`

Hidden 3D owns infrastructure only: motion, topology/left-right identity, sockets, contacts/root data, physics, depth/occlusion, semantic guides and secondary-motion drivers.

It does **not** own final visible character color pixels.

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
    - Alucard external-reference test — INVALID/CLOSED
    - Alucard text-only native-128 control — FAIL/CLOSED
    - **automated local generative-source search — CLOSED**
    - **authored native source V1** ← READY TO RUN
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

Locked `640×360`, orthographic `26 deg`, protagonist `128 px`.

## G2 — PASS

Real motion source: CMU `105_34 NormalWalk`, 120 fps. Major-limb topology, left/right alternation and deterministic structure validated.

## G3 / G3R

G3 proved deterministic native-grid processing technically possible but not production-looking. G3R proved renderer-only refinement cannot invent authored 2D form from a primitive mannequin.

## G3V-R — PASS

Accepted retarget: **`DIRECTION_SPACE_FK`**.

Measured facts:

- `0` parent mismatches;
- mean source/target rest-orientation difference `83.1874 deg`, max `180.0289 deg`;
- 4 unique target poses;
- mean elbow/knee error `0.0000 deg`, max `0.0001 deg`;
- rest-independent chain-shape metric passed;
- visual source/target skeleton comparison passed.

Marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

## G3V — FAIL

Representative MPFB body animated coherently after validated retarget, but the direct visible translation still read as coarse 3D rather than deliberate modern pixel art.

Decision: hidden 3D remains control/infrastructure only.

Marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

# G3S-A source-search history

## Qwen direct-native — FAIL

Native `640×360` corrected Qwen output collapsed flat. The same model/runtime at its preferred preprocessing produced a coherent `1392×752` Exilada-like design control.

The control remains at:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Pinned SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

It is design/scaffold material only, never animation owner.

## SD1.5 native re-author — FAIL

Native `640×360` SD1.5 + pixel LoRA produced a block/mannequin and lost Exilada identity. No tuning permitted.

Marker:

`tools/structured-2d-character-pipeline/g3s_a_sd15_failure.json`

## PixelLock — FAIL

Footprint-perfect `128×128` result but only one opaque RGB value `[99,9,25]`; a monochrome silhouette, not a source sprite.

Marker:

`tools/structured-2d-character-pipeline/g3s_a_pixellock_failure.json`

PixelLock may return later only after a canonical sprite exists.

## Alucard — CLOSED

### External-reference run — INVALID

A Qwen-derived design image was incorrectly used as Alucard `ref`; upstream uses `ref` as a previous sprite/animation frame. That run is not a model-quality verdict. Its 128 conditioning reduction also lost the mouth, correctly identified during review.

Marker:

`tools/structured-2d-character-pipeline/g3s_a_alucard_reference_invalid.json`

### Text-only upstream control — FAIL

Documented text-to-sprite mode, no reference input:

- native `128×128 RGBA`;
- seed `20260905`;
- 20 Euler steps;
- CFG text `5.0`;
- model revision `b8e7602`;
- raw SHA256 `c3143b76444abc7c5b6f7b1fe6c0d66a51e7f83d4fff7519018fe3a97739bc5a`;
- alpha bbox full canvas `[0,0,127,127]`;
- `12525` opaque pixels;
- `12059` unique opaque colors.

Visual result: full-canvas mottled/noisy texture with no coherent sprite.

Decision: Alucard FAIL/CLOSED. No seed/CFG/prompt/sampler fishing.

Marker:

`tools/structured-2d-character-pipeline/g3s_a_alucard_failure.json`

# G3S-A authored native source — CURRENT

The automated local generative-source search is **closed**. G3S-A is now a finite native-authoring problem.

Current method:

`fixed Qwen design scaffold -> deterministic 128x128 base -> explicit native pixel patch data -> 1x review -> revise patch data if needed -> approve canonical source`

This is not a return to per-frame manual art. It is a one-time canonical source construction. Once approved, G3S-B decomposes it into persistent parts and G3S-C animates those parts deterministically from the validated hidden motion.

V1 patch explicitly restores/introduces:

- readable mouth;
- both wrist cuffs;
- both ankle restraints;
- short broken-chain remnants.

Tooling:

- `tools/structured-2d-character-pipeline/g3s_a_authored_native_v1.py`
- `tools/structured-2d-character-pipeline/g3s_a_authored_patch_v1.json`
- `tools/structured-2d-character-pipeline/07_run_g3s_a_authored_native.ps1`

Output:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_authored\g3s_a_authored_contact_sheet.png`

If review requests changes, edit the explicit patch data. **Do not search another source model.**

## Exact next action — ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\07_run_g3s_a_authored_native.ps1"
```

Then STOP. Share the authored contact sheet. Do not run G3S-B or G4.

## Workspaces

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- deterministic backbone + G3S outputs: `Z:\AI\RogueliteCharacterPipeline`
- Qwen runtime/reference: `Z:\AI\QwenImageEditSpike`
- PixelLock evidence/dependencies: `Z:\AI\PixelLockSpike`
- Alucard evidence/dependencies: `Z:\AI\AlucardSpike`
- retarget preflight: `Z:\AI\RogueliteCharacterPipeline\g3v_retarget`
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
