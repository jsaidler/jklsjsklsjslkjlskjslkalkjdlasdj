#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

LOGICAL = (96, 160)
MODEL = (576, 960)
BG = (14, 14, 18)
TEXT = (236, 236, 240)
DIM = (170, 170, 180)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def font():
    return ImageFont.load_default()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-manifest", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    run_path = Path(args.run_manifest)
    body_path = Path(args.body)
    ws = Path(args.workspace)
    if not run_path.is_file():
        raise FileNotFoundError(run_path)
    if not body_path.is_file():
        raise FileNotFoundError(body_path)
    ws.mkdir(parents=True, exist_ok=True)

    run = json.loads(run_path.read_text(encoding="utf-8-sig"))
    if run.get("gate") != "G3S-C1B" or run.get("revision") != "FLUX2_EIGHT_POSE_VISUAL_PROOF_V1":
        raise RuntimeError("unexpected C1B run manifest")
    outputs = run.get("outputs", [])
    if len(outputs) != 8:
        raise RuntimeError(f"expected 8 generated frames, got {len(outputs)}")

    logical_frames = []
    review_rows = []
    for row in outputs:
        p = Path(row["generated"])
        if not p.is_file():
            raise FileNotFoundError(p)
        im = Image.open(p).convert("RGB")
        if im.size != MODEL:
            raise RuntimeError(f"unexpected generated size {im.size}: {p}")
        # Review-only logical sampling. These pixels are NOT promoted as production assets.
        logical = im.resize(LOGICAL, Image.Resampling.NEAREST)
        logical_path = ws / f"g3s_c1b_review_{int(row['index']):02d}_{row['event']}_logical.png"
        logical.save(logical_path)
        logical_frames.append(logical)
        review_rows.append({
            "index": int(row["index"]),
            "frame": int(row["frame"]),
            "event": str(row["event"]),
            "support_foot": str(row["support_foot"]),
            "generated": str(p),
            "generated_sha256": sha256_file(p),
            "logical_review": str(logical_path),
            "logical_review_sha256": sha256_file(logical_path),
        })

    display_frames = [im.resize((LOGICAL[0]*3, LOGICAL[1]*3), Image.Resampling.NEAREST) for im in logical_frames]
    gif_path = ws / "g3s_c1b_exilada_walk_visual_proof.gif"
    display_frames[0].save(
        gif_path,
        save_all=True,
        append_images=display_frames[1:],
        duration=int(run.get("frame_duration_ms", 83)),
        loop=0,
        disposal=2,
        optimize=False,
    )

    cell_w, cell_h = 288, 480
    footer_h = 130
    sheet = Image.new("RGB", (cell_w*4, cell_h*2 + footer_h), BG)
    d = ImageDraw.Draw(sheet)
    for i, (frame, row) in enumerate(zip(display_frames, review_rows)):
        x = (i % 4) * cell_w
        y = (i // 4) * cell_h
        sheet.paste(frame, (x, y))
        d.rectangle((x, y, x+cell_w, y+28), fill=(8, 8, 11))
        d.text((x+8, y+9), f"{row['event']} | src {row['frame']} | support {row['support_foot']}", fill=TEXT, font=font())

    body = Image.open(body_path).convert("RGBA")
    body_big = body.resize((body.width*3, body.height*3), Image.Resampling.NEAREST)
    fy = cell_h*2 + 10
    sheet.paste(body_big, (18, fy), body_big)
    d.text((150, fy+8), "C1B VISUAL PROOF — generated frames are REVIEW CANDIDATES, not promoted production sprites.", fill=TEXT, font=font())
    d.text((150, fy+30), "B3B V4 at left remains the canonical static identity/body-style anchor and was not warped.", fill=DIM, font=font())
    d.text((150, fy+52), "Required review: same woman, coherent anatomy, same left-facing 3/4 family, gait follows C1A skeleton.", fill=DIM, font=font())
    d.text((150, fy+74), "Hair/clothing/accessories remain deferred. No hidden-3D RGB is visible here.", fill=DIM, font=font())

    sheet_path = ws / "g3s_c1b_exilada_walk_contact_sheet.png"
    sheet.save(sheet_path)

    review = {
        "gate": "G3S-C1B",
        "revision": "FLUX2_EIGHT_POSE_VISUAL_REVIEW_V1",
        "status": "REVIEW_REQUIRED",
        "frames": review_rows,
        "gif": str(gif_path),
        "gif_sha256": sha256_file(gif_path),
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": sha256_file(sheet_path),
        "production_promotion": false,
        "note": "Nearest-neighbor 96x160 reductions are inspection views only; generated high-resolution outputs are not mechanically promoted into final sprite art."
    }
    review_path = ws / "g3s_c1b_review.json"
    review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")

    print("G3S-C1B VISUAL REVIEW PACKAGE READY")
    print(f"GIF={gif_path}")
    print(f"SHEET={sheet_path}")
    print(f"REVIEW={review_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
