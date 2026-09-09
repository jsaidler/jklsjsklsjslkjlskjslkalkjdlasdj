# Gameplay character scale recalibration — 2026-09-08

Status: **CANONICAL CORRECTION / 128PX HARD BASELINE RETIRED / GAMEPLAY HEIGHT REOPENED**

## Why this correction exists

The previously documented `128px` visible-height baseline for the Exilada at native `640×360` was promoted too aggressively from a narrow internal screen test. Earlier work compared approximately `112/128/144px` and treated `128px` as a local compromise between protagonist legibility and combat space, but that was **not** benchmarked against named belt-scroller references and was never sufficient evidence for a hard production lock.

The user challenged the assumption after inspecting the actual Runner52 sprites, correctly pointing out that the character was being compressed before the pixel-art language itself had been solved.

Therefore `128px` is retired as a hard gameplay or asset-production baseline.

## External sanity check

A useful classic comparator is **Final Fight** arcade:

- published arcade screenshots are `384×224`;
- technical sprite examples for Final Fight list playable-character frames about `93px` high;
- `93/224 ≈ 41.5%` of screen height;
- the same vertical occupancy at `360px` would be about `149px`.

By contrast, `128/360 ≈ 35.6%`.

This does not prove that `149px` is correct for Roguelite. It proves that the previous `128px` lock was already below a core genre reference in relative screen occupancy, while Roguelite additionally wants mature adult anatomy, long hair, torn cloth, chains/restraints and a richer contemporary pixel-art treatment.

Modern beat'em-ups also vary substantially by camera, multiplayer count and art direction. The project will not replace one arbitrary pixel number with another without composition testing.

## New scale contract — LOCKED

### 1. Relative world scale is semantic, not a pixel height

`relative_scale=1.0` continues to mean baseline adult-human / Exilada world scale.

It no longer implies `128px`, or any other fixed visible height.

Larger/smaller creatures derive their occupancy and atlas needs from the chosen gameplay composition plus `relative_scale`; they are not non-uniformly stretched.

### 2. Gameplay apparent height is OPEN pending benchmark

At native `640×360`, the first deliberate comparison set will test the Exilada at approximately:

- `160px` visible standing height (~44% of viewport height);
- `180px` (~50%);
- `200px` (~56%).

These are **comparison candidates**, not a new hard lock.

The final baseline must be chosen from real gameplay composition with:

- protagonist + multiple ordinary enemies;
- depth-lane movement;
- attack envelopes;
- hair/cloth/chain extents;
- HUD-safe area;
- at least one materially larger monster/boss case;
- readability of mature anatomy and pixel-art materials.

### 3. Authoring-master resolution is separate from gameplay occupancy

Do not shrink the pixel-art master merely because the runtime camera may display it smaller.

Until final gameplay scale is chosen:

- renderer/master review should preserve roughly `256–320px` of visible character height where practical;
- action cells may be `384×384` or larger when the action envelope requires it;
- the final runtime asset can later be derived/tested at chosen gameplay occupancy without sacrificing the higher-resolution reconstruction evidence.

### 4. Runner52's `192×192` cells are diagnostic history

Runner52 remains valid evidence for:

- one-action/one-row packing;
- adult-body structure preservation at Kontext denoise0.45;
- pose fidelity;
- alpha feasibility.

Its `192×192` cell / roughly small-character review output is **not** a production-scale recommendation.

## Immediate renderer consequence

Runner53 should no longer downpack its LoRA probe to `192×192` cells.

Its renderer inference remains the same, but the review/master packing target is raised to `384×384` cells so the resulting character remains around the high-200px range rather than being prematurely compressed.

This change is a packaging/master-scale correction, not a new model-quality variable.

## References used for sanity checking

- MobyGames Final Fight arcade screenshots: original screenshot size `384×224`.
- Brutal Deluxe sprite proof-of-concept page: Final Fight sample sprite dimensions include `84×93` and `56×93`.
- Dotemu / Streets of Rage 4 press material: modern hand-drawn beat'em-up comparator.
- PlayStation / Dragon's Crown Pro: modern classic beat'em-up comparator.
- TMNT: Shredder's Revenge remains a useful deliberately-retro, multiplayer-heavy counterexample, but its smaller-character composition is not treated as the Roguelite target.

## Hard conclusion

**`128px` is retired as a hard baseline.**

The project will lock gameplay character height only after comparative viewport testing. Authoring/render masters remain materially larger than the eventual display target until pixel-art quality and gameplay composition are both proven.
