# Characters — Living Document

Status date: **2026-09-07**

Status: **Exilada core identity and initial condition locked; canonical complete initial-state master retained; runtime complete-character spritesheet architecture locked; W1 painterly/1980s visual direction approved for continued validation; exact initial cloth-tear/exposure pattern still open.**

This document stores canonical character decisions and distinguishes fixed identity, narrative state, gameplay-variable appearance, reference material and temporary generation artifacts.

## Process rule — living documentation

All material character decisions and changes must be recorded here as they occur. When a decision changes, edit this document instead of creating a parallel version or relying on chat history.

## Exilada — protagonist

### Canonical core

The protagonist is an **adult woman**, currently designated **Exilada**.

Locked traits:

- height approximately **162 cm**;
- origin: **Ilhas do Sul**;
- adult, mature and severe presence;
- lean, functional and resilient body rather than exaggerated heroic musculature;
- natural adult feminine proportions;
- olive-to-brown skin;
- hard, mature face;
- very long, heavy, voluminous, messy black hair;
- hair mass is a primary silhouette anchor;
- posture communicates alertness, contained violence and survival;
- identity must remain recognizable without relying on a particular weapon or complete outfit.

The body should look materially lived-in: fatigue, dirt, wounds and scars may be visible when causally justified.

### Narrative initial condition

The Exilada was **enslaved and abandoned to die**.

Her initial state therefore represents deprivation rather than a designed warrior costume.

This supports:

- almost no possessions;
- minimal clothing;
- severely torn and degraded cloth;
- improvised bindings;
- visible evidence of captivity;
- partial or complete nudity when appropriate to material/narrative state;
- vulnerability, danger, sensuality and physical presence coexisting;
- an exposed, precarious body that remains dangerous.

## 1980s / inspiration lineage — LOCKED 2026-09-07

The Exilada must continue to be read through the project's principal visual lineage:

- **Heavy Metal**;
- **Conan**;
- **Red Sonja**;
- **Frank Frazetta**;
- **Julie Bell**.

The user explicitly wants an **1980s sword-and-sorcery charge**, consistent with the golden period of these inspirations.

For the Exilada this means adult sensuality, danger, grime, heroic physical presence, damaged materials and erotic charge may coexist without turning her into a clean decorative fantasy costume.

The 1980s influence is tonal and pictorial, not a requirement for VHS/CRT gimmicks.

## Erotic charge — LOCKED

The Exilada does **not** need to be visually desexualized in order to be treated seriously.

- erotic charge is allowed and may be intentional;
- adult nudity or minimal clothing may read as sensual, erotic, heroic, vulnerable, brutal or matter-of-fact depending on state/scene;
- physical attractiveness and sexual presence do not invalidate severity, danger, agency or suffering;
- the body may remain aesthetically charged when dirty, wounded, exhausted or deprived;
- framing should be intentional rather than automatically sanitized or automatically sexualized.

Captivity may be depicted directly, but the body/character's erotic charge should not be confused with making coercion itself the only erotic subject unless explicitly chosen for a scene.

## Body / nudity source rule — LOCKED

Offline authoring owns a **complete adult body source independent of hair, clothing and equipment**.

Consequences:

- the same body identity exists under every garment/binding/cuff;
- nudity is a normal supported gameplay/world state;
- chest and pelvic anatomy must remain coherent;
- there is no mandatory censor garment;
- scars/body marks belong to body/state authoring, not a garment;
- wounds/blood/wetness/dirt remain attached to correct body regions.

This is an offline authoring/state rule only. Runtime frames are complete/precomposed.

## Initial clothing — UPDATED 2026-09-07

The current approved direction uses:

- minimal asymmetrical cloth coverage;
- dirty, ragged and **more severely torn** chest cloth rather than a neat intact bandeau;
- irregular tears/holes/edge loss that may expose substantially more torso skin;
- **partial breast exposure is allowed and desirable as a candidate initial-state treatment** when it follows the torn-cloth logic;
- torn asymmetrical hip cloth/loincloth with similarly degraded edges;
- occasional worn cloth bindings on arm or leg;
- bare feet;
- dirty, frayed, materially exhausted fabric;
- no clean decorative fantasy-costume logic.

Exact tear geometry and exact amount of breast exposure are **not yet canonized** by a temporary prompt. They will be visually approved in a controlled appearance test after the current framing gate.

When exported to the game, all visible clothing is already baked into complete-character animation frames.

## Captivity markers

The **history of captivity is canonical**.

- cuffs/shackles and broken chain segments may exist as separate offline state sources;
- restraint state may later be removed/damaged/detached/replaced through offline variant production;
- wrist/ankle attachment relationships must remain coherent across motion;
- exact anatomical side ownership of every visible initial broken segment is not canonized by temporary proxy scripts;
- the approved visual master remains the initial-state reference until a semantic equipment/state definition locks details;
- exported sprites bake visible restraints/chains into the complete frame.

## Weapon rule

**No weapon is part of the Exilada's permanent identity.** Weapons are gameplay-variable equipment.

## Runtime character representation — LOCKED

The game does **not** construct the visible Exilada from body/hair/clothing/equipment layers at runtime.

Runtime representation:

`complete authored character state -> complete animation frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

Every frame already includes, where present:

- body motion;
- soft-tissue/jiggle;
- hair motion;
- clothing/binding motion;
- restraints/chains/accessories;
- final occlusion.

Runtime visible-character layer assembly is abolished.

## Gameplay-variable appearance

Expected variable systems include weapons, armor, added clothing, restraint/chain state, ornaments/trophies, complete or partial nudity, blood, dirt, wounds, scars, fatigue/injury posture, material wear and other causal state consequences.

Variation is solved **offline**; exported runtime animation remains complete/precomposed.

## Canonical initial-state reference asset

Canonical file:

`assets/source/characters/exilada/reference/exilada_master.png`

For current animation work this remains the approved **complete initial-state appearance reference**. It establishes:

- adult lean anatomy/proportions;
- severe mature face;
- olive/brown skin;
- long black hair mass;
- minimal degraded clothing;
- captivity evidence;
- bare feet;
- weaponless initial identity.

The new 2026-09-07 art-direction decision allows the eventual final state to push the clothing damage/exposure further than the present master, but that change must be explicitly approved rather than inferred silently.

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

This remains anatomy/proportion reference only.

## Historical pixel-art body reference / production body source

Historical structured-2D work remains useful evidence/reference but no longer forces the final visible language to be pixel art.

Recorded artifacts include:

- `tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`;
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`;
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`.

The production body source recorded `37×128` RGBA and visible standing height `128 px`. It remains valid offline anatomy/scale research, not the final visible-art mandate.

## W1 visual result — APPROVED DIRECTIONAL EVIDENCE 2026-09-07

Wan-Animate-2 W1 generated the Exilada from the master plus the official raw driving video.

The user explicitly approved the resulting **painterly illustrated 2D look** as highly desirable for the whole game.

Directional conclusions:

- smooth/painterly rendering is no longer a defect by itself;
- localized, restrained motion blur is acceptable and may improve temporal vitality;
- long black hair moving as a heavy non-rigid mass is strongly desirable;
- the game may look like high-quality animated dark-fantasy illustration rather than deliberate pixel art;
- exact identity, restraints/accessories and framing still require technical improvement.

W1A increased `reference_image_strength` from 1.0 to 1.5. It did not provide a meaningful identity/accessory gain and introduced more blur/ghosting in several phases. Current preferred Wan conditioning balance therefore remains **reference strength 1.0** pending contrary evidence.

## Gameplay-scale identity anchors

These anchors must survive:

1. large dark hair mass;
2. adult natural feminine body proportions;
3. asymmetry/minimality of initial clothing;
4. severe posture;
5. readable body/limb separation;
6. captivity evidence in the initial state;
7. strong grouping between skin, hair and cloth.

Facial microdetail is secondary at gameplay scale, but gross facial/anatomical errors are unacceptable.

## Current production architecture

`complete-state appearance reference + raw driving video + automatic preprocessing -> complete visible animation frames -> automatic spritesheet/atlas + metadata -> runtime playback`

Automatic preprocessing/postprocessing is allowed. Routine manual rigging, keyframing, simulation repair, mask repair, repainting and hand compositing are not.

## Character-design rules

### Do

- preserve strong silhouettes and mature anatomy;
- remember the 1980s / Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell lineage;
- allow deliberate erotic/sensual body language;
- allow torn cloth to expose more body when materially/narratively coherent;
- let history/simulation affect visual state;
- test production art at gameplay scale and in motion;
- keep restraints and attachments temporally coherent.

### Do not

- shorten/flatten the body for convenience;
- make a weapon permanent by default;
- reconstruct hidden anatomy by subtracting clothes/hair from a composite;
- turn deprivation clothing into a clean generic fantasy-warrior costume;
- sanitize adult nudity merely because it is erotic;
- accept gross facial/anatomical artifacts;
- treat temporary generated details as canon without approval;
- reintroduce runtime visible-character layer assembly.

## Open character decisions

Not yet fixed: proper name beyond `Exilada`, exact age, detailed family history, exact enslavement/abandonment circumstances, detailed personality/voice, faction relationships, religion/culture beyond Ilhas do Sul, long-term clothing progression, armor/equipment variant production strategy, exact initial tear/exposure geometry, final gameplay head/face treatment, and role of the masculine counterpart.
