# Runner50 FLUX Kontext — Visual Failure Record

Status date: **2026-09-08**

Status: **MODEL/TASK FAIL / RENDERER-LAYOUT + IDENTITY/BODY-PROPORTION FAIL / PIXEL-ART QUALITY PARTIAL**

Canonical project state: `docs/PROJECT_STATE.md`.

Renderer spike: `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`.

## Completed inference evidence

Runner50 completed successfully at the infrastructure/integration layer.

Evidence recovered from the local manifest/log:

- prompt id: `56576cf4-165a-4ad2-8a96-ec28bf75da1e`;
- elapsed: `296.63s`;
- model: `flux1-dev-kontext_fp8_scaled.safetensors`;
- 20 steps;
- guidance `2.5`;
- CFG `1.0`;
- Euler/simple;
- seed `0`;
- denoise `1.0`;
- output size `1024×1024`;
- runtime review sheet `768×576`, `192×192` cells.

Therefore this is not an infrastructure or integration failure. It is genuine renderer/task evidence.

## User visual verdict

Runner50 is **rejected for production**.

Primary failures:

1. **Adult body/identity drift**
   - the renderer changed the Exilada's physical structure instead of only changing rendering language;
   - body proportions became shorter/thicker and the face/body read more juvenile/infantilized;
   - this violates the mature adult anatomy and identity contract.

2. **Spritesheet temporal/layout semantics wrong**
   - Runner50 selected 12 frames by even temporal coverage across the entire 124-frame H0 sequence;
   - it then treated those 12 scattered poses as one global `4×3` contact sheet;
   - the user requires a real spritesheet organization in which **each row contains one coherent temporal animation sequence**.

3. **Art-direction weakening**
   - some pixel-art qualities were promising, but the result softened the locked mature 1980s sword-and-sorcery charge;
   - Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell remain mandatory art-direction anchors;
   - mature danger, sensuality, grime, heroic adult anatomy and pulp-fantasy physicality must survive the renderer.

4. **Renderer freedom too high**
   - full-sheet generation at denoise `1.0` gave Kontext too much freedom to reinterpret anatomy and design;
   - 12 small figures in one 1024 square also limited per-character detail and encouraged redraw rather than structure-preserving reconstruction.

## What did work

Do not discard the useful evidence:

- Kontext local inference is operational on the RTX 3060 12GB path;
- the FP8-scaled model can produce a coherent pixel-art-like rendering language;
- automatic neutral-background removal produced usable RGBA structure for many edges;
- the local runtime/model installation is now reusable and should not be reinstalled for every renderer iteration.

## Controlled repair — Runner51

The next gate keeps the same local Kontext model/runtime but changes the task formulation rather than switching model families.

Runner51:

`tools/structured-2d-character-pipeline/51_run_flux_kontext_h0_dance3x4_temporal_rows_structure_lock.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance3x4_temporal_rows_structure_lock.py`

Controlled changes:

1. **one temporal animation per row**;
2. select one short coherent 16-frame high-motion window inside each third of the H0 video;
3. choose four ordered frames from each window at offsets `0,5,10,15`;
4. render each row separately as a `2×2` `1024×1024` Kontext input, so each character is materially larger during reconstruction;
5. reduce denoise from `1.0` to **`0.45`** to preserve source structure;
6. harden the prompt against infantilization/body redesign;
7. explicitly lock the mature 1980s sword-and-sorcery inspiration lineage;
8. repack the three rendered four-frame sequences into a final `4×3` sheet where each row is one animation.

No H3 regeneration is required.

## Runner51 pass boundary

Runner51 is not accepted merely if inference completes.

PASS requires:

- each row reads as one temporally coherent four-frame animation;
- adult Exilada body proportions remain materially consistent with H0 and the canonical reference;
- no infantilization, cute/chibi drift, shortened torso/limbs or enlarged head;
- pose/silhouette preservation materially improves over Runner50;
- pixel art remains deliberate and high quality;
- Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell mature sword-and-sorcery charge remains visible;
- hair, torn cloth, cuffs, shackles and chains remain readable;
- final RGBA packaging remains automatic.

If Runner51 still changes body structure at denoise `0.45`, classify that specifically before changing renderer family or precision.
