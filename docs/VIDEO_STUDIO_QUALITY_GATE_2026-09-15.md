# Local Video Studio — production quality gate

Date: **2026-09-15**  
Updated: **2026-09-18**  
Status: **ACTIVE / PRODUCTION QUALITY NOT APPROVED**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why this gate exists

A technically functional avatar is not enough. The finished result must satisfy both **render quality** and **personal identity quality**.

The project explicitly separates three identities:

1. visual identity;
2. voice identity;
3. behavioral identity.

Behavioral identity means João's characteristic facial expressions, head movement, gesture language, posture and delivery rhythm learned/reused from his real footage.

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
15. **Generalization** — the system must preserve João identity on a **new script not present in the behavioral reference video**.
16. **Overall release standard** — publishable without manual frame-by-frame repair.

A conspicuous failure in any major category means **production fail**.

## Important benchmark rule

Do not claim behavioral-identity failure or success unless the candidate actually received João's behavioral evidence in a mechanism intended to carry that motion identity forward.

Static-image + audio benchmarks such as the completed Wan S2V tests are useful for visual rendering quality but are **not behavioral-identity tests**.

For the current architecture, the behavioral evidence is a newly assembled driving performance selected from João's own motion-unit library using pose/prosody constraints. A single fixed source clip is not sufficient as the product hypothesis.

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

### HeyGen Avatar V / Digital Twin

This branch is **retired and invalid for the active project** because the canonical execution policy is local/self-hosted and zero-cost, and João's identity material must not be uploaded to an external avatar provider.

Historical documentation may remain for provenance, but HeyGen is not an active benchmark, fallback or next step.

## Current behavioral benchmark — LOCAL MOTION UNITS + INSTALLED WAN-ANIMATE-2

The next gate explicitly tests reusable behavioral identity from João's own local footage without an external service.

Required sequence:

1. build a `status=complete` behavior profile for `VID_20260911_140124885.mp4` with real whole-body/hand pose data plus local prosody descriptors;
2. inspect the motion-unit manifest before rendering;
3. create a **new ~4–5 s performance from several motion units**, not a replay of one fixed source clip;
4. choose/order units using prosodic compatibility, pose continuity and diversity;
5. pass that locally assembled driving video to the already-installed Wan-Animate-2;
6. judge behavioral identity independently from pixel/visual identity.

The current extractor deliberately permits `status=incomplete_pose` only as a segmentation/prosody diagnostic. Such a manifest is **not eligible for this gate**.

Do not install lip-sync or final voice cloning before this body/head behavioral gate. Mouth timing may be imperfect at this stage; that does not relax the requirement that body, head, posture and gesture language feel like João.

## Behavioral-profile pre-gate

Before diffusion rendering, the profile itself must be inspectable and credible.

At minimum verify:

- units reference real original RGB spans;
- cuts tend to fall at pauses and/or low-motion transition points;
- start/end pose exists for each eligible unit;
- head, hands and body activity are populated from pose rather than guessed from generic motion;
- motion energy and speech/pause descriptors are plausible when spot-checked against the source;
- enough different units exist to form a short performance without immediate repetition;
- transition candidates include compatible end/start poses.

Automatic segmentation metrics are supporting evidence only. They do not prove João's behavioral identity.

## Required human verdict

The renderer benchmark passes only if the reviewer can answer **yes** to both:

> Does this look like João?

> Does this move and react like João?

A yes to only the first question is not enough.

For the first behavior gate, the second question has priority over final lipsync/voice polish.

## Required evidence per quality run

Store where technically possible:

- local renderer/model/version;
- source behavioral-reference video path/hash;
- behavior-profile schema/version and manifest;
- selected motion-unit IDs and source time ranges;
- transition/selection scores used to assemble the driving performance;
- look/identity reference path/hash;
- target script/audio identity;
- generation settings;
- duration/dimensions;
- elapsed local runtime;
- final MP4;
- human verdict per acceptance category;
- explicit final classification: `PASS`, `FAIL`, or `INCONCLUSIVE`.

No automatic metric may override visible human defects or João's judgment of his own behavioral identity.