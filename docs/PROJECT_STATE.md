# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** This file records the current active work, latest validated checkpoints, rejected routes and exact next gate. Detailed design lives in the linked living documents.

## Canonical living documents

Read in this order before acting:

1. `docs/PROJECT_STATE.md`
2. `docs/ANIMATION_PIPELINE.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/PIXEL_ART_PRODUCTION.md`
6. current tooling under the relevant `tools/` spike directory

GitHub living documents are the source of truth across chats.

## Mandatory checkpoint protocol

After every material project step:

1. update the relevant thematic living document;
2. update this file;
3. commit tooling/documentation changes with a focused commit;
4. record PASS/FAIL, observed result and next gate;
5. do not rely only on chat history or memory.

## Current active focus

**Production Pixel Master validation for the Exilada.**

The project has identified a blocking distinction:

- `exilada_master.png` is the approved **high-detail identity/design master**;
- it is **not** the final gameplay sprite master;
- mass animation work is paused until a convincing, reproducible Production Pixel Master exists in true modern pixel art.

The final visual target remains true modern pixel art, not a high-resolution generated image with pixel texture and not a simple procedural/mannequin raster.

Detailed production rules live in `docs/PIXEL_ART_PRODUCTION.md`.

## Current visual-production findings

### Identity/design master: PASS

Canonical Exilada reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It successfully defines:

- adult female identity;
- lean functional anatomy;
- long black hair as dominant mass;
- olive/brown skin;
- minimal degraded clothing;
- captivity/restraint markers;
- barefoot, weaponless initial state.

It remains canonical for identity.

### Direct image generation as Production Pixel Master: FAIL

Observed:

- outputs around `1024 × 1536`, not native sprite canvases;
- image treatment merely resembled pixel art;
- excessive generative texture and detail;
- no trustworthy native-grid cluster/palette control.

Decision:

**Do not continue prompt-iterating this route as the final sprite authoring method.**

### Native Python/Pillow geometric sprite spike: FAIL visually

A real `96 × 96` RGBA Exilada candidate was produced with:

- no downscale;
- no antialiasing;
- controlled palette;
- real native pixels.

Technical raster correctness passed, but visual quality failed:

- generic procedural/mannequin character;
- weak anatomy and authored silhouette;
- far below the project's best-in-class modern pixel-art quality target;
- structurally similar to the already rejected idea of treating simple procedural forms as final art.

Decision:

**Python/Pillow remains useful for deterministic QA/export/masks/palette checks, but is rejected as the system that invents final character art through primitive geometry.**

## Locked pixel-art starting parameters

These remain provisional-but-locked for the current validation gate:

- native gameplay raster: `640 × 360`;
- Exilada target visible height: ~`64 px`;
- allowed composition tuning band: `56–72 px`;
- idle/locomotion canvas: `96 × 96`;
- ordinary melee/action canvas: `128 × 128`;
- approval first at native `1×`;
- final character reference family ultimately needs eight directions;
- first directional gate is only `S`, `NE`, `N`.

Do not generate a walk cycle before these three static directions pass.

## Locked visual inspiration translation

The project explicitly wants the Exilada and broader human visual language to retain the original sword-and-sorcery inspirations:

- Conan / sword-and-sorcery brutality and material scarcity;
- Frank Frazetta's decisive masses, physicality and dangerous silhouette;
- Heavy Metal's adult, less sanitized fantasy sensibility and bodily/material freedom;
- Julie Bell's anatomical/sculptural confidence, without drifting into polished bodybuilding glamour.

For the Exilada this means:

- lean functional body, not fitness-model musculature;
- clothing as residue of captivity, not designed barbarian costume;
- nudity/skin exposure is acceptable when materially/narratively coherent;
- hair as dominant violent mass, not strand soup;
- asymmetry, degradation and bodily presence must feel lived rather than decorative.

## Next production-art gate

### Agent-operated native pixel editor/source workflow

The next candidate must combine:

1. a **real native pixel canvas/source**, and
2. enough **visual authorship and iterative inspection** to reach professional modern pixel-art quality.

Preferred workflow shape:

`identity/pose reference -> native canvas -> agent draws/edits -> preview at 1× -> critique -> cluster repair -> validation -> save`

Current researched candidates:

- **Aseprite MCP:** strongest current architecture; true pixel-level operations, layers/frames/palette, preview/QA loop; MIT; requires Aseprite locally.
- **LibreSprite-MCP:** free/GPL fallback, but its own docs describe the implementation as brittle and lightly tested.
- **code-as-pixelart:** useful MIT structured-source architecture for semantic colors/parts/views/frames/anchors; not yet proven as sufficient artistic authoring on its own.
- **Spriteloom:** local and useful for some tasks, but remains diffusion + postprocess and is not accepted as the canonical Production Pixel Master authoring foundation.

**Exact next gate:** choose and validate one agent-native editor/source route with a single `S` Exilada sprite on the real target grid. Do not proceed to `NE`, `N` or animation until `S` is visually convincing.

## Animation pipeline — preserved but paused at visual dependency

The existing FLUX.2 Klein + RefControl local spike remains technically relevant for character re-posing, but it is no longer the immediate next action.

Validated execution state remains:

- STEP 1 preflight: PASS;
- STEP 2 ComfyUI portable runtime: PASS;
- STEP 3 required weights: PASS;
- STEP 4 canonical reference + four deterministic COCO-18 poses: PASS;
- STEP 5 runtime schema/workflow validation: tooling ready, local target-machine run still pending.

Active tooling:

`tools/flux2-refcontrol-spike/`

Do not discard or silently restart that work. Resume only after the Production Pixel Master direction is sufficiently resolved, unless the user explicitly prioritizes the pose spike again.

## Target machine / relevant paths

- Windows 11 Home Single Language;
- 47.7 GB usable RAM detected;
- NVIDIA GeForce RTX 3060 12 GB;
- project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`;
- FLUX spike workspace: `D:\AI\Flux2RefControlSpike`.

## Rejected / stopped routes

Do not revive casually:

- Sprite Sheet Diffusion — tested and rejected;
- Wan-Animate-2 Base INT8 — tested and rejected;
- PixelLab hosted/tiered route — stopped;
- Pixel Engine — disqualified as hosted/paid dependency;
- Retro Diffusion hosted route — disqualified under same rule;
- direct generic image generation as final pixel master — rejected;
- primitive Python/Pillow geometry as final artistic authoring — rejected;
- generic video diffusion is not the current architecture.

## Latest documentation commits

- `957f89315850bd967d95877ba8098736a3303715` — record direct-image and native-Pillow Production Pixel Master failures; lock agent-native pixel-editing next gate.

## Exact next action

**Do not generate another image or scripted primitive sprite.**

The next action is to validate a real agent-operated pixel editor/source workflow, beginning with a single `S` Exilada at the native target grid, and only advance when that result passes both technical raster and artistic-quality gates.