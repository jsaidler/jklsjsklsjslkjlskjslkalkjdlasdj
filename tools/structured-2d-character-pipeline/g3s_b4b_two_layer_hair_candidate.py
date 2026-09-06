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
BODY_X = (WORKING_CANVAS[0] - EXPECTED_BODY_SIZE[0]) // 2
BODY_Y = BODY_GROUND_Y - EXPECTED_BODY_SIZE[1]
GAMEPLAY_CANVAS = (640, 360)

# Native-pixel palette: deliberately dark, low-chroma, and compact.
OUTLINE = (4, 5, 7, 255)
DEEP = (8, 10, 13, 255)
BASE = (13, 15, 19, 255)
BASE2 = (18, 20, 24, 255)
MID = (24, 26, 31, 255)
MID2 = (31, 33, 38, 255)
HIGH = (42, 43, 48, 255)
HIGH2 = (54, 53, 57, 255)
PALETTE = [OUTLINE, DEEP, BASE, BASE2, MID, MID2, HIGH, HIGH2]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_rgba_sha256(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def checkerboard(size: tuple[int, int], tile: int = 8) -> Image.Image:
    out = Image.new("RGBA", size, (30, 30, 34, 255))
    d = ImageDraw.Draw(out)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            c = (38, 38, 42, 255) if ((x // tile + y // tile) & 1) == 0 else (55, 55, 60, 255)
            d.rectangle((x, y, x + tile - 1, y + tile - 1), fill=c)
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


def draw_lock(
    layer: Image.Image,
    points: list[tuple[int, int]],
    widths: list[int],
    fill: tuple[int, int, int, int],
    highlight: tuple[int, int, int, int] | None = None,
    highlight_offset: tuple[int, int] = (-1, 0),
) -> None:
    if len(points) < 2 or len(points) != len(widths):
        raise ValueError("lock points/widths mismatch")
    d = ImageDraw.Draw(layer)
    for i in range(len(points) - 1):
        p0, p1 = points[i], points[i + 1]
        w = max(1, round((widths[i] + widths[i + 1]) / 2))
        d.line([p0, p1], fill=OUTLINE, width=w + 2)
        d.line([p0, p1], fill=fill, width=w)
    for p, w in zip(points, widths):
        r = max(1, w // 2)
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill, outline=OUTLINE)
    if highlight is not None and len(points) >= 3:
        hx, hy = highlight_offset
        hp = [(x + hx, y + hy) for x, y in points[1:-1]]
        if len(hp) >= 2:
            d.line(hp, fill=highlight, width=1)


def authored_rear_hair() -> Image.Image:
    layer = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Main rear mass: authored from the identity language of the master, not copied from it.
    outer = [
        (43, 17), (36, 18), (30, 22), (25, 29), (21, 39), (18, 51),
        (19, 64), (16, 76), (18, 91), (20, 105), (25, 119), (31, 111),
        (34, 98), (38, 84), (42, 70), (47, 60), (52, 66), (57, 79),
        (62, 94), (66, 108), (71, 120), (76, 112), (78, 98), (76, 83),
        (78, 69), (75, 54), (72, 41), (68, 30), (61, 21), (53, 17),
    ]
    inner = [
        (43, 20), (36, 22), (30, 28), (27, 37), (25, 50), (25, 67),
        (24, 83), (27, 99), (31, 104), (35, 92), (39, 76), (44, 62),
        (49, 55), (54, 63), (59, 78), (63, 94), (68, 105), (71, 96),
        (70, 82), (72, 67), (68, 51), (65, 37), (59, 27), (51, 21),
    ]
    d.polygon(outer, fill=OUTLINE)
    d.polygon(inner, fill=DEEP)

    rear_locks = [
        ([(34, 22), (27, 34), (23, 49), (25, 65), (21, 81), (24, 99), (22, 114)], [7,7,7,6,6,5,3], BASE, MID2),
        ([(40, 20), (33, 34), (31, 49), (34, 63), (30, 79), (33, 96), (29, 110)], [8,8,7,7,6,5,3], BASE2, HIGH),
        ([(45, 19), (39, 31), (37, 46), (41, 59), (38, 75), (41, 91), (37, 105)], [8,8,7,6,6,5,3], BASE, MID),
        ([(50, 19), (45, 31), (44, 43), (48, 55), (46, 70), (49, 84), (46, 99)], [8,8,7,6,6,5,3], BASE2, HIGH),
        ([(55, 20), (53, 32), (55, 45), (53, 59), (57, 74), (55, 90), (59, 105)], [8,8,7,7,6,5,3], BASE, MID2),
        ([(60, 22), (61, 35), (59, 49), (63, 63), (61, 79), (66, 94), (66, 111)], [8,8,7,7,6,5,3], BASE2, HIGH),
        ([(65, 26), (68, 39), (66, 54), (71, 69), (69, 85), (73, 101), (71, 116)], [7,7,7,6,6,5,3], BASE, MID),
        ([(29, 28), (23, 41), (22, 55), (19, 68), (21, 82), (18, 97), (22, 109)], [6,6,6,5,5,4,2], DEEP, MID),
        ([(68, 30), (73, 43), (71, 57), (75, 71), (73, 85), (76, 99), (73, 112)], [6,6,6,5,5,4,2], DEEP, MID),
    ]
    for pts, widths, fill, hi in rear_locks:
        draw_lock(layer, pts, widths, fill, hi)

    # Coarse value grouping only; no strand-level noise.
    d.line([(28, 39), (25, 56), (27, 73), (25, 89)], fill=HIGH2, width=1)
    d.line([(37, 30), (34, 49), (37, 65), (34, 82)], fill=HIGH, width=1)
    d.line([(48, 27), (47, 43), (50, 59), (48, 75)], fill=MID2, width=1)
    d.line([(60, 31), (62, 47), (61, 64), (65, 81)], fill=HIGH, width=1)
    d.line([(69, 41), (70, 57), (72, 72), (70, 89)], fill=MID2, width=1)
    return layer


def authored_front_hair() -> Image.Image:
    layer = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Crown/framing mass. The face remains intentionally open enough for gameplay readability.
    crown_outer = [(35, 20), (40, 16), (49, 15), (57, 18), (63, 24), (64, 31), (61, 38), (56, 40), (54, 34), (51, 28), (47, 25), (43, 27), (40, 34), (35, 37), (32, 32), (32, 25)]
    crown_inner = [(38, 21), (42, 18), (49, 18), (55, 20), (60, 24), (61, 29), (58, 34), (55, 35), (53, 30), (49, 23), (44, 23), (41, 29), (38, 33), (35, 31), (35, 25)]
    d.polygon(crown_outer, fill=OUTLINE)
    d.polygon(crown_inner, fill=BASE)

    front_locks = [
        ([(38, 23), (35, 34), (33, 46), (36, 58), (34, 71), (37, 84), (34, 96)], [6,6,5,5,4,4,2], BASE2, HIGH),
        ([(42, 21), (40, 31), (42, 41), (39, 52), (42, 63), (40, 75), (43, 86)], [6,6,5,5,4,4,2], BASE, MID2),
        ([(55, 20), (58, 31), (57, 42), (60, 53), (58, 65), (62, 76), (60, 90)], [6,6,5,5,4,4,2], BASE2, HIGH),
        ([(59, 22), (63, 33), (61, 45), (65, 57), (63, 69), (67, 81)], [6,6,5,5,4,3], BASE, MID),
        ([(45, 20), (44, 29), (46, 37), (44, 46), (46, 55), (45, 65)], [5,5,4,4,3,2], BASE2, HIGH2),
        ([(50, 19), (52, 28), (50, 36), (53, 45), (51, 54), (54, 64)], [5,5,4,4,3,2], BASE, MID2),
    ]
    for pts, widths, fill, hi in front_locks:
        draw_lock(layer, pts, widths, fill, hi)

    # A few broken edge tufts so the silhouette reads messy rather than salon-groomed.
    d.polygon([(31,25),(28,23),(30,29),(27,31),(33,32)], fill=DEEP)
    d.polygon([(62,22),(66,21),(64,26),(68,28),(62,30)], fill=BASE)
    d.polygon([(35,38),(31,41),(34,43),(30,47),(36,46)], fill=BASE2)
    d.polygon([(61,39),(66,42),(63,45),(67,49),(61,48)], fill=BASE)
    return layer


def compose(body: Image.Image, rear: Image.Image, front: Image.Image) -> tuple[Image.Image, Image.Image]:
    body_work = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    body_work.alpha_composite(body, (BODY_X, BODY_Y))
    composite = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    composite.alpha_composite(rear)
    composite.alpha_composite(body_work)
    composite.alpha_composite(front)
    return body_work, composite


def gameplay_preview(composite: Image.Image) -> Image.Image:
    scene = Image.new("RGBA", GAMEPLAY_CANVAS, (18, 18, 21, 255))
    d = ImageDraw.Draw(scene)
    ground_y = 286
    d.rectangle((0, ground_y, GAMEPLAY_CANVAS[0], GAMEPLAY_CANVAS[1]), fill=(38, 31, 27, 255))
    bbox = composite.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError("empty body+hair composite")
    crop = composite.crop(bbox)
    x = GAMEPLAY_CANVAS[0] // 2 - crop.width // 2
    y = ground_y - crop.height
    scene.alpha_composite(crop, (x, y))
    return scene


def make_contact_sheet(master: Image.Image, rear: Image.Image, body_work: Image.Image, front: Image.Image, composite: Image.Image, gameplay: Image.Image, out: Path) -> None:
    sheet = Image.new("RGBA", (1600, 900), (16, 16, 19, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    d.text((24, 18), "G3S-B4B V2 AUTHORED TWO-LAYER HAIR REVIEW", fill=(238,238,242), font=font)
    d.text((24, 42), "MASTER = IDENTITY INSPIRATION ONLY; HAIR PIXELS ARE NEW NATIVE-PIXEL AUTHORING", fill=(220,180,90), font=font)
    d.text((24, 64), "COMPOSITION: rear_hair -> immutable body -> front_hair", fill=(220,220,225), font=font)

    d.text((24, 96), "A  CANONICAL MASTER / HAIR IDENTITY", fill=(220,220,225), font=font)
    mp = fit_inside(master, (390, 690))
    paste_center(sheet, mp, (20, 120, 430, 830))

    def layer_panel(layer: Image.Image, title: str, x: int, y: int, scale: int = 3):
        d.text((x, y - 24), title, fill=(220,220,225), font=font)
        bg = checkerboard(layer.size)
        bg.alpha_composite(layer)
        big = bg.resize((layer.width * scale, layer.height * scale), Image.Resampling.NEAREST)
        sheet.alpha_composite(big, (x, y))

    layer_panel(rear, "B  rear_hair / NEW AUTHORED PIXELS", 470, 140, 3)
    layer_panel(front, "C  front_hair / NEW AUTHORED PIXELS", 790, 140, 3)
    layer_panel(composite, "D  COMPOSITE 3x", 1110, 140, 3)

    d.text((470, 650), "E  NATIVE 640x360 GAMEPLAY PREVIEW", fill=(220,220,225), font=font)
    gp = gameplay.resize((640, 360), Image.Resampling.NEAREST)
    sheet.alpha_composite(gp, (470, 680))

    d.text((1140, 650), "F  STRUCTURAL CONTRACT", fill=(220,220,225), font=font)
    notes = [
        "rear_hair: new geometry behind head/shoulders/back",
        "body: canonical B3B V4, byte/pixel unchanged",
        "front_hair: new geometry crossing face/neck/chest",
        "master pixels used in hair layers: NO",
        "external paid API/model: NO",
        "automatic promotion: NO",
    ]
    yy = 682
    for line in notes:
        d.text((1140, yy), line, fill=(190,190,196), font=font)
        yy += 24

    sheet.convert("RGB").save(out, quality=95)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--preflight-meta", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    master_path = Path(args.master)
    body_path = Path(args.body)
    preflight_meta_path = Path(args.preflight_meta)
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    for p in (master_path, body_path, preflight_meta_path):
        if not p.is_file():
            raise FileNotFoundError(p)

    body_file_sha = file_sha256(body_path)
    body = Image.open(body_path).convert("RGBA")
    body_raw_sha = raw_rgba_sha256(body)
    if body.size != EXPECTED_BODY_SIZE:
        raise RuntimeError(f"body size mismatch: got={body.size} expected={EXPECTED_BODY_SIZE}")
    if body_file_sha != EXPECTED_BODY_PNG_SHA256:
        raise RuntimeError(f"body PNG SHA mismatch: got={body_file_sha} expected={EXPECTED_BODY_PNG_SHA256}")
    if body_raw_sha != EXPECTED_BODY_RAW_RGBA_SHA256:
        raise RuntimeError(f"body raw RGBA SHA mismatch: got={body_raw_sha} expected={EXPECTED_BODY_RAW_RGBA_SHA256}")

    preflight = json.loads(preflight_meta_path.read_text(encoding="utf-8"))
    master_sha = file_sha256(master_path)
    expected_master_sha = preflight.get("master_sha256")
    if expected_master_sha and master_sha != expected_master_sha:
        raise RuntimeError(f"master changed since B4A preflight: got={master_sha} expected={expected_master_sha}")
    master = Image.open(master_path).convert("RGBA")

    rear = authored_rear_hair()
    front = authored_front_hair()
    body_work, composite = compose(body, rear, front)
    gameplay = gameplay_preview(composite)

    if rear.getchannel("A").getbbox() is None or front.getchannel("A").getbbox() is None:
        raise RuntimeError("authored hair layer is unexpectedly empty")
    if raw_rgba_sha256(body) != EXPECTED_BODY_RAW_RGBA_SHA256:
        raise RuntimeError("body changed during B4B")

    rear_path = workspace / "g3s_b4b_rear_hair_candidate.png"
    front_path = workspace / "g3s_b4b_front_hair_candidate.png"
    body_path_out = workspace / "g3s_b4b_body_on_canvas.png"
    composite_path = workspace / "g3s_b4b_body_hair_composite.png"
    gameplay_path = workspace / "g3s_b4b_gameplay_preview.png"
    contact_path = workspace / "g3s_b4b_contact_sheet.png"

    rear.save(rear_path)
    front.save(front_path)
    body_work.save(body_path_out)
    composite.save(composite_path)
    gameplay.save(gameplay_path)
    make_contact_sheet(master, rear, body_work, front, composite, gameplay, contact_path)

    meta = {
        "gate": "G3S-B4B",
        "revision": "B4B_V2_AUTHORED_TWO_LAYER_STATIC",
        "status": "REVIEW_REQUIRED",
        "date": "2026-09-06",
        "working_canvas": list(WORKING_CANVAS),
        "body_ground_y": BODY_GROUND_Y,
        "body_png_sha256": body_file_sha,
        "body_raw_rgba_sha256": body_raw_sha,
        "master_sha256": master_sha,
        "master_role": "identity/mass inspiration only; no master pixels are copied into hair assets",
        "composition_order": ["rear_hair", "body", "front_hair"],
        "rear_hair": str(rear_path),
        "rear_hair_raw_rgba_sha256": raw_rgba_sha256(rear),
        "front_hair": str(front_path),
        "front_hair_raw_rgba_sha256": raw_rgba_sha256(front),
        "composite": str(composite_path),
        "gameplay_preview": str(gameplay_path),
        "contact_sheet": str(contact_path),
        "contact_sheet_sha256": file_sha256(contact_path),
        "palette_rgba": [list(c) for c in PALETTE],
        "master_pixels_used_for_hair": False,
        "external_paid_api_used": False,
        "external_model_used": False,
        "automatic_promotion": False,
        "body_modified": False,
        "notes": "Both mandatory hair depth layers are newly authored at the native pixel grid. Rear hair includes new coverage behind head, shoulders and back that is not recoverable from the canonical master."
    }
    meta_path = workspace / "g3s_b4b_two_layer_hair_candidate.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"MASTER:       {master_path}")
    print(f"MASTER SHA:   {master_sha}")
    print(f"BODY SHA:     {body_file_sha}")
    print(f"REAR HAIR:    {rear_path}")
    print(f"FRONT HAIR:   {front_path}")
    print(f"COMPOSITE:    {composite_path}")
    print(f"GAMEPLAY:     {gameplay_path}")
    print(f"CONTACT:      {contact_path}")
    print(f"META:         {meta_path}")
    print("STATUS: REVIEW REQUIRED — NEW TWO-LAYER HAIR PIXELS AUTHORED; NOTHING PROMOTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
