# Exilada master revision / local editor — 2026-09-08

Status: **ACTIVE CHARACTER-DESIGN GATE / CURRENT MASTER REOPENED / RUNNER53 PAUSED**

## Why this gate exists

The current `exilada_master.png` remains useful identity/anatomy evidence, but it is no longer accepted as the final visual-design authority.

The user identified two unresolved problems before further spritesheet/render work:

1. the captivity cloth is still too intact/generic and does not yet exploit the already-approved direction of more severe tearing, irregular edge loss and materially caused adult body exposure;
2. the character still reads too much like generic contemporary dark-fantasy concept art and not strongly enough through the locked Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell lineage.

Continuing Runner53 against the old master would risk improving pixel-art rendering language while preserving the wrong character design. Therefore character-master revision now precedes the style-adapter gate.

## Adult nudity / exposure contract — reaffirmed

The Exilada is an unambiguously adult fictional woman. Adult nudity is a normal supported character/world state and is not treated as a failure condition.

For the initial captivity state, valid candidates include:

- severely torn, asymmetrical cloth rather than a neat bandeau/costume;
- irregular holes, missing edges, displaced fabric and incomplete coverage;
- substantially greater torso exposure than the current master;
- partial breast exposure where materially caused by the torn cloth;
- near-nudity or full nudity when deliberately chosen for the state rather than added as an accidental model artifact;
- torn/degraded hip cloth with similarly precarious coverage;
- dirt, sweat, wounds/scars and captivity evidence remaining causal rather than decorative.

No censor garment is mandatory. The design must not be automatically sanitized merely because an adult body is exposed or erotically charged.

Exact tear geometry and exact exposure remain subject to visual approval in the local editor.

## Visual-direction problem

The locked inspiration lineage is not satisfied by merely naming references in a prompt. The revised master must visibly move away from generic fantasy toward:

- strong adult physicality and weight;
- severe, dangerous silhouette and face;
- long heavy black hair as a dominant non-rigid mass;
- tactile skin, cloth and metal;
- grime, deprivation and pulp-fantasy excess;
- adult sensual/erotic charge without cute/chibi/glamour drift;
- late-1970s/1980s sword-and-sorcery illustration energy;
- avoidance of clean MMO/cosplay/fantasy-heroine costume logic.

The goal is not to copy a particular existing composition or artist-specific character. References are used to establish high-level pictorial lineage and design criteria.

## Local-only authoring decision

Detailed visual iteration should occur locally rather than through the chat image-generation surface.

Reason:

- the user needs unrestricted iterative control over an adult character's clothing damage/nudity state;
- the same local model/reference stack will ultimately feed the production pipeline;
- provenance, seeds and model parameters must remain reproducible;
- approved results must be directly usable as project assets rather than recreated manually.

This is a tooling/workflow decision, not an instruction to generate an image in chat.

## Runner54 — local Exilada master editor

Launcher:

`tools/structured-2d-character-pipeline/54_run_exilada_master_editor.ps1`

Application:

`tools/flux-kontext-spike/exilada_master_editor.py`

Uses the already-installed local FLUX.1 Kontext workspace at:

`Z:\AI\FluxKontext`

UI defaults to:

`http://127.0.0.1:7860`

ComfyUI API defaults to:

`http://127.0.0.1:8191`

### Editor inputs

- current working master / uploaded replacement;
- optional approved nude anatomy turnaround;
- optional visual-direction reference 1;
- optional visual-direction reference 2;
- editable clothing/tear/exposure brief;
- editable body/identity lock;
- editable material/captivity brief;
- editable pictorial-direction brief;
- per-iteration specific change;
- seed, steps, guidance and denoise.

### Editor guarantees

- no 128px asset assumption;
- no 192px/384px forced final packing;
- native useful Kontext output is preserved;
- candidates are versioned with prompt/settings/hashes;
- iterative candidates can become the next working input;
- `exilada_master.png` is not overwritten by inference;
- only the explicit **APPROVE** action promotes a candidate to the canonical local master;
- the previous master is backed up under `assets/source/characters/exilada/reference/history/`.

### Canonical anatomy reference

When present, the local editor can use:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

It is used as anatomy evidence only. The prompt explicitly rejects copying the turnaround layout into the new master.

## Parameter philosophy

The editor is intentionally interactive rather than a single locked runner.

Default starting point:

- Kontext FP8 installed set;
- Euler/simple;
- CFG 1;
- guidance 2.5;
- 20 steps;
- denoise 0.38;
- seed 0.

Denoise is exposed because the task is now deliberate character redesign. Lower values preserve the old master more strongly; higher values permit more material/design change but increase identity drift risk. Each candidate records the actual value.

## Current pipeline order

Previous immediate order:

`Runner53 pixel-art style probe -> full action -> gameplay scale ...`

is paused.

Current order:

1. run Runner54;
2. revise the Exilada master locally using the existing master, approved anatomy reference and any visual references the user chooses;
3. approve one new canonical master only when body identity, torn-cloth/exposure treatment and 1980s sword-and-sorcery charge all pass;
4. regenerate/revalidate H3 motion against the newly approved master if the visual difference is material;
5. only then resume the downstream pixel-art renderer/style-adapter validation;
6. derive runtime sprites from the production-resolution video/frame chain with no arbitrary 128px asset stage.

## Gate criterion

The master-revision gate passes only when the user explicitly approves a candidate.

Technical inference completion alone is not a pass.
