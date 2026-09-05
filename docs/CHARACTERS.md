# Characters — Living Document

Status: **Exilada core identity and initial condition locked; canonical high-detail design reference approved; final gameplay pixel-art production master still under development; masculine counterpart exploratory**

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
- olive-to-brown skin;
- hard, mature face;
- very long, heavy, voluminous, messy black hair;
- hair mass is a primary silhouette anchor;
- posture should communicate alertness, contained violence and survival rather than glamour;
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
- partial or near nudity when appropriate to the material reality of the situation;
- vulnerability without erotic framing;
- the visual contrast of an exposed, precarious body that remains dangerous.

### Initial clothing

The approved visual direction uses:

- minimal asymmetrical cloth coverage;
- dirty ragged chest wrap/bandeau;
- torn asymmetrical hip cloth/loincloth;
- occasional cloth bindings on arm or leg;
- bare feet;
- worn, dirty and frayed materials;
- no decorative fantasy-costume logic.

The clothing should read as **residue of captivity and abandonment**, not as an intentional class outfit.

Nudity is acceptable within the mature visual language. The design must treat the body matter-of-factly rather than emphasizing erotic display.

### Captivity markers — updated 2026-09-05

The **history of captivity is canonical**.

The high-detail master includes broken restraint hardware, but production layering is now explicitly separated from permanent body pixels.

Locked production rule:

- **broken chain segments are not baked into the permanent base-body sprite**;
- chain segments may be part of the **initial accessory loadout/state**;
- chain art owns independent sockets/state and may be removed, damaged, detached or replaced without repainting the base character;
- initial chain sockets are planned at both wrists and both ankles;
- exact persistence of cuffs/shackle hardware beyond the initial state remains a separate equipment/state decision.

This is not a narrative retcon. Captivity evidence remains part of the starting condition; only the technical ownership of those pixels changes.

### Weapon rule

**No weapon is part of the Exilada's permanent identity.**

Weapons are gameplay-variable equipment.

A curved blade appeared in earlier exploration, but it is not a fixed protagonist attribute and must not anchor future references.

### Gameplay-variable appearance

Expected variable systems include:

- weapons;
- armor;
- added clothing layers;
- acquired equipment;
- restraint/chain accessory state;
- ornaments/trophies acquired through world interaction;
- blood;
- dirt;
- wounds;
- scars resulting from history;
- fatigue/injury posture;
- material wear;
- other state-driven consequences.

Variation should be causal and constrained by world simulation whenever feasible.

## Canonical reference asset

Canonical file:

`assets/source/characters/exilada/reference/exilada_master.png`

It is the approved **high-detail design and identity reference** for the Exilada.

It establishes:

- adult lean anatomy and approximate proportions;
- severe mature face;
- olive/brown skin;
- long black hair as dominant silhouette mass;
- minimal degraded clothing;
- captivity/restraint visual history;
- bare feet;
- weaponless base identity;
- full-body reference framing suitable for automated conditioning and structured production work.

### Production clarification

The master is too detailed to be treated as proof of strict production pixel art. It remains canonical for **design identity**, while final gameplay-scale pixel art is a separate production task.

Consequences:

- the master must not be redesigned merely to accommodate a tool;
- final visible pixels must be deliberate modern pixel art at native gameplay scale;
- no manual frame-by-frame redraw burden is assumed for the user;
- generated or rendered intermediate references do not become canon automatically.

## Gameplay-scale identity anchors

These anchors must survive:

1. large dark hair mass;
2. compact adult body proportions;
3. asymmetry of minimal initial clothing;
4. severe posture;
5. readable body/limb separation;
6. captivity evidence in the initial state, preferably through modular accessory/state layers;
7. strong light/dark grouping between skin, hair and cloth.

Facial microdetail is secondary to silhouette at gameplay scale, but gross facial errors are not acceptable. The current structured-2D pipeline therefore isolates `head_face` as a replaceable persistent part rather than forcing whole-character redraws.

## Current production architecture

Current visible-character architecture:

`real motion -> validated hidden rig -> projected joints/depth/sockets -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns control data only, not final visible color pixels.

The current G3S-B decomposition intentionally separates:

- head/face;
- torso/pelvis;
- upper/lower limbs;
- hands/feet;
- hair masses;
- front cloth mass;
- initial chain accessory sockets.

Detailed status is maintained in:

- `docs/PROJECT_STATE.md`
- `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
- `docs/G3S_B_PERSISTENT_PART_DECOMPOSITION_LOG.md`

## Masculine counterpart — exploratory human-family variant

A masculine counterpart has been explored using the same broad reference format and visual language.

Current exploratory traits:

- adult man;
- lean, functional and resilient build;
- long heavy black hair;
- mature severe face;
- dirty/scarred body;
- minimal degraded clothing;
- captivity markers;
- barefoot;
- weaponless reference pose.

### Status

**Exploratory, not canonical as a playable character or alternate protagonist.**

Do not infer narrative role, identity, origin, name or player-selectability until explicitly approved.

## Character-design rules

### Do

- design for actual high-oblique gameplay readability;
- preserve strong silhouettes;
- distinguish permanent identity from equipment/accessories;
- let history and simulation affect visual state;
- use mature anatomy and grounded material logic;
- preserve the canonical design while production-raster translation is developed;
- test every production character at gameplay scale and in motion;
- keep detachable chains/restraints as modular state when practical.

### Do not

- make a particular weapon part of the Exilada by default;
- bake broken chain segments permanently into the base-body sprite;
- turn minimal clothing into a generic fantasy-barbarian costume;
- sexualize deprivation or captivity;
- depend only on portrait-scale facial detail for gameplay identity;
- accept gross facial/anatomical artifacts merely because the macro silhouette works;
- add decorative scars, ornaments or props without systemic/narrative reason;
- treat the current high-detail master as if it already proves final pixel-art execution;
- accept a final production solution that merely hides generic illustration behind a superficial pixel filter;
- treat exploratory generated details as canon without approval.

## Open character decisions

Not yet canonically fixed for the Exilada:

- proper name beyond `Exilada`;
- exact age;
- detailed family history;
- exact circumstances and agents of enslavement;
- reason/mechanism of abandonment;
- exact persistence/removal rules for cuffs/shackle hardware after the initial state;
- detailed personality and voice;
- faction relationships;
- religion/culture beyond origin in the Ilhas do Sul;
- exact long-term clothing progression;
- final approved gameplay head/face pixel asset;
- whether the masculine counterpart is playable, an alternate protagonist, an NPC family template or only a production test.
