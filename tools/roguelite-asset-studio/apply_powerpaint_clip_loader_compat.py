#!/usr/bin/env python3
"""Apply the Runner72 PowerPaint / ComfyUI-BrushNet compatibility patches safely.

The project pins ComfyUI and ComfyUI-BrushNet independently because other proven
Asset Studio backends depend on the current ComfyUI runtime. Runner72 therefore
owns a very small compatibility layer rather than asking the user to patch a
custom node by hand or globally upgrading/downgrading the shared runtime.

This patcher currently handles three proven integration mismatches:

1. PowerPaint learned CLIP loading
   The exact learned state is shape-compatible with the current ComfyUI CLIP,
   but copy-based load_state_dict failed in the full graph after the larger
   BrushNet stack was already resident. Use assign=True to avoid a second full
   parameter copy.

2. comfy.ops.pick_operations / scaled_fp8
   The pinned BrushNet code passes scaled_fp8, while the pinned shared ComfyUI
   pick_operations does not accept that keyword. Preserve upstream behavior on
   runtimes that support it and retry without only that keyword when the exact
   compatibility TypeError occurs.

3. sampler wrapper kwargs
   Newer ComfyUI sampler wrappers may provide extra keyword arguments. Make the
   pinned BrushNet wrapper accept and forward **kwargs without changing normal
   behavior.

Every edit is idempotent and fail-closed. A source fragment is changed only when
it exactly matches the expected pinned upstream text. Unknown upstream source is
never modified.
"""

from __future__ import annotations

import argparse
from pathlib import Path

CLIP_MARKER = "# RUNNER72_COMPAT_ASSIGN_LOAD"
CLIP_ORIGINAL = "        pp_text_encoder.load_state_dict(comfy.utils.load_torch_file(pp_CLIP_file), strict=False)"
CLIP_PATCHED = """        # RUNNER72_COMPAT_ASSIGN_LOAD
        pp_state = comfy.utils.load_torch_file(pp_CLIP_file)
        pp_load_result = pp_text_encoder.load_state_dict(pp_state, strict=False, assign=True)
        print('PowerPaint CLIP state loaded with assign=True:', pp_load_result)
        del pp_state"""

OPS_MARKER = "# RUNNER72_COMPAT_PICK_OPERATIONS"
OPS_ORIGINAL = """        operations = comfy.ops.pick_operations(model.model.model_config.unet_config.get(\"dtype\", None), model.model.manual_cast_dtype,
                                               fp8_optimizations=fp8, scaled_fp8=model.model.model_config.scaled_fp8)"""
OPS_PATCHED = """        # RUNNER72_COMPAT_PICK_OPERATIONS
        try:
            operations = comfy.ops.pick_operations(model.model.model_config.unet_config.get(\"dtype\", None), model.model.manual_cast_dtype,
                                                   fp8_optimizations=fp8, scaled_fp8=model.model.model_config.scaled_fp8)
        except TypeError as exc:
            if \"scaled_fp8\" not in str(exc) or \"unexpected keyword argument\" not in str(exc):
                raise
            print('RUNNER72-COMPAT: pick_operations has no scaled_fp8 keyword; retrying without scaled_fp8')
            operations = comfy.ops.pick_operations(model.model.model_config.unet_config.get(\"dtype\", None), model.model.manual_cast_dtype,
                                                   fp8_optimizations=fp8)"""

SAMPLER_MARKER = "# RUNNER72_COMPAT_SAMPLER_KWARGS"
SAMPLER_DEF_ORIGINAL = "def brushNet_out_sample_wrapper(wrapper_executor, noise, latent_image, sampler, sigmas, denoise_mask=None, callback=None, disable_pbar=False, seed=None):"
SAMPLER_DEF_PATCHED = """# RUNNER72_COMPAT_SAMPLER_KWARGS
def brushNet_out_sample_wrapper(wrapper_executor, noise, latent_image, sampler, sigmas, denoise_mask=None, callback=None, disable_pbar=False, seed=None, **kwargs):"""
SAMPLER_CALL_ORIGINAL = "        out = wrapper_executor(noise, latent_image, sampler, sigmas, denoise_mask=denoise_mask, callback=callback, disable_pbar=disable_pbar, seed=seed)"
SAMPLER_CALL_PATCHED = "        out = wrapper_executor(noise, latent_image, sampler, sigmas, denoise_mask=denoise_mask, callback=callback, disable_pbar=disable_pbar, seed=seed, **kwargs)"


def patch_exact(text: str, marker: str, original: str, patched: str, label: str) -> tuple[str, bool]:
    if marker in text:
        print(f"RUNNER72-COMPAT: {label} already applied")
        return text, False

    count = text.count(original)
    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one pinned source fragment, found {count}; "
            "refusing to patch unknown upstream source"
        )
    return text.replace(original, patched, 1), True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brushnet-nodes", required=True)
    parser.add_argument("--model-patch", required=True)
    args = parser.parse_args()

    brushnet_nodes = Path(args.brushnet_nodes).resolve()
    model_patch = Path(args.model_patch).resolve()
    for path in (brushnet_nodes, model_patch):
        if not path.is_file():
            raise FileNotFoundError(path)

    nodes_text = brushnet_nodes.read_text(encoding="utf-8")
    nodes_text, clip_changed = patch_exact(
        nodes_text, CLIP_MARKER, CLIP_ORIGINAL, CLIP_PATCHED, "assign=True CLIP load"
    )
    nodes_text, ops_changed = patch_exact(
        nodes_text, OPS_MARKER, OPS_ORIGINAL, OPS_PATCHED, "pick_operations scaled_fp8 compatibility"
    )
    if clip_changed or ops_changed:
        brushnet_nodes.write_text(nodes_text, encoding="utf-8", newline="\n")

    model_text = model_patch.read_text(encoding="utf-8")
    if SAMPLER_MARKER in model_text:
        print("RUNNER72-COMPAT: sampler **kwargs compatibility already applied")
        sampler_changed = False
    else:
        def_count = model_text.count(SAMPLER_DEF_ORIGINAL)
        call_count = model_text.count(SAMPLER_CALL_ORIGINAL)
        if def_count != 1 or call_count != 1:
            raise RuntimeError(
                "sampler **kwargs compatibility: expected exactly one pinned wrapper definition "
                f"and call, found def={def_count} call={call_count}; refusing to patch unknown upstream source"
            )
        model_text = model_text.replace(SAMPLER_DEF_ORIGINAL, SAMPLER_DEF_PATCHED, 1)
        model_text = model_text.replace(SAMPLER_CALL_ORIGINAL, SAMPLER_CALL_PATCHED, 1)
        model_patch.write_text(model_text, encoding="utf-8", newline="\n")
        sampler_changed = True

    verify_nodes = brushnet_nodes.read_text(encoding="utf-8")
    verify_model = model_patch.read_text(encoding="utf-8")
    required_markers = (
        (CLIP_MARKER, verify_nodes),
        (OPS_MARKER, verify_nodes),
        (SAMPLER_MARKER, verify_model),
    )
    missing = [marker for marker, content in required_markers if marker not in content]
    if missing:
        raise RuntimeError(f"post-write verification failed; missing markers: {missing}")

    if clip_changed:
        print(f"RUNNER72-COMPAT: applied assign=True CLIP load patch: {brushnet_nodes}")
    if ops_changed:
        print(f"RUNNER72-COMPAT: applied scaled_fp8 compatibility patch: {brushnet_nodes}")
    if sampler_changed:
        print(f"RUNNER72-COMPAT: applied sampler **kwargs compatibility patch: {model_patch}")
    if not (clip_changed or ops_changed or sampler_changed):
        print("RUNNER72-COMPAT: all compatibility patches already present")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
