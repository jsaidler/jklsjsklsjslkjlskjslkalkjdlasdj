# Roguelite — Core Game Vision

Status: **canonical high-level game vision.** This document defines what the game is. Production pipelines, character art, animation and tooling are subordinate to these gameplay/systemic goals.

## Project identity

The game is a **systemic action RPG with roguelite structure, persistent fortress growth and a living sword-and-sorcery world**.

The design goal is not to imitate one existing title. The useful shorthand is:

- the systemic/world fantasy that games such as *Conan Exiles* suggest, but pushed toward a more autonomous and causally simulated world;
- the immediacy, spatial readability and physical combat language of arcade belt-scrolling beat'em ups;
- roguelite expedition/risk structure and meaningful meta-progression;
- persistent protagonist, fortress and world consequences rather than disposable disconnected runs.

The game must remain viable for end-to-end production through ChatGPT and project tooling without a conventional art/content team.

## Five coupled layers

### 1. Living world

The world exists as a system rather than as a static collection of quests waiting for the player.

Cultures, peoples, creatures, settlements, resources and factions should act from constrained rules such as:

- species/race and culture;
- needs and resource access;
- geography and climate;
- security and military pressure;
- trade and scarcity;
- relationships and prior history;
- population state;
- material condition;
- territory and migration pressure.

Procedural generation must be **causal and behavior-driven**, not arbitrary content randomization.

Desired consequences include, where feasible:

- settlements growing, declining, moving or disappearing;
- territorial conflict and occupation;
- resource shortages changing behavior;
- migration and displacement;
- equipment and resources circulating after conflict;
- populations reacting to player intervention and to each other;
- persistent evidence of prior events;
- emergent situations that do not require a hand-authored quest to become meaningful.

The aspiration of an effectively long-lived or "infinite" game comes from a rich evolving state space, not endless randomly generated quest text.

### 2. Fortress / persistent base

The player establishes a persistent foothold in the world.

The fortress is not merely an upgrade menu between runs. It is part of the same simulated world and should be able to affect and be affected by it.

Its progression may include:

- shelter and defenses;
- population;
- production and storage;
- specialists and functions;
- resource flows;
- territorial influence;
- security;
- relationships with nearby groups;
- expansion and new capabilities.

The intended progression language is closer to:

`survival -> foothold -> settlement -> production -> defense -> influence -> expansion`

than to a sequence of abstract percentage bonuses.

### 3. Protagonist meta-progression

The Exilada persists as an individual across the broader game structure.

Progression can include:

- learned capabilities;
- physical competence;
- equipment;
- knowledge;
- relationships;
- wounds/scars and other persistent history where systemically appropriate;
- access to places, people and systems;
- changes in status or world role.

Weapons are equipment state, not permanent identity anchors.

### 4. Expeditions / runs

The player repeatedly leaves relative safety and enters dangerous spaces for exploration, combat, resources, knowledge and intervention.

Runs are not isolated arcade stages detached from the world. Their outcomes must feed back into:

- the Exilada;
- the fortress;
- faction/world state;
- access and future opportunities;
- local danger and resources.

The world may also change independently while the player acts elsewhere.

### 5. Immediate gameplay

Moment-to-moment play should inherit the clarity and physical directness of arcade beat'em ups while being designed as a contemporary systemic action game.

Desired properties:

- immediate spatial readability;
- continuous movement rather than grid stepping;
- strong control of distance and positioning;
- enemies exerting different kinds of group pressure;
- readable impact and physicality;
- compact but meaningful combat spaces;
- weapons, obstacles, vertical layers and environment changing encounters;
- enemy behavior derived from role/species/culture/state instead of generic random aggression;
- bosses and elite enemies relying on behavior, context and readable mechanics rather than inflated hit-point pools.

## World-space presentation baseline

### Locked baseline: elevated 2D belt-scroller / false 3D

The current preferred gameplay projection is a **2D elevated belt-scroller with false-3D spatial reading**.

This is not a pure side-scrolling platformer.

The player moves primarily across the screen while also moving continuously along a walkable depth axis. The camera is elevated enough to expose ground plane, spatial relationships and overlapping depth, but the protagonist remains large and readable in a mostly lateral / three-quarter action presentation.

This choice is intended to preserve:

- the spatial immediacy of arcade beat'em ups;
- clear full-body character animation;
- strong weapon/combat readability;
- layered environments with foreground/background depth;
- doors, stairs, bridges, paths, interiors and elevation cues;
- a convincing false-3D world while keeping production fundamentally 2D.

It also materially reduces production complexity compared with an eight-direction isometric/top-down character system.

### Not locked

The following still require gameplay-composition validation:

- exact camera elevation/pitch;
- exact walkable depth-band size;
- perspective versus orthographic-like treatment;
- amount of vertical/elevation traversal inside a scene;
- exact protagonist screen height;
- internal native raster if `640 × 360` proves unsuitable;
- number of distinct character facing families required beyond left/right mirroring;
- camera follow, framing and zoom behavior.

## Map structure

The living world does not require a single continuous open-world camera presentation.

A valid structure is a persistent world composed of connected, dense gameplay spaces such as:

`road -> forest -> bridge -> settlement -> ruins -> fortress`

with branches, alternate routes, interiors and stateful ownership/conditions.

Each space can be authored/procedural-systemic as a belt-scroller map while the higher-level world simulation persists across them.

The camera therefore does not need to reproduce the full freedom of the simulation. It needs to make the player's local interactions legible and satisfying.

## Design rules

- Do not confuse the current character-art spike with the game itself.
- Visual production decisions must be evaluated against the needs of the living world, fortress, progression and combat systems.
- Procedural systems must express causes, constraints and history rather than decorative randomness.
- Content scalability matters: the pipeline must support many humans, creatures, equipment states and world conditions without multiplying manual art labor beyond feasibility.
- Dense meaningful spaces are preferred over large areas whose main function is traversal time.
- Combat difficulty should emerge from behaviors, compositions, resources, terrain and state; avoid boss design based primarily on health inflation.

## Current project priority

The immediate project focus remains **visual-production feasibility**, using the Exilada as the first representative production character.

Reason:

Before building the game at scale, the project must prove that its chosen 2D visual language can actually produce:

1. a convincing protagonist at gameplay scale;
2. reproducible animation;
3. equipment/state variation;
4. characters that inhabit the selected false-3D projection coherently;
5. a scalable production route that does not require manual frame-by-frame art from the user.

This is a feasibility gate for the whole game, not a change of project scope.
