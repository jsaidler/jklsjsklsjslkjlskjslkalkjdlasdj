# Runner50 — CLIP-L SHA256 preflight failure

Status date: **2026-09-08**

Status: **RESOLVED / INTEGRATION FAIL / PRE-INFERENCE / ZERO KONTEXT QUALITY EVIDENCE**

Canonical renderer spike: `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`.

## Incident

Runner50 successfully downloaded and verified the FLUX.1 Kontext FP8-scaled diffusion model, then downloaded `clip_l.safetensors` from the intended Hugging Face source.

The runner rejected that CLIP-L file because the expected SHA256 embedded in project tooling was wrong by one extra/missing `c0` sequence.

Observed downloaded SHA256:

`660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`

Incorrect repository expectation before repair:

`660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c8576cd796491d9a6cdd`

Independent Hugging Face file metadata confirms the observed downloaded hash is the correct SHA256 for the standard 246MB FLUX `clip_l.safetensors` file.

The runner deleted the correctly downloaded CLIP-L file because the local expected hash was wrong. Therefore the next run must download CLIP-L again, but the already verified ~11.9GB Kontext diffusion file is preserved and will be reused.

## Classification

**INTEGRATION FAIL / PRE-INFERENCE.**

No ComfyUI Kontext inference was submitted, no prompt id was created, and this incident contains **zero evidence about FLUX.1 Kontext image quality**.

## Repair

Corrected the CLIP-L SHA256 in both:

- `tools/structured-2d-character-pipeline/50_run_flux_kontext_h0_dance12_pixelart_proof.ps1`
- `tools/flux-kontext-spike/run_h0_dance12_pixelart_proof.py`

Also re-checked the remaining first-spike hashes before asking for another run:

- Kontext FP8-scaled: `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`
- CLIP-L: `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`
- T5XXL FP16: `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`
- Flux AE/VAE: `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`

## Resume behavior

The corrected Runner50 is intentionally resumable:

- the already verified Kontext diffusion model remains in place and will only be hash-checked;
- CLIP-L must be downloaded again because the previous runner deleted it after the false mismatch;
- T5XXL FP16 and VAE then continue normally;
- no H3 video generation is repeated.
