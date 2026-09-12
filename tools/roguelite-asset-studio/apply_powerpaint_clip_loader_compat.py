#!/usr/bin/env python3
"""Apply the Runner72 PowerPaint CLIP loader compatibility patch safely.

The pinned ComfyUI-BrushNet loader performs a regular copy-based load_state_dict
of the ~492 MB learned PowerPaint CLIP state after the much larger BrushNet stack
has already been materialized. On the current portable runtime the exact same
state loads successfully in isolation, with zero shape mismatches, but the full
workflow process dies while copying that state.

This patch is deliberately narrow and behavior-preserving: use PyTorch's
load_state_dict(assign=True) so compatible tensors become the module parameters
without a second full tensor copy. The project diagnostic proved all shared
shapes and the three task-token tensors are compatible.

The patch is idempotent and fail-closed. It only edits the exact upstream line
expected at the pinned ComfyUI-BrushNet commit.
"""

from __future__ import annotations

import argparse
from pathlib import Path

MARKER = "# RUNNER72_COMPAT_ASSIGN_LOAD"
ORIGINAL = "        pp_text_encoder.load_state_dict(comfy.utils.load_torch_file(pp_CLIP_file), strict=False)"
PATCHED = """        # RUNNER72_COMPAT_ASSIGN_LOAD\n        pp_state = comfy.utils.load_torch_file(pp_CLIP_file)\n        pp_load_result = pp_text_encoder.load_state_dict(pp_state, strict=False, assign=True)\n        print('PowerPaint CLIP state loaded with assign=True:', pp_load_result)\n        del pp_state"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brushnet-nodes", required=True)
    args = parser.parse_args()

    path = Path(args.brushnet_nodes).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"RUNNER72-COMPAT: already applied: {path}")
        return 0

    count = text.count(ORIGINAL)
    if count != 1:
        raise RuntimeError(
            f"expected exactly one pinned PowerPaint CLIP load line, found {count}; "
            "refusing to patch unknown upstream source"
        )

    updated = text.replace(ORIGINAL, PATCHED, 1)
    path.write_text(updated, encoding="utf-8", newline="\n")

    verify = path.read_text(encoding="utf-8")
    if MARKER not in verify or ORIGINAL in verify:
        raise RuntimeError("post-write verification failed")

    print(f"RUNNER72-COMPAT: applied assign=True CLIP load patch: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
