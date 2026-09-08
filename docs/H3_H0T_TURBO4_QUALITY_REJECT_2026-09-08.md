# H3 H0T / Runner49 — Turbo4 quality rejection

Status date: **2026-09-08**

Status: **COMPLETED ENOUGH FOR VISUAL REVIEW / REJECTED FOR PRODUCTION QUALITY / BASE50 RESTORED**

Canonical state: `docs/PROJECT_STATE.md`.

## Purpose

Preserve the controlled production-speed experiment that compared the official MiniMax H3 Ref2V Turbo4 path against the already-approved H0 Base50 quality baseline.

## Controlled change

Runner49 kept the H0 references/geometry/prompt and introduced the official Turbo path:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- LoRA strength `1.0`;
- `4 steps`;
- `res_multistep/simple`.

H0 comparison baseline remained:

- `448×800`;
- `124f @24fps`;
- `ref_image_size=match`;
- seed `0`;
- same target appearance reference;
- same movement reference;
- same prompt semantics.

## Human visual verdict

The user reviewed the 4-step result and **did not like the quality**. The user explicitly requested returning to the initial H0 configuration that produced the preferred video:

- Base Ref2VA;
- `50 steps`;
- `res_multistep/beta`;
- no Turbo LoRA;
- all other proven H0 settings retained.

Classification for production selection:

**MODEL/SETTING QUALITY FAIL FOR THIS TURBO4 CONFIGURATION**.

This does **not** count as a failure of the MiniMax H3 family. It rejects only the Turbo4 production-speed configuration.

## Evidence discipline

Do not invent exact Turbo4 elapsed time, prompt id, output hash or artifact path in canonical documents unless those values are recovered from the local Runner49 manifest/log/output.

The qualitative human verdict is sufficient to reject Turbo4 as the default production setting.

## Decision

**LOCKED:** H3 Base50 H0 becomes the canonical motion-master quality configuration again.

**REJECTED:** Turbo4 must not be used by default merely for speed.

A future faster H3 configuration may be tested only as a new controlled hypothesis and must match the Base50 visual quality before replacing it.

## Cleanup

Preserve the local Turbo4 output/log/manifest if available until the rejection is fully archived. After evidence is preserved, the ~1.96GB Turbo LoRA may be removed because it is no longer an active production dependency.
