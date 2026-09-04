# Roguelite — Current Project State

Status date: **2026-09-04**

Purpose: **canonical cross-chat operational handoff.** This file is intentionally concise. It records the current active work, last validated checkpoint, next exact gate, machine/workspace facts and the process rule for keeping project memory synchronized. Detailed design decisions remain in the linked living documents rather than being duplicated here.

## Canonical living documents

- `docs/VISUAL_DIRECTION.md` — locked visual language, camera, production constraints and art-pipeline principles.
- `docs/CHARACTERS.md` — canonical character definitions, including the Exilada.
- `docs/ANIMATION_PIPELINE.md` — animation architecture, rejected approaches, research, active spike and acceptance/rejection gates.
- `docs/PROJECT_STATE.md` — current operational checkpoint and cross-chat handoff.

These documents are the durable project memory. When a decision changes, edit the relevant existing canonical document instead of creating parallel versions.

## Mandatory checkpoint protocol

After **every material project step** — success, failure, architectural decision, rejected route, new constraint, installed component, generated validation artifact or changed next gate — do all of the following before moving on:

1. update the relevant canonical living document(s);
2. update this `PROJECT_STATE.md` with the latest validated checkpoint and exact next action;
3. record any repository tooling change in git with a focused commit;
4. do not rely only on chat history or model memory for state that another chat must recover;
5. when a chat is near its context limit, stop before starting a new technical step, sync the documents, then hand off with a prompt that instructs the new chat to read these canonical files first.

The assistant should also keep its available project/personal memory aligned with these durable documents when the product permits it, but **GitHub living documents are the source of truth** for cross-chat continuity.

## Active focus

**Character re-posing validation: FLUX.2 Klein Base 4B FP8 + RefControl Pose, fully local, headless/CLI, Windows 11, RTX 3060 12 GB.**

This is not video generation and not motion-sequence generation. The current spike asks one narrow question: can the canonical Exilada design reference be rendered into four explicit walk key poses while maintaining source identity/anatomy and obeying the supplied COCO-18 skeletons?

Final gameplay modern-pixel-art compliance is a separate downstream production-raster gate. The current high-detail `exilada_master.png` is the canonical design/identity reference, not proof of final gameplay pixel construction.

## Locked constraints relevant to the active spike

- no paid/proprietary hosted generation APIs;
- local/self-hosted code and weights only unless the user explicitly authorizes an exception in advance;
- no manual frame-by-frame art work;
- no seed fishing;
- no inpainting/manual repair to rescue a failed route;
- no Pixel Art LoRA in this spike;
- no video generation;
- no interpolation;
- one fixed seed: `20260904`;
- four deterministic walk poses only: `contact_L`, `passing_L`, `contact_R`, `passing_R`;
- one render per pose once generation is authorized;
- no inference before the runtime/workflow schema gate passes.

## User machine / paths

Target machine:

- Windows 11 Home Single Language;
- 47.7 GB usable RAM detected;
- NVIDIA GeForce RTX 3060 12 GB;
- driver observed during preflight: `595.95`;
- repository: `D:\GOOGLE DRIVE\DEV\Roguelite`;
- active spike workspace: `D:\AI\Flux2RefControlSpike`.

Canonical Exilada master:

`D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png`

Active repository tooling:

`tools/flux2-refcontrol-spike/`

## FLUX.2 + RefControl spike — validated execution state

### STEP 1 — preflight: PASS

Validated:

- Windows 11;
- 47.7 GB RAM;
- RTX 3060 12 GB;
- sufficient free disk space;
- canonical Exilada master exists;
- git and winget available;
- 7-Zip available.

No model download or inference occurred.

### STEP 2 — ComfyUI portable runtime: PASS

Installed/validated at:

`D:\AI\Flux2RefControlSpike\ComfyUI_windows_portable`

Validated runtime:

- Python `3.13.14`;
- PyTorch `2.13.0+cu130`;
- CUDA runtime `13.0`;
- `torch.cuda.is_available() = True`;
- GPU `NVIDIA GeForce RTX 3060`;
- VRAM reported by PyTorch: `12.00 GB`.

Important history: two script-only failures occurred before this pass — a Windows PowerShell 5.1 scalar `.Count` issue and quoting corruption in an inline Python `-c` probe. Both were corrected. They were not GPU/runtime failures.

Current script: `tools/flux2-refcontrol-spike/01_install_comfyui.ps1`.

### STEP 3 — required weights: PASS

Exactly four required model files were installed and hash-validated. No generation occurred.

Required model set:

- `flux-2-klein-base-4b-fp8.safetensors`;
- `qwen_3_4b.safetensors`;
- `flux2-vae.safetensors`;
- `refcontrol-pose-klein-4b.safetensors`.

No OpenPose model, video model, Pixel Art LoRA or additional generation model is part of this spike.

Current script: `tools/flux2-refcontrol-spike/02_download_models.ps1`.

### STEP 4 — canonical reference + deterministic skeleton inputs: PASS

Prepared reference:

`D:\AI\Flux2RefControlSpike\ComfyUI_windows_portable\ComfyUI\input\exilada_master.png`

It is copied byte-for-byte from the canonical repository master and hash-checked; no resize, crop, repaint, palette modification or regeneration is performed.

Prepared pose PNGs:

- `refcontrol_poses\pose_00_contact_L.png`;
- `refcontrol_poses\pose_01_passing_L.png`;
- `refcontrol_poses\pose_02_contact_R.png`;
- `refcontrol_poses\pose_03_passing_R.png`.

Pose specification JSONs:

`D:\AI\Flux2RefControlSpike\pose_specs\`

Manifest:

`D:\AI\Flux2RefControlSpike\input_manifest.json`

Pose format:

- deterministic OpenPose-style COCO-18;
- 18 explicit joints;
- black background;
- canvas `768 × 1024`;
- no pose-estimation model;
- no network access in this step;
- no random geometry;
- no inference.

Current script: `tools/flux2-refcontrol-spike/03_prepare_inputs.ps1`.

## Exact next gate — do not skip

### STEP 5 — runtime schema/workflow validation **without inference**

Next conversation must continue here, not rerun completed setup unless validation reveals corruption.

Goal:

1. start the already-installed ComfyUI portable headless on `127.0.0.1:8188`;
2. query/save its local `/object_info` schema;
3. verify that the installed runtime exposes the exact core node types and loader contracts required for the FLUX.2 Klein two-reference edit path plus model-only RefControl LoRA;
4. verify the four installed filenames are visible to the correct loaders;
5. verify the intended way to supply **image 1 = COCO-18 target skeleton** and **image 2 = Exilada reference** using the current ComfyUI core FLUX.2 edit architecture (`ReferenceLatent`/equivalent) before constructing an executable workflow;
6. stop the server after validation;
7. perform **zero inference** and queue **zero prompts** in this step.

Only after STEP 5 passes should the repository gain the executable headless workflow builder/runner for the four one-shot renders.

## Current architecture evidence already established

The installed/current ComfyUI codebase contains native FLUX.2 support, including:

- FLUX.2 model detection/support;
- `CLIPLoader` support for `flux2` / Qwen3 4B;
- `EmptyFlux2LatentImage`;
- `Flux2Scheduler`;
- `ReferenceLatent` (Set Reference Latent) for edit-model reference latents;
- `LoraLoaderModelOnly`;
- the official `Image Edit (Flux.2 Klein 4B)` blueprint using `flux-2-klein-base-4b-fp8.safetensors`, `qwen_3_4b.safetensors` and `flux2-vae.safetensors`.

Do not assume the final two-reference API graph until STEP 5 inspects the runtime's actual `/object_info` schema locally.

## Relevant repository milestone commits from this spike

- `090dc4ee3e06f3c3010657fe9bd01b52e692ee69` — preflight tooling added.
- `36059f75e14626f56abaf214eec708add6600216` — final Windows PowerShell-compatible ComfyUI runtime validation fix.
- `d6f19fb8ba79dbb048e5b96ccb862537c56cdb58` — four-weight downloader/validator.
- `e047ee70c31cb72c193c5dfa08daf1a1db8c1d58` — canonical reference and deterministic four-pose input preparation.

## Rejected / stopped animation routes that must not be revived casually

Detailed rationale lives in `docs/ANIMATION_PIPELINE.md`. Current status:

- Sprite Sheet Diffusion — tested locally, rejected;
- Wan-Animate-2 Base INT8 — tested locally, rejected;
- PixelLab skeleton route — stopped because relevant production path requires hosted/tiered service;
- Pixel Engine — disqualified as paid/proprietary hosted dependency;
- Retro Diffusion hosted route — disqualified under the same rule;
- generic video diffusion is not the current architecture.

## What a new chat must read before acting

In order:

1. `docs/PROJECT_STATE.md`;
2. `docs/ANIMATION_PIPELINE.md`;
3. `docs/VISUAL_DIRECTION.md`;
4. `docs/CHARACTERS.md`;
5. current files under `tools/flux2-refcontrol-spike/` if code changes are required.

After reading, continue **only from STEP 5** above unless the user explicitly changes the plan.
