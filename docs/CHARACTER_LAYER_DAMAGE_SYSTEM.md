# Character Layer, Equipment Damage and Exposure System — Living Plan

Status date: **2026-09-07**

Status: **CANONICAL — OFFLINE MODULAR AUTHORING / COMPLETE-CHARACTER RUNTIME SPRITESHEETS**

## Architecture correction

The earlier assumption that the runtime would assemble the visible character from body, hair, clothing, armor, restraints and equipment layers is **abolished**.

The runtime receives **complete already-composed character frames**. Each animation/state family is exported as a full-character spritesheet.

Internal source assets may still be modular offline because that is useful for authoring armor, equipment, damage, exposure and secondary motion. Those modules are production inputs, not runtime-visible character layers.

Locked invariant:

> offline source state may be modular; runtime sprite output is complete/precomposed.

## Current initial-state reference

For the Exilada's first animation proof:

`assets/source/characters/exilada/reference/exilada_master.png`

is the complete initial-state appearance reference.

The walk sequence must preserve and animate together:

- body;
- long hair;
- base clothing/bindings;
- shackles/chains/restraints;
- visible accessories in the master;
- correct occlusion among all of the above.

## Offline logical source stack

The production pipeline may still represent the source character using stable semantic parts such as:

1. body base;
2. hair masses;
3. base clothing / bindings;
4. outer clothing;
5. armor;
6. restraints / accessories;
7. weapons / tools;
8. surface-state masks;
9. transient VFX inputs.

This stack exists to make authoring, motion control and variation manageable. It does **not** imply runtime composition.

## Complete-frame export rule

Before spritesheet export, all persistent visible source systems for the selected character state must be resolved into one temporally coherent frame sequence.

Each exported frame must already contain:

- final body pose;
- body soft-tissue/jiggle state;
- hair secondary motion;
- cloth/binding motion;
- armor/equipment motion if equipped in that state;
- shackles/chains/restraints motion;
- occlusion/depth result;
- selected persistent damage/exposure/surface appearance for that variant.

Detached, frozen or migrating source elements are authoring failures and cannot be delegated to the runtime.

## Equipment / armor variation — OPEN IMPLEMENTATION

The game still requires changing armor, accessories and other equipment states.

The exact scalable production strategy is intentionally deferred until the complete-character animation route is stable.

Allowed future production approaches may include:

- offline recomposition and rerendering into complete variant spritesheets;
- bounded armor/equipment state families;
- reusable offline semantic masks or source modules;
- selective precomputed variant atlases;
- other deterministic offline methods that avoid routine frame-by-frame repainting.

The following is no longer an allowed assumption:

- assembling body + armor + hair + accessories into the final visible character at runtime.

## Damage model retained

Damage still has two conceptual axes.

### Surface damage

Does not materially change silhouette/topology:

- blood;
- dirt/mud;
- wetness;
- scratches;
- scorch/soot;
- discoloration;
- material wear.

These may be produced from semantic masks/parameters offline and baked into the chosen full-character state/variant.

### Structural damage

Changes silhouette, coverage, attachment or physical behavior:

- torn/missing cloth;
- broken straps;
- missing armor pieces;
- detached panels;
- displaced equipment;
- exposed body;
- severed/damaged attached components.

Structural changes require deterministic source-state ownership before complete-frame export.

## Body exposure

The source-authoring character should retain a complete underlying body because clothing may be removed or damaged. This remains an **offline authoring requirement**.

When coverage changes, the offline state resolver determines what becomes visible and exports a new complete-character state/animation family according to the later variation strategy.

No runtime body-under-clothing assembly is implied.

## Stable identity / ownership

Offline source elements should preserve:

- stable item/state IDs;
- equipment slots/classes;
- parent body region/socket;
- anatomical side (`L`, `R`, `center`);
- coverage and occlusion ownership;
- detach/drop rule;
- sever inheritance rule;
- secondary-motion eligibility.

This information prevents left/right migration and makes complete variant generation reproducible.

## Hair / cloth / restraints secondary motion

Hair, loose cloth and chains/restraints are not optional decoration. Their motion is part of the baked animation output.

The authoring system may use temporal image/video priors, deterministic rigs, secondary bones, spring/damped solvers, constrained simulation, offline layer-specific generation/composition or other offline controls, provided the final result is a stable complete-character frame sequence.

## Runner 34 result — IMPORTANT SECONDARY-MOTION EVIDENCE

Runner 34 proved that complete-character frames and spritesheets can be generated/packed successfully from the initial master.

It also proved that **body OpenPose control alone is insufficient** for the locked secondary-motion requirement:

- hair remained mostly frozen/warped;
- cloth did not gain convincing inertial motion;
- jiggle was not controllable/readable enough;
- wrist chain remained largely static;
- ankle restraint/chain detached and mutated in middle frames.

Therefore secondary systems cannot be left to an unconstrained temporal prior if stable ownership/physics is required.

## Next source-authoring requirement

The next offline authoring gate must introduce richer complete-motion control for hair, cloth, restraints/chains and soft tissue while preserving the final complete-frame export invariant.

A hidden modular rig/simulation is explicitly allowed for this purpose because it is an **offline source-control system**, not runtime composition.

## Later G6/G7 decision

After the complete-character animation route is stable, choose how armor/equipment/damage/state variation is generated efficiently offline without combinatorial manual work.

The future system must satisfy both:

1. scalable authoring of variants/states;
2. complete-character runtime spritesheets.

## Kill switches

- If a variation strategy requires routine manual repainting across every frame, reject it.
- If an offline modular source cannot keep ownership/occlusion stable across animation, fix the source architecture before expanding equipment content.
- If secondary motion routinely breaks attachments or anatomical sides, reject/simplify that authoring method.
- Do not solve production complexity by reintroducing runtime character assembly without an explicit new architectural decision.

## Locked production rule

**The visible runtime character is always a complete baked sprite frame. Modular character structure, where useful, belongs to offline authoring only.**
