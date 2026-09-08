# MiniMax H3 Base Ref2VA — local production screening spike

Status date: **2026-09-08**

Status: **CANONICAL / H0 COMPLETE / PASS_CANDIDATE / H1 GAME-RELEVANT WALK NEXT**

Canonical project state: `docs/PROJECT_STATE.md`.

Incident record: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

## Purpose

Determine whether **MiniMax H3 Base Ref2VA** can satisfy the Roguelite complete-character production contract on Windows11 / RTX3060 12GB /48GB RAM:

`Exilada appearance reference + arbitrary real driving video -> complete coherent animated character -> automatic gameplay-scale conversion -> spritesheet`

No routine manual rigging, keyframing, repair, masks, repainting or hand compositing.

## Transition from Wan

Wan-Animate-2 is **PAUSED AFTER W1L**, not exhausted. Preserve local W1H/W1L evidence. H3 is now the active family.

## Ref2VA mapping

- `<Picture 1>` = Exilada appearance/identity/anatomy/clothing/hair/art language;
- `<Video 1>` = movement/performance/timing/weight transfer only.

The prompt explicitly ignores the driver's identity/body/clothing/hair/environment/style.

## Integration history

Runner46 prepared the dedicated ComfyUI v0.34.0 environment and H0 inputs. Runner47 was rejected before inference because `MiniMaxH3ReferenceToVideo.audio_vae` is a required node input even without audio references. This was classified **INTEGRATION_FAIL / PRE-INFERENCE**.

Runner48 added only the official schema-required audio VAE and preserved every quality variable.

Correct minimal H3 Ref2VA set:

1. `models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors` — ~21GB.
2. `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` — ~15.7GB.
3. `models/vae/minimax_h3_video_vae_fp16.safetensors` — ~5.21GB.
4. `models/vae/minimax_h3_audio_vae_fp32.safetensors` — 605,254,808 bytes; SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`.

Total active payload ~42.5GB. The audio VAE is a schema dependency only; H0 uses no audio reference and produces no audio output.

Explicitly excluded: FL2VA, alternate Ref2VA quantizations, Turbo LoRA and style embeddings.

## H0 input preparation

Appearance:

`assets/source/characters/exilada/reference/exilada_master.png`

Driver:

`ComfyUI/input/roguelite_h3/h0_driver_24fps_124f.mp4`

Driver normalization:

- exactly124 frames at24fps;
- no crop;
- no resize;
- no tracking/recentering/stabilization;
- audio removed;
- timestamp resampling only.

## H0 exact completed baseline

- task `ref2va`;
- `448×800`;
-124 frames @24fps;
- duration ~5.17s;
- `ref_image_size=match`;
-50 steps;
- `res_multistep`;
- `beta`;
- seed0;
- H3 sigma shifts video12/audio3;
- no Turbo;
- Picture1 = Exilada appearance;
- Video1 = motion only;
- audio VAE wired only because required by schema.

Completion evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- canonical output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- output SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`;
- gameplay proxy `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4`;
- proxy SHA256 `32d9f2873798e4920639055c1a0ea9336dffd891d857a36e03ccf142a874ecbd`.

## H0 visual review

The uploaded 448×800 video and 90×160 gameplay proxy were reviewed across the 124-frame sequence.

### Verdict

**PASS_CANDIDATE / FAMILY ADVANCES.**

### Strong evidence

- stable head/torso/two arms/two legs across the sequence;
- no observed duplicated/fused/disappearing limbs or whole-body ghost doubles;
- torso/hip/body proportions stay materially coherent;
- face and general identity remain internally stable;
- hair remains long/heavy and visibly responds to motion;
- torn cloth moves with the body while remaining attached;
- shackles/chains remain accessory geometry rather than morphing into flesh;
- image stays materially sharper and structurally more legible than the problematic Wan runs;
- painterly illustrated dark-fantasy rendering is highly compatible with the locked Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell direction;
- gameplay-scale proxy retains a clear pose/silhouette near the target ~128px character height.

### Residual defects

- chain geometry is not perfectly invariant; length/curve/attachment details drift somewhat;
- toward the end of the clip the character reaches the right frame edge and the right foot becomes partially cropped. This is classified as a **framing/driver-envelope issue**, not observed anatomy collapse;
- exact one-to-one fidelity against the canonical master remains an art-finalization check, although the generated character remains internally stable through H0.

## Resolution decision

`448×800` passes the quality gate. Do **not** escalate to `480×864`, `512×896` or a 768-short-edge control without a new failure that specifically points to under-resolution.

`ref_image_size=max` is also deferred. H0 does not show a clear identity-collapse problem that justifies the additional reference-token cost.

This supports the project hypothesis that generating below the model's usual 768-short-edge regime can be practical because final runtime sprites are only ~128px tall.

## Gameplay-scale result

The proxy is 90×160. With the character occupying most of the frame, the visible figure is roughly in the target runtime-height range. Pose, body mass, hair silhouette and limb direction remain readable. Minor high-frequency texture loss at this scale is acceptable; the important topology survives.

## Throughput

H0 elapsed `4504.8s` for124 frames: ~36.3s/generated frame. Treat this only as an offline Base-quality reference because it is not directly comparable to Wan's different frame count/resolution/sampler. Do not optimize speed before the game-relevant locomotion gate passes.

## Manifest metadata note

The completed uploaded H0 manifest has a legacy top-level `audio_vae: null` inherited from the base executor, while its `integration_fix` block correctly records `minimax_h3_audio_vae_fp32.safetensors`. The repaired wrapper is corrected for future runs so top-level `audio_vae` is also populated. The metadata discrepancy did not affect the completed H0 graph or output.

## NEXT — H1 GAME-RELEVANT WALK DRIVER

Do not tune nearby H0 settings again. Replace only the motion reference with a game-relevant real walking/performance clip while retaining the successful H0 quality baseline.

Required driver properties:

- one adult performer;
- whole body visible;
- fixed camera;
- continuous shot;
- screen-left locomotion;
- mostly lateral/slight 3/4, targeting the locked `72°` facing baseline;
- at least one complete gait cycle;
- enough head/feet/lateral margin that no source-envelope crop is forced;
- performer clothing/hair/identity/body resemblance irrelevant.

Initial H1 settings remain:

- `448×800`;
- Base50;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`.

H1 pass criteria:

- correct locomotion timing and weight transfer;
- complete body through the gait cycle;
- H0-level topology stability;
- readable hair/cloth/restraint secondary response;
- usable gameplay-scale silhouette for a locomotion spritesheet.

After H1 passes, advance to stronger secondary dynamics/wind/restraint stress. Turbo/speed optimization comes afterward.

## Cleanup

H3 is now both technically and visually proven active. Paused Wan large checkpoint weights may be removed while preserving W1H/W1L videos, prompts, manifests and logs. Keep only the minimal four-file H3 Ref2VA set. Do not accumulate FL2VA/Turbo/style/alternate quantizations until a later explicit hypothesis requires them. Keep SSD/Moore comparison evidence until explicit abandonment/final verdict.
