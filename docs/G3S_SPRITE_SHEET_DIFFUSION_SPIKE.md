# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **RUNNER 34 EXPORT PASS / CURRENT MOORE+SSD CONFIGURATION QUALITY FAIL / EXACT SSD BLOCKED / MOORE+SSD EXHAUSTION AUDIT ACTIVE**

## Runtime target — LOCKED

The runtime target is conventional playback of **complete-character spritesheets**:

`complete authored frames -> complete-character spritesheet/atlas + metadata -> ordinary runtime playback`

Runtime construction of the visible character from body/hair/clothing/equipment layers is abolished. Offline authoring may internally use rigs/layers/controls, but export is a fully composed character frame sequence.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

For current work this master defines the entire initial visible character state.

## Local SSD environment — PASS / RETAIN

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- env `ssd`, Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- DWPose;
- SD1.5 UNet/VAE/CLIP image encoder;
- released SSD denoising/reference UNets;
- baseline AnimateAnyone pose guider + motion module.

Do not clean this workspace while the exhaustion audit is active.

## Exact upstream SSD — BLOCKED, NOT VISUALLY REJECTED

The SSD method is an AnimateAnyone adaptation using ReferenceNet, Pose Guider and Motion Module. The released public fine-tuned weights available to us contain the SSD reference and denoising UNets, but not the custom SSD pose-guider checkpoint required by the exact published graph.

Therefore exact upstream SSD has **not been reproduced locally**.

Correct classification:

- **BLOCKED** as an exact public-weight reproduction;
- **not** “SSD model failed our task.”

A Moore baseline pose guider can be used as a compatibility workaround, but that creates a different graph/weight combination whose behavior must be judged separately.

## Moore-compatible fallback

Current runnable reconstruction:

`Moore-AnimateAnyone graph + Moore baseline pose guider/motion module + released SSD fine-tuned denoising/reference UNets`

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

This is explicitly **not exact published SSD**.

## Runner history

### Runner 29

Technical PASS / configuration quality FAIL:

- weak phase differentiation;
- unstable lower legs/feet;
- detached accessory artifacts;
- insufficient locomotion.

### Runner 30 — critical integration evidence

Runner 30 fixed a concrete target-pose registration defect: the earlier `640×360 -> 512×512` mapping introduced `1.7778×` relative vertical stretch.

Uniform scaling/registration to the reference footprint materially improved pose response and lower-limb reconstruction.

This is important evidence that **our integration/preprocessing can materially determine the visible result**. It is therefore invalid to promote every poor render directly to a model-level failure.

### Runner 31–33

- runner 31 locked gameplay facing at `72 deg`;
- runner 32 V1 remained too generic;
- runner 33 V2 added restrained feminine projected body treatment but was not final locomotion approval;
- V2 remains a provisional motion/control input for diagnostics, not proof of final gait quality.

## Runner 34 complete-character playable proof — RESULT

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

Configuration:

- full `exilada_master.png` appearance reference;
- eight V2 poses at `72 deg`;
- Moore-compatible SSD fallback;
- `512×512`;
- 8 frames;
- 25 steps;
- CFG `3.5`;
- seed `42`;
- fp16.

### Technical/export result — PASS

Runner 34 generated/package-tested:

- eight complete-character frames;
- RGBA transparency;
- `4×2`, `2048×1024` spritesheet;
- playback GIF;
- metadata for ordinary complete-frame playback.

The complete-character spritesheet export architecture is proven workable.

### Current configuration quality — FAIL

Observed:

- hair mostly frozen or locally warped;
- cloth changes shape without controlled physical lag;
- intentional jiggle not reliably readable;
- wrist chain mostly static;
- ankle restraint/chain detaches/mutates;
- lower legs/feet degrade under larger displacement;
- later phases become too similar and loop closure is weak.

Correct verdict:

> **Runner 34 configuration FAIL; Moore+SSD/SSD model capability unresolved.**

Do not use this one configuration as evidence that SSD “cannot do it.”

## Model exhaustion protocol as applied to SSD

Before switching models, the retained SSD/Moore environment must answer the following controlled questions.

### A — Moore reference baseline

Run the **pure Moore baseline** with its own reference UNet, denoising UNet, pose guider and motion module, using exactly the same validated reference/pose preprocessing.

Purpose: prove that our local Moore graph and pose-domain contract behave correctly before judging the hybrid.

### B — SSD-weight substitution A/B

With the same seed, inputs, scheduler, frame count and preprocessing, replace only Moore reference/denoising UNets with the released SSD fine-tuned UNets.

Purpose: isolate what the SSD fine-tuning actually changes instead of comparing multiple moving variables.

### C — pose-domain audit

Verify that target pose images are not merely visually plausible skeletons but match the representation, scale, registration, colors/channels and spatial footprint expected by the actual pose guider.

Runner 30 proved this is a first-order issue.

### D — pose-guider bottleneck test

Determine whether the Moore baseline pose guider is the ceiling when paired with SSD-finetuned UNets.

If body pose adherence remains poor in both Moore baseline and SSD substitution, fix integration/pose domain first. If Moore behaves correctly while SSD substitution degrades specifically, investigate weight-graph compatibility.

### E — complete-character complexity ladder

Do not ask the model to solve every secondary system before its body control is validated. Test in this order with the same master where possible:

1. body/major locomotion adherence;
2. identity/topology stability;
3. hair/cloth response;
4. restraints/chains;
5. soft-tissue/jiggle;
6. loop coherence.

The final accepted output must contain all of them, but staged diagnostics identify the failing component.

### F — exact-SSD decision

If the Moore-compatible reconstruction reaches a repeatable ceiling, decide explicitly whether recovering/retraining/building a compatible SSD pose guider is practical.

If not practical, the conclusion is:

> **exact SSD remains BLOCKED and the public compatibility reconstruction is exhausted for our production constraints.**

That is materially different from claiming that the published SSD method itself was proven incapable.

## Parameter sweeps — allowed only as controlled diagnostics

The earlier blanket instruction “do not tune CFG/steps/resolution” is superseded.

Controlled sweeps are allowed when they test a real hypothesis:

- fixed seed;
- fixed inputs;
- one variable at a time;
- small predefined range;
- outputs and metrics recorded side-by-side.

Random seed hunting or cosmetic rerolls remain prohibited as a production strategy.

## Wan-Animate-2 historical comparison

Wan's previous local configuration also failed, but under the same exhaustion protocol it should be classified as **a failed tested configuration, not exhaustive proof against the whole model family**.

Its workspace was already deleted under the earlier premature cleanup decision. Do not rebuild it while the retained SSD/Moore branch still has unresolved integration questions.

## Current next action

Stay on the retained Moore/SSD branch and build the controlled **Moore baseline vs SSD-weight substitution integration audit** before any new model installation.

## Variation strategy — later

Armor, equipment, accessories, damage and exposure still need scalable offline variation. Final runtime frames remain complete/precomposed.

## Cleanup

Retain runner-34 outputs, current SSD assets/environment and motion evidence until the exhaustion audit is explicitly closed.
