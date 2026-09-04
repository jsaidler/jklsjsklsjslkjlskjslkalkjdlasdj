# Characters — Living Document

Status: **Exilada core identity and initial condition locked; canonical high-detail design reference approved; final gameplay pixel-art production master still under development; masculine counterpart exploratory**

This document stores canonical character decisions. It distinguishes fixed identity, initial state, gameplay-variable equipment, canonical reference material and exploratory variants so temporary generation details do not become canon accidentally.

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

### Captivity markers

The approved initial reference includes visible broken restraints:

- broken wrist shackle with short chain;
- ankle shackle / broken restraint.

The history of captivity is canonical. Whether all restraint hardware remains physically attached throughout long-term progression is still open.

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
- broken restraints;
- bare feet;
- weaponless base identity;
- full-body reference framing suitable for automated pose conditioning.

### 2026-09-04 clarification

The current master is **too detailed to be treated as proof of strict production pixel art**. That is not considered a defect in the character design or, by itself, a failure of a model that faithfully reproduces it.

The asset is therefore canonical for **design identity**, while the final gameplay-scale pixel-art representation is still a separate production task.

Consequences:

- animation/pose experiments must first preserve this design faithfully;
- a model should not be rejected merely for matching the source's high-detail treatment;
- final modern-pixel-art translation must be solved downstream through an automatic/scalable production method;
- no manual redraw by the user is assumed or required;
- the canonical source must not be redesigned just to accommodate one animation model.

## Gameplay-scale identity anchors

Regardless of the eventual production-raster method, these anchors must survive:

1. large dark hair mass;
2. compact adult body proportions;
3. asymmetry of minimal initial clothing;
4. severe posture;
5. readable body/limb separation;
6. captivity markers in the initial state;
7. strong light/dark grouping between skin, hair and cloth.

Facial microdetail is secondary at gameplay scale. Identity cannot depend only on tiny portrait-level features.

## Current animation-production use

The canonical reference is currently used by the active local FLUX.2 Klein + RefControl Pose spike.

The test uses:

- `exilada_master.png` as image 2 / identity reference;
- deterministic OpenPose-style COCO-18 skeletons as image 1 / target pose;
- four fundamental walk key poses;
- one fixed seed and configuration;
- no manual frame correction or seed fishing.

Full technical status is maintained in `docs/ANIMATION_PIPELINE.md`.

## Masculine counterpart — exploratory human-family variant

A masculine counterpart has been explored using the same broad reference format and visual language.

Current exploratory traits:

- adult man;
- lean, functional and resilient build;
- long heavy black hair;
- mature severe face;
- dirty/scarred body;
- minimal degraded clothing;
- broken restraints;
- barefoot;
- weaponless reference pose.

### Status

**Exploratory, not canonical as a playable character or alternate protagonist.**

Do not infer narrative role, identity, origin, name or player-selectability until explicitly approved.

## Character-design rules

### Do

- design for actual high-oblique gameplay readability;
- preserve strong silhouettes;
- distinguish permanent identity from equipment;
- let history and simulation affect visual state;
- use mature anatomy and grounded material logic;
- preserve the canonical design while production-raster translation is developed;
- test every production character at gameplay scale and in motion.

### Do not

- make a particular weapon part of the Exilada by default;
- turn minimal clothing into a generic fantasy-barbarian costume;
- sexualize deprivation or captivity;
- depend on portrait-scale facial detail for gameplay identity;
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
- permanent versus temporary persistence of physical shackles;
- detailed personality and voice;
- faction relationships;
- religion/culture beyond origin in the Ilhas do Sul;
- exact long-term clothing progression;
- final automatic gameplay-scale pixel-art production method;
- whether the masculine counterpart is playable, an alternate protagonist, an NPC family template or only a production test.
