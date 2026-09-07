# Characters — Living Document

Status: **Exilada core identity and initial condition locked; canonical complete initial-state master approved; runtime complete-character spritesheet architecture locked; offline source modularity retained only for authoring/variation**

This document stores canonical character decisions. It distinguishes fixed identity, initial state, gameplay-variable appearance, canonical reference material and exploratory production techniques so temporary implementation details do not become canon accidentally.

## Process rule — living documentation

All material character decisions and changes must be recorded here as they occur. This document is canonical across chats. When a decision changes, edit this document instead of creating a parallel version or relying on conversation history.

## Exilada — protagonist

### Canonical core

The protagonist is an **adult woman**, currently designated **Exilada**.

Locked traits:

- height: approximately **162 cm**;
- origin: **Ilhas do Sul**;
- adult, mature and severe presence;
- lean, functional and resilient body rather than exaggerated heroic musculature;
- natural adult feminine proportions — **not shortened, squat or deliberately “compact”**;
- olive-to-brown skin;
- hard, mature face;
- very long, heavy, voluminous, messy black hair;
- hair mass is a primary silhouette anchor;
- posture should communicate alertness, contained violence and survival rather than glamour alone;
- character identity must remain recognizable without relying on a particular weapon or complete outfit.

The body should look materially lived-in: fatigue, dirt, wounds and scars may be visible when causally justified by state/history.

### Narrative initial condition

Locked interpretation:

The Exilada was **enslaved and abandoned to die**.

Her initial visual state therefore represents extreme deprivation rather than a designed warrior costume.

This supports:

- almost no possessions;
- minimal clothing;
- torn and degraded cloth;
- improvised bindings;
- visible evidence of captivity;
- partial or complete nudity when appropriate to material/narrative state;
- vulnerability, danger, sensuality and physical presence being allowed to coexist;
- the visual contrast of an exposed, precarious body that remains dangerous.

### Erotic charge — LOCKED 2026-09-05

The Exilada does **not** need to be visually desexualized in order to be treated seriously.

The project's reference lineage — **Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell** — carries an explicit adult erotic/sensual charge. That vocabulary is relevant and must not be automatically removed.

For the Exilada:

- erotic charge is allowed and may be intentional;
- adult nudity or minimal clothing may read as sensual, erotic, heroic, vulnerable, brutal or matter-of-fact depending on scene/state;
- physical attractiveness and sexual presence do not invalidate severity, danger, agency or suffering;
- the body may remain aesthetically charged even when dirty, wounded, exhausted or deprived;
- no blanket rule requires neutral, clinical or anti-erotic framing;
- framing should be intentional to the scene rather than automatically sanitized or automatically sexualized.

## Body / nudity source rule — LOCKED

The offline production character owns a **complete adult body source independent of hair, clothing and equipment**.

Locked consequences:

- the same body identity exists under every garment, binding, hair mass, cuff and chain in authoring;
- removing all clothing/equipment must reveal that same body rather than reconstructing hidden anatomy from a dressed composite;
- nudity is a normal supported world/gameplay state;
- chest and pelvic anatomy must be coherent at native gameplay scale;
- there is no structurally mandatory censor garment;
- permanent scars/body marks belong to body/state authoring, not to a specific garment;
- wounds, blood, wetness, dirt and gore remain attached to the correct body regions.

**Important runtime distinction:** this body-source independence is an offline authoring/state rule. It does **not** mean the runtime assembles a visible body layer under visible clothing. Runtime character frames are complete/precomposed sprites.

## Initial clothing

The approved visual direction uses:

- minimal asymmetrical cloth coverage;
- dirty ragged chest wrap/bandeau;
- torn asymmetrical hip cloth/loincloth;
- occasional cloth bindings on arm or leg;
- bare feet;
- worn, dirty and frayed materials;
- no decorative fantasy-costume logic.

These may remain separate **offline authoring sources** so motion, damage and future variants can be controlled. When the initial state is exported to the game, however, the clothing is already baked into each complete-character animation frame.

## Captivity markers

The **history of captivity is canonical**.

Locked rule:

- cuffs/shackles and broken chain segments may exist as separate offline authoring/state sources;
- chain/restraint state may later be removed, damaged, detached or replaced through offline variant production;
- wrist/ankle attachment relationships must remain coherent across motion;
- the exact anatomical side ownership of every visible initial broken segment is **not independently canonized by temporary proxy scripts**; the approved visual master is the initial-state reference until a semantic equipment/state definition explicitly locks side ownership;
- in the exported initial-state spritesheet, visible shackles/chains are already baked into the complete character frame.

## Weapon rule

**No weapon is part of the Exilada's permanent identity.** Weapons are gameplay-variable equipment.

## Runtime character representation — LOCKED 2026-09-07

The game does **not** construct the visible Exilada from body/hair/clothing/equipment layers at runtime.

Runtime representation:

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

Every frame already includes, where present:

- body motion;
- soft-tissue/jiggle;
- hair motion;
- clothing/binding motion;
- restraints/chains/accessories;
- final occlusion among all parts.

Runtime visible-character layer assembly is **ABOLISHED/CLOSED**.

Offline modular sources are still allowed and likely useful for producing variants efficiently. They are production controls, not runtime rendering components.

## Gameplay-variable appearance

Expected variable systems include weapons, armor, added clothing, restraint/chain state, ornaments/trophies, complete or partial nudity, blood, dirt, wounds, scars, fatigue/injury posture, material wear and other causal state consequences.

The exact scalable production strategy remains open. Current lock:

- variation is solved **offline**;
- exported runtime animation remains complete/precomposed;
- no future design may silently assume that arbitrary body/armor/accessory layers will be assembled visually at runtime.

## Canonical initial-state reference asset

Canonical file:

`assets/source/characters/exilada/reference/exilada_master.png`

For current animation work this is the approved **complete initial-state appearance reference**, not merely an identity/body anchor. It establishes:

- adult lean anatomy/proportions;
- severe mature face;
- olive/brown skin;
- long black hair mass;
- minimal degraded clothing;
- captivity evidence including visible restraints/chain details;
- bare feet;
- weaponless initial identity.

It is not itself the final gameplay sprite, but current complete-character animation generation must preserve this whole initial state.

## Supporting high-resolution nude anatomy reference

Canonical expected local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

Recorded source identity:

- SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`;
- `2048×1401`;
- front / back / profile / front-three-quarter;
- adult natural feminine proportions;
- lean / functional / resilient;
- severe, sensual, dangerous and lived-in;
- full pelvic anatomy visible;
- no occluding garment.

This is anatomy/proportion reference only and is not visible sprite source.

## Locked pixel-art body reference

Marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Recorded source:

- SHA256 `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`;
- `1168×784` JPEG;
- front/back/profile/front-three-quarter;
- adult nude/hairless body;
- pixel-art imagery on flat dark background.

This reference loop is closed. Do not ask for another body turnaround or Grok body reference.

## Canonical production nude/hairless body source — PASS

Canonical production files:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

Recorded facts:

- `37×128` RGBA;
- visible standing height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- front-three-quarter elevated belt-scroller view;
- adult nude/hairless/barefoot state.

This remains a valid **offline body-source/reference artifact**. It is no longer evidence for runtime layered body composition.

## Gameplay-scale identity anchors

These anchors must survive:

1. large dark hair mass when hair is present;
2. adult natural feminine body proportions at ~162 cm identity, lean/functional/resilient — never deliberately shortened or squat;
3. asymmetry of minimal initial clothing;
4. severe posture;
5. readable body/limb separation;
6. captivity evidence in the initial state;
7. strong light/dark grouping between skin, hair and cloth.

Facial microdetail is secondary to silhouette at gameplay scale, but gross facial/anatomical errors are not acceptable.

## Current production architecture

Current runtime/export direction:

`real/captured body motion + offline complete-motion controls + complete-state appearance reference -> complete visible animation frames -> spritesheet/atlas + metadata -> runtime playback`

Offline controls may internally use:

- body rigs/references;
- hair masses;
- clothing sources;
- restraints/chains/equipment sources;
- secondary-motion solvers;
- simulations;
- image/video generation models.

All of those must resolve into **one complete visible character frame before export**.

### Historical staged-layer exploration

The earlier `body -> hair -> clothing/restraints -> layered animation` plan remains useful as a history of source-asset experiments and may inform future offline variant authoring. It is **superseded as a runtime/composition architecture**.

Current route-level animation status is documented in:

- `docs/PROJECT_STATE.md`
- `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
- `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`

## Masculine counterpart — exploratory human-family variant

Exploratory only, not canonical as playable character or alternate protagonist.

## Character-design rules

### Do

- preserve strong silhouettes and mature anatomy;
- distinguish permanent identity/state semantics from temporary generation artifacts;
- let history/simulation affect visual state;
- preserve the approved Exilada body and complete initial-state direction at gameplay scale;
- test production art at gameplay scale and in motion;
- keep offline state sources coherent enough to generate future complete variants;
- allow deliberate erotic/sensual body language where it belongs.

### Do not

- shorten/flatten the body because of the word “compact”;
- make a particular weapon permanent by default;
- reconstruct hidden anatomy by subtracting clothes/hair from a composite;
- turn minimal clothing into generic fantasy-barbarian costume;
- sanitize adult nudity merely because it is erotic;
- accept gross facial/anatomical artifacts;
- accept filtered 3D or superficial pixelation as final production art;
- treat generated exploratory details as canon without approval;
- reintroduce runtime visible-character layer assembly without an explicit architectural decision.

## Open character decisions

Not yet fixed: proper name beyond `Exilada`, exact age, detailed family history, exact enslavement/abandonment circumstances, detailed personality/voice, faction relationships, religion/culture beyond Ilhas do Sul, long-term clothing progression, armor/equipment variant production strategy, final approved gameplay head/face detail treatment, and the role of the masculine counterpart.
