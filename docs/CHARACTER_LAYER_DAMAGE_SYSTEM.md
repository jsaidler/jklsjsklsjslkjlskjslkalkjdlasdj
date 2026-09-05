# Character Layer, Equipment Damage and Exposure System — Living Plan

Status: **canonical architecture.** Character body, clothing, armor, restraints, equipment, surface states and structural damage are persistent modular systems. They must not be regenerated independently per animation frame and must not require body×equipment×damage×animation combinatorial sprite authoring.

## Purpose

This document defines how a character is assembled, damaged, exposed and rendered across animation while preserving anatomical side, attachment ownership, body continuity and systemic state.

The system must support, without manual frame repair:

- removable and replaceable clothing;
- damaged/torn clothing;
- damaged/broken armor;
- exposed body under missing/damaged layers;
- blood, dirt, wetness, burns and other surface states;
- restraints/chains and weapons attached to stable sockets;
- severed body parts carrying the correct attached clothing/equipment;
- wind/secondary motion on eligible layers;
- persistent state across animation clips and gameplay sessions.

## Canonical character layer stack

The logical stack is not a fixed painter's-order list; actual visibility is depth/occlusion-aware. Every layer has a stable semantic ID.

1. **Body base**
   - complete persistent body geometry;
   - anatomy, skin, scars, wounds and sever zones;
   - exists independently of clothing;
   - owns canonical anatomical left/right identity.

2. **Hair / body-attached secondary masses**
   - persistent rigged masses/curves;
   - may use deterministic secondary motion and wind response;
   - not regenerated as independent frame detail.

3. **Underlayers / soft clothing**
   - wraps, underwear, tunics, shirts, trousers, bindings and similar garments;
   - separate meshes/material regions from body;
   - may be damaged, removed or exposed.

4. **Outer clothing**
   - coats, skirts, loose cloth, capes, belts and layered fabric/leather pieces;
   - persistent objects with attachment and damage zones.

5. **Armor**
   - rigid/semi-rigid plates, mail, leather armor, helmets, greaves, bracers, shields where equipped;
   - each piece has its own condition and structural state.

6. **Restraints/accessories**
   - shackles, chains, jewelry, pouches and other persistent attachments;
   - fixed named sockets/endpoints.

7. **Weapons/tools**
   - socketed modular objects;
   - own durability/damage state where applicable.

8. **Surface-state overlays**
   - blood, dirt, mud, wetness, frost, burn/soot, poison/acid residue and wear;
   - applied through semantic/body/material masks rather than full-character redraw.

9. **Transient VFX**
   - sprays, sparks, droplets, debris, smoke, impact flashes and similar event-driven effects;
   - not persisted as part of the base character sprite unless converted into a persistent surface/world state.

## Stable identity and ownership

Every persistent object must carry at least:

- unique asset/state ID;
- equipment slot/layer class;
- material class;
- parent body region or named socket(s);
- anatomical side where applicable (`L`, `R`, `center`);
- coverage/body-region mask;
- occlusion/depth behavior;
- structural damage zones;
- surface-state mask channels;
- detach/drop rule;
- sever inheritance rule;
- wind/secondary-motion eligibility;
- persistence/serialization state.

No render/edit process is allowed to reinterpret a left-side item as right-side or vice versa.

## Damage model — two independent axes

Damage is separated into **surface damage** and **structural damage**.

### Surface damage

Does not change the topology of the item.

Examples:

- scratches;
- abrasions;
- blood staining;
- dirt/mud;
- wetness;
- soot/scorch marks;
- discoloration;
- wear/polish loss;
- shallow cuts/marks that do not alter silhouette.

Surface damage should be represented by persistent semantic/material masks and parameterized pixel rendering where possible.

### Structural damage

Changes silhouette, coverage, attachment or physical behavior.

Examples:

- cloth tear/opening;
- missing cloth section;
- broken strap;
- detached sleeve/panel;
- armor dent severe enough to alter silhouette;
- cracked/broken plate;
- missing armor segment;
- displaced piece;
- shattered shield section;
- severed equipment attachment.

Structural damage uses a finite set of deterministic geometry/mesh state transitions rather than arbitrary per-frame generative reconstruction.

## Material-specific damage language

### Cloth

Supported classes include:

- cut;
- tear propagation;
- puncture;
- frayed edge;
- burned edge/hole;
- soaked/wet state;
- blood/dirt absorption;
- partial loss/detachment.

### Leather / hide

- cut;
- puncture;
- abrasion;
- strap failure;
- split seam;
- burn/scorch;
- deformation;
- wet/darkened state.

### Metal armor

- scratch;
- dent;
- edge deformation;
- crack where material/design permits;
- buckle/collapse;
- broken fastening;
- missing plate/component;
- blood/dirt/water surface state.

### Wood / bone / rigid organic equipment

- scratch;
- crack;
- splinter/chip;
- fracture;
- missing section;
- complete break where gameplay permits.

The final visible pixel vocabulary for each material is validated at gameplay scale; the physical state is independent from how many pixels can represent it.

## Damage zones and state progression

Each garment/armor asset defines named damage zones such as:

- front torso;
- back torso;
- left/right shoulder;
- left/right upper arm;
- left/right forearm;
- waist;
- left/right thigh;
- left/right lower leg;
- edge/hem/strap-specific zones.

Damage events target a known zone based on hit location/direction and item coverage.

A zone may have a small deterministic progression, for example:

`intact -> surface_damaged -> structurally_damaged -> failed/missing`

The exact number of states is asset/material dependent. We do not require every item to implement every stage.

## Body exposure

The complete body base always exists under removable/damageable clothing.

When clothing or armor coverage is lost:

- underlying clothing layer becomes visible if present;
- otherwise the correct body region becomes visible;
- scars/wounds/blood remain attached to the body region;
- no new body pixels are generated from scratch;
- exposure persists across every animation because it is a state of the modular character, not of one sprite frame.

This architecture supports partial or complete unclothed states without making clothing technically mandatory.

## Combat and armor logic integration

Visual damage must be causally connected to gameplay state where appropriate.

Examples:

- armor absorbs/deflects a hit and receives a dent/scratch;
- fastening failure causes a plate to detach and changes protection;
- cloth is cut at the actual hit region;
- shield structural failure changes collision/defense state;
- broken armor may expose body or underlayer;
- a severed limb carries/drops any attached compatible garment/armor component according to its sever rule.

Purely cosmetic wear may exist, but structural failure should not visually claim gameplay consequences that are absent unless explicitly designed that way.

## Gore integration

The damage system must interoperate with named anatomical sever zones.

On sever/dismemberment:

- body region is removed at the deterministic cut boundary;
- attached clothing/armor component is either severed with the part, broken, detached or retained according to asset rules;
- wound-cap/gore socket appears at the correct anatomical boundary;
- detached body/equipment objects inherit motion and collision;
- blood emitter originates from the correct wound socket;
- no intact hidden layer may incorrectly cover the removed body part.

## Wind and secondary-motion integration

Eligible damaged pieces can alter secondary motion.

Examples:

- torn cloth produces a loose flap;
- broken strap allows a plate/pouch to swing or fall;
- detached cloth becomes world debris;
- exposed loose layers react to wind more strongly.

These effects must remain deterministic and scriptable. If a damage state requires routine manual simulation repair, that implementation is rejected.

## Liquid and surface-state integration

Coverage determines where liquids/states accumulate.

Examples:

- armor can shield cloth/body from some splashes;
- blood may stain outer cloth before underlying skin;
- rain/water can wet exposed skin and clothing separately;
- damage holes allow underlying layers/body to receive direct state;
- mud/wetness can change discrete material palette ramps.

State propagation is causal and mask-based, not random decoration.

## Rendering/composition architecture

The production target avoids combinatorial sprite explosion.

Preferred data flow:

`body + modular layer geometry/state -> deterministic rig/depth -> semantic passes -> native-pixel renderer -> modular depth-aware composition`

The renderer may output separate pixel layers/passes for:

- body;
- hair;
- each relevant clothing/armor slot/group;
- equipment;
- state overlays;
- depth/occlusion metadata.

If fully independent per-item depth composition proves impractical at gameplay scale, G6 must choose a bounded front/back/slot-family strategy before the equipment catalog is expanded.

## Persistence/data model

Character save/state must be able to represent, without saving individual rendered frames:

- equipped item IDs;
- per-item durability/condition;
- per-zone structural state;
- surface-state intensities/masks as required;
- detached/missing components;
- body injury/sever state;
- wetness/blood/dirt and related causal states.

Rendered animation is derived from this state.

## Validation gate — G6D clothing/armor damage

Before broad equipment production, test one representative soft garment and one representative rigid armor piece on the generic/early production character.

The test must include:

1. intact state;
2. surface damage;
3. structural damage changing silhouette/coverage;
4. one detach/broken-fastener event;
5. correct body/underlayer exposure;
6. the same states across locomotion and one high-energy action;
7. blood and wetness interaction;
8. one wind interaction on a damaged soft piece;
9. deterministic headless rebuild/export from saved state.

### PASS requires

- no frame-specific redraw dependency;
- damage remains on the same item/body zone through motion;
- anatomical left/right ownership remains stable;
- exposure is correct;
- occlusion/depth is correct;
- structural state matches gameplay state;
- no body×item×damage×animation combinatorial asset explosion;
- native-pixel readability remains acceptable.

## Kill switches

- If a damage type requires generative reconstruction per frame, reject that implementation.
- If structural damage cannot remain stable across arbitrary clips, rework geometry/state ownership before producing items.
- If modular composition causes unacceptable occlusion artifacts, solve the layer architecture before adding more equipment.
- If damage-state multiplication becomes combinatorial, reduce to semantic overlays + a small deterministic set of silhouette-changing structural variants.
- If damaged secondary motion needs manual Blender cleanup per clip, simplify the physical model.

## Locked production rule

**Clothing and armor damage are not optional polish. They are first-class systemic character state and must be supported by the canonical deterministic character pipeline before content production scales.**
