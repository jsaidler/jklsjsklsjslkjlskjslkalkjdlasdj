# Characters — Living Document

Status: **Exilada core identity and initial condition locked; canonical identity master approved; high-resolution body reference approved; final gameplay pixel-art body master still under development; masculine counterpart exploratory**

This document stores canonical character decisions. It distinguishes fixed identity, initial state, gameplay-variable equipment, canonical reference material and exploratory variants so temporary production details do not become canon accidentally.

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

### Body-base and nudity rule — LOCKED 2026-09-05

The production character owns a **complete adult body base independent of hair, clothing and equipment**.

This is not an alternate costume or a special generated nude version. It is the canonical underlying character body from which every equipped state is composed.

Locked consequences:

- the body exists completely under every garment, binding, hair mass, cuff and chain;
- removing all clothing/equipment reveals the same persistent body rather than reconstructing hidden pixels;
- nudity is a normal supported world/gameplay state;
- chest and pelvic anatomy must be coherent at native gameplay scale;
- the body may be framed neutrally, erotically, heroically, vulnerably or brutally according to scene intent;
- there is no structurally mandatory censor garment;
- hair is a separate asset/layer and the body base itself is hairless;
- permanent scars/body marks belong to the body or body-state overlays, not to clothing;
- wounds, blood, wetness, dirt and gore remain attached to the correct body regions;
- severed body parts inherit/detach compatible clothing/equipment by state rules rather than carrying baked garment pixels.

Current production order is body first, then hair, then clothing/restraints/accessories.

### Initial clothing

The approved visual direction uses:

- minimal asymmetrical cloth coverage;
- dirty ragged chest wrap/bandeau;
- torn asymmetrical hip cloth/loincloth;
- occasional cloth bindings on arm or leg;
- bare feet;
- worn, dirty and frayed materials;
- no decorative fantasy-costume logic.

These are **equipped overlay assets**, not part of the permanent body sprite.

### Captivity markers — updated 2026-09-05

The **history of captivity is canonical**.

Locked production rule:

- broken chain segments are not baked into the permanent base-body sprite;
- cuffs/shackles are equipment/accessory assets rather than body pixels;
- chain segments may be part of the initial accessory loadout/state;
- chain/restraint art owns independent sockets/state and may be removed, damaged, detached or replaced without repainting the body;
- initial sockets are planned at wrists and ankles.

### Weapon rule

**No weapon is part of the Exilada's permanent identity.** Weapons are gameplay-variable equipment.

## Gameplay-variable appearance

Expected variable systems include weapons, armor, added clothing layers, restraint/chain state, ornaments/trophies, complete or partial nudity according to equipment/state, blood, dirt, wounds, scars, fatigue/injury posture, material wear and other state-driven consequences.

Variation should be causal and constrained by world simulation whenever feasible.

## Canonical identity reference asset

Canonical file:

`assets/source/characters/exilada/reference/exilada_master.png`

It is the approved **high-detail design and identity reference**. It establishes adult lean anatomy/proportions, severe mature face, olive/brown skin, long black hair mass, minimal degraded clothing, captivity history, bare feet and weaponless base identity.

It is not the final gameplay sprite and does not contain enough information to recover the complete nude body by subtraction.

## Approved high-resolution body reference — 2026-09-05

A user-supplied Grok four-view body turnaround is approved as the **primary high-resolution body reference for B3B**.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Recorded source identity:

- SHA256 `2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474`;
- `1168×784`;
- front / back / profile / front-three-quarter views;
- bald/hairless for body-reference purposes;
- adult, natural feminine proportions;
- lean / functional / resilient;
- sensual, severe, dangerous and lived-in physical presence;
- aligned with Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell.

The turnaround contains a minimal dark loincloth/tapa-sexo. This is **reference-only occlusion**, not body geometry and not a permanent coverage requirement. Final B3B pelvic pixels belong to the complete body owner; any later loincloth belongs to clothing/equipment layers.

This body reference resolves the intended body direction. It is **not** production pixel art and must not simply be resized/quantized into the final sprite.

## Gameplay-scale identity anchors

These anchors must survive:

1. large dark hair mass when hair is present;
2. **adult natural feminine body proportions at ~162 cm identity, lean/functional/resilient — never deliberately shortened or squat**;
3. asymmetry of minimal initial clothing when equipped;
4. severe posture;
5. readable body/limb separation;
6. captivity evidence in the initial state through modular accessory/state layers;
7. strong light/dark grouping between skin, hair and cloth.

Facial microdetail is secondary to silhouette at gameplay scale, but gross facial/anatomical errors are not acceptable.

## Current production architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel assets -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns control data only, not final visible RGB, alpha or silhouette.

Locked staged construction:

1. complete nude/hairless body base;
2. separate hair asset/layer family;
3. separate clothing/bindings/restraints/chains/equipment assets;
4. layered animation proof.

Detailed status:

- `docs/PROJECT_STATE.md`
- `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
- `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
- `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`

## Masculine counterpart — exploratory human-family variant

Exploratory only, not canonical as playable character or alternate protagonist.

## Character-design rules

### Do

- preserve strong silhouettes and mature anatomy;
- distinguish permanent body identity from hair/equipment/accessories;
- let history/simulation affect visual state;
- preserve the approved Exilada body direction while translating to production raster;
- test production art at gameplay scale and in motion;
- keep detachable restraints modular;
- keep the complete body valid when garments are absent;
- allow deliberate erotic/sensual body language where it belongs.

### Do not

- shorten/flatten the body because of the word “compact”;
- make a particular weapon permanent by default;
- bake hair, garments, cuffs or chains into the base body;
- reconstruct the body by subtracting clothes/hair from a composite;
- turn minimal clothing into generic fantasy-barbarian costume;
- sanitize adult nudity merely because it is erotic;
- accept gross facial/anatomical artifacts;
- accept filtered 3D or superficial pixelation as final production art;
- treat generated exploratory details as canon without approval.

## Open character decisions

Not yet fixed: proper name beyond `Exilada`, exact age, detailed family history, exact enslavement/abandonment circumstances, detailed personality/voice, faction relationships, religion/culture beyond Ilhas do Sul, long-term clothing progression, final approved nude body-base pixel asset, final approved hair asset, final approved gameplay head/face detail asset, and the role of the masculine counterpart.
