# Character Production Pipeline — End-to-End Living Plan

Status date: **2026-09-08**

Status: **CANONICAL ROADMAP — ALL-LOCAL CHARACTER/ACTION AUTHORING -> H3 BASE50 MOTION MASTER -> AUTOMATIC DISTILLATION -> FLUX.1 KONTEXT PIXEL-ART RECONSTRUCTION -> RUNTIME SPRITESHEET**

Canonical state: `docs/PROJECT_STATE.md`.

Canonical local UI/workflow specification: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Non-negotiable production contract

- final visible language is 2D pixel-art sprite animation for the elevated belt-scroller;
- runtime playback uses complete already-composed character frames;
- runtime character construction from body/hair/clothing/equipment layers is abolished;
- final exported frames contain the complete visible character state;
- motion comes from real driving video rather than unrelated guessed poses;
- anatomy, proportions and left/right identity remain stable;
- hair, cloth, restraints, weapons and secondary masses move coherently;
- no routine manual frame-by-frame repainting, manual masks or per-frame alignment;
- recurring operations must be scriptable/headless;
- normal production should be exposed through one local UI;
- equipment/damage/state variation must scale offline without reintroducing runtime assembly.

Canonical Exilada appearance reference:

`assets/source/characters/exilada/reference/exilada_master.png`

## Production architecture — LOCKED

`reference image or locally generated reference -> relative world scale + real driver + action preset -> H3 Base50 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> FLUX.1 Kontext [dev] pixel-art reconstruction -> transparent spritesheet/atlas + metadata -> runtime playback`

MiniMax H3 painterly/raster video is an **intermediate motion representation**, not final runtime art.

## Character-source modes

The local authoring tool must support:

1. **existing image** — upload an approved complete character reference;
2. **text description** — generate a complete local reference image, select/approve it, then use that image for motion generation.

The exact text-to-image model is still open. SDXL-class and FLUX text-to-image families are current candidates.

## Relative world scale

The authoring job carries explicit `relative_scale` metadata.

- `1.0` = baseline adult-human/Exilada scale;
- Exilada is about `128px` visible height in the canonical gameplay composition at `1.0`;
- different monsters/creatures may be much smaller or larger;
- scale affects target runtime occupancy, cell/atlas dimensions and source-resolution policy;
- scale does not mean non-uniformly stretching existing art.

Exact scale bounds remain open.

## Motion backbone — MiniMax H3 Base Ref2VA

Canonical quality configuration is restored to H0 Base50:

- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no Turbo/FL2VA/style embedding.

Completed H0 evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Verdict: **PASS_CANDIDATE / preferred motion-master quality baseline**.

## Turbo4 — CLOSED AS DEFAULT

The 4-step official Ref2V Turbo experiment was visually rejected by the user.

Do not make it the default production setting. Base50 remains canonical until a faster controlled experiment is visually equivalent.

Record: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

## Action presets

Initial local UI must include common actions and `custom`, including:

- idle, walk, run, jump, land, dodge, roll;
- punch, kick, block, parry, hit reaction, knockdown, get-up, death;
- taunt, dance/gesture;
- sword slash/overhead/thrust, axe swing, spear thrust, bow shot, staff attack, spell cast and special attack.

The real video remains authoritative for the actual motion. Action type supplies metadata and extraction/loop/pivot/event defaults.

## H3 temporal rule

Do not default to 8–12 **generated H3 frames**.

The current proven motion-master regime is `124f@24fps`.

Production baseline:

`124-frame Base50 master -> action-dependent compact frame set -> final renderer`

Typical first final frame sets are 8–16 frames, but no global count is locked.

## Current downstream proof source

The existing H0 video is a **dance/gesture-like action**, not locomotion.

It has already been used to prove basic frame extraction and raster sheet packing. It must now be reused for the first final pixel-art reconstruction test so the downstream pipeline can be validated without paying another Base50 generation cost.

## Automatic action distillation

The system must:

1. extract video frames;
2. identify the useful action interval or loop/cycle;
3. select an action-appropriate compact frame set;
4. preserve action timing and optional event markers;
5. reject obvious crop/structural failures where automatic confidence permits;
6. output high-resolution frames for alpha/rendering.

Manual per-frame selection is not a required production step.

## Automatic alpha/pivot/alignment

The system must:

- isolate complete visible character;
- preserve hair/cloth/weapon/accessory extents;
- output RGBA;
- derive stable action-appropriate pivot/root;
- preserve valid body bob, jump arcs and knockback;
- allocate cells based on action envelope and relative scale.

No routine manual masks or alignment.

## Final pixel-art reconstruction — REQUIRED / CURRENT CANDIDATE

**FLUX.1 Kontext [dev] is the preferred first local model to validate.**

Preferred strategy:

- canonical/approved character reference as identity anchor;
- selected action frames supplied as a coherent strip/shared-context set when practical;
- preserve pose/silhouette/foot placement/frame order;
- reconstruct authored-looking high-quality pixel art with coherent palette and material reading;
- split back to exact cells;
- deterministic pixel-grid/palette QA afterward.

Simple nearest-neighbor downscale/palette quantization is a control only, not the final-art plan.

### License caveat

Open-weight Kontext [dev] is non-commercial. It is suitable for technical validation. Commercial shipping later requires appropriate BFL commercial licensing or a renderer with compatible terms.

SDXL/img2img remains fallback for quality/hardware/license failure.

## Runtime output — LOCKED

Per action/state family:

- motion-master MP4;
- selected transparent PNG frames;
- final pixel-art spritesheet PNG;
- preview GIF/equivalent;
- optional trimmed atlas PNG;
- atlas/action JSON with frame rectangles, pivots, durations and events;
- provenance manifest including source hashes, H3 settings, renderer settings, relative scale and action preset.

Visible runtime character remains one complete rendered sprite per frame.

## Local UI

One local authoring interface is required.

Current V1 scaffold choice: **Gradio**.

Minimum controls:

- character source mode: image / text generation;
- character image or description;
- character name/category;
- relative world scale;
- action-video upload;
- action-type dropdown/custom action;
- optional facing/frame-count override;
- H3 production preset hidden/locked to Base50 by default;
- progress and previews;
- final file access.

## Variation architecture — later

After baseline local authoring + final pixel-art reconstruction are proven, solve armor/equipment/accessory/damage variation offline. Every runtime variant still exports as complete-character frames.

## Damage / exposure integration

Offline source state may retain complete body, clothing/armor coverage semantics, damage zones, attachment sockets, anatomical side ownership and surface-state masks. Those resolve offline into complete runtime sprite families. Adult nudity/partial nudity remains a legitimate state.

## Automated QA contract

Production batches should check at least:

- full body present;
- stable topology/identity;
- no unacceptable source-envelope crop in selected frames;
- hair/cloth/weapons/restraints remain attached/coherent;
- alpha matte preserves intended extents;
- pivot/ground/action-path consistency;
- pixel-art frame consistency;
- no interpolation blur;
- atlas metadata matches geometry/timing;
- relative scale and action metadata are preserved.

## Immediate gate

**Install/validate FLUX.1 Kontext [dev] locally and use the existing H0 dance/gesture motion master to produce the first genuinely final-style pixel-art spritesheet.**

Do not spend another Base50 H3 generation merely to test downstream rendering.
