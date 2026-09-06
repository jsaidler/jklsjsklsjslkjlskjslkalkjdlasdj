#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

EXPECTED_BODY_SIZE = (37, 128)
EXPECTED_BODY_PNG_SHA256 = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"
EXPECTED_BODY_RAW_RGBA_SHA256 = "818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c"
LOGICAL_CANVAS = (96, 160)
BODY_GROUND_Y = 152
BODY_X = (LOGICAL_CANVAS[0] - EXPECTED_BODY_SIZE[0]) // 2
BODY_Y = BODY_GROUND_Y - EXPECTED_BODY_SIZE[1]
UPSCALE = 6
MODEL_CANVAS = (LOGICAL_CANVAS[0] * UPSCALE, LOGICAL_CANVAS[1] * UPSCALE)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_rgba_sha256(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    body_path = Path(args.body)
    master_path = Path(args.master)
    input_dir = Path(args.input_dir)
    workspace = Path(args.workspace)
    input_dir.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)

    for p in (body_path, master_path):
        if not p.is_file():
            raise FileNotFoundError(p)

    body = Image.open(body_path).convert("RGBA")
    if body.size != EXPECTED_BODY_SIZE:
        raise RuntimeError(f"body size mismatch: got={body.size} expected={EXPECTED_BODY_SIZE}")
    if file_sha256(body_path) != EXPECTED_BODY_PNG_SHA256:
        raise RuntimeError("canonical body PNG SHA mismatch")
    if raw_rgba_sha256(body) != EXPECTED_BODY_RAW_RGBA_SHA256:
        raise RuntimeError("canonical body raw-RGBA SHA mismatch")

    logical = Image.new("RGBA", LOGICAL_CANVAS, (228, 226, 222, 255))
    logical.alpha_composite(body, (BODY_X, BODY_Y))
    model_ref = logical.convert("RGB").resize(MODEL_CANVAS, Image.Resampling.NEAREST)

    body_ref_path = input_dir / "g3s_b4c_body_pose_reference.png"
    master_ref_path = input_dir / "g3s_b4c_exilada_master.png"
    model_ref.save(body_ref_path)
    shutil.copy2(master_path, master_ref_path)

    logical_preview_path = workspace / "g3s_b4c_body_reference_logical.png"
    logical.convert("RGB").save(logical_preview_path)

    meta = {
        "gate": "G3S-B4",
        "revision": "B4C_FLUX2_VISUAL_ADAPTER_INPUTS_V1",
        "status": "PREPARED",
        "body_png_sha256": EXPECTED_BODY_PNG_SHA256,
        "body_raw_rgba_sha256": EXPECTED_BODY_RAW_RGBA_SHA256,
        "master_sha256": file_sha256(master_path),
        "logical_canvas": list(LOGICAL_CANVAS),
        "model_canvas": list(MODEL_CANVAS),
        "integer_upscale": UPSCALE,
        "body_anchor": {"x": BODY_X, "y": BODY_Y, "ground_y": BODY_GROUND_Y},
        "body_reference": str(body_ref_path),
        "master_reference": str(master_ref_path),
        "note": "Body reference is exact canonical B3B pixels composited on a flat neutral field and enlarged by integer nearest-neighbor only. It is a conditioning/reference image, not a new production sprite."
    }
    meta_path = workspace / "g3s_b4c_input_manifest.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("G3S-B4C INPUT PREP: PASS")
    print(f"BODY_REF:   {body_ref_path}")
    print(f"MASTER_REF: {master_ref_path}")
    print(f"META:       {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
