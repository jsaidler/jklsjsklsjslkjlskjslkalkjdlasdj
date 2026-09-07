# Character Production Pipeline — End-to-End Living Plan

Status date: **2026-09-07**

Status: **CANONICAL PRODUCTION ROADMAP — COMPLETE-CHARACTER SPRITESHEET EXPORT**

## Non-negotiable production contract

The character pipeline must satisfy all of the following:

- final visible language is 2D sprite animation for the elevated belt-scroller;
- runtime playback uses complete already-composed character frames;
- runtime character construction from body/hair/clothing/equipment layers is abolished;
- source-authoring may remain modular offline where that improves variation, damage, attachment or secondary-motion control;
- the final exported frame must contain the whole visible character state;
- motion is based on real/captured/deterministic motion infrastructure rather than guessed unrelated key poses;
- anatomy, proportions and left/right identity must remain stable;
- hair, cloth, restraints and other secondary masses must move coherently through the sequence;
- no routine manual frame-by-frame repainting as the production method;
- recurring operations must be scriptable/headless;
- armor/equipment/state variation must eventually scale without reintroducing runtime character assembly.

Canonical initial Exilada reference:

`assets/source/characters/exilada/reference/exilada_master.png`

For the current proof this master defines the **complete initial visible state**, not merely the body identity.

## Current production architecture

`gameplay camera/scale -> motion control -> complete-state appearance reference -> temporal character authoring -> secondary motion -> complete-frame cleanup/alpha -> spritesheet packing -> runtime playback`

Possible offline internal stages may still include rigs, semantic layers, masks, equipment modules, physics or image/video generation, but they must resolve before export into one complete character image per frame.

## Runtime output — LOCKED

Per animation/state family, expected output:

- complete-character PNG sequence or atlas/spritesheet;
- transparency;
- fixed pivot/root metadata;
- frame duration/timing;
- optional event metadata such as foot contacts, attack markers and hitbox helpers;
- provenance/version manifest.

Runtime does not need to know which pixels belong to body, hair, clothing or equipment unless a later gameplay-specific shader/effect requires auxiliary masks. Even then, the visible character remains one complete rendered sprite.

## Complete-frame animation requirement

Every selected state/variant must bake all relevant motion:

- body locomotion/action;
- soft-tissue/jiggle motion;
- hair motion;
- base clothing/binding motion;
- armor/equipment motion where present;
- shackles/chains/restraints motion;
- correct self-occlusion.

If hair, clothing or restraints are temporally wrong, that is a failure of the authored animation, not a future runtime composition task.

## Current motion backbone

Retained infrastructure:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk` mechanical source;
- eight gait phases;
- locked first gameplay facing `72 deg` azimuth from travel heading.

Runner 33 V2 is not final walk approval. It is retained as the provisional motion driver for the first complete-character proof because the project must now determine whether the whole visible pipeline works before further gait micro-adjustment.

## Current visible-authoring candidate

Exact upstream Sprite Sheet Diffusion is blocked by the unreleased custom multi-scale pose-guider checkpoint.

Current runnable fallback:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion + released SSD denoising/reference UNets`

Runner 30 proved corrected pose registration materially improves visible pose response.

## Immediate gate — complete-character playable proof

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

The proof uses:

- full `exilada_master.png` initial appearance;
- runner-33 V2 eight-frame guide at `72 deg`;
- 512×512 temporal generation;
- 8 frames;
- 25 steps;
- CFG 3.5;
- seed 42;
- fp16;
- connected-background extraction to transparent RGBA;
- 4×2 complete-character spritesheet packing;
- fixed pivot derived from the aligned master pose.

## Current proof success criteria

The first proof does not need final production polish. It needs to answer whether the route is structurally useful.

PASS for continuation requires enough of the following to be true:

- Exilada identity survives across the sequence;
- locomotion reads as a coherent walk;
- limbs do not catastrophically mutate;
- hair behaves as a temporal mass rather than eight unrelated drawings;
- base cloth/bindings move plausibly;
- jiggle/soft-body response is believable enough to preserve physicality;
- shackles/chains/restraints remain attached to the correct anatomical ownership;
- frame alignment/pivot is stable enough for sprite playback;
- the packed spritesheet can be inspected or used directly as a runtime proof.

A failure in secondary motion is not hidden by stripping those elements out; they are part of the test.

## Variation architecture — later production gate

After the initial-state animation route is proven, the project must solve armor/equipment/accessory/damage variation.

The later system may use modular source assets offline, semantic masks, rigs or bounded state families, but each runtime variant must still export as a complete-character animation family.

Candidate later approaches may include:

- offline compositing/regeneration per equipment state;
- precomputed bounded variant families;
- source-state parameterization with automated batch export;
- reusable masks/semantic passes that accelerate offline generation;
- other deterministic authoring strategies.

Do not lock one until the baseline complete-character temporal route is proven.

## Damage / exposure integration

Damage and exposure remain first-class state problems, but they are now interpreted through offline complete-frame variant generation.

The source character may retain:

- complete underlying body;
- clothing/armor coverage semantics;
- damage zones;
- attachment sockets;
- anatomical side ownership;
- surface-state masks;
- structural damage states.

Those source states are resolved offline into complete sprite families as needed by the future state system.

## Automated QA contract

Production batches should validate at least:

- exact frame dimensions;
- transparency integrity;
- stable pivot/root;
- frame count and timing;
- loop closure where relevant;
- identity/silhouette area anomalies;
- attachment continuity;
- foot-contact consistency;
- left/right ownership;
- unexpected detached foreground fragments;
- deterministic output hashes where inputs/tooling are unchanged.

Each batch should also generate:

- contact sheet;
- looping preview GIF/video;
- spritesheet PNG;
- metadata/QA JSON.

## Production scaling principle

Once a working authoring route is validated, a new animation or complete character state should require configuration/source selection and automated generation—not manual repainting of every frame.

Expected later flow:

`motion/action source + selected complete character state -> offline authoring/secondary motion -> complete frames -> QA -> spritesheet + metadata`

## Kill switches

- If the complete-character temporal route cannot keep identity and secondary masses coherent, change visible-authoring strategy before building an animation library.
- If a variation system becomes combinatorial manual labor, redesign offline state generation before expanding equipment content.
- If a tool requires recurring GUI/manual repair per clip, reject or simplify that stage.
- Do not reintroduce runtime character assembly as a convenience without an explicit architectural reopening.

## Current operator step

Run runner 34 and judge the actual complete-character spritesheet before returning to detailed locomotion polish.
