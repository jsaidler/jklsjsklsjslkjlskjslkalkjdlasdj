# Local Video Studio — production quality gate

Date: **2026-09-15**  
Updated: **2026-09-18**  
Status: **ACTIVE / PRODUCTION QUALITY NOT APPROVED**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why this gate exists

A technically functional avatar is not enough. The finished result must satisfy both **render quality** and **personal identity quality**.

The project now explicitly separates three identities:

1. visual identity;
2. voice identity;
3. behavioral identity.

Behavioral identity means João's characteristic facial expressions, head movement, gesture language, posture and delivery rhythm learned from his real footage.

A clip that looks like João but moves like a generic presenter is a production failure.

## Hard acceptance checklist

A production candidate must be acceptable at normal viewing size and under full-resolution inspection for all of the following:

1. **Visual identity** — facial/body geometry remains recognizably João across the full clip.
2. **Eyes / glasses** — no eye drift, warped rims/lenses, disappearing temples or distracting geometry changes.
3. **Hair / beard** — no crawling edges, shape changes, texture boiling or identity-changing hairline/beard behavior.
4. **Mouth / teeth / jaw** — lipsync is natural; the mouth is not rubbery, over-articulated, melted or structurally inconsistent.
5. **Hands / fingers / wrists** — no conspicuous anatomy errors, fused fingers, implausible wrists or unstable hand topology.
6. **Arms / shoulders / body topology** — no attachment drift, body-part reconfiguration or unnatural symmetry.
7. **Behavioral identity** — expressions, gesture timing, head movement, posture and delivery rhythm feel recognizably like João, not merely human/plausible.
8. **No generic presenter performance** — no repetitive, mirrored, theatrical, caricatured or stock-avatar choreography that João would not naturally use.
9. **Skin / texture** — no distracting waxy surface, crawling detail or temporal sharpening/softening pulses.
10. **Clothing** — garment topology, seams, collar, sleeves and material remain coherent through motion.
11. **Scene geometry** — background objects, lines and surfaces do not melt, breathe or transform without cause.
12. **Lighting** — face/body/background illumination remains physically coherent.
13. **Camera / composition** — framing follows the requested shot without unexplained zooming/reframing.
14. **Voice identity / AV sync** — when the final voice stage is present, voice identity remains convincing and synchronization does not visibly slip.
15. **Generalization** — a personal-avatar system must preserve João identity on a **new script not present in the behavioral reference video**.
16. **Overall release standard** — publishable without manual frame-by-frame repair.

A conspicuous failure in any major category means **production fail**.

## Important benchmark rule

Do not claim behavioral-identity failure or success unless the candidate actually received João's behavioral video/reference in a way intended to condition or train motion identity.

Static-image + audio benchmarks such as the completed Wan S2V tests are useful for visual rendering quality but are **not behavioral-identity tests**.

## Evidence from completed branches

### H3

Functional architecture pass, production visual quality fail. Generic autonomous gesture language remains unacceptable.

### Wan2.2-S2V 10-step

Structurally promising but visual-quality fail.

### Wan2.2-S2V 20-step

João's review on 2026-09-18:

- visually, the generated person was essentially João;
- expressions and movements did not feel like João;
- the performance felt caricatured.

Because the Wan path used static image + audio and **did not receive behavioral footage**, classify this as:

**visual identity strong / behavioral identity not tested / production fail for the actual product.**

Do not try to repair personal mannerisms through prompt wording alone.

### HunyuanVideo-Avatar local

Runtime/payload passed, but 720p quality path timed out after nearly three hours at `0/30` on RTX 3060 12 GB. No visual verdict. Local practicality fail.

## Current production benchmark — Avatar V

The next gate must explicitly test reusable behavioral identity learned from João's actual footage.

Use HeyGen Avatar V / Digital Twin first because current product documentation states that it learns specific gestures, expressions and mannerisms from short real-human video footage.

The benchmark must:

- use existing João footage as motion/behavior reference;
- use a new Portuguese script not present in that footage;
- avoid exaggerated emotional direction;
- preserve an easy-to-judge look/framing;
- collect a separate human verdict for visual identity and behavioral identity.

## Required human verdict

The benchmark passes only if the reviewer can answer **yes** to both:

> Does this look like João?

> Does this move and react like João?

A yes to only the first question is not enough.

## Required evidence per quality run

Store where technically possible:

- renderer/model/version;
- source behavioral-reference video identity/hash or provider asset ID;
- look/identity reference identity/hash or provider asset ID;
- script;
- voice source/model;
- generation settings;
- duration/dimensions;
- elapsed time and cost;
- final MP4;
- human verdict per acceptance category;
- explicit final classification: `PASS`, `FAIL`, or `INCONCLUSIVE`.

No automatic metric may override visible human defects or the user's judgment of his own behavioral identity.