# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / WAN W1L RUNNING AS FINAL CURRENT WAN RUN / MINIMAX H3 REF2VA NEXT / WAN PAUSES AFTER W1L / SCAIL-2 LATER IF NEEDED**

## Purpose

Select a production model that generates the complete Exilada from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

The model must consume richer information than skeleton-only pose and automatically infer locomotion, soft-body response, long-hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

## Screening order — LOCKED 2026-09-08

1. finish the already-running Wan W1L and preserve its evidence;
2. screen **MiniMax H3 Base Ref2VA** locally next;
3. Wan becomes **PAUSED**, not exhausted, after W1L;
4. SCAIL-2 remains a later candidate if H3 does not satisfy the contract.

This supersedes the previous rule that Wan had to reach `EXHAUSTED_FAIL` before moving to another family.

## Model-exhaustion / comparison protocol

- distinguish infrastructure, integration, configuration and model/task failures;
- fixed inputs/seeds unless the variable is intentionally changed;
- one-variable experiments by default;
- compound configuration searches allowed when explicitly labeled as such;
- no seed fishing or manual rescue;
- do not delete an active model family until evidence is secured and the route is genuinely paused/abandoned.

## Wan canonical history

- W0: local Base-BF16 route passed with `--disable-pinned-memory`.
- W1 ref1.0: approved painterly/motion language; crop/restraint/limb issues.
- W1A ref1.5: stronger apparent topology but more ghosting under old geometry.
- W1F: whole-frame letterbox failed crop; closed.
- W1G: tracked/recentered raw driver worsened ghosting and temporal anatomy; closed permanently.
- W1H: `512×912` with untouched `480×854` driver fixed dominant crop and became best Wan geometry baseline; heavy fast-motion smear plus structural changes remain.
- W1I: pose-end0.70 did not materially improve those defects; not preferred.
- W1J / W1K: prepared, never executed, superseded before run.

## W1L — RUNNING / FINAL CURRENT WAN GATE

Runner:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Parent = exact W1H.

Compound changes:

- `reference_image_strength 1.5 -> 1.0`;
- `pose_strength 1.00 -> 0.80`;
- `steps 20 -> 30`.

Everything else remains W1H. Classification policy: **COMPOUND_CONFIGURATION_SEARCH**.

After W1L completes, preserve its output/manifest and do not launch another Wan inference before the H3 spike.

## MiniMax H3 Ref2VA — NEXT ACTIVE FAMILY

Why it qualifies for screening:

- Ref2VA accepts multimodal reference inputs including images and videos;
- this maps directly to Exilada appearance reference + arbitrary real driving video;
- it generates a complete video character rather than a skeleton-only motion representation;
- current ComfyUI support exposes consumer-GPU quantized/offloaded execution suitable for a local RTX 3060-class screening route.

Only **Ref2VA** is relevant initially. Do not download FL2VA in parallel.

## H3 local-resolution strategy

The game uses a protagonist around `128 px` tall, so screening must optimize for the final sprite use case rather than blindly generating at 768p or 2K.

First local H3 target: **`448×800`**.

Rationale:

- divisible by 32 in both axes;
- aspect `0.56`, matching the current portrait driving video closely;
- only about 34.7% as many spatial pixels/cells as `1344×768`;
- still several times larger than the final 128px-tall runtime character, leaving useful supersampling for anatomy, hair, cloth and alpha extraction.

Escalation ladder only if needed:

1. `448×800` first;
2. `480×864` if structure/identity is under-resolved;
3. `512×896` if still needed;
4. one 768-short-edge control to distinguish low-resolution failure from model failure.

Do not generate directly at 128px. Very low model-space resolution can destroy anatomy/identity/temporal coherence before downsampling.

## Required H3 QA

Every candidate is judged at:

1. full generated resolution — topology, anatomy, identity, motion adherence, hair/cloth/restraint dynamics;
2. automatically downsampled gameplay preview — character approximately `128 px` tall.

Minor local blur may become irrelevant at gameplay scale. Missing body parts, topology changes, silhouette failure and identity drift remain hard failures even if downsampling hides detail.

## H3 install policy

- no H3 download while W1L is still running;
- planned workspace: `Z:\AI\MiniMaxH3`;
- use only the chosen Ref2VA quantized/pruned route plus required encoder/VAE components;
- do not accumulate FL2VA or alternative quantizations without an explicit hypothesis;
- preserve Wan W1L evidence before any large-asset cleanup.

## Cleanup

Wan BF16 assets remain until W1L is complete. Once H3 becomes the validated active route, reevaluate whether to remove the Wan ~45.7GB asset set. Preserve small proof files and SSD comparison evidence until explicit abandonment/final verdict.
