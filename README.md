# Roguelite — Living World Kernel

Codebase for a persistent, potentially unbounded sword & sorcery roguelite sandbox. The project begins with the **Living World Kernel 0A** because world causality, memory and behavioral coherence are the highest-risk systems.

## Current milestone

Kernel 0A simulates a tiny region with:

- two cultures;
- four systemic factions (three civic/commercial actors plus one raider faction);
- one settlement dependent on salt;
- one trade route and procedural caravans;
- a territorial predator species;
- faction needs and utility-based decisions;
- delayed information propagation;
- adaptation after learned threats;
- deterministic per-system random streams;
- an event timeline and decision audit log.

The simulation is deliberately independent of rendering. A world entity is data first; visual/gameplay representation will be attached later according to simulation level of detail.

## Run tests

Godot 4.x:

```bash
godot --headless --path . --script res://tests/kernel_0a_test.gd
```

## Run a simulation trace

```bash
godot --headless --path . --script res://tools/run_kernel_0a.gd -- 190512 120
```

See [`docs/ARCHITECTURE_KERNEL_0A.md`](docs/ARCHITECTURE_KERNEL_0A.md) for the invariants and test contract.
