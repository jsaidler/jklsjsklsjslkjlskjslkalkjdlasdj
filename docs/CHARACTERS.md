# Characters — Living Document

Status date: **2026-09-08**

Status: **Exilada core identity locked / existing master reopened for visual revision / adult nudity and severe captivity-cloth damage reaffirmed / local master editor is current gate.**

This document stores canonical character decisions and distinguishes fixed identity, narrative state, gameplay-variable appearance, reference material and temporary generation artifacts.

## Process rule — living documentation

All material character decisions and changes must be recorded here as they occur. When a decision changes, edit this document instead of creating a parallel version or relying on chat history.

## Exilada — protagonist

### Canonical core — LOCKED

The protagonist is an **unambiguously adult woman**, currently designated **Exilada**.

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

The body should look materially lived-in: fatigue, dirt, sweat, wounds, abrasions and scars may be visible when causally justified.

## Narrative initial condition — LOCKED

The Exilada was **enslaved and abandoned to die**.

Her initial state represents deprivation rather than a designed warrior costume.

This supports:

- almost no possessions;
- minimal or absent clothing;
- severely torn and degraded cloth;
- improvised bindings;
- visible evidence of captivity;
- partial or complete adult nudity when appropriate to material/narrative state;
- vulnerability, danger, sensuality and physical presence coexisting;
- an exposed, precarious body that remains dangerous.

## Adult nudity / erotic charge — HARD LOCK

The Exilada does **not** need to be visually desexualized in order to be treated seriously.

- adult nudity is a normal supported character/world state;
- complete nudity is valid when appropriate to state/scene;
- partial nudity is valid and may result naturally from damaged clothing;
- erotic/sensual charge is allowed and may be intentional;
- physical attractiveness and sexual presence do not invalidate severity, danger, agency or suffering;
- a dirty, wounded, exhausted or deprived body may remain aesthetically and erotically charged;
- there is no mandatory censor garment;
- framing should be intentional rather than automatically sanitized or automatically sexualized.

Captivity may be depicted directly. The character's erotic charge is not the same thing as making coercion itself the sole erotic subject.

## Body / nudity source rule — LOCKED

Offline authoring owns a **complete adult body source independent of hair, clothing and equipment**.

Consequences:

- the same body identity exists under every garment/binding/cuff;
- chest and pelvic anatomy must remain coherent when clothing is damaged or absent;
- nudity does not require a substitute garment;
- scars/body marks belong to body/state authoring, not a garment;
- wounds/blood/wetness/dirt remain attached to correct body regions.

This is an offline authoring/state rule only. Runtime frames remain complete/precomposed.

## Initial clothing / exposure direction — REOPENED FOR VISUAL APPROVAL

The existing master does **not** yet push the initial-state clothing damage far enough and currently reads too much like a designed fantasy costume.

Current required exploration space:

- minimal, asymmetrical coverage;
- chest cloth that is severely torn/degraded rather than a neat intact bandeau;
- irregular tears, holes, missing edges and displaced remnants;
- substantially more exposed torso skin than the current master;
- **partial breast exposure is explicitly allowed and desirable as a candidate** when caused by the torn-cloth geometry;
- near-nudity is valid as a candidate;
- complete nudity is valid when deliberately chosen for the state rather than appearing as an accidental generation artifact;
- torn asymmetrical hip cloth/loincloth with similarly damaged and precarious coverage;
- occasional worn cloth bindings on arm/leg only when materially justified;
- bare feet;
- dirty, frayed, materially exhausted fabric;
- no clean decorative fantasy-costume logic;
- no automatic addition of extra cloth merely to censor adult anatomy.

Exact tear geometry and exact amount of breast/pelvic exposure are **not canonized yet**. They are now part of the active local master-revision gate.

## 1980s / inspiration lineage — HARD LOCK / MUST BE VISIBLE

The Exilada must read through the project's principal visual lineage:

- **Heavy Metal**;
- **Conan**;
- **Red Sonja**;
- **Frank Frazetta**;
- **Julie Bell**.

This means more than prompt keywords. The approved master must visibly carry:

- adult sensuality and physical weight;
- danger and severity;
- grime/deprivation;
- strong heroic-but-natural adult anatomy;
- tactile damaged materials;
- pulp-fantasy excess;
- a strong late-1970s/1980s sword-and-sorcery charge;
- a long heavy hair mass that feels physical rather than decorative.

Reject a result that still reads primarily as generic contemporary dark-fantasy concept art, clean MMO character design, cosplay polish, cute/chibi fantasy or sanitized fantasy-heroine key art.

The goal is a lineage/charge, not copying a specific existing composition or character design.

## Captivity markers

The **history of captivity is canonical**.

- cuffs/shackles and broken chain segments may exist as separate offline state sources;
- restraint state may later be removed/damaged/detached/replaced through offline variant production;
- wrist/ankle attachment relationships must remain coherent across motion;
- exact side ownership of every visible initial broken segment is not canonized by temporary proxy scripts;
- exported sprites bake visible restraints/chains into the complete frame.

## Weapon rule — LOCKED

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

## Current Exilada master — PROVISIONAL / REOPENED

Current file:

`assets/source/characters/exilada/reference/exilada_master.png`

It remains useful evidence for:

- adult lean anatomy/proportions;
- severe mature face;
- olive/brown skin;
- long black hair identity;
- weaponless identity;
- broad captivity-state concept.

It is **no longer final visual-design authority** because:

- the cloth damage/exposure is not severe enough;
- the design still reads too generically relative to the locked inspiration lineage.

Do not build new production animation/style validation around it as though the visual design were closed.

## Supporting high-resolution nude anatomy reference — CANONICAL EVIDENCE

Expected local path:

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

This remains anatomy/proportion reference. It can be used by the local master editor to reconstruct anatomy hidden under damaged/removed clothing, but must not force a turnaround layout into the master.

## Local master-revision workflow — CURRENT CHARACTER GATE

Launcher:

`tools/structured-2d-character-pipeline/54_run_exilada_master_editor.ps1`

Application:

`tools/flux-kontext-spike/exilada_master_editor.py`

Detailed record:

`docs/EXILADA_MASTER_REVISION_LOCAL_EDITOR_2026-09-08.md`

The editor exists so the user can work on adult character visual details locally, including clothing damage/nudity, without depending on the chat image-generation surface.

It provides:

- current master input;
- optional nude anatomy reference;
- two optional visual-direction reference uploads;
- editable clothing/tear/exposure brief;
- editable body/identity brief;
- editable material/captivity brief;
- editable pictorial-direction brief;
- iteration-specific instructions;
- seed/steps/guidance/denoise controls;
- candidate versioning and provenance;
- iterative candidate-as-input workflow;
- explicit approval/version backup before replacing the canonical master.

No inference automatically replaces `exilada_master.png`.

## Historical structured-2D/body evidence

Earlier structured-2D assets remain useful research evidence, but old `37×128` / `128px` production-body assumptions are retired as final asset-resolution mandates.

The visible production sprite should preserve the useful resolution of the approved video/frame/render chain. Runtime apparent size is independent.

## Character-design rules

### Do

- preserve mature adult anatomy and identity;
- strengthen the Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell charge until it is visibly present;
- allow deliberate erotic/sensual presence;
- allow severe torn cloth to expose substantially more body when materially/narratively coherent;
- allow adult partial/complete nudity as normal states;
- let history/simulation affect visual state;
- keep long black hair as a major physical silhouette element;
- keep restraints and attachments temporally coherent;
- evaluate the master before spending more animation/render validation time.

### Do not

- shorten/flatten/juvenilize the body for convenience;
- make a weapon permanent by default;
- reconstruct hidden anatomy merely by subtracting clothes/hair from a composite when the approved nude anatomy source exists;
- turn deprivation clothing into a clean generic fantasy-warrior costume;
- sanitize adult nudity merely because it is erotic;
- add censor cloth automatically;
- accept gross facial/anatomical artifacts;
- treat temporary generated details as canon without explicit approval;
- reintroduce runtime visible-character layer assembly;
- call the old `exilada_master.png` visually final while the current revision gate remains open.

## Open character decisions

Not yet fixed: proper name beyond `Exilada`, exact age, detailed family history, exact enslavement/abandonment circumstances, detailed personality/voice, faction relationships, religion/culture beyond Ilhas do Sul, long-term clothing progression, armor/equipment variant production strategy, exact initial tear/exposure geometry, final gameplay head/face treatment, and role of the masculine counterpart.
