#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EXPECTED_BODY_SIZE = (37, 128)
EXPECTED_BODY_RAW_RGBA_SHA256 = "818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c"
EXPECTED_BODY_PNG_SHA256 = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"
WORKING_CANVAS = (96, 160)
BODY_GROUND_Y = 152


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_rgba_sha256(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def checkerboard(size: tuple[int, int], tile: int = 8) -> Image.Image:
    w, h = size
    out = Image.new("RGBA", size, (34, 34, 38, 255))
    d = ImageDraw.Draw(out)
    a = (38, 38, 42, 255)
    b = (54, 54, 60, 255)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            d.rectangle((x, y, x + tile - 1, y + tile - 1), fill=a if ((x // tile + y // tile) & 1) == 0 else b)
    return out


def fit_inside(im: Image.Image, box: tuple[int, int]) -> Image.Image:
    bw, bh = box
    scale = min(bw / im.width, bh / im.height)
    nw = max(1, round(im.width * scale))
    nh = max(1, round(im.height * scale))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def paste_center(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    x = x0 + (x1 - x0 - src.width) // 2
    y = y0 + (y1 - y0 - src.height) // 2
    dst.alpha_composite(src, (x, y))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    master_path = Path(args.master)
    body_path = Path(args.body)
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    if not master_path.is_file():
        raise FileNotFoundError(f"canonical Exilada master not found: {master_path}")
    if not body_path.is_file():
        raise FileNotFoundError(f"canonical promoted body base not found: {body_path}")

    body_file_sha = file_sha256(body_path)
    body = Image.open(body_path).convert("RGBA")
    body_raw_sha = raw_rgba_sha256(body)
    if body.size != EXPECTED_BODY_SIZE:
        raise RuntimeError(f"body size mismatch: got={body.size} expected={EXPECTED_BODY_SIZE}")
    if body_file_sha != EXPECTED_BODY_PNG_SHA256:
        raise RuntimeError(f"body PNG SHA mismatch: got={body_file_sha} expected={EXPECTED_BODY_PNG_SHA256}")
    if body_raw_sha != EXPECTED_BODY_RAW_RGBA_SHA256:
        raise RuntimeError(f"body raw RGBA SHA mismatch: got={body_raw_sha} expected={EXPECTED_BODY_RAW_RGBA_SHA256}")

    master = Image.open(master_path).convert("RGBA")
    master_sha = file_sha256(master_path)

    # Shared B4 working frame. This is diagnostic only and does not alter/promote art.
    work = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    bx = (WORKING_CANVAS[0] - body.width) // 2
    by = BODY_GROUND_Y - body.height
    work.alpha_composite(body, (bx, by))
    work_path = workspace / "g3s_b4_body_in_shared_hair_canvas.png"
    work.save(work_path)

    # Review sheet: master identity reference, immutable body base, and explicit depth split.
    sheet = Image.new("RGBA", (1600, 900), (16, 16, 19, 255))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    draw.text((24, 18), "G3S-B4 HAIR PREFLIGHT — REFERENCE + IMMUTABLE BODY + TWO-LAYER DEPTH CONTRACT", fill=(235, 235, 238), font=font)
    draw.text((24, 42), "DIAGNOSTIC ONLY — NO HAIR PIXELS AUTHORED OR PROMOTED IN THIS STEP", fill=(220, 180, 90), font=font)

    # Panel A: canonical master as visual reference only.
    draw.text((24, 78), "A  CANONICAL EXILADA MASTER — HAIR IDENTITY / MASS REFERENCE", fill=(220, 220, 225), font=font)
    master_preview = fit_inside(master, (650, 720))
    paste_center(sheet, master_preview, (20, 110, 700, 850))

    # Panel B: canonical promoted body on shared frame, enlarged nearest-neighbor.
    draw.text((730, 78), "B  PROMOTED B3B BODY — MUST REMAIN PIXEL/BYTE UNCHANGED", fill=(220, 220, 225), font=font)
    work_bg = checkerboard(WORKING_CANVAS)
    work_bg.alpha_composite(work)
    work_big = work_bg.resize((WORKING_CANVAS[0] * 4, WORKING_CANVAS[1] * 4), Image.Resampling.NEAREST)
    paste_center(sheet, work_big, (720, 110, 1160, 850))

    # Panel C: explicit layer-depth contract, no invented hair geometry.
    draw.text((1190, 78), "C  MINIMUM HAIR OWNERSHIP", fill=(220, 220, 225), font=font)
    x0, y0, x1, y1 = 1200, 130, 1560, 720
    draw.rounded_rectangle((x0, y0, x1, y1), radius=12, outline=(100, 100, 110), width=2)
    items = [
        ("FRONT_HAIR", "drawn in front of face/neck/shoulders/body where required"),
        ("BODY", "canonical B3B V4 asset; immutable"),
        ("REAR_HAIR", "drawn behind head/neck/shoulders/back/body"),
    ]
    yy = 180
    for name, desc in items:
        draw.rectangle((1240, yy, 1520, yy + 74), outline=(150, 150, 160), width=2)
        draw.text((1252, yy + 12), name, fill=(240, 240, 244), font=font)
        draw.text((1252, yy + 34), desc, fill=(185, 185, 192), font=font)
        yy += 122
    draw.text((1200, 755), "Shared review canvas: 96×160; body ground anchor y=152", fill=(190, 190, 196), font=font)
    draw.text((1200, 778), "Canvas size is provisional until master/body visual inspection.", fill=(190, 190, 196), font=font)
    draw.text((1200, 801), "At least two persistent transparent PNG layers are mandatory.", fill=(190, 190, 196), font=font)

    sheet_path = workspace / "g3s_b4_hair_preflight_contact_sheet.png"
    sheet.convert("RGB").save(sheet_path, quality=95)

    meta = {
        "gate": "G3S-B4",
        "revision": "B4A_HAIR_PREFLIGHT_V1",
        "status": "REVIEW_REQUIRED",
        "master": str(master_path),
        "master_sha256": master_sha,
        "master_dimensions": list(master.size),
        "body": str(body_path),
        "body_png_sha256": body_file_sha,
        "body_raw_rgba_sha256": body_raw_sha,
        "body_dimensions": list(body.size),
        "shared_working_canvas": list(WORKING_CANVAS),
        "body_ground_y": BODY_GROUND_Y,
        "minimum_layer_order_back_to_front": ["rear_hair", "body", "front_hair"],
        "purpose": "inspect canonical hair identity reference against the promoted native body and lock B4 layer geometry before authoring hair pixels",
        "production_art_created": False,
        "automatic_promotion": False,
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": file_sha256(sheet_path),
    }
    meta_path = workspace / "g3s_b4_hair_preflight.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"MASTER:      {master_path}")
    print(f"MASTER SHA:  {master_sha}")
    print(f"MASTER SIZE: {master.size[0]}x{master.size[1]}")
    print(f"BODY:        {body_path}")
    print(f"BODY SHA:    {body_file_sha}")
    print(f"WORK FRAME:  {WORKING_CANVAS[0]}x{WORKING_CANVAS[1]}")
    print(f"CONTACT:     {sheet_path}")
    print(f"META:        {meta_path}")
    print("STATUS: REVIEW REQUIRED — SHARE CONTACT SHEET; NO HAIR ART PROMOTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
