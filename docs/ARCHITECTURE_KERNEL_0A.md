# Living World Kernel 0A — Architecture

## Purpose

The first technical milestone proves that a small sword & sorcery world can be deterministic, causal, inspectable, persistent, and capable of reacting to information rather than omniscient global state.

## Core invariants

1. **World truth and knowledge are separate.** An event may be true while a faction does not know it yet.
2. **Behavior is composed.** Species, culture, faction, role, needs, traits, memory/knowledge, and context contribute to decisions.
3. **Important decisions are explainable.** Utility scores are written to `decision_log` so designers can inspect why an action happened.
4. **Randomness resolves uncertainty; it does not invent motives.** A faction raids because it needs salt and sees an opportunity. Seeded randomness may resolve the uncertain combat outcome.
5. **Random streams are isolated.** World generation, ecology combat, faction combat, and caravan generation have separate deterministic streams.
6. **Simulation is rendering-agnostic.** Nothing in the kernel depends on `Node2D`, sprites, animation, camera, or physics.
7. **Persistence preserves determinism.** Save/reload must retain RNG stream state, IDs, event history, knowledge, scheduled information and all state needed to continue exactly.

## Kernel 0A scenario

Asha is a small settlement dependent on salt from the White Salt Quarry. When stock falls below its reorder point, it requests a shipment. The Salt Bearers dispatch a caravan over the White Road. The Red Knives evaluate whether resource need and opportunity justify an attack. Ash hyenas overlap the road and may harass weak caravans when hunger is high.

If bandits attack, the attack exists immediately as world truth. Asha learns later through physical information channels. Once the Road Wardens receive credible reports, they increase escort strength. Successful raiding can satisfy the Red Knives' salt need; failed raids reduce strength and increase fear.

## Persistence format — schema 1

`WorldSerializer` stores a versioned envelope containing the complete logical `WorldState`, deterministic RNG stream states and ID counters. Kernel 0A uses Godot Variant binary serialization (`FileAccess.store_var`) rather than JSON so 64-bit RNG state is not coerced through JSON number precision.

This is a prototype persistence contract, not the final long-term save format. Schema versioning begins immediately so migrations can be introduced before real long-lived saves exist.

## Execution order per simulated day

1. deliver knowledge packets whose travel delay has elapsed;
2. update ecology and predator hunger;
3. consume settlement resources and create trade requests;
4. update faction resources and process acquired knowledge;
5. dispatch/move caravans and evaluate interactions;
6. persist current deterministic RNG stream states into `WorldState`.

## Testing contract

```bash
godot --headless --path . --script res://tests/kernel_0a_test.gd
```

The suite checks:

- same seed -> same history;
- different seed -> divergent history;
- salt shortage -> trade request -> caravan;
- bandit need/opportunity -> auditable attack decision;
- world truth precedes Asha's knowledge;
- Road Wardens adapt after learned attacks;
- 120 continuous days == 60 days + save/reload + 60 days.

Trace a world with:

```bash
godot --headless --path . --script res://tools/run_kernel_0a.gd -- 190512 120
```

## Still required before 0A approval

- at least two real simulation LODs;
- materialization/desmaterialization continuity contract;
- richer individual witness/memory propagation;
- runtime execution of the headless test suite proven on Godot 4.7.2.
