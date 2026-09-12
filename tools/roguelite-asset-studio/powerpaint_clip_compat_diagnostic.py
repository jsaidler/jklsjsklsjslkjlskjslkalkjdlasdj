#!/usr/bin/env python3
"""Diagnose PowerPaint learned-CLIP compatibility against the current ComfyUI CLIP runtime.

This performs no diffusion inference and downloads nothing. It reproduces only the
PowerPaintCLIPLoader setup path, then compares the current CLIP state_dict with the
PowerPaint learned text-encoder state before attempting load_state_dict.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path


def shape_of(value):
    shape = getattr(value, "shape", None)
    if shape is None:
        return None
    return [int(x) for x in shape]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", required=True)
    parser.add_argument("--base-clip", required=True)
    parser.add_argument("--powerpaint-bin", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    comfy_root = Path(args.comfy_root).resolve()
    base_clip = Path(args.base_clip).resolve()
    pp_bin = Path(args.powerpaint_bin).resolve()
    report_path = Path(args.report).resolve()
    brushnet_root = comfy_root / "custom_nodes" / "ComfyUI-BrushNet"
    pp_utils_dir = brushnet_root / "brushnet"

    for required in (comfy_root, brushnet_root, pp_utils_dir, base_clip, pp_bin):
        if not required.exists():
            raise FileNotFoundError(required)

    sys.path.insert(0, str(comfy_root))
    sys.path.insert(0, str(pp_utils_dir))

    import torch
    import transformers
    import comfy.sd
    import comfy.utils
    from powerpaint_utils import TokenizerWrapper, add_tokens

    print(f"RUNNER72-CLIP-DIAG: torch={torch.__version__} transformers={transformers.__version__}")
    print(f"RUNNER72-CLIP-DIAG: base_clip={base_clip}")
    print(f"RUNNER72-CLIP-DIAG: powerpaint_bin={pp_bin}")

    pp_clip = comfy.sd.load_clip(ckpt_paths=[str(base_clip)])
    pp_tokenizer = TokenizerWrapper(pp_clip.tokenizer.clip_l.tokenizer)
    pp_text_encoder = pp_clip.patcher.model.clip_l.transformer

    add_tokens(
        tokenizer=pp_tokenizer,
        text_encoder=pp_text_encoder,
        placeholder_tokens=["P_ctxt", "P_shape", "P_obj"],
        initialize_tokens=["a", "a", "a"],
        num_vectors_per_token=10,
    )

    current_state = pp_text_encoder.state_dict()
    learned_state = comfy.utils.load_torch_file(str(pp_bin))
    if not isinstance(learned_state, dict):
        raise TypeError(f"unexpected PowerPaint state type: {type(learned_state)!r}")

    current_keys = set(current_state)
    learned_keys = set(learned_state)
    common = sorted(current_keys & learned_keys)
    missing_in_current = sorted(learned_keys - current_keys)
    missing_in_learned = sorted(current_keys - learned_keys)

    mismatches = []
    compatible = []
    for key in common:
        a = shape_of(current_state[key])
        b = shape_of(learned_state[key])
        if a != b:
            mismatches.append({"key": key, "current_shape": a, "learned_shape": b})
        else:
            compatible.append(key)

    task_tokens = ("P_ctxt", "P_shape", "P_obj")
    task_keys = sorted(k for k in learned_keys if any(token in k for token in task_tokens))
    task_details = []
    for key in task_keys:
        task_details.append(
            {
                "key": key,
                "learned_shape": shape_of(learned_state[key]),
                "current_shape": shape_of(current_state[key]) if key in current_state else None,
                "compatible": key in current_state and shape_of(current_state[key]) == shape_of(learned_state[key]),
            }
        )

    load_error = None
    try:
        pp_text_encoder.load_state_dict(learned_state, strict=False)
    except Exception as exc:  # diagnostic: preserve exact PyTorch error text
        load_error = f"{type(exc).__name__}: {exc}"
        print("RUNNER72-CLIP-DIAG: exact load_state_dict failure follows:")
        print(load_error)

    report = {
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "current_key_count": len(current_keys),
        "learned_key_count": len(learned_keys),
        "common_key_count": len(common),
        "shape_mismatch_count": len(mismatches),
        "shape_mismatches": mismatches,
        "missing_in_current_count": len(missing_in_current),
        "missing_in_current": missing_in_current,
        "missing_in_learned_count": len(missing_in_learned),
        "missing_in_learned": missing_in_learned,
        "task_keys": task_details,
        "task_keys_all_compatible": bool(task_details) and all(item["compatible"] for item in task_details),
        "load_state_dict_error": load_error,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"RUNNER72-CLIP-DIAG: current_keys={len(current_keys)} learned_keys={len(learned_keys)} common={len(common)}")
    print(f"RUNNER72-CLIP-DIAG: shape_mismatches={len(mismatches)}")
    for item in mismatches[:40]:
        print(
            "  MISMATCH "
            f"{item['key']}: current={item['current_shape']} learned={item['learned_shape']}"
        )
    print(f"RUNNER72-CLIP-DIAG: task_keys={len(task_details)} all_compatible={report['task_keys_all_compatible']}")
    for item in task_details:
        print(
            "  TASK "
            f"{item['key']}: current={item['current_shape']} learned={item['learned_shape']} compatible={item['compatible']}"
        )
    print(f"RUNNER72-CLIP-DIAG: report={report_path}")
    print("RUNNER72-CLIP-DIAG: PASS - DIAGNOSTIC COMPLETE / NO INFERENCE EXECUTED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"RUNNER72-CLIP-DIAG: FAIL - {type(exc).__name__}: {exc}")
        traceback.print_exc()
        raise SystemExit(1)
