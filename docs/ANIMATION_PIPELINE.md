# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **COMPLETE-CHARACTER RAW-VIDEO GENERATION ACTIVE. WAN W1L IS RUNNING. AFTER W1L, WAN PAUSES AND MINIMAX H3 REF2VA BECOMES THE ACTIVE SCREENING ROUTE.**

Canonical state: `docs/PROJECT_STATE.md`.

## Hard production constraints

- complete Exilada appearance reference + separate real driving video;
- driver identity/clothing/hair may differ completely;
- infer body locomotion, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing;
- runtime consumes complete precomposed sprite frames.

## Visual direction

Painterly illustrated dark fantasy with explicit 1980s sword-and-sorcery charge: Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Adult sensuality/nudity is legitimate. Localized motion blur may be positive; global smear, anatomy loss and topology drift are defects.

## Wan record

- W1 established the approved painterly/motion language.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H changed generation geometry to `512×912` while keeping the raw `480×854` driver untouched; dominant crop was solved and temporal body coherence improved.
- W1I pose-end0.70 did not materially improve heavy motion blur/structural changes.
- W1J and W1K were prepared but never executed.
- W1L is the only current Wan run and uses ref1.0 + pose0.80 +30 steps on the W1H branch.

Runner:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Do not launch another Wan run after W1L before screening H3.

## Screening transition — LOCKED 2026-09-08

After W1L finishes:

1. preserve W1L video, prompt, manifest and executor log;
2. mark Wan as **PAUSED AFTER W1L**, not exhausted;
3. activate **MiniMax H3 Base Ref2VA** local screening;
4. keep SCAIL-2 as a later candidate if H3 does not satisfy the production contract.

## MiniMax H3 Ref2VA production hypothesis

Ref2VA is relevant because it accepts multimodal references including images and videos. The intended project mapping is:

`Exilada appearance reference + real driving video -> complete generated character video -> automatic extraction/downsample/packing -> spritesheet`

No FL2VA download is needed for the first spike.

## H3 resolution policy — FIRST SPIKE

The runtime character is only about `128 px` tall. Generating every production source at a 768px short edge would therefore be wasteful unless the model actually needs that scale for quality.

Initial target: **`448×800`**.

Why:

- both dimensions are multiples of 32;
- aspect `0.56` closely matches the current portrait driver;
- it contains about 34.7% of the spatial pixels/cells of `1344×768`;
- it still provides roughly 5–6× linear supersampling relative to a 128px-tall runtime sprite when the character occupies most of the frame.

If quality is under-resolved, escalate only as needed:

`448×800 -> 480×864 -> 512×896 -> one 768-short-edge control`

Do not use `512×912` for H3 because dimensions should be multiples of 32. Do not generate directly at 128px because anatomy/identity/temporal coherence can fail before downsampling.

## Dual-resolution QA — REQUIRED

Every H3 result must be evaluated at two levels:

1. **source scale:** body topology, hands/feet, face/identity, hair, cloth, restraints, motion adherence and temporal coherence;
2. **gameplay scale:** automatic extraction/downsample to character height ~`128 px`, checking silhouette, readability and whether harmless local artifacts vanish.

Downsampling is allowed to make small texture/detail defects irrelevant. It is not allowed to hide topology loss, missing limbs, detached parts or identity drift.

## H3 local resource policy

Planned workspace: `Z:\AI\MiniMaxH3`.

Use the smallest current ComfyUI-compatible Ref2VA route appropriate for RTX 3060 12GB +48GB RAM, with DynamicVRAM/offloading where required. Lowering canvas size reduces latent/activation work but does not reduce model-weight size, so RAM/offload cost remains significant.

## Cleanup

- do not remove Wan assets while W1L is running;
- after W1L evidence is secured and H3 is validated enough to become active, reevaluate removal of the Wan BF16 asset set;
- do not accumulate H3 FL2VA, multiple quantizations or unused components;
- keep small evidence and SSD comparison material until explicit abandonment/final verdict.
