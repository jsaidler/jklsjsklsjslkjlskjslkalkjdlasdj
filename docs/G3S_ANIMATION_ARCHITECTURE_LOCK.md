# G3S — Animation Architecture Lock

Status date: **2026-09-08**

Status: **CANONICAL / COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME / H3 REF2VA MOTION-MASTER AUTHORING / FINAL HIGH-QUALITY PIXEL-ART RECONSTRUCTION / NO MANUAL ANIMATION OR PER-FRAME CLEANUP**

## Presentation lock

The game uses an elevated arcade beat'em-up / belt-scroller false-3D presentation:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- protagonist about `128px` tall;
- first locomotion family screen-left and mostly lateral/three-quarter;
- intended first gameplay facing `72°`.

## Final runtime representation — LOCKED

Runtime consumes **complete, already-composed character frames**:

`complete pixel-art frames -> spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment layer assembly.

## Final visual rendering — LOCKED 2026-09-08

Final runtime character graphics are deliberate high-quality pixel art.

H3 painterly/raster output is classified as a **motion-master intermediate**, not the final runtime raster style.

Canonical production chain:

`pixel-art appearance reference + real driving video -> H3 complete-character motion master -> automatic action/cycle distillation -> automatic segmentation/alignment -> high-quality pixel-art reconstruction -> complete transparent spritesheet/atlas -> runtime`

The exact pixel-art reconstruction model/tool is still a separate validation gate.

## Complete-frame motion requirement — LOCKED

Every valid exported animation must bake together, where present:

- body locomotion and weight transfer;
- soft-tissue/jiggle;
- hair inertia/follow-through;
- clothing/binding motion;
- material/wind response;
- shackles/chains/restraints/accessories;
- final occlusion changes.

## Initial Exilada source — LOCKED

Canonical appearance reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It owns the complete initial visible state for current authoring.

## Dual-reference motion-authoring contract — LOCKED

Motion authoring uses two semantically separate sources:

1. **appearance:** complete Exilada master;
2. **movement:** arbitrary real driving video.

The driving performer does not need matching costume, hair, body or identity.

The motion model must consume richer evidence than skeleton pose so it can infer non-rigid temporal behavior for hair, cloth, soft tissue, wind and accessories.

## No-manual-production rule — LOCKED

Disallowed as required production steps:

- manual rigging/weight painting;
- manual keyframing;
- manual hair animation;
- manual cloth/chain setup or repair;
- manual pose alignment;
- manual mask repair;
- per-frame repainting/retouching;
- hand compositing or cleanup.

Allowed: fully automatic preprocessing, segmentation, crop/resize, background removal, cycle/action detection, frame extraction, alignment, pixel-art reconstruction, packing, QA and metadata.

## Model-screening state

1. **MiniMax H3 Ref2VA — ACTIVE / H0 PASS_CANDIDATE as motion-master family.**
2. Wan-Animate-2 — paused after W1L, not exhausted.
3. SCAIL-2 — later only if H3 fails a later production gate.

Pose-only Moore/SSD routes remain research evidence and do not satisfy the richer raw-video motion contract.

## H3 H0 quality baseline

Completed local H0:

-448×800;
-124f @24fps;
-50 steps;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`.

Visual verdict: **PASS_CANDIDATE**. Stable body topology, coherent hair/cloth motion, no destructive whole-body smear. Chain detail still drifts. Late crop follows source driver envelope.

## H3 temporal production rule

Do not assume the production route should ask H3 for only8–12 generated frames.

Current H3 uses the `17k+5` temporal grid and documents its trained video range around124–362 frames @24fps.

Production baseline:

`fast124-frame motion master -> automatic cycle/action distillation -> ~12 selected game frames -> final pixel-art reconstruction`

Shorter H3 windows are optional later optimization only after evidence.

## Current gate — H0T / Runner49

H0 Base50 quality is good but ~75 minutes per run is too slow for ordinary action iteration.

Runner49 tests the official Ref2V Turbo4 path on the exact H0 inputs:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- LoRA strength1.0;
-4 steps;
- `res_multistep/simple`;
- same Picture1/Video1;
- same448×800/124f/24fps;
- same `ref_image_size=match`, seed0 and prompt.

Speed and quality must both pass before Turbo becomes the H1-S production path.

## H1-S walk architecture

After throughput choice:

1. use a fixed-camera full-body screen-left real walk with safe margins and one clear gait cycle;
2. keep the proven124-frame H3 temporal regime; a clean cycle may be automatically tiled/repeated in the driver;
3. generate a complete H3 motion master;
4. automatically select one stable gait cycle;
5. distill to ~12 useful frames;
6. automatically segment and pivot-align complete character frames;
7. reconstruct the full selected set as coherent high-quality pixel art;
8. pack final transparent spritesheet/atlas + metadata.

## First runtime locomotion target

- visible character ~128px;
-12 unique frames;
- initial cell192×192;
-4×3 review sheet =768×576;
- transparent RGBA;
- optional trimmed atlas with frame rectangles, pivots and durations.

## Cleanup discipline — LOCKED

- keep Base H3 Ref2VA files;
- add only the single official Turbo4 LoRA for the explicit throughput hypothesis;
- do not accumulate FL2VA/style/alternate quantizations without evidence;
- Wan large weights may be removed while W1H/W1L proof/results remain;
- keep SSD comparison evidence until explicit abandonment/final verdict.

## Closed routes / assumptions

- runtime visible-character layer assembly — CLOSED;
- body-pose-only animation as final motion foundation — CLOSED;
- manual hidden secondary animation as required production method — CLOSED;
- independent unconstrained full-body redraw per frame — CLOSED;
- using the tiny H0 gameplay proxy as final production art — CLOSED;
- treating H3 painterly video itself as the final mandatory runtime pixel style — CLOSED.

## Current validation question

> Can the official H3 Ref2V Turbo4 path retain the H0 motion/topology quality while reducing wall-clock cost enough that a 124-frame motion master can be a practical upstream source for automatic ~12-frame high-quality pixel-art spritesheets?
