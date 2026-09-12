#!/usr/bin/env python3
"""Run a Python script with one dependency overlay prepended to sys.path.

Designed for embedded/portable Python distributions that may ignore PYTHONPATH.
The overlay is process-local: it does not modify the base interpreter or its
site-packages. Usage:

    python python_overlay_launcher.py OVERLAY_DIR TARGET_SCRIPT [args...]
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: python_overlay_launcher.py OVERLAY_DIR TARGET_SCRIPT [args...]")

    overlay = Path(sys.argv[1]).resolve()
    target = Path(sys.argv[2]).resolve()
    target_args = sys.argv[3:]

    if not overlay.is_dir():
        raise FileNotFoundError(f"dependency overlay not found: {overlay}")
    if not target.is_file():
        raise FileNotFoundError(f"target script not found: {target}")

    sys.path.insert(0, str(overlay))
    sys.argv = [str(target), *target_args]
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
