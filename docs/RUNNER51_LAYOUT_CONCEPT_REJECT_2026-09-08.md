# Runner51 — Layout concept rejected before execution

Status date: **2026-09-08**

Classification: **CONFIGURATION / TASK-FORMULATION FAIL — PRE-INFERENCE**

Runner51 was prepared but must **not** be used as the canonical spritesheet layout test.

## What was wrong

Runner51 incorrectly interpreted the current single `dance_or_gesture` action as three separate final rows, each containing four frames from a different temporal window.

That violates the intended authoring contract.

## Correct spritesheet contract — HARD LOCK

**One action = one spritesheet row.**

For the current H0 `dance_or_gesture` proof:

- all selected frames belong to the same action;
- frames are ordered left-to-right in time;
- current target = `12 columns × 1 row`;
- cell size = `192×192`;
- final review sheet = `2304×192`;
- per-frame durations remain in metadata/JSON;
- complete character remains visible in every cell.

A multi-action character sheet may stack several action rows later, e.g. `idle`, `walk`, `run`, `jump`, `punch`, `kick`, weapon attacks, defenses and damage/death actions. Each row is a distinct action.

## Internal processing tiles are not final rows

The Kontext renderer may still process four frames at a time in a temporary `2×2` `1024×1024` tile to preserve working resolution.

For a 12-frame action:

- processing chunk 1 = final action frames 1–4;
- processing chunk 2 = final action frames 5–8;
- processing chunk 3 = final action frames 9–12.

After inference, all 12 cells are extracted and concatenated into **one horizontal action row**.

The internal `2×2` topology has no semantic meaning in the final spritesheet.

## What remains valid from Runner51

The following controlled changes remain useful and are carried forward:

- same installed FLUX.1 Kontext [dev] FP8-scaled runtime;
- canonical Exilada reference as identity/art-direction authority;
- `20 steps`;
- `guidance=2.5`;
- `CFG=1.0`;
- Euler/simple;
- seed0;
- `denoise=0.45` instead of Runner50 `1.0`;
- explicit mature-adult body preservation;
- explicit no-infantilization requirement;
- Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell art-direction lock;
- four-frame high-resolution internal tiles.

## Replacement gate

Runner52 replaces Runner51 as the current gate:

`tools/structured-2d-character-pipeline/52_run_flux_kontext_h0_dance12_single_action_row.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance12_single_action_row_structure_lock.py`

Runner52 uses the complete H0 action interval, selects 12 ordered samples across it, renders them as three internal four-frame tiles, and reconstructs the final `1×12` action row.

No Runner51 inference evidence exists and no model-quality conclusion may be drawn from Runner51.
