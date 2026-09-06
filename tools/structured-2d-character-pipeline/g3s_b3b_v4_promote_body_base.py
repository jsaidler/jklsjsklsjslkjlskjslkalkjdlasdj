#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

EXPECTED_SIZE = (37, 128)
# Authoritative digest observed from the user's actual local V4 candidate.
EXPECTED_RAW_RGBA_SHA256 = "818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c"
LOCKED_REFERENCE_SHA256 = "f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a"
REVIEWED_CONTACT_SHEET_SHA256 = "2b3ad85e956fdd432fe6cd52ac94d71afd30b5603b071681f81d2dbd8788a182"
PROMOTION_HASH_MISMATCH_MARKER = "tools/structured-2d-character-pipeline/g3s_b3b_v4_promotion_hash_mismatch.json"


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
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--repo-root", required=True)
    args = ap.parse_args()

    candidate = Path(args.candidate)
    repo_root = Path(args.repo_root)
    if not candidate.is_file():
        raise FileNotFoundError(candidate)

    im = Image.open(candidate).convert("RGBA")
    if im.size != EXPECTED_SIZE:
        raise RuntimeError(f"candidate size mismatch: got={im.size} expected={EXPECTED_SIZE}")

    raw_hash = raw_rgba_sha256(im)
    if raw_hash != EXPECTED_RAW_RGBA_SHA256:
        raise RuntimeError(
            "candidate raw-RGBA digest mismatch; refusing promotion. "
            f"got={raw_hash} expected={EXPECTED_RAW_RGBA_SHA256}"
        )

    alpha = im.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("candidate alpha is empty")
    if bbox[3] - bbox[1] != 128:
        raise RuntimeError(f"visible alpha height changed: bbox={bbox}")

    out_dir = repo_root / "assets/source/characters/exilada/body"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "exilada_body_base_b3b_v4.png"
    out_json = out_dir / "exilada_body_base_b3b_v4.json"

    shutil.copyfile(candidate, out_png)
    png_sha = file_sha256(out_png)

    metadata = {
        "asset": "Exilada nude hairless body base",
        "gate": "G3S-B3B-V4",
        "status": "PROMOTED_PRODUCTION_BODY_BASE",
        "date": "2026-09-06",
        "canonical_png": "assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png",
        "png_sha256": png_sha,
        "raw_rgba_sha256": raw_hash,
        "dimensions_px": list(im.size),
        "visible_standing_height_px": 128,
        "native_scene": [640, 360],
        "camera_pitch_deg": 26,
        "view": "front-three-quarter elevated belt-scroller",
        "body_state": "adult nude hairless barefoot body base",
        "locked_visual_reference_sha256": LOCKED_REFERENCE_SHA256,
        "reviewed_contact_sheet_sha256": REVIEWED_CONTACT_SHEET_SHA256,
        "promotion_hash_mismatch_marker": PROMOTION_HASH_MISMATCH_MARKER,
        "visible_ownership": "persistent 2D pixel asset",
        "not_included": ["hair", "clothing", "restraints", "accessories", "weapons"],
        "notes": "Promoted from the user's actual local V4 candidate after correcting an implementation bug that had hardcoded an assistant-side reconstructed raw-RGBA digest. Promotion itself performs no smoothing, palette synthesis, anatomy repair, hidden-3D RGB/mask use, or render-to-pixel conversion."
    }
    out_json.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"PROMOTED PNG:  {out_png}")
    print(f"METADATA:      {out_json}")
    print(f"PNG SHA256:    {png_sha}")
    print(f"RAW RGBA SHA:  {raw_hash}")
    print("STATUS: PROMOTED LOCALLY - READY FOR FOCUSED GIT COMMIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
