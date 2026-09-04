# Animation Source Library — Living Production Catalog

Status: **canonical source/ingestion policy for reusable motion assets.** The project must prefer permissively licensed, scriptable, locally cacheable motion sources. Animation acquisition is treated as production infrastructure, not ad-hoc browsing.

## Core rule

Blender is the deterministic motion/rig processing tool, not the sole animation source.

The production library is built from external motion assets imported/retargeted into canonical rig families and then normalized, tagged, versioned and cached locally.

Primary source selection criteria:

- commercial use permitted;
- raw asset redistribution restrictions understood and respected;
- downloadable/cacheable locally;
- importable into Blender by script (`.blend`, `.fbx`, `.glb`, `.bvh`, `.amc/.asf` through conversion tooling);
- no recurring GUI/manual requirement for production;
- enough motion coverage to justify ingestion/normalization work;
- source provenance and license recorded per clip.

A source that requires an interactive account may be used opportunistically, but cannot be a required dependency of the automated production pipeline.

## Humanoid sources

### Quaternius — Universal Animation Library

License: **CC0**; free for personal, educational and commercial use.

Coverage documented by source:

- 120+ humanoid animations;
- 8-direction locomotion;
- walk / jog / sprint;
- push;
- crawling;
- swimming;
- sitting;
- death;
- combat / gun;
- emotes and other actions.

Formats include FBX, GLB and Blender source variants. Built around a reusable humanoid rig and intended for retargeting.

Use in project: **primary curated humanoid library candidate.**

### Quaternius — Universal Animation Library 2

License: **CC0**; free for personal, educational and commercial use.

Coverage documented by source:

- 130+ additional humanoid animations;
- melee and armed combos;
- 3- and 4-hit combos with individual hits/recoveries;
- parkour;
- farming;
- fishing;
- zombie locomotion;
- additional action coverage complementary to the first library.

Use in project: **primary combat/action expansion candidate.**

### Carnegie Mellon Motion Capture Database

License/use policy: dataset states free for all uses; may be included in commercially sold products; raw data may not be resold directly even in converted form.

Scale:

- thousands of recorded trials;
- locomotion;
- human interaction;
- environmental interaction;
- sports/physical activities;
- scenarios/behaviors.

Especially relevant confirmed motion examples include:

- walking and uneven-terrain walking;
- careful / creeping / expressive walks;
- limping and hurt-leg walks;
- laying down and getting up;
- get-up from face-down / side / back;
- swordplay;
- stairs;
- stretching and many other natural recorded motions.

Use in project: **primary real-mocap source for natural locomotion, injury/recovery and specialized physical motion.**

Important quality note from CMU: hand/toe data may be noisy and some older captures are lower quality. Ingestion must therefore include clip QA and contact cleanup rather than assuming every trial is production-ready.

### Adobe Mixamo

Official Adobe FAQ states:

- free with an Adobe ID;
- no Creative Cloud subscription required;
- characters and animations may be used royalty-free in personal, commercial and non-profit projects, including games;
- current autorigger/animation library is for biped humanoids only.

Project policy: **secondary/opportunistic source, not a mandatory automated dependency.**

Reason: acquisition normally requires the web service / Adobe account and there is no project-approved unattended batch-download API. Raw Mixamo animation files also must not be redistributed as standalone asset packages.

If specific missing motions are only available there, they may be acquired once and cached locally with provenance/license metadata, but the main pipeline must remain functional without recurring Mixamo interaction.

## Animal / creature sources

### Quaternius — Ultimate Animated Animal Pack

License: **CC0**.

Coverage:

- 12 different animals;
- more than 12 animations per animal;
- attack;
- death;
- kicks;
- gallop;
- walk;
- jump;
- additional species-specific motions.

Formats include FBX, OBJ, glTF and Blend.

Use in project: **initial quadruped/animal motion reference and rig-family validation source.**

### Quaternius — Farm Animal Pack

License: **CC0**.

Coverage:

- 7 animated farm-animal models with their own animations.

Use in project: supplemental quadruped/ambient-fauna source.

### Quaternius — Animated Monster Pack

License: **CC0**.

Coverage:

- 4 animated monsters with their own animations.

Use in project: non-human creature motion/reference source.

### Quaternius — Animated Dinosaur Pack

License: **CC0**.

Coverage:

- 6 animated dinosaurs with their own animations.

Use in project: bipedal/non-human and large-creature motion/reference source.

### Quaternius — Bestiary / Dungeon Monsters

Free for personal, educational and commercial use; humanoid-rigged monsters compatible with the Quaternius Universal Animation Library.

Use in project: useful for proving that a common humanoid animation library can drive non-human fantasy silhouettes while keeping one canonical rig family.

## Rig-family strategy

Do not force every creature through one humanoid skeleton.

The production library will normalize motions by **rig family**, for example:

1. humanoid biped;
2. quadruped;
3. avian / winged biped;
4. serpentine;
5. arachnid / multi-legged;
6. large heavy creature / special rigs.

Within a rig family, clips are retargeted to a canonical project skeleton and exposed through common semantic tags.

Between rig families, only behavior semantics are shared, not bone topology.

## Motion taxonomy

Every ingested clip receives machine-readable metadata such as:

- `family`: humanoid / quadruped / ...
- `category`: locomotion / combat / recovery / idle / traversal / social / work / injury / death / swim / etc.
- `action`: walk / sprint / limp / get_up_back / sword_slash / swim_forward / breathe_heavy / ...
- `weapon_class`: none / sword / axe / spear / staff / bow / shield / ...
- `stance`: neutral / defensive / wounded / exhausted / ...
- `loop`: true/false;
- `root_motion`: true/false;
- `contact_events`: foot/hand/weapon contacts;
- `source` and original clip identifier;
- `license` and attribution/redistribution constraints;
- quality flags;
- natural speed / stride / duration;
- retarget version/hash.

This lets gameplay request semantic motion without depending on source-specific filenames.

## Motions that should be procedural/additive instead of library-dependent

Not every state needs a dedicated mocap clip.

Good additive/procedural candidates include:

- breathing intensity;
- fatigue sway;
- minor pain posture;
- head/look offsets;
- weapon aim offsets;
- recoil layers;
- subtle idle variation;
- small secondary hand/shoulder adjustments;
- contextual leaning on slopes or acceleration.

For example, breathing can be a deterministic additive chest/spine/shoulder layer whose amplitude/frequency responds to exertion rather than selecting dozens of almost-identical full-body clips.

Major topology/weight-bearing motion such as walking, falling, getting up, swimming, striking or limping should still begin from captured/curated motion when available.

## Blender ingestion pipeline

All reusable source animation is converted into a canonical local library through headless scripts:

`download/cache -> license/provenance manifest -> import -> source skeleton inspection -> retarget -> normalize axes/scale -> contact/root extraction -> optional cleanup -> bake -> QA -> canonical action library`

The user does not perform retargeting or animation editing manually.

## Lighting / VFX opportunity created by the hidden 3D backbone

Blender also becomes a deterministic **production-time lighting/VFX factory**, while the final visible game remains true pixel art.

Useful outputs include:

- stable shadow/occlusion geometry;
- light-direction and light-ID masks;
- view/world normals;
- depth;
- material/body IDs;
- rim/light masks;
- environment interaction reference;
- particle/VFX simulation passes.

Potential production uses:

- blood spray trajectories;
- dust impacts;
- sparks;
- debris;
- rain/snow reference and spawn masks;
- smoke/fire reference simulations;
- water splash/reference motion;
- cloth/hair secondary motion;
- weapon trails;
- contact-based effects.

The final pixel result must still pass through the project pixel-specific renderer or authored VFX rules. A conventional smooth Blender render or simulation is never accepted merely because it is physically plausible.

For many runtime effects, the preferred architecture may be:

`Blender simulation/reference -> deterministic pixel VFX atlas/parameters -> runtime particle system`

rather than rendering every effect instance offline.

## Automation and access policy

The assistant may research and download public assets when a stable public URL and license permit it, and may write scripts that do the same locally.

Sources requiring interactive authentication or account-specific access are not assumed to be fully automatable. They are supplemental only unless a supported automated access method is explicitly validated.

## Immediate library-validation goal

Before mass-downloading assets, prove the ingestion architecture with a deliberately small but varied set:

1. one natural humanoid walk;
2. one limp;
3. one fall/get-up or ground-recovery clip;
4. one armed attack;
5. one swim;
6. one quadruped walk/attack pair.

If these can all be imported/normalized/retargeted/QA'd headlessly into canonical rig families, the same ingestion system can expand to the broader free libraries without requiring the user to learn Blender.
