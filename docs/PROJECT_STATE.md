# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** GitHub living documents are the source of truth; detailed design stays in thematic docs rather than being duplicated here.

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
12. current tooling under `tools/deterministic-character-pipeline/`

After every material step: update the relevant thematic document(s) + this file, record PASS/FAIL/next gate, and commit focused changes.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Immediate gameplay presentation baseline:

**elevated 2D belt-scroller / false 3D**.

Final visible character/environment language remains **true modern pixel art** at native gameplay raster. Hidden 3D may own motion/topology/physics but is not the final visible style.

## Exilada visual identity — LOCKED

Canonical high-detail identity/design master:

`assets/source/characters/exilada/reference/exilada_master.png`

The master is not the final gameplay sprite. It defines identity, proportions, face, dominant long black hair mass, degraded beige clothing language, scars/restraints and overall physical character.

## Direct per-frame diffusion — CLOSED AS PRIMARY ARCHITECTURE

FLUX.2 Klein + RefControl V1/V2/V3 is frozen/rejected as production direct-frame animation because it failed topology/temporal/accessory consistency, culminating in a three-leg/three-foot frame in V3.

Qwen-Image-Edit-2509 tooling remains preserved but **PAUSED**. A perfect isolated generated pose would not prove natural motion, stable anatomy, equipment continuity or production scalability.

## Active character-production architecture — LOCKED FOR VALIDATION

Canonical roadmap:

`docs/CHARACTER_PRODUCTION_PIPELINE.md`

Pipeline:

`gameplay camera/scale -> real motion -> deterministic rig/topology -> persistent secondary systems -> native-raster semantic passes -> pixel-specific renderer -> modular equipment/state composition -> sprite/runtime export -> automated QA`

Hard user-operation constraint:

- no routine Blender GUI work;
- no manual rigging/animation/pixel-production operation by the user;
- no hired art/animation team assumed;
- recurring production must be driven by ChatGPT-authored command-line/headless tooling.

Canonical pattern:

`PowerShell -> blender.exe --background --python ... -> deterministic outputs/reports`

## Animation source strategy — LOCKED

Canonical catalog:

`docs/ANIMATION_SOURCE_LIBRARY.md`

Primary permissive sources already identified include:

- Quaternius Universal Animation Library / Library 2 — CC0 humanoid motion families;
- CMU Graphics Lab Motion Capture Database — real captured locomotion/recovery/combat-style trials under its stated reuse terms;
- Quaternius animal/monster/dinosaur packs — CC0 sources for quadruped/creature rig-family validation.

Blender is the deterministic import/retarget/bake backbone, not the sole animation source.

## Physical interaction / body / equipment architecture — LOCKED

Canonical docs:

- `docs/PHYSICAL_INTERACTION_VFX_GORE.md`
- `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`

Architectural requirements already include:

- persistent full body under clothing;
- modular removable/damageable clothing and armor;
- stable named equipment/restraint sockets;
- hair/cloth secondary motion and wind interaction;
- wetness/blood/dirt/material state via semantic masks;
- event-driven water/blood VFX;
- deterministic named gore/sever zones and detached-part behavior;
- discrete palette-band dynamic lighting using normal/material/depth metadata;
- support for unclothed body states without depending on generative image synthesis;
- damage persistence without body×item×damage×animation combinatorial sprite authoring.

## Risk-first gate order — LOCKED

- **G0 — automation:** headless Blender/toolchain proof.
- **G1 — camera/native scale:** belt-scroller framing and actual character pixel density.
- **G2 — motion/topology:** real captured walk on persistent generic rig with contacts/sockets.
- **G3 — pixel translation:** prove hidden 3D can become intentional native-grid pixel art before building Exilada geometry.
- **G4 — identity mapping:** low-detail Exilada production proxy / Production Pixel Master.
- **G5 — temporal stress:** locomotion + extreme action + impact/recovery.
- **G6 — equipment/attachments.**
- **G6A — wind/secondary motion.**
- **G6B — liquid/contact VFX.**
- **G6C — gore topology.**
- **G6D — clothing/armor damage.**
- **G7 — systemic state/dynamic lighting.**
- **G8 — production scaling.**

A later expensive stage does not start merely because an earlier demo looked attractive.

# Current execution state

## G0 — HEADLESS AUTOMATION: PASS / CLOSED

Validated target environment:

- Windows 11 Home Single Language `10.0.26200`;
- Blender `5.1.1`;
- Blender executable: `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`;
- workspace: `Z:\AI\RogueliteCharacterPipeline`;
- diagnostic engine: `BLENDER_EEVEE`.

Successful outputs:

- `Z:\AI\RogueliteCharacterPipeline\g0\g0_probe.png`
- `Z:\AI\RogueliteCharacterPipeline\g0\g0_probe.blend`
- `Z:\AI\RogueliteCharacterPipeline\g0\g0_manifest.json`
- `Z:\AI\RogueliteCharacterPipeline\g0\g0_result.json`

Validated PNG SHA256:

`bb8c938d6fe64a84de264a7c01824b1dabad27f3abd307485f706553b0d19d53`

The successful run emitted benign Blender 5.1 deprecation warnings to stderr, which Windows PowerShell 5.1 displayed as `NativeCommandError` records even though Blender completed and G0 passed. The launcher has since been hardened to use `Start-Process` with one explicitly quoted argument string and redirected logs, eliminating that parent-shell noise without reintroducing the old path-with-spaces bug.

Detailed incident history:

`docs/G0_AUTOMATION_LOG.md`

**No G0 rerun is required for progression.**

## G1 — CAMERA / NATIVE SCALE: ACTIVE NEXT GATE

Tooling:

- `tools/deterministic-character-pipeline/01_run_g1.ps1`
- `tools/deterministic-character-pipeline/g1_camera_scale_blockout.py`

Purpose: establish gameplay framing before mocap, final art or Exilada production geometry.

G1 renders the same primitive belt-scroller composition in a controlled 3×3 matrix at provisional native raster `640×360`:

- rows: camera pitch `18° / 26° / 34°`;
- columns: protagonist visible height target `112 / 128 / 144 px`;
- one protagonist proxy;
- five enemy proxies at different depth positions;
- walkable depth band;
- attack/depth reach markers;
- fixed orthographic camera family.

The Python script calibrates orthographic scale against measured projected protagonist height rather than assuming a guessed world-to-pixel conversion.

Outputs include nine native renders, `g1_manifest.json`, `g1_blockout.blend`, `g1_result.json` and one labeled `g1_contact_sheet.png` for review.

G1 does **not** use Exilada art, mocap or the final pixel renderer.

### Exact next action — DO ONLY THIS

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\01_run_g1.ps1"
```

Then **STOP**. Do not start G2.

Share:

`Z:\AI\RogueliteCharacterPipeline\g1\g1_contact_sheet.png`

The contact sheet is the primary G1 review artifact; console output is needed only if the runner fails.

## Workspace state

- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`
- paused Qwen spike: `Z:\AI\QwenImageEditSpike`
- active deterministic pipeline: `Z:\AI\RogueliteCharacterPipeline`
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`
