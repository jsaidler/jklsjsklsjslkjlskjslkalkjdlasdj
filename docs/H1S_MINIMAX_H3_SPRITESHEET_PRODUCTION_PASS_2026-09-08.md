# H1-S — MiniMax H3 spritesheet production pass

Status date: **2026-09-08**

Status: **CANONICAL / H3 H0 PASSED AS MOTION-MASTER CANDIDATE / FINAL RUNTIME TARGET RETURNS TO HIGH-QUALITY PIXEL ART / THROUGHPUT GATE BEFORE WALK PRODUCTION**

Canonical state: `docs/PROJECT_STATE.md`.

## Why this document exists

H0 proved that MiniMax H3 Ref2VA can produce a temporally coherent complete Exilada from a still appearance reference plus a real driving video. It did **not** prove the final game-art pipeline.

Three concepts must remain separate:

1. **motion master:** H3-generated video used to solve motion, anatomy, hair, cloth and restraints;
2. **action distillation:** automatic reduction of that video to a small set of game-relevant animation frames;
3. **runtime render:** reconstruction of those selected frames as the final high-quality pixel-art sprites used by the game.

The tiny H0 gameplay proxy is retired as a production-art concept. It was only a legibility diagnostic.

## Final visible-art decision — UPDATED 2026-09-08

The canonical Exilada reference is pixel-art based. H3 may reinterpret it into a painterly/raster video while solving motion, but **that intermediate video is not the final visible runtime asset**.

Final runtime characters must return to a **deliberate high-quality pixel-art rendering**, better resolved and more coherent than the current reference while preserving the locked 1980s sword-and-sorcery art direction.

Therefore the production chain is now:

`canonical pixel-art appearance reference + real driver -> H3 motion master -> automatic action-frame extraction/alignment -> pixel-art reconstruction pass -> transparent complete-character spritesheet/atlas + metadata -> runtime playback`

The H3 painterly result remains useful evidence and may influence the final pictorial language, but it is an intermediate motion representation rather than the final raster doctrine.

## Important correction: do NOT ask H3 to generate only 8–12 frames as the default production route

The current ComfyUI H3 node uses the model's `17k+5` temporal grid and documents the trained video range as approximately **124–362 frames** at 24 fps. H0 used 124 frames for this reason.

So the production optimization is **not** initially:

`124 generated frames -> 8 generated frames`

Instead it is:

`124-frame H3 motion master at a fast sampler -> extract 8–12 final sprite frames from the useful action/cycle`

A shorter-than-trained H3 temporal window may be tested later as an explicit optimization, but it is not the baseline because it could trade away the temporal coherence that H0 just proved.

## Why H0 took too long

Completed H0:

- 124 frames;
- 448×800;
- 50 sampling steps;
- Base Ref2VA;
- elapsed `4504.8s` (~75m05s).

This was a **quality screening baseline**, not a viable per-action production throughput target.

## Immediate throughput gate — H0T / Runner49

Before spending another hour on a walking clip, compare H0 against the official Ref2V Turbo path on the **same H0 references and geometry**.

The official ComfyUI R2V template includes:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- `LoraLoaderModelOnly` at `strength_model=1`;
- an explicit switch from the full model to the LoRA-patched model;
- an explicit switch from full sampling to **4 steps**.

H0T is therefore a controlled **production-throughput configuration gate**, not a new model-family test.

### H0T exact settings

Keep from H0:

- Picture1 = canonical Exilada;
- Video1 = exact same H0 driver;
- 448×800;
- 124 frames @24fps;
- `ref_image_size=match`;
- seed0;
- `res_multistep`;
- same prompt;
- same Ref2VA diffusion/text/video-VAE/audio-VAE set.

Change only the official Turbo path:

- add `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- LoRA strength `1.0`;
- steps `4`;
- scheduler `simple`, matching the official template's Turbo/full switch structure.

Turbo LoRA evidence:

- file size approximately **1.96GB**;
- SHA256 `5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c`.

### H0T pass criteria

H0T passes for production use only if:

1. wall-clock time drops enough to make per-action iteration practical;
2. complete-body topology remains materially H0-level stable;
3. motion transfer remains faithful;
4. face/body/hair/costume identity does not collapse;
5. hair/cloth/restraint dynamics remain readable;
6. no destructive blur/ghost-body reappears.

Target throughput is **well below the 75-minute H0 baseline**. The first measurement is empirical; do not promise linear 50/4 scaling because text encoding, loading, VAE work and DynamicVRAM/offload remain.

If Turbo4 is visually unacceptable, the next speed branch is not random tuning. Use one documented higher-quality fallback such as the current full model at a lower official step count before considering another family.

## H1-S actual walking-production contract

Once the throughput path is chosen, H1-S produces a genuine game locomotion asset rather than another generic video demo.

### Driver

Use one clean real walking source with:

- fixed camera;
- one adult performer;
- complete body visible throughout;
- screen-left travel;
- mostly lateral/slight 3/4, targeting the locked `72°` first locomotion direction;
- no source-frame crop of head, feet, hands or motion envelope;
- generous real margin for hair, cloth and chain swing;
- one clearly readable gait cycle.

Performer identity, sex presentation, clothing, hair and body type are not appearance references.

### H3 temporal strategy

For the first production walk, retain the proven **124-frame / 24fps** H3 temporal regime.

A short clean gait cycle may be automatically repeated/tiled in the driving reference to fill the 124-frame conditioning interval while keeping the camera fixed. This gives H3 enough trained-range temporal context without requiring 124 unique gameplay frames.

The output 124-frame video is the **motion master**, not the runtime animation.

## Action distillation — from motion master to game frames

For the first walk cycle, target **12 unique sprite frames**.

The automatic distillation stage must:

1. identify one stable complete gait cycle in the generated motion master;
2. reject frames with accidental source-envelope crop or obvious structural failure;
3. select 12 phase-distributed frames across that cycle, preferably by motion/phase spacing rather than simple arbitrary time sampling;
4. segment the complete character automatically;
5. preserve hair, cloth and chain extents in the alpha matte;
6. align a stable ground/pivot point while preserving legitimate vertical body motion;
7. output a high-resolution transparent 12-frame action strip for the final art renderer.

Routine manual masks, manual frame repainting and per-frame alignment are still prohibited.

## Pixel-art reconstruction stage — REQUIRED, NOT YET PROVEN

A simple whole-frame downscale is **not** the final solution. The 90×160 H0 proxy demonstrated only silhouette survival and was too small/illegible to stand in for final art.

The selected action frames must be reconstructed into deliberate pixel art.

The preferred validation architecture is:

- give the pixel-art renderer the canonical Exilada reference;
- give it the complete selected action strip/contact sheet so all frames are seen as one coherent set rather than independently redrawn images;
- preserve pose, silhouette, foot placement and frame ordering from the H3 motion master;
- improve pixel clustering, palette discipline, material readability and character identity;
- keep final art on an exact pixel grid with no blurry interpolation.

The exact pixel-art reconstruction model/tool is a **separate production gate**. H3 is not considered responsible for the final pixel clusters.

A deterministic nearest-neighbor/palette-quantization conversion may be kept as a cheap control, but it is not assumed capable of the required final quality.

## Initial runtime sprite target

For the first locomotion asset:

- visible protagonist height: approximately **128 px**;
- initial unique frames: **12**;
- playback target: approximately **12 fps** for the art frames, adjusted by gameplay timing rather than by regenerating animation;
- pivot: stable ground/contact reference;
- complete character already composited per frame;
- transparent RGBA runtime sprites.

A practical first review sheet is:

- cell: **192×192 px**;
- grid: **4×3**;
- sheet: **768×576 px**;
- character visible height ~128px within the cell, leaving room for hair/cloth/restraint excursions.

Production packaging may additionally use a trimmed atlas with per-frame pivot/trim metadata for texture efficiency.

## Expected H1-S artifact chain

Example naming:

- `walk_left_motion_master.mp4` — H3 124-frame intermediate;
- `walk_left_cycle_manifest.json` — detected cycle and chosen phases;
- `walk_left_rgba/frame_00.png` … `frame_11.png` — extracted high-resolution transparent action frames;
- `walk_left_pose_sheet.png` — high-resolution 12-frame pre-pixel-art strip;
- `walk_left_pixelart_sheet.png` — final 4×3 runtime review sheet;
- `walk_left_atlas.png` — optional trimmed production atlas;
- `walk_left_atlas.json` — frame rectangles, pivots, durations and action metadata.

## Production timing objective

The pipeline should not require ~75 minutes for every ordinary action iteration.

Immediate order:

1. benchmark H0T Turbo4 against the already-proven H0 quality baseline;
2. if Turbo4 passes, use it for the first H1-S walk motion master;
3. distill that 124-frame master to ~12 final animation frames;
4. validate the pixel-art reconstruction stage;
5. only then decide whether further H3 temporal shortening is worth the risk.

## Current gate

**Runner49 / H0T Turbo4 throughput-quality comparison comes before the new walking inference.**

This directly answers whether MiniMax H3 can become a practical production tool rather than merely a high-quality one-hour screening tool.
