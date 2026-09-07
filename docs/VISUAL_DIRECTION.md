# Visual Direction — Living Document

Status date: **2026-09-07**

Status: **the previous hard lock to deliberate modern pixel art is superseded. The Wan-Animate-2 W1 painterly 2D result is now the preferred visible-art direction under gameplay-scale validation, with an explicit 1980s sword-and-sorcery / dark-fantasy charge.**

## Process rule — living documentation

All material visual-direction decisions, accepted/rejected approaches and validation results must be recorded here or in the relevant linked canonical document. When a decision changes, edit the living document rather than relying on chat history.

The high-level game vision is defined in `docs/GAME_VISION.md`.

## Core production constraint

The project must be producible end-to-end through ChatGPT and project tooling without routine bespoke manual art/animation work from the user or a hired art team.

A visual direction is invalid if it can make one attractive concept but cannot be animated, varied, maintained and expanded by the same production system.

## Current preferred visible-art language — LOCKED AS DIRECTION, STILL UNDER GAMEPLAY-SCALE VALIDATION

The Wan-Animate-2 W1 Exilada result changed the visual target materially.

The user explicitly approved the result as exceptionally beautiful and stated that a whole game at this quality/language would be highly desirable. Therefore the earlier requirement that final gameplay art must read as deliberate pixel art is **no longer a hard constraint**.

Current preferred language:

- high-quality painterly / illustrated 2D character rendering;
- severe, physical, mature dark fantasy;
- strong silhouette and readable large masses;
- rich skin, hair and fabric rendering without requiring visible pixel clusters;
- localized, restrained motion blur is allowed and may be desirable because it prevents the animation from reading as a rigid sequence of still illustrations;
- blur must remain motion-local and controlled rather than globally softening the image;
- temporal coherence and complete-character readability matter more than preserving a pixel-art construction doctrine;
- output must still survive actual gameplay scale, background extraction/composition and ordinary complete-sprite playback.

This does **not** mean any smooth AI-video output is accepted automatically. Identity, topology, restraints/accessories, framing, motion readability and production reproducibility remain hard QA requirements.

## 1980s sword-and-sorcery charge — LOCKED 2026-09-07

The game should deliberately carry an **1980s fantasy / sword-and-sorcery visual charge**, consistent with the golden period of its central inspirations.

Canonical inspiration lineage includes:

- **Heavy Metal**;
- **Conan**;
- **Red Sonja**;
- **Frank Frazetta**;
- **Julie Bell**.

Interpretation:

- adult sensuality, heroic anatomy, danger, grime, erotic charge and pulp-fantasy excess may coexist;
- the game should not sanitize its mature body language;
- materials may feel painted, illustrated, tactile and dramatic rather than digitally sterile;
- the 1980s influence is a tonal/art-direction layer, not a requirement to imitate VHS defects, CRT scanlines or retro UI clichés;
- the result should feel like the fantasy imagery of that period made playable with contemporary animation/systemic production quality.

## Exilada appearance reference

Canonical Exilada identity/state reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It remains the canonical complete initial-state appearance reference for current animation work.

The W1 output demonstrated that the reference can be reinterpreted into the preferred painterly animation language while preserving the coarse Exilada package. Exact face/body detail, restraints and framing still require improvement.

## Exilada initial-state erotic/body direction — LOCKED IN PRINCIPLE

The Exilada does not need to be visually desexualized to be treated seriously.

Her initial deprivation/captivity state may include:

- much more severely torn cloth;
- irregular holes and edge loss that expose additional skin;
- partial breast exposure where consistent with the torn garment state;
- asymmetrical coverage rather than a neat fantasy bandeau;
- simultaneous vulnerability, danger, sensuality and physical presence.

This is an intentional mature sword-and-sorcery vocabulary, not a censoring problem. Exact tear geometry and exact amount of exposure are still subject to final visual-state approval rather than being fixed by a temporary prompt.

## Erotic charge and adult-body language — LOCKED

The project does **not** treat erotic charge as something to be automatically removed or sanitized.

Adult characters may be beautiful, sensual, sexualized, nude or partially nude when appropriate to character/state/scene. Heroic, violent, grotesque, vulnerable, erotic and matter-of-fact body readings may coexist.

For the Exilada specifically, her body may carry erotic charge even while wounded, dirty, deprived or minimally clothed. Captivity itself does not have to become the erotic subject; framing and narrative intent remain deliberate.

## Systemic visual rule

Whenever feasible, visually relevant state should follow simulation/history rather than arbitrary decoration.

Examples include scars, equipment wear, blood, dirt, wetness, burns, frost, fatigue, hunger, injury posture and clothing damage.

Procedural variation must be causal and constrained rather than random noise.

## Character visual principles

Characters must remain identifiable first through silhouette, large masses, posture and controlled contrast.

At gameplay scale:

- hair mass, body proportions, clothing asymmetry and equipment shapes must remain readable;
- facial microdetail cannot be the only identity carrier;
- clothing/equipment may evolve without erasing body/hair/posture identity;
- anatomy remains adult and materially grounded;
- exposed skin, partial nudity and full adult nudity are valid states;
- motion-local blur is allowed only where it improves motion reading without erasing silhouette/anatomy.

## Runtime / production architecture

Visible runtime characters are complete precomposed frames:

`reference image + raw driving video -> complete animated character frames -> automatic extraction/packing -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

There is no visible runtime body/hair/clothing/equipment layer assembly.

Routine manual rigging, keyframing, mask repair, repainting and per-frame cleanup remain disallowed.

## Gameplay projection — LOCKED BASELINE

The game remains an **elevated 2D belt-scroller / 2.5D false-3D presentation** inspired by arcade beat'em-up spatial language but updated for a contemporary systemic action RPG/roguelite.

Core principles:

- strong lateral travel axis plus continuous walkable depth axis;
- elevated camera exposing the ground plane;
- large readable mostly lateral / three-quarter characters;
- foreground/background layering and depth ordering;
- combat readability over geometric purity;
- not a pure side-scroller and not the superseded high-oblique 360-degree system.

Current gameplay composition locks elsewhere include native `640×360`, camera pitch `26°` and protagonist about `128 px` tall, subject to final visual integration QA.

## Animation direction — CURRENT

Wan-Animate-2 Base BF16 is the active complete-character animation model family under exhaustion testing.

W0 official baseline proved raw-video motion transfer locally. W1 with the Exilada produced the newly preferred painterly visual language and meaningful non-rigid hair/cloth behavior, but exposed problems in framing and accessory/identity persistence.

The user approved the W1 painterly look and specifically accepted **localized, restrained blur** as potentially beneficial.

W1A (`reference_image_strength 1.5`) did not materially improve the result and introduced more blur/ghosting in several motion phases; current preferred conditioning balance therefore remains W1 `reference_image_strength=1.0` unless later evidence changes it.

The current gate is automatic driver safe-framing before any 1980s/torn-clothing prompt variant or Internet walking driver.

## Framing rule — PRODUCTION BLOCKER

The complete body, head and hair must remain safely inside frame throughout a generated sequence.

Post-generation cropping repair is not acceptable because missing pixels cannot be reconstructed without another generative/manual step.

Current correction strategy is automatic **pre-driver safe framing**:

- preserve the complete original raw driver frame;
- scale it into a smaller fixed centered safe box;
- add stable margins without temporal camera breathing;
- feed that still-raw temporal video to Wan;
- no manual tracking/alignment.

Runner 39 tests an 80% fixed safe box at `640×800` while holding W1 model/seed/prompt/conditioning fixed.

## Historical modern-pixel-art direction — SUPERSEDED AS HARD LOCK

The project previously required deliberate modern pixel art with coherent raster clusters as the final visible language. That work and its assets remain useful research/reference evidence, but the W1 visual approval supersedes the requirement that production output itself must be pixel-art constructed.

Do not revive pixel art as a mandatory acceptance criterion unless explicitly re-approved.

## Current visual gates

1. **W1F framing proof:** remove inherited edge/head crop without damaging scale/motion quality.
2. **1980s Exilada appearance variant:** same successful technical setup, then test stronger sword-and-sorcery art direction and more severely torn/exposing cloth.
3. **W2 locomotion:** clean real Internet walking driver.
4. **W3 secondary-motion stress:** body bounce, hair, loose cloth/wind and restraint dynamics.
5. validate the preferred painterly language at actual ~128 px gameplay occupancy inside the belt-scroller scene.

## Current decision

**LOCKED:** W1-style painterly illustrated 2D is the preferred visible-art direction under gameplay-scale validation; modern pixel art is no longer a hard final-art requirement.

**LOCKED:** 1980s sword-and-sorcery visual charge should be intentionally present.

**LOCKED:** Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell remain active reference lineage.

**LOCKED:** mature erotic charge, nudity and partial nudity are legitimate parts of the visual language and must not be sanitized by default.

**LOCKED:** localized, restrained motion blur may be aesthetically positive.

**LOCKED:** runtime remains complete-character 2D playback and production must remain scalable without routine manual art labor.

**CURRENT GATE:** automatic safe-framing proof (Runner 39), then the 1980s/torn-clothing Exilada appearance variant.
