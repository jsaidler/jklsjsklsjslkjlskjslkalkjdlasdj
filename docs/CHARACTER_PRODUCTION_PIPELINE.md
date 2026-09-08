# Character Production Pipeline — End-to-End Living Plan

Status date: **2026-09-08**

Status: **CANONICAL PRODUCTION ROADMAP — H3 COMPLETE-CHARACTER MOTION MASTER -> AUTOMATIC ACTION DISTILLATION -> HIGH-QUALITY PIXEL-ART SPRITESHEET**

## Non-negotiable production contract

- final visible language is 2D pixel-art sprite animation for the elevated belt-scroller;
- runtime playback uses complete already-composed character frames;
- runtime character construction from body/hair/clothing/equipment layers is abolished;
- final exported frames contain the complete visible character state;
- motion comes from real driving video rather than unrelated guessed poses;
- anatomy, proportions and left/right identity remain stable;
- hair, cloth, restraints and secondary masses move coherently;
- no routine manual frame-by-frame repainting, manual masks or per-frame alignment;
- recurring operations must be scriptable/headless;
- equipment/damage/state variation must scale offline without reintroducing runtime assembly.

Canonical Exilada appearance reference:

`assets/source/characters/exilada/reference/exilada_master.png`

## Current production architecture — LOCKED 2026-09-08

`pixel-art Exilada reference + real driver -> H3 complete-character motion master -> automatic action/cycle detection and frame distillation -> automatic segmentation/alignment -> high-quality pixel-art reconstruction -> transparent spritesheet/atlas + metadata -> runtime playback`

MiniMax H3 painterly/raster video is an **intermediate motion representation**. It is not the final runtime art.

Detailed H1-S definition: `docs/H1S_MINIMAX_H3_SPRITESHEET_PRODUCTION_PASS_2026-09-08.md`.

## Runtime output — LOCKED

Per animation/state family:

- transparent complete-character PNG sequence and/or spritesheet/atlas;
- fixed/declared pivot/root metadata;
- per-frame duration/timing;
- optional event metadata such as foot contacts, attack markers and hitbox helpers;
- provenance/version manifest.

Visible runtime character remains one complete rendered sprite per frame.

## Complete-frame animation requirement

Every exported animation bakes all relevant motion:

- body locomotion/action;
- soft-tissue/jiggle response;
- hair motion;
- clothing/binding motion;
- armor/equipment motion where present;
- shackles/chains/restraints;
- self-occlusion.

If those elements are temporally wrong, the authored animation fails; runtime does not repair them.

## Motion backbone — UPDATED

The old G2/CMU/Moore walk proof remains historical research only.

Active motion backbone is **MiniMax H3 Ref2VA**:

- Picture1 = complete Exilada appearance;
- Video1 = arbitrary real movement/performance;
- raw-video temporal conditioning preserves richer motion than skeleton-only pose;
- H0 at448×800/124f proved stable complete-character topology and coherent hair/cloth motion.

Wan remains paused comparison evidence. Moore/SSD is no longer the active complete-motion path.

## H3 H0 quality baseline

Completed H0:

-448×800;
-124f@24fps;
-50 steps;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`.

Verdict: **PASS_CANDIDATE as motion-master family**.

H0 solved the dominant Wan problem: destructive whole-body smear/topology instability did not recur. Residual chain-detail drift remains; late crop follows the source driver envelope.

## Production-throughput gate — CURRENT

A 75-minute Base50 run is not the ordinary action-production target.

Runner49 tests the official Ref2V Turbo4 path against exact H0 inputs:

- LoRA `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- strength1.0;
-4 steps;
- `res_multistep/simple`;
- same448×800/124f/24fps;
- same Picture1/Video1/ref_image_size/seed/prompt.

Turbo becomes production-eligible only if it materially reduces wall clock without losing H0-level topology/identity/motion quality.

## H3 temporal rule

Do not default to 8–12 **generated H3 frames**.

Current H3 uses the `17k+5` temporal grid and documents trained video range around124–362 frames @24fps.

Production baseline is therefore:

`fast124-frame motion master -> distill one useful action/cycle -> ~12 runtime frames`

Shorter H3 windows may be tested later only with explicit quality evidence.

## H1-S locomotion production

After the throughput path is chosen:

1. use a fixed-camera full-body screen-left real walk with safe real margins and one clean gait cycle;
2. keep the proven124-frame H3 regime; a clean gait cycle may be automatically repeated/tiled through the reference interval;
3. generate a complete H3 motion master;
4. automatically detect one coherent generated gait cycle;
5. select ~12 phase-distributed frames;
6. automatically reject crop/structural failures;
7. automatically segment complete character including hair/cloth/chains;
8. pivot-align to stable ground while preserving valid vertical bob;
9. build a high-resolution transparent action strip/contact sheet.

No manual masks, repainting or frame alignment.

## Final pixel-art reconstruction — REQUIRED / NOT YET PROVEN

The H3 motion-master frames must then be reconstructed as deliberate high-quality pixel art.

Preferred validation architecture:

- canonical Exilada pixel-art reference;
- complete selected action strip/contact sheet supplied together so all frames share one coherent design/palette;
- pose/silhouette/foot placement preserved from H3;
- stronger pixel clustering, palette discipline and material readability than the current reference;
- exact pixel grid, no blurry interpolation.

Simple nearest-neighbor downscale/palette quantization is a cheap control only and is not assumed sufficient.

## First walk runtime target

- visible protagonist ~128px tall;
-12 unique frames;
- art playback around12fps, with actual action speed controlled by metadata/gameplay;
-192×192 initial review cells;
-4×3 sheet =768×576;
- transparent RGBA complete-character sprites;
- optional trimmed atlas + JSON frame rectangles/pivots/durations.

## Variation architecture — later

After baseline animation + final pixel-art reconstruction are proven, solve armor/equipment/accessory/damage variation offline.

Candidate production may use source modules/masks/state families internally, but every runtime variant still exports as complete-character animation frames.

## Damage / exposure integration

Offline source state may retain complete body, clothing/armor coverage semantics, damage zones, attachment sockets, anatomical side ownership and surface-state masks.

Those are resolved offline into complete runtime sprite families. Adult nudity/partial nudity remains a legitimate state.

## Automated QA contract

Production batches should check at least:

- full body present;
- stable topology/identity;
- no driver-forced crop inside selected runtime cycle;
- hair/cloth/restraints remain attached and coherent;
- alpha matte preserves all intended extents;
- pivot/ground consistency;
- pixel-art frame consistency;
- no unexpected palette/interpolation blur;
- atlas metadata matches frame geometry/timing.

## Cleanup discipline

- keep Base H3 Ref2VA files;
- add only the single official Turbo4 LoRA for current throughput hypothesis;
- do not accumulate FL2VA/style/alternate quantizations without evidence;
- Wan large checkpoints may be removed while W1H/W1L proof remains;
- keep SSD/Moore evidence until explicit final abandonment.

## Current gate

**Runner49 H0T Turbo4 throughput-quality comparison.**

Do not spend another Base50 hour on a new walking driver before deciding whether Turbo4 can preserve H0 quality at practical speed.
