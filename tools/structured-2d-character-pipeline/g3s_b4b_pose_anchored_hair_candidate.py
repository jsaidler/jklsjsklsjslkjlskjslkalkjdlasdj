#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
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

# Warm-neutral black ramp, deliberately compact for 1x readability.
OUTLINE = (3, 4, 6, 255)
DEEP = (7, 8, 11, 255)
BASE = (11, 12, 16, 255)
BASE2 = (16, 17, 21, 255)
MID = (22, 23, 28, 255)
MID2 = (29, 30, 35, 255)
HIGH = (39, 39, 44, 255)
HIGH2 = (50, 49, 53, 255)
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
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.Resampling.LANCZOS)


def paste_center(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    dst.alpha_composite(src, (x0 + (x1 - x0 - src.width) // 2, y0 + (y1 - y0 - src.height) // 2))


def opaque_count(im: Image.Image) -> int:
    return sum(1 for a in im.getchannel("A").getdata() if a)


def row_span(alpha: Image.Image, y: int) -> tuple[int, int] | None:
    p = alpha.load()
    xs = [x for x in range(alpha.width) if p[x, y] > 0]
    if not xs:
        return None
    return min(xs), max(xs)


def weighted_center(alpha: Image.Image, y0: int, y1: int) -> float:
    p = alpha.load()
    xs: list[int] = []
    for y in range(max(0, y0), min(alpha.height, y1 + 1)):
        for x in range(alpha.width):
            if p[x, y] > 0:
                xs.append(x)
    if not xs:
        return (alpha.width - 1) / 2.0
    return sum(xs) / len(xs)


def detect_pose_anchors(body: Image.Image) -> dict[str, float | int]:
    alpha = body.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("canonical body alpha is empty")
    x0, y0, x1, y1 = bbox
    h = y1 - y0
    if h < 100:
        raise RuntimeError(f"body alpha height implausible: {h}")

    head_end = y0 + round(h * 0.20)
    head_cx = weighted_center(alpha, y0, head_end)

    shoulder_start = y0 + round(h * 0.14)
    shoulder_end = y0 + round(h * 0.35)
    shoulder_rows: list[tuple[int, int, int, int]] = []
    for y in range(shoulder_start, min(alpha.height, shoulder_end + 1)):
        span = row_span(alpha, y)
        if span is None:
            continue
        left, right = span
        shoulder_rows.append((right - left + 1, y, left, right))
    if not shoulder_rows:
        raise RuntimeError("could not detect shoulder span from canonical body")
    _, shoulder_y, shoulder_left, shoulder_right = max(shoulder_rows)

    torso_start = y0 + round(h * 0.28)
    torso_end = y0 + round(h * 0.52)
    torso_cx = weighted_center(alpha, torso_start, torso_end)

    head_rows = []
    for y in range(y0, min(alpha.height, head_end + 1)):
        span = row_span(alpha, y)
        if span is not None:
            head_rows.append(span)
    head_left = min(s[0] for s in head_rows)
    head_right = max(s[1] for s in head_rows)

    # The production body is a 3/4 view. Head-vs-torso displacement gives a first
    # orientation cue; if nearly centered, fall back to the canonical view's left-facing bias.
    delta = head_cx - torso_cx
    if delta < -0.35:
        facing = -1
    elif delta > 0.35:
        facing = 1
    else:
        facing = -1
    back_side = -facing

    return {
        "body_top": y0,
        "body_bottom": y1 - 1,
        "body_height": h,
        "head_cx": head_cx,
        "head_left": head_left,
        "head_right": head_right,
        "head_top": y0,
        "head_bottom": head_end,
        "shoulder_y": shoulder_y,
        "shoulder_left": shoulder_left,
        "shoulder_right": shoulder_right,
        "torso_cx": torso_cx,
        "facing": facing,
        "back_side": back_side,
    }


def wpt(x: float, y: float) -> tuple[int, int]:
    return round(BODY_X + x), round(BODY_Y + y)


def tapered_polygon(points: list[tuple[float, float]], widths: list[float]) -> list[tuple[int, int]]:
    if len(points) != len(widths) or len(points) < 2:
        raise ValueError("tapered polygon points/widths mismatch")
    left: list[tuple[int, int]] = []
    right: list[tuple[int, int]] = []
    for i, ((x, y), width) in enumerate(zip(points, widths)):
        if i == 0:
            tx, ty = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            tx, ty = x - points[i - 1][0], y - points[i - 1][1]
        else:
            tx, ty = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        mag = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / mag, tx / mag
        hw = width / 2.0
        left.append(wpt(x + nx * hw, y + ny * hw))
        right.append(wpt(x - nx * hw, y - ny * hw))
    return left + list(reversed(right))


def draw_lock(layer: Image.Image, points: list[tuple[float, float]], widths: list[float], fill, highlight=None) -> None:
    d = ImageDraw.Draw(layer)
    poly = tapered_polygon(points, widths)
    d.polygon(poly, fill=fill, outline=OUTLINE)
    if highlight is not None and len(points) >= 3:
        hpts = [wpt(x - 0.6, y) for x, y in points[1:-1]]
        if len(hpts) >= 2:
            d.line(hpts, fill=highlight, width=1)


def authored_hair_from_body_pose(body: Image.Image, anchors: dict[str, float | int]) -> tuple[Image.Image, Image.Image]:
    rear = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    front = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rear)
    fd = ImageDraw.Draw(front)

    hc = float(anchors["head_cx"])
    hl = float(anchors["head_left"])
    hr = float(anchors["head_right"])
    ht = float(anchors["head_top"])
    hb = float(anchors["head_bottom"])
    sy = float(anchors["shoulder_y"])
    sl = float(anchors["shoulder_left"])
    sr = float(anchors["shoulder_right"])
    tc = float(anchors["torso_cx"])
    bh = float(anchors["body_height"])
    facing = int(anchors["facing"])
    back = int(anchors["back_side"])

    front_edge = sl if facing < 0 else sr
    back_edge = sr if back > 0 else sl
    front_s = -1 if facing < 0 else 1
    back_s = -front_s

    # Rear crown sits behind the actual detected production head, not the master pose.
    rear_crown = [
        wpt(hc - 6, ht + 1),
        wpt(hc - 2, ht - 2),
        wpt(hc + 4, ht - 1),
        wpt(hc + back_s * 7, ht + 4),
        wpt(hc + back_s * 9, hb + 2),
        wpt(tc + back_s * 8, sy + 7),
        wpt(tc + front_s * 5, sy + 6),
        wpt(hc + front_s * 6, hb + 1),
    ]
    rd.polygon(rear_crown, fill=DEEP, outline=OUTLINE)

    # Four broad rear locks anchored to the production pose. The back-side locks are
    # deliberately longer/heavier; the facing side remains lighter so the 3/4 body reads.
    draw_lock(
        rear,
        [(hc + back_s * 3, ht + 4), (back_edge + back_s * 5, sy + 5),
         (tc + back_s * 12, sy + 28), (tc + back_s * 15, sy + 55),
         (tc + back_s * 13, ht + bh * 0.78)],
        [9, 12, 13, 11, 5], BASE2, HIGH,
    )
    draw_lock(
        rear,
        [(hc + back_s * 1, ht + 3), (tc + back_s * 4, sy + 2),
         (tc + back_s * 5, sy + 24), (tc + back_s * 3, sy + 48),
         (tc + back_s * 5, ht + bh * 0.70)],
        [8, 11, 11, 9, 4], BASE, MID2,
    )
    draw_lock(
        rear,
        [(hc + front_s * 3, ht + 5), (front_edge + front_s * 3, sy + 4),
         (tc + front_s * 8, sy + 24), (tc + front_s * 9, sy + 44),
         (tc + front_s * 7, ht + bh * 0.61)],
        [7, 9, 9, 7, 3], BASE2, MID,
    )
    draw_lock(
        rear,
        [(hc + back_s * 5, ht + 7), (back_edge + back_s * 8, sy + 11),
         (tc + back_s * 16, sy + 32), (tc + back_s * 18, sy + 51),
         (tc + back_s * 16, ht + bh * 0.67)],
        [6, 8, 8, 6, 3], BASE, HIGH2,
    )

    # Broken rear edge tufts, also relative to actual shoulders.
    rd.polygon([wpt(back_edge + back_s * 4, sy - 1), wpt(back_edge + back_s * 10, sy + 2),
                wpt(back_edge + back_s * 6, sy + 6), wpt(back_edge + back_s * 12, sy + 9),
                wpt(back_edge + back_s * 4, sy + 10)], fill=BASE2, outline=OUTLINE)
    rd.polygon([wpt(front_edge + front_s * 2, sy + 3), wpt(front_edge + front_s * 7, sy + 6),
                wpt(front_edge + front_s * 4, sy + 10), wpt(front_edge + front_s * 8, sy + 13),
                wpt(front_edge + front_s * 2, sy + 13)], fill=BASE, outline=OUTLINE)

    # Front scalp cap follows the detected head bbox. It covers the bald scalp but leaves
    # the actual facing-side face opening substantially visible.
    cap = [
        wpt(hl - 1, ht + 5),
        wpt(hc - 3, ht),
        wpt(hc + 3, ht - 1),
        wpt(hr + 2, ht + 4),
        wpt(hr + 2, hb - 2),
        wpt(hc + back_s * 4, hb + 1),
        wpt(hc + front_s * 1, hb - 2),
        wpt(hl + 1, hb - 3),
    ]
    fd.polygon(cap, fill=BASE, outline=OUTLINE)

    # Facing-side temple lock: follows actual head/shoulder coordinates and stops around chest.
    draw_lock(
        front,
        [(hc + front_s * 4, ht + 6), (hl if facing < 0 else hr, hb - 1),
         (front_edge + front_s * 1, sy + 9), (front_edge + front_s * 1, sy + 26),
         (tc + front_s * 7, sy + 38)],
        [5, 6, 6, 5, 2], BASE2, HIGH,
    )

    # Back-side shoulder lock: longer but lateral; it does not cover the torso center.
    draw_lock(
        front,
        [(hc + back_s * 4, ht + 6), (hr if back > 0 else hl, hb),
         (back_edge + back_s * 1, sy + 7), (back_edge + back_s * 2, sy + 23),
         (tc + back_s * 9, sy + 39), (tc + back_s * 10, sy + 54)],
        [5, 6, 6, 5, 4, 2], BASE2, MID2,
    )

    # One narrow inner lock near cheek/neck, intentionally short.
    draw_lock(
        front,
        [(hc + front_s * 1, ht + 5), (hc + front_s * 2, hb - 2),
         (tc + front_s * 3, sy + 4), (tc + front_s * 2, sy + 17)],
        [4, 4, 3, 1.5], BASE, HIGH2,
    )

    # Wild silhouette tufts tied to the measured scalp, not fixed master coordinates.
    fd.polygon([wpt(hc + front_s * 5, ht + 2), wpt(hc + front_s * 9, ht + 1),
                wpt(hc + front_s * 7, ht + 5), wpt(hc + front_s * 10, ht + 7),
                wpt(hc + front_s * 5, ht + 8)], fill=DEEP, outline=OUTLINE)
    fd.polygon([wpt(hc + back_s * 5, ht + 1), wpt(hc + back_s * 9, ht - 1),
                wpt(hc + back_s * 7, ht + 4), wpt(hc + back_s * 11, ht + 5),
                wpt(hc + back_s * 5, ht + 7)], fill=BASE2, outline=OUTLINE)

    return rear, front


def body_work(body: Image.Image) -> Image.Image:
    out = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    out.alpha_composite(body, (BODY_X, BODY_Y))
    return out


def composite_layers(body_layer: Image.Image, rear: Image.Image, front: Image.Image) -> Image.Image:
    out = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    out.alpha_composite(rear)
    out.alpha_composite(body_layer)
    out.alpha_composite(front)
    return out


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


def anchor_review(body_layer: Image.Image, anchors: dict[str, float | int]) -> Image.Image:
    out = body_layer.copy()
    d = ImageDraw.Draw(out)
    hc = wpt(float(anchors["head_cx"]), float(anchors["head_top"]) + 7)
    sl = wpt(float(anchors["shoulder_left"]), float(anchors["shoulder_y"]))
    sr = wpt(float(anchors["shoulder_right"]), float(anchors["shoulder_y"]))
    tc = wpt(float(anchors["torso_cx"]), float(anchors["shoulder_y"]) + 18)
    d.ellipse((hc[0]-1,hc[1]-1,hc[0]+1,hc[1]+1), fill=(255,220,70,255))
    d.line([sl, sr], fill=(90,220,255,255), width=1)
    d.ellipse((tc[0]-1,tc[1]-1,tc[0]+1,tc[1]+1), fill=(255,90,180,255))
    return out


def make_contact_sheet(master: Image.Image, anchored_body: Image.Image, rear: Image.Image,
                       front: Image.Image, composite: Image.Image, gameplay: Image.Image,
                       anchors: dict[str, float | int], out: Path) -> None:
    sheet = Image.new("RGBA", (1600, 900), (16, 16, 19, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    d.text((24, 18), "G3S-B4B V4 POSE-ANCHORED TWO-LAYER HAIR REVIEW", fill=(238,238,242), font=font)
    d.text((24, 42), "V3 CLOSED: MASTER/PRODUCTION POSE MISMATCH. V4 AUTHORS FROM ACTUAL B3B BODY ANCHORS.", fill=(220,180,90), font=font)
    d.text((24, 64), "COMPOSITION: rear_hair -> immutable body -> front_hair", fill=(220,220,225), font=font)

    d.text((24, 96), "A  MASTER / IDENTITY + MATERIAL ONLY", fill=(220,220,225), font=font)
    mp = fit_inside(master, (360, 650))
    paste_center(sheet, mp, (20, 120, 400, 810))

    def panel(layer: Image.Image, title: str, x: int, y: int, scale: int = 3) -> None:
        d.text((x, y-24), title, fill=(220,220,225), font=font)
        bg = checkerboard(layer.size)
        bg.alpha_composite(layer)
        big = bg.resize((layer.width*scale, layer.height*scale), Image.Resampling.NEAREST)
        sheet.alpha_composite(big, (x, y))

    panel(anchored_body, "B  ACTUAL B3B BODY + DETECTED POSE ANCHORS", 420, 140)
    panel(rear, "C  rear_hair / POSE-ANCHORED", 730, 140)
    panel(front, "D  front_hair / POSE-ANCHORED", 1040, 140)
    panel(composite, "E  COMPOSITE 3x", 1290, 140)

    d.text((420, 650), "F  NATIVE 640x360 GAMEPLAY PREVIEW", fill=(220,220,225), font=font)
    sheet.alpha_composite(gameplay, (420, 680))

    d.text((1090, 650), "G  DETECTED BODY-POSE CONTRACT", fill=(220,220,225), font=font)
    facts = [
        f"head_cx={float(anchors['head_cx']):.2f}",
        f"shoulder_y={int(anchors['shoulder_y'])} span={int(anchors['shoulder_left'])}..{int(anchors['shoulder_right'])}",
        f"torso_cx={float(anchors['torso_cx']):.2f}",
        f"facing={'viewer-left' if int(anchors['facing']) < 0 else 'viewer-right'}",
        "master pose coordinates used for hair placement: NO",
        "body canonical B3B V4 byte/pixel unchanged: YES",
        "external paid API/model: NO",
        "automatic promotion: NO",
    ]
    yy = 684
    for fact in facts:
        d.text((1090, yy), fact, fill=(190,190,196), font=font)
        yy += 22

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

    body = Image.open(body_path).convert("RGBA")
    if body.size != EXPECTED_BODY_SIZE:
        raise RuntimeError(f"body size mismatch: got={body.size} expected={EXPECTED_BODY_SIZE}")
    if file_sha256(body_path) != EXPECTED_BODY_PNG_SHA256:
        raise RuntimeError("canonical body PNG SHA mismatch")
    if raw_rgba_sha256(body) != EXPECTED_BODY_RAW_RGBA_SHA256:
        raise RuntimeError("canonical body raw-RGBA SHA mismatch")

    preflight = json.loads(preflight_meta_path.read_text(encoding="utf-8"))
    expected_master_sha = preflight.get("master_sha256")
    if not expected_master_sha:
        raise RuntimeError("preflight metadata has no master_sha256")
    master_sha = file_sha256(master_path)
    if master_sha != expected_master_sha:
        raise RuntimeError(f"canonical master changed since B4A preflight: got={master_sha} expected={expected_master_sha}")
    master = Image.open(master_path).convert("RGBA")

    anchors = detect_pose_anchors(body)
    rear, front = authored_hair_from_body_pose(body, anchors)
    bw = body_work(body)
    comp = composite_layers(bw, rear, front)
    gameplay = gameplay_preview(comp)
    anchored = anchor_review(bw, anchors)

    if opaque_count(rear) < 350:
        raise RuntimeError("rear_hair implausibly small")
    if opaque_count(front) < 90:
        raise RuntimeError("front_hair implausibly small")
    if opaque_count(front) >= opaque_count(rear):
        raise RuntimeError("V4 contract violated: front hair must remain subordinate to rear hair")

    rear_path = workspace / "g3s_b4b_rear_hair_candidate.png"
    front_path = workspace / "g3s_b4b_front_hair_candidate.png"
    comp_path = workspace / "g3s_b4b_body_hair_composite.png"
    gameplay_path = workspace / "g3s_b4b_gameplay_preview.png"
    sheet_path = workspace / "g3s_b4b_contact_sheet.png"
    meta_path = workspace / "g3s_b4b_two_layer_hair_candidate.json"

    rear.save(rear_path)
    front.save(front_path)
    comp.save(comp_path)
    gameplay.save(gameplay_path)
    make_contact_sheet(master, anchored, rear, front, comp, gameplay, anchors, sheet_path)

    meta = {
        "gate": "G3S-B4",
        "revision": "B4B_AUTHORED_TWO_LAYER_HAIR_V4_POSE_ANCHORED",
        "status": "REVIEW_REQUIRED",
        "method": "new native-pixel hair authored from measured canonical B3B body pose anchors; master is identity/style inspiration only",
        "working_canvas": list(WORKING_CANVAS),
        "body_anchor": {"x": BODY_X, "y": BODY_Y, "ground_y": BODY_GROUND_Y},
        "detected_pose_anchors": anchors,
        "body_png_sha256": EXPECTED_BODY_PNG_SHA256,
        "body_raw_rgba_sha256": EXPECTED_BODY_RAW_RGBA_SHA256,
        "master_sha256": master_sha,
        "composition_order": ["rear_hair", "body", "front_hair"],
        "rear_hair_opaque_pixels": opaque_count(rear),
        "front_hair_opaque_pixels": opaque_count(front),
        "palette": [list(c) for c in PALETTE],
        "critical_v3_correction": [
            "master pose coordinates no longer drive hair placement",
            "head center, shoulder span, torso center and facing bias are measured from the actual production body",
            "rear/front geometry is authored relative to those production-pose anchors",
            "contact sheet exposes detected pose anchors for review"
        ],
        "automatic_promotion": False,
        "outputs": {
            "rear_hair": str(rear_path),
            "front_hair": str(front_path),
            "composite": str(comp_path),
            "gameplay_preview": str(gameplay_path),
            "contact_sheet": str(sheet_path)
        },
        "contact_sheet_sha256": file_sha256(sheet_path)
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("G3S-B4B V4: POSE-ANCHORED REVIEW PACKAGE READY")
    print(f"POSE: head_cx={float(anchors['head_cx']):.2f} shoulders={int(anchors['shoulder_left'])}..{int(anchors['shoulder_right'])}@y={int(anchors['shoulder_y'])} torso_cx={float(anchors['torso_cx']):.2f} facing={int(anchors['facing'])}")
    print(f"REAR:    {rear_path}")
    print(f"FRONT:   {front_path}")
    print(f"CONTACT: {sheet_path}")
    print(f"META:    {meta_path}")
    print("STOP. Share the contact sheet. Do not promote hair and do not start B5/C.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
