# Living World Kernel 0A — Architecture

## Purpose

The first technical milestone is not a combat demo. It is proof that a small sword & sorcery world can be deterministic, causal, inspectable, persistent in principle, and capable of reacting to information rather than omniscient global state.

## Core invariants

1. **World truth and knowledge are separate.** An event may be true while a faction does not know it yet.
2. **Behavior is composed.** Species, culture, faction, role, needs, traits, memory/knowledge, and context contribute to decisions.
3. **Important decisions are explainable.** Utility scores are written to `decision_log` so designers can inspect why an action happened.
4. **Randomness resolves uncertainty; it does not invent motives.** A faction decides to raid because it needs salt and sees an opportunity. Seeded randomness may resolve the uncertain combat outcome.
5. **Random streams are isolated.** World generation, ecology combat, faction combat, and caravan generation have separate deterministic streams.
6. **Simulation is rendering-agnostic.** Nothing in the kernel depends on `Node2D`, sprites, animation, camera, or physics.

## Kernel 0A scenario

Asha is a small settlement dependent on salt from the White Salt Quarry. When stock falls below its reorder point, it requests a shipment. The Salt Bearers dispatch a caravan over the White Road. The Red Knives have their own resource needs and evaluate whether the caravan is worth attacking. Ash hyenas overlap the road and may harass weak caravans when hunger is high.

If bandits attack, the attack exists immediately as world truth. Asha does not learn it immediately: reports travel with delay. Once the Road Wardens receive credible reports, they increase escort strength for future caravans. Successful raiding can temporarily satisfy the Red Knives' salt need, reducing the motive for subsequent attacks; failed raids increase fear and reduce their strength.

This is deliberately small. Its job is to prove a feedback loop, not to simulate an entire civilization yet.

## Execution order per simulated day

1. deliver knowledge packets whose travel delay has elapsed;
2. update ecology and predator hunger;
3. consume settlement resources and create trade requests when necessary;
4. update faction resources and process newly acquired knowledge;
5. dispatch/move caravans and evaluate predator/bandit interactions;
6. persist deterministic RNG stream states.

## Testing contract

Run with Godot 4.x headless:

```bash
godot --headless --path . --script res://tests/kernel_0a_test.gd
```

Print a simulated timeline:

```bash
godot --headless --path . --script res://tools/run_kernel_0a.gd -- 190512 120
```

The test suite checks same-seed determinism, seed divergence, the salt shortage -> trade -> caravan chain, auditable bandit decisions, delayed information propagation, and Road Warden adaptation.

## Next technical increments

- explicit save/load serialization for the whole `WorldState`;
- individual witness knowledge and rumor mutation;
- settlement production/consumption graph beyond salt;
- abstract off-screen agent groups and simulation LOD;
- player intervention hooks with attribution depending on witnesses/evidence;
- inspector UI once a visual Godot shell exists.
